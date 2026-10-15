"""Four-player host-authoritative coop, lobby, builds, cinematics and result sync."""
import errno
import select
import socket
import time
import uuid
import math
import traceback
from entities import V
from session import GameSession
from netcode import Peer,VERSION,PORT,address,movement,local_addresses,socket_message
from network_log import event
from netstate import snapshot,restore
from cinematics import Cinematic
from maps import MAPS
from settings import CHARACTERS
import upgrades
import progression
import missions

def profile(save,key):
    return {'key':key,'meta':dict(save.data['meta']),'items':sorted(missions.unlocked(save.data)),
            'unlocked':save.visible_characters(),'short_cinema':save.data['settings']['short_cinema'],'clip_seen':list(save.data['clip_seen'])}

def clean_profile(data):
    if not isinstance(data,dict) or data.get('key') not in CHARACTERS:raise ValueError('Personagem inválido')
    result={'key':data['key'],'meta':{},'items':['knives'],'unlocked':[]}
    for k,spec in progression.META.items():
        v=data.get('meta',{}).get(k,0)
        if type(v) is int:result['meta'][k]=max(0,min(spec[2],v))
    result['items']=sorted({'knives'}|{x for x in data.get('items',[]) if x in missions.MISSIONS})
    result['unlocked']=[x for x in data.get('unlocked',[]) if x in CHARACTERS]
    if result['key'] not in result['unlocked']:raise ValueError('Personagem bloqueado')
    result['short_cinema']=data.get('short_cinema') is not False
    values=data.get('clip_seen',[])
    result['clip_seen']=[v for v in values if isinstance(v,str) and len(v)<96][:256] if isinstance(values,list) else []
    return result

