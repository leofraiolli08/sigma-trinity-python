"""Explicit render-state codec; never deserializes Python code or arbitrary types."""
import math
from entities import V,Player,Enemy,Projectile,Area,Telegraph,Pickup,Particle,FloatText,DefeatEcho
from ascension import Effect
from rhythm import Note,Rhythm
from session import GameSession

COLLECTIONS={'enemies':Enemy,'projectiles':Projectile,'areas':Area,'telegraphs':Telegraph,
             'pickups':Pickup,'particles':Particle,'texts':FloatText,'effects':Effect,'corpses':DefeatEcho}
FIELDS=('time','spawn_cd','uid','kills','total_damage','boss_spawned','result','shake','hitstop','transform_pause',
        'message','message_left','events','chests','coins','challenge','run_rule','objectives','discovered','telemetry')
LIMITS={'enemies':160,'projectiles':280,'areas':48,'telegraphs':300,'pickups':300,'particles':400,'texts':75,'effects':90,'corpses':45}

def validate_wire(value,depth=0):
    if depth>16:raise ValueError('Estado excessivamente aninhado')
    if isinstance(value,dict):
        if any(not isinstance(k,str) for k in value):raise ValueError('Chave inválida')
        if set(value)=={'v'}:
            row=value['v']
            if not isinstance(row,list) or len(row)!=2 or any(type(n) not in (int,float) or abs(n)>1e7 or not math.isfinite(n) for n in row):raise ValueError('Vetor inválido')
        if set(value)=={'n'}:
            row=value['n']
            if not isinstance(row,list) or len(row)!=3 or type(row[0]) not in (int,float) or type(row[1]) is not int or not 0<=row[1]<4 or type(row[2]) is not bool:raise ValueError('Nota inválida')
        if set(value) in ({'p'},{'e'}):
            ref=next(iter(value.values()))
            if type(ref) is not int or ref<0:raise ValueError('Referência inválida')
        for item in value.values():validate_wire(item,depth+1)
    elif isinstance(value,list):
        if len(value)>2000:raise ValueError('Coleção inválida')
        for item in value:validate_wire(item,depth+1)
    elif type(value) is int:
        if abs(value)>10**12:raise ValueError('Inteiro fora do intervalo')
    elif type(value) is float:
        if not math.isfinite(value) or abs(value)>1e12:raise ValueError('Número inválido')
    elif isinstance(value,str):
        if len(value)>512:raise ValueError('Texto grande demais')
    elif value is not None and type(value) is not bool:raise ValueError('Tipo inválido')

def validate_fields(info,prototype):
    if not isinstance(info,dict):raise ValueError('Entidade inválida')
    for name,base in prototype.items():
        if name not in info:raise ValueError('Campo ausente: '+name)
        value=info[name]
        if isinstance(base,V):
            if not isinstance(value,dict) or set(value)!={'v'}:raise ValueError('Vetor inválido: '+name)
        elif type(base) is bool:
            if type(value) is not bool:raise ValueError('Booleano inválido: '+name)
        elif type(base) in (float,int):
            if type(value) not in (int,float):raise ValueError('Número inválido: '+name)
            if name in ('pid','uid','kind','level','pending','stage','kills','phase','action','pierce','bounce','owner','puppet_owner','dance_pose','rerolls','transforms','ultimates','count','number','remaining','completed') and type(value) is not int:raise ValueError('Inteiro inválido: '+name)
        elif isinstance(base,set):
            if not isinstance(value,dict) or set(value)!={'s'} or not isinstance(value['s'],list) or any(type(x) not in (str,int) for x in value['s']):raise ValueError('Conjunto inválido: '+name)
        elif isinstance(base,dict):
            if not isinstance(value,dict):raise ValueError('Tabela inválida: '+name)
        elif isinstance(base,list) and not isinstance(value,list):raise ValueError('Lista inválida: '+name)
        elif isinstance(base,str) and not isinstance(value,str):raise ValueError('Texto inválido: '+name)
        elif isinstance(base,tuple):
            if not isinstance(value,list) or len(value) not in (3,4) or any(type(n) is not int or not 0<=n<=255 for n in value):raise ValueError('Cor inválida: '+name)