class Multiplayer:
    def __init__(self,save,key='leo',host=False,target=None,port=PORT,sound=None):
        self.is_host=host;self.pid=0 if host else None;self.sound=sound;self.error=''
        self.trace_id=uuid.uuid4().hex[:10];self.connection_stage='validar';self.handshake_started=None
        self.listener=None;self.peers=[];self.server=None;self.pending_socket=None;self.connecting=False;self.connected=False
        self.profiles={0:clean_profile(profile(save,key))} if host else {}
        self.local_profile=clean_profile(profile(save,key));self.members=[];self.ready={0:False} if host else {}
        self.run_rule='standard';self.rtt_ms=None;self.ping_clock=0.;self.ping_nonce=0;self.pending_pings={}
        self.map_key='crypt';self.phase='lobby';self.session=None;self.match_id='';self.inputs={};self.input_age={}
        self.offers={};self.tokens={};self.clip=None;self.clip_action=None
        self.result_acks=set();self.remote_results_ready=False
        self.send_clock=0.;self.input_clock=0.;self.last_pump=time.monotonic();self.port=port
        self.seed=7319;self.closed=False;self.addresses=local_addresses()
        event(self,'created',protocol=VERSION)
        try:
            if host:
                self.connection_stage='escutar'
                self.listener=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                if hasattr(socket,'SO_EXCLUSIVEADDRUSE'):self.listener.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
                else:self.listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
                self.listener.bind(('0.0.0.0',port));self.port=self.listener.getsockname()[1]
                self.listener.listen(4);self.listener.setblocking(False);self.connected=True
                self.connection_stage='sala';event(self,'listening',port=self.port)
                self.refresh_members()
            else:
                dest=address(target,port)
                self.port=dest[1]
                self.connection_stage='conectar';event(self,'connect_begin',endpoint=dest)
                sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.pending_socket=sock  # Track ownership even if connect_ex raises.
                sock.setblocking(False)
                code=sock.connect_ex(dest)
                event(self,'connect_ex',code=code)
                if code not in (0,errno.EINPROGRESS,errno.EWOULDBLOCK,errno.EALREADY,10035,10036,10037):
                    raise OSError(code,'connect_ex')
                # On Windows, TCP_NODELAY (inside Peer) can raise WinError 10022
                # while a nonblocking connect is still pending. Defer wrapping.
                self.connecting=True;self.connect_started=time.monotonic()
        except (OSError,ValueError) as exc:
            event(self,'exception',operation=self.connection_stage,exception=repr(exc),traceback=traceback.format_exc(limit=8))
            self.fail(socket_message(exc,self.port) if isinstance(exc,OSError) else str(exc))
    def fail(self,message):
        self.error=str(message)[:300];self.phase='error';event(self,'failed',operation=self.connection_stage,reason=self.error);self.close()
    def close(self):
        if self.closed:return
        if self.listener:
            try:self.listener.close()
            except OSError:pass
            self.listener=None
        for peer in self.peers:peer.close()
        if self.server:self.server.close()
        if self.pending_socket:
            try:self.pending_socket.close()
            except OSError:pass
            self.pending_socket=None
        self.closed=True;self.connecting=False;self.connected=False;event(self,'closed')

    def finish_connect(self):
        """Wait for TCP connect completion before configuring or using its socket."""
        sock=self.pending_socket
        if sock is None:raise ValueError('Socket de conexão ausente')
        if time.monotonic()-self.connect_started>=8:
            self.fail('Tempo esgotado ao conectar. Confira IP, Radmin VPN, porta e firewall.');return False
        _, writable, failed=select.select([], [sock], [sock], 0)
        if not (writable or failed):
            return False
        code=sock.getsockopt(socket.SOL_SOCKET,socket.SO_ERROR)
        event(self,'connect_complete',code=code,writable=bool(writable),exceptional=bool(failed))
        if code:
            raise OSError(code,'SO_ERROR')
        if failed and not writable:raise OSError(10022,'select: conexão sinalizada como falha sem SO_ERROR')
        # Transfer ownership to Peer only after the connection has succeeded.
        self.connection_stage='configurar';peer=Peer(sock);event(self,'peer_configured')
        self.server=peer;self.pending_socket=None;self.connecting=False
        self.connection_stage='handshake';self.handshake_started=time.monotonic()
        peer.send({'type':'hello','version':VERSION,'profile':self.local_profile})
        event(self,'hello_sent')
        return True
    def refresh_members(self):
        self.members=[{'pid':i,'key':p['key'],'ready':self.ready.get(i,False)} for i,p in sorted(self.profiles.items())]
    def command(self,action,**data):
        if self.is_host:self.receive(0,{'type':'action','action':action,**data})
        elif self.connected and self.server:self.server.send({'type':'action','action':action,**data})
    @property
    def results_ready(self):return set(self.profiles)<=self.result_acks if self.is_host else self.remote_results_ready
    def set_character(self,save,key):
        self.local_profile=clean_profile(profile(save,key));self.command('profile',profile=self.local_profile)
    def receive(self,pid,msg):
        if msg.get('type')=='ping':
            nonce=msg.get('nonce')
            if type(nonce) is int and 0<=nonce<=10**12:
                peer=next((p for p in self.peers if p.pid==pid),None)
                if peer:peer.send({'type':'pong','nonce':nonce})
            return
        if msg.get('type')=='input':
            self.inputs[pid]=V(movement(msg.get('move')));self.input_age[pid]=self.session.time if self.session else 0;return
        if msg.get('type')!='action':return
        action=msg.get('action')
        if self.phase=='lobby':
            if action=='ready':self.ready[pid]=not self.ready.get(pid,False)
            elif action=='profile':self.profiles[pid]=clean_profile(msg.get('profile'));self.ready[pid]=False
            elif action=='map' and pid==0 and msg.get('map') in MAPS:self.map_key=msg['map']
            elif action=='rule' and pid==0:
                from expedition import RULES
                if msg.get('rule') in RULES:self.run_rule=msg['rule'];self.ready={i:False for i in self.profiles}
            elif action=='start' and pid==0:self.start()
            self.refresh_members();self.send_clock=1.;return
        if not self.session:return
        if action=='result_ack' and self.phase=='result':self.result_acks.add(pid);return
        if action=='restart' and pid==0 and self.phase=='result' and self.results_ready:
            self.phase='lobby';self.session=None;self.match_id='';self.offers.clear();self.tokens.clear()
            self.clip=None;self.inputs.clear();self.input_age.clear();self.ready={i:False for i in self.profiles}
            self.refresh_members();self.send_clock=1.;return
        if action=='skip' and self.clip and pid in (0,self.clip.pid):self.clip.age=self.clip.duration;return
        if action=='endless' and pid==0 and self.phase=='result' and self.results_ready:
            if self.session.waves.continue_endless(self.session):self.phase='play';self.prepare_offers()
            return
        if self.phase=='upgrade':
            if msg.get('token')!=self.tokens.get(pid) or pid not in self.offers:return
            p=self.session.owner(pid)
            if action=='reroll' and p.rerolls>0 and (p.specialization or p.level<4):p.rerolls-=1;self.make_offer(p)
            elif action=='choice':
                index=msg.get('index')
                if type(index) is int and 0<=index<len(self.offers[pid]):
                    upgrades.apply(p,self.offers[pid][index]);p.pending=max(0,p.pending-1)
                    if p.pending:self.make_offer(p)
                    else:self.offers.pop(pid,None)
            if not self.offers:self.phase='play'
            self.send_clock=1.;return
        if self.phase!='play':return
        p=self.session.owner(pid)
        if p.hp<=0:return
        if action=='transform':
            if self.session.action_for(pid,action):
                self.clip=Cinematic.player(p,'transform');self.clip_action=None;self.phase='cinema'
        elif action=='ultimate':
            if p.transformed and not p.ultimate_used and self.session.transform_pause<=0:
                self.clip=Cinematic.player(p,'ultimate');self.clip_action='ultimate';self.phase='cinema'
        elif action in ('dash','soul'):self.session.action_for(pid,action)
        elif isinstance(action,str) and action in ('note:0','note:1','note:2','note:3'):self.session.action_for(pid,action)
    def handshake(self,peer,msg):
        if msg.get('type')!='hello' or msg.get('version')!=VERSION:
            from release_info import RELEASE_ID
            peer.reject('Versões diferentes; use o mesmo ZIP '+RELEASE_ID);event(self,'handshake_rejected',reason='version');return
        if self.phase!='lobby' or len(self.profiles)>=4:
            peer.reject('Sala cheia ou partida já iniciada');event(self,'handshake_rejected',reason='room');return
        pid=next(i for i in range(1,4) if i not in self.profiles)
        pf=clean_profile(msg.get('profile'))
        self.profiles[pid]=pf;peer.pid=pid;self.ready[pid]=False
        peer.send({'type':'welcome','version':VERSION,'pid':pid});self.refresh_members();self.send_clock=1.
        event(self,'handshake_ok',pid=pid)
    def start(self):
        if self.phase!='lobby' or len(self.profiles)<2 or not all(self.ready.get(i) for i in self.profiles):return False
        self.session=GameSession(self.profiles[0]['key'],self.seed,self.sound,self.map_key,run_rule=self.run_rule)
        for pid,pf in sorted(self.profiles.items()):
            p=self.session.player if pid==0 else self.session.add_player(pf['key'],pid)
            progression.meta_apply({'meta':pf['meta']},p);p.allowed_items=set(pf['items']);p.short_cinema=pf['short_cinema'];p.clip_seen=set(pf['clip_seen'])
        self.match_id=uuid.uuid4().hex;self.phase='play';self.connection_stage='partida';self.result_acks.clear();self.send_clock=1.
        event(self,'match_started',match=self.match_id,players=len(self.profiles),map=self.map_key);return True
    def make_offer(self,p):
        self.offers[p.pid]=upgrades.choices(p,self.session.rng);self.tokens[p.pid]=self.tokens.get(p.pid,0)+1
    def prepare_offers(self):
        for p in self.session.allied_players:
            if p.pending and p.pid not in self.offers:self.make_offer(p)
        if self.offers:self.phase='upgrade'
    def state_message(self):
        result={'type':'state','version':VERSION,'phase':self.phase,'members':self.members,'map':self.map_key,'run_rule':self.run_rule,'match':self.match_id,
                'offers':{str(pid):{'token':self.tokens[pid],'choices':[[u.id,upgrades.RARITIES.index(r)] for u,r in rows]} for pid,rows in self.offers.items()},
                'clip':self.clip.wire() if self.clip else None,'results_ready':self.results_ready}
        if self.session:result['session']=snapshot(self.session)
        return result
    def client_receive(self,msg):
        kind=msg.get('type')
        if kind=='pong':
            if type(msg.get('nonce')) is not int or not 0<=msg['nonce']<=10**12:raise ValueError('Resposta de latência inválida')
            started=self.pending_pings.pop(msg.get('nonce'),None)
            if started is not None:self.rtt_ms=max(0,min(15000,(time.monotonic()-started)*1000))
            return
        if kind=='reject':self.fail(msg.get('reason','Sala recusada'));return
        if kind=='welcome':
            if msg.get('version')!=VERSION:raise ValueError('Versões diferentes; use o mesmo ZIP')
            if self.pid is not None or type(msg.get('pid')) is not int or not 1<=msg['pid']<=3:raise ValueError('Identificação inválida da sala')
            self.pid=msg['pid'];self.connected=True;self.connection_stage='sala';event(self,'welcome_received',pid=self.pid);return
        if kind!='state' or self.pid is None:return
        if msg.get('version')!=VERSION:raise ValueError('Versões diferentes')
        if msg.get('phase') not in ('lobby','play','cinema','upgrade','result') or msg.get('map') not in MAPS:raise ValueError('Estado da sala inválido')
        members=msg.get('members')
        if not isinstance(members,list) or not 1<=len(members)<=4:raise ValueError('Membros da sala inválidos')
        if any(not isinstance(m,dict) or type(m.get('pid')) is not int or not 0<=m['pid']<4 or m.get('key') not in CHARACTERS or type(m.get('ready')) is not bool for m in members):raise ValueError('Membro inválido')
        if len({m['pid'] for m in members})!=len(members) or self.pid not in {m['pid'] for m in members}:raise ValueError('Vaga ausente')
        if not isinstance(msg.get('match'),str) or len(msg['match'])>128:raise ValueError('Partida inválida')
        from expedition import RULES
        if msg.get('run_rule') not in RULES:raise ValueError('Regra de sala inválida')
        self.run_rule=msg['run_rule']
        if msg.get('session') and msg['session'].get('world',{}).get('run_rule')!=self.run_rule:raise ValueError('Regra de mundo incompatível')
        old_match=self.match_id
        self.phase=msg['phase'];self.members=msg['members'];self.map_key=msg['map'];self.match_id=msg['match']
        if self.match_id!=old_match and self.match_id:
            self.connection_stage='partida';event(self,'match_received',match=self.match_id,players=len(self.members))
        elif self.phase=='lobby':self.connection_stage='sala'
        self.remote_results_ready=msg.get('results_ready') is True
        self.clip=Cinematic.read(msg['clip']) if msg.get('clip') else None
        if msg.get('session'):
            old_players={p.pid:V(getattr(p,'render_pos',p.pos)) for p in self.session.allied_players} if self.session and old_match==self.match_id else {}
            old_enemies={e.uid:V(getattr(e,'render_pos',e.pos)) for e in self.session.enemies} if self.session and old_match==self.match_id else {}
            self.session=restore(msg['session'],self.pid,self.session if old_match==self.match_id else None)
            for p in self.session.allied_players:p.render_pos=old_players.get(p.pid,V(p.pos))
            for e in self.session.enemies:e.render_pos=old_enemies.get(e.uid,V(e.pos))
            self.session.interpolation_age=0.
        elif self.phase=='lobby':self.session=None
        self.offers={};self.tokens={}
        lookup={u.id:u for u in upgrades.UPGRADES}
        for pid,offer in msg.get('offers',{}).items():
            rows=[]
            for key,rarity in offer['choices']:
                u=lookup.get(key)
                if u is None and key=='recovery':u=upgrades.Upgrade('recovery','Reabastecimento','Cura 35 de vida','heal',35,999)
                if u is None or type(rarity) is not int or not 0<=rarity<4:raise ValueError('Melhoria inválida')
                rows.append((u,upgrades.RARITIES[rarity]))
            self.offers[int(pid)]=rows;self.tokens[int(pid)]=offer['token']
    def pump(self,dt,move=None):
        if self.closed:return
        if move is None:move=V()
        dt=max(0,min(.15,dt));self.send_clock+=dt;self.input_clock+=dt
        try:
            if self.is_host:
                for _ in range(4):
                    try:sock,_=self.listener.accept()
                    except BlockingIOError:break
                    try:peer=Peer(sock)
                    except OSError as exc:
                        sock.close();event(self,'accept_config_failed',exception=repr(exc));continue
                    event(self,'accepted')
                    if len(self.peers)>=6:peer.close();continue
                    self.peers.append(peer)
                for peer in list(self.peers):
                    if peer.pid is None and not peer.closing and time.monotonic()-peer.created>8:peer.reject('Handshake não recebido no prazo')
                    for msg in peer.pump():
                        try:
                            if peer.pid is None:self.handshake(peer,msg)
                            else:self.receive(peer.pid,msg)
                        except (ValueError,TypeError,KeyError,AttributeError,IndexError) as exc:
                            event(self,'invalid_request',pid=peer.pid,exception=repr(exc));peer.reject('Solicitação inválida')
                        if not peer.alive or peer.closing:break
                    if not peer.alive:
                        event(self,'peer_disconnected',pid=peer.pid,reason=peer.error)
                        if peer.pid is not None:
                            self.profiles.pop(peer.pid,None);self.ready.pop(peer.pid,None);self.offers.pop(peer.pid,None)
                            self.inputs.pop(peer.pid,None)
                            self.input_age.pop(peer.pid,None);self.tokens.pop(peer.pid,None);self.result_acks.discard(peer.pid)
                            if self.session:
                                if self.clip and self.clip.pid==peer.pid:
                                    self.clip=None;self.clip_action=None;self.session.transform_pause=0.;self.phase='play'
                                departed=self.session.owner(peer.pid);self.session.departed_players[peer.pid]=departed
                                count=len(self.session.allied_players)
                                self.session.allied_players[:]=[p for p in self.session.allied_players if p.pid!=peer.pid]
                                factor=(1+.65*max(0,count-2))/(1+.65*(count-1))
                                for e in self.session.enemies:e.hp*=factor;e.max_hp*=factor
                                self.session.notice('ALIADO DESCONECTADO • A EXPEDIÇÃO CONTINUA',3.)
                                if all(p.hp<=0 for p in self.session.allied_players):self.session.result='GAME_OVER';self.phase='result'
                            self.refresh_members();self.send_clock=1.
                        self.peers.remove(peer)
                self.inputs[0]=V(move);self.input_age[0]=self.session.time if self.session else 0
                if self.phase=='play':
                    for pid in list(self.inputs):
                        if self.session.time-self.input_age.get(pid,0)>.5:self.inputs[pid]=V()
                    remaining=dt
                    while remaining>1e-8 and self.phase=='play':
                        step=min(remaining,1/60);self.session.update(step,self.inputs);remaining-=step
                        if self.session.result:self.phase='result';self.result_acks.clear();self.send_clock=1.
                        else:self.prepare_offers()
                elif self.phase=='upgrade' and not self.offers:self.phase='play'
                elif self.phase=='cinema' and self.clip and self.clip.update(dt):
                    self.session.transform_pause=0.
                    if self.clip_action:self.session.action_for(self.clip.pid,self.clip_action)
                    self.clip=None;self.clip_action=None;self.phase='result' if self.session.result else 'play'
                if self.send_clock>=.05:
                    self.send_clock=0.;packet=self.state_message()
                    for peer in self.peers:
                        if peer.pid is not None:peer.send(packet);peer.flush()
            else:
                if self.connecting:
                    if not self.finish_connect():
                        return
                for msg in self.server.pump():self.client_receive(msg)
                if self.closed:return
                if not self.server.alive and not self.closed:self.fail('Anfitrião desconectado. '+self.server.error);return
                if not self.connected and time.monotonic()-self.handshake_started>8:
                    self.fail('TCP conectado, mas a sala não respondeu ao handshake. Use o mesmo ZIP nos dois PCs.');return
                self.ping_clock+=dt
                if self.connected and self.ping_clock>=1.5:
                    self.ping_clock=0.;self.ping_nonce=(self.ping_nonce+1)%10**12;self.pending_pings={self.ping_nonce:time.monotonic()};self.server.send({'type':'ping','nonce':self.ping_nonce})
                if self.connected and self.input_clock>=.05:
                    self.input_clock=0.;self.server.send({'type':'input','move':[move.x,move.y]});self.server.flush()
                if self.session:
                    self.session.interpolation_age=min(.05,self.session.interpolation_age+dt)
                    for actor in self.session.allied_players+self.session.enemies:
                        if hasattr(actor,'render_pos'):actor.render_pos=actor.render_pos.lerp(actor.pos,1-math.exp(-dt*35))
        except (OSError,ValueError,TypeError,KeyError,IndexError,AttributeError,OverflowError) as exc:
            event(self,'exception',operation=self.connection_stage,exception=repr(exc),traceback=traceback.format_exc(limit=8))
            self.fail(socket_message(exc,self.port) if isinstance(exc,OSError) else 'Falha na comunicação: '+str(exc))