def pack(value):
    if isinstance(value,V):return {'v':[value.x,value.y]}
    if isinstance(value,set):return {'s':sorted(value)}
    if isinstance(value,Player):return {'p':value.pid}
    if isinstance(value,Enemy):return {'e':value.uid}
    if isinstance(value,Note):return {'n':[value.time,value.lane,value.judged]}
    if isinstance(value,dict):return {str(k):pack(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [pack(v) for v in value]
    if value is None or isinstance(value,(str,bool,int)):return value
    if isinstance(value,float) and math.isfinite(value):return value
    raise ValueError('Campo de estado inválido')

def unpack(value,players,enemies):
    if isinstance(value,dict):
        if set(value)=={'v'}:return V(*value['v'])
        if set(value)=={'s'}:return set(value['s'])
        if set(value)=={'p'}:return players.get(value['p'])
        if set(value)=={'e'}:return enemies.get(value['e'])
        if set(value)=={'n'}:return Note(*value['n'])
        return {k:unpack(v,players,enemies) for k,v in value.items()}
    if isinstance(value,list):return [unpack(v,players,enemies) for v in value]
    return value

def snapshot(s):
    active={p.pid for p in s.allied_players}
    return {'map':s.arena.key,'players':[pack(p.__dict__) for p in s.allied_players],
            'world':{k:pack(getattr(s,k)) for k in FIELDS},'waves':pack(s.waves.__dict__),
            'boss':s.boss.uid if s.boss and s.boss in s.enemies else None,
            'rhythms':{str(pid):pack(r.__dict__) for pid,r in s.rhythms.items() if pid in active},
            **{k:[pack(x.__dict__) for x in getattr(s,k)[:LIMITS[k]]] for k in COLLECTIONS}}

def restore(data,pid,s=None):
    from settings import CHARACTERS
    from maps import MAPS
    validate_wire(data)
    if not isinstance(data,dict) or data.get('map') not in MAPS or not isinstance(data.get('players'),list) or not 1<=len(data['players'])<=4:raise ValueError('Estado de sala inválido')
    if not isinstance(data.get('world'),dict) or not isinstance(data.get('waves'),dict):raise ValueError('Mundo inválido')
    validate_fields(data['world'],dict(time=0.,spawn_cd=0.,uid=0,kills=0,total_damage=0.,boss_spawned=False,
        shake=0.,hitstop=0.,transform_pause=0.,message='',message_left=0.,events={},chests=0,coins=0))
    world=data['world']
    from expedition import RULES
    from specializations import SPECS
    if world.get('run_rule') not in RULES:raise ValueError('Regra inválida')
    nodes=world.get('objectives')
    if not isinstance(nodes,list) or len(nodes)!=3:raise ValueError('Objetivos inválidos')
    for i,n in enumerate(nodes):
        if not isinstance(n,dict) or set(n)!={'x','y','progress','done','available'}:raise ValueError('Objetivo incompleto')
        if any(type(n[k]) not in (int,float) or not 0<=n[k]<=3600 for k in ('x','y')) or type(n['progress']) not in (int,float) or not 0<=n['progress']<=8 or type(n['done']) is not bool or type(n['available']) is not int or n['available']!=2+i*2:raise ValueError('Progresso de objetivo inválido')
    tags=world.get('discovered')
    allowed_tags={f'{theme}:{i}' for theme in MAPS for i in range(7)}
    if not isinstance(tags,dict) or set(tags)!={'s'} or not isinstance(tags['s'],list) or any(not isinstance(t,str) or t not in allowed_tags for t in tags['s']):raise ValueError('Bestiário inválido')
    telemetry=world.get('telemetry')
    if not isinstance(telemetry,dict) or set(telemetry)!={'first_form','boss_started','boss_seconds'} or any(type(v) not in (int,float) or not 0<=v<=1e7 for v in telemetry.values()):raise ValueError('Métricas inválidas')
    if world.get('challenge') not in (None,'leozauxta','leozauxtaci'):raise ValueError('Desafio inválido')
    if any(type(world['events'].get(k)) is not int or world['events'][k]<0 for k in ('hits','pickups','dance_pulses','skills')):raise ValueError('Eventos inválidos')
    if any(world[k]<0 for k in ('time','uid','kills','total_damage','chests','coins')):raise ValueError('Contador inválido')
    if any(not isinstance(p,dict) for p in data['players']):raise ValueError('Jogador inválido')
    if any(p.get('key') not in CHARACTERS or type(p.get('pid')) is not int or not 0<=p['pid']<4 for p in data['players']):raise ValueError('Jogador inválido')
    for info in data['players']:
        validate_fields(info,Player(info['key']).__dict__)
        if info['run_rule']!=world['run_rule'] or type(info['specialization_rank']) is not int or not 0<=info['specialization_rank']<=3:raise ValueError('Especialização inválida')
        sid=info['specialization']
        if sid and (sid not in SPECS or SPECS[sid][0]!=info['key'] or info['specialization_rank']==0) or not sid and info['specialization_rank']!=0:raise ValueError('Caminho incompatível')
        if type(info['counters']) is not int or info['counters']<0:raise ValueError('Contra-ataque inválido')
        cap=3 if info['key'] in ('musashi','thorfinn','holden') else 2 if info['key'] in ('klein','joe') else 1 if info['key'] in ('ippo','eren') else 0
        if not 0<=info['stage']<=cap or info['base_hp']<=0 or info['hp']<0:raise ValueError('Atributos de jogador inválidos')
        if any(type(v) is not int or not 0<=v<=999 for v in info['upgrades'].values()):raise ValueError('Melhoria inválida')
        from ascension import RECIPES
        if any(k not in RECIPES or type(v) is not int or not 1<=v<=4 for k,v in info['aux'].items()):raise ValueError('Arma inválida')
    prototypes={'projectiles':Projectile(V(),V(),1.,'token'),'areas':Area(V(),1.,1.,'wave'),
        'telegraphs':Telegraph(V(),1.,1.,'hostile_blast',1.),'pickups':Pickup(V(),1.),
        'particles':Particle(V(),V(),1.,(1,1,1)),'texts':FloatText(V(),'1',(1,1,1)),
        'effects':Effect('spark',V(),V(),(1,1,1)),'corpses':DefeatEcho(V(),0)}
    for key,cls in COLLECTIONS.items():
        values=data.get(key)
        if not isinstance(values,list) or len(values)>LIMITS[key]:raise ValueError('Limite de entidades inválido')
        for info in values:
            if not isinstance(info,dict):raise ValueError('Entidade inválida')
            if key=='enemies':
                if type(info.get('uid')) is not int or type(info.get('kind')) is not int or not 0<=info['kind']<6:raise ValueError('Inimigo inválido')
                validate_fields(info,Enemy(info['uid'],V(),info['kind']).__dict__)
                if info['max_hp']<=0 or not 1<=info['phase']<=3:raise ValueError('Atributos de inimigo inválidos')
            else:validate_fields(info,prototypes[key].__dict__)
            if key=='corpses' and (type(info['kind']) is not int or not 0<=info['kind']<6 or info['theme'] not in MAPS or not 0<=info['life']<=.55):raise ValueError('Pose de derrota inválida')
            if 'radius' in info and (type(info['radius']) not in (int,float) or not 0<info['radius']<=6000):raise ValueError('Raio inválido')
            if key=='telegraphs':
                from boss_patterns import HOSTILE_KINDS
                if info['kind'] in HOSTILE_KINDS and info['radius']>600:raise ValueError('Perigo fora do intervalo')
                if not 0<=info['count']<=40 or not 0<=info['reach']<=1500 or not 0<=info['spread']<=360:raise ValueError('Ataque inválido')
                if info['kind'] in ('charge','ranged','boss_fan','boss_sweep') and (not isinstance(info['direction'],dict) or set(info['direction'])!={'v'}):raise ValueError('Direção ausente')
    if not set(FIELDS)<=set(data['world']) or data['world'].get('result') not in (None,'GAME_OVER','VICTORY'):raise ValueError('Mundo incompleto')
    if len({e['uid'] for e in data['enemies']})!=len(data['enemies']):raise ValueError('Inimigo duplicado')
    from waves import Waves
    validate_fields(data['waves'],Waves().__dict__)
    if data['waves']['number']<1 or data['waves']['remaining']<0:raise ValueError('Onda inválida')
    if not isinstance(data.get('rhythms'),dict):raise ValueError('Ritmo inválido')
    ids=[p['pid'] for p in data['players']]
    if len(set(ids))!=len(ids) or pid not in ids:raise ValueError('Vaga ausente')
    if any(k not in {str(i) for i in ids} for k in data['rhythms']):raise ValueError('Ritmo sem jogador')
    for values in data['rhythms'].values():
        validate_fields(values,Rhythm().__dict__)
        if any(not isinstance(n,dict) or set(n)!={'n'} for n in values['notes']):raise ValueError('Nota ausente')
    if 'boss' not in data or data['boss'] is not None and (type(data['boss']) is not int or not any(e['uid']==data['boss'] and e['boss'] for e in data['enemies'])):raise ValueError('Chefe ausente')
    if s is None or s.arena.key!=data['map']:s=GameSession(data['players'][0]['key'],map_key=data['map'])
    players={p.pid:p for p in s.allied_players};ids=[p['pid'] for p in data['players']]
    if len(set(ids))!=len(ids) or pid not in ids:raise ValueError('Vaga ausente')
    for info in data['players']:
        if info['pid'] not in players:
            from weapons import WEAPONS
            p=Player(info['key']);p.pid=info['pid'];players[p.pid]=p
            s.weapons[p.pid]=WEAPONS[p.key]();s.rhythms[p.pid]=Rhythm();s.player_timers[p.pid]={}
    enemies={}
    for info in data.get('enemies',[])[:160]:
        e=Enemy(info['uid'],V(),info['kind']);enemies[e.uid]=e
    for info in data['players']:
        p=players[info['pid']];allowed=set(p.__dict__)
        for k,v in info.items():
            if k in allowed:setattr(p,k,unpack(v,players,enemies))
    s.allied_players=[players[i] for i in ids]
    for key,cls in COLLECTIONS.items():
        values=data.get(key,[])
        if not isinstance(values,list) or len(values)>LIMITS[key]:raise ValueError('Limite de entidades inválido')
        result=[]
        for info in values:
            if key=='enemies':obj=enemies[info['uid']];allowed=set(obj.__dict__)|{'name','trial_key'}
            else:
                obj=cls.__new__(cls);allowed=set(cls.__dataclass_fields__)
            for k,v in info.items():
                if k in allowed:setattr(obj,k,unpack(v,players,enemies))
            result.append(obj)
        setattr(s,key,result)
    for k in FIELDS:
        if k in data['world']:setattr(s,k,unpack(data['world'][k],players,enemies))
    for k in s.waves.__dict__:
        if k in data['waves']:setattr(s.waves,k,data['waves'][k])
    for i,values in data.get('rhythms',{}).items():
        if int(i) in s.rhythms:
            r=s.rhythms[int(i)]
            for k in r.__dict__:
                if k in values:setattr(r,k,unpack(values[k],players,enemies))
    s.boss=enemies.get(data['boss']);s.player=players[pid];s.weapon=s.weapons[pid];s.rhythm=s.rhythms[pid]
    return s
