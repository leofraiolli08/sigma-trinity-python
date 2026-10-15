"""World simulation. No display, input events or file operations live here."""
import math
import random
from contextlib import contextmanager
from entities import (V,Player,Enemy,Projectile,Area,Telegraph,Pickup,Particle,FloatText,DefeatEcho,unit,segment_distance)
from weapons import WEAPONS
from maps import Arena
from rhythm import Rhythm
from settings import RUN_DURATION,MAX_ENEMIES,MAX_PROJECTILES,MAX_PARTICLES,CHARACTERS
import ascension
from waves import Waves,FAMILIES,tune

class OwnedTelegraphs(list):
    def __init__(self,session):super().__init__();self.session=session
    def append(self,item):
        item.owner=self.session.player.pid
        if item.total_delay<=0:item.total_delay=max(.001,item.delay)
        if item.kind in ('charge','ranged','enemy_melee') and isinstance(item.source,Enemy):item.source.windup_left=max(item.source.windup_left,item.delay)
        super().append(item)

class GameSession:
    def __init__(self,key,seed=0,sound=None,map_key='crypt',run_rule='standard'):
        self.rhythm=Rhythm(); self.evolution_pending=False;
        self.arena=Arena(map_key); self.hazard_cd=8.
        self.rng=random.Random(seed); self.player=Player(key);
        self.allied_players=[self.player]
        if map_key=='usj': self.player.pos=V(1800,2050)
        self.weapon=WEAPONS[key]()
        self.enemies=[]; self.projectiles=[]; self.areas=[]; self.telegraphs=[]; self.pickups=[]; self.particles=[]; self.texts=[]
        self.time=0.; self.spawn_cd=.3; self.uid=0; self.kills=0; self.total_damage=0.; self.boss_spawned=False
        self.boss=None; self.result=None; self.shake=0.; self.hitstop=0.; self.transform_pause=0.
        self.message='SOBREVIVA À DIMENSÃO SIGMA'; self.message_left=3.; self.sound_callback=sound
        self.events={'hits':0,'pickups':0,'dance_pulses':0,'skills':0}
        self.effects=[];self.aux_timers={};self.next_elite=60.;self.chests=0;self.coins=0;self.reward=0;self.awarded=[]
        self.waves=Waves();self.victory_paid=False;self.banked={};self.last_saved_wave=0
        self.weapons={0:self.weapon};self.rhythms={0:self.rhythm};self.player_timers={0:self.aux_timers}
        self.telegraphs=OwnedTelegraphs(self);self.challenge=None
        self.departed_players={}
        self.enemy_index=None
        self.corpses=[]
        from expedition import setup
        setup(self,run_rule)
    def add_player(self,key,pid):
        if len(self.allied_players)>=4 or pid in self.weapons:raise ValueError('Vaga inválida')
        p=Player(key);p.pid=pid;p.pos=self.arena.constrain(self.allied_players[0].pos+V(75*pid,30),p.radius)
        from expedition import configure
        configure(p,self.run_rule)
        self.allied_players.append(p);self.weapons[pid]=WEAPONS[key]();self.rhythms[pid]=Rhythm();self.player_timers[pid]={}
        return p
    @contextmanager
    def acting(self,p):
        previous=(self.player,self.weapon,self.rhythm,self.aux_timers)
        self.player=p;self.weapon=self.weapons[p.pid];self.rhythm=self.rhythms[p.pid];self.aux_timers=self.player_timers[p.pid]
        try:yield
        finally:self.player,self.weapon,self.rhythm,self.aux_timers=previous
    def owner(self,pid):return next((p for p in self.allied_players if p.pid==pid),self.departed_players.get(pid,self.allied_players[0]))
    def action_for(self,pid,action):
        p=self.owner(pid)
        if p.hp<=0 or self.result:return False
        with self.acting(p):
            if action.startswith('note:'):return self.rhythm_tap(int(action[5:]))
            if action not in ('dash','transform','ultimate','soul'):return False
            return getattr(self,{'soul':'toggle_musashi_soul_mode'}.get(action,action))()
    def sound(self,name):
        if self.sound_callback: self.sound_callback(name)
    def notice(self,text,duration=2.): self.message=text; self.message_left=duration
    def add_projectile(self,p):
        p.owner=self.player.pid
        if len(self.projectiles)<MAX_PROJECTILES:self.projectiles.append(p);return p
    def add_area(self,a):
        a.owner=self.player.pid
        if len(self.areas)>=48: self.areas.pop(0)
        self.areas.append(a)
    def collect_pickup(self,item,collector=None):
        if item.life<=0:return
        if item.kind=='xp':
            for ally in self.allied_players:ally.xp_gain(item.value)
        elif item.kind=='chest':
            old_coins,old_chests=self.coins,self.chests
            for ally in self.allied_players:
                with self.acting(ally):ascension.chest(self)
            self.coins,self.chests=old_coins+15,old_chests+1
        elif item.kind=='health':
            for ally in ([collector] if collector else self.allied_players):
                if ally.hp>0:ally.hp=min(ally.max_hp,ally.hp+item.value)
        item.life=0
    def add_pickup(self,item):
        # XP can merge only with XP. Rare loot is never lost at the population cap.
        if len(self.pickups)<300:self.pickups.append(item);return
        stacks=[q for q in self.pickups if q.kind=='xp' and q.life>0]
        if item.kind=='xp' and stacks:
            target=min(stacks,key=lambda q:q.pos.distance_squared_to(item.pos))
            target.value+=item.value;target.life=max(target.life,item.life)
        else:self.collect_pickup(item)
    def apply_ally_aura(self,source,radius,duration,power=0.,speed=0.,regen=0.,armor=0.):
        """Apply an ally-compatible buff. In solo the source is the only ally."""
        if source.key in ('musashi','thorfinn'):
            bonus=1+source.support_bonus;power*=bonus;speed*=bonus;regen*=bonus;armor*=bonus
        affected=0
        for ally in self.allied_players:
            if ally.hp<=0:continue
            if ally.pos.distance_squared_to(source.pos)>(radius+ally.radius)**2:continue
            ally.aura_left=max(ally.aura_left,duration)
            ally.aura_power=max(ally.aura_power,power);ally.aura_speed=max(ally.aura_speed,speed)
            ally.aura_regen=max(ally.aura_regen,regen);ally.aura_armor=max(ally.aura_armor,armor)
            affected+=1
        return affected
    def toggle_musashi_soul_mode(self):
        p=self.player
        if p.key!='musashi' or p.stage<3:return False
        p.soul_mode='bond' if p.soul_mode=='self' else 'self'
        self.notice('CAMINHO DA ALMA • '+('VÍNCULO' if p.soul_mode=='bond' else 'EGO'),1.5)
        ascension.effect(self,'soul_aura',p.pos,radius=165,life=.5)
        return True
    def nearest(self,pos,limit=99999,excluded=None):
        candidates=(e for e in self.enemies if not e.dead and e.puppet_left<=0 and (not excluded or e.uid not in excluded))
        best=None; d=limit*limit
        for e in candidates:
            n=e.pos.distance_squared_to(pos)
            if n<d: best=e; d=n
        return best
    def particles_at(self,pos,color,n=12,speed=110):
        for _ in range(min(n,MAX_PARTICLES-len(self.particles))):
            angle=self.rng.random()*360; v=V(1,0).rotate(angle)*self.rng.uniform(speed*.2,speed)
            self.particles.append(Particle(V(pos),v,self.rng.uniform(.2,.65),color,self.rng.randint(2,5)))
    def spawn(self,kind=None,boss=False,pos=None,elite=None):
        if len(self.enemies)>=MAX_ENEMIES and not boss: return None
        if boss and self.boss_spawned: return self.boss
        if pos is None:
            # A circular spawn radius beyond the 1280x720 viewport's half diagonal.
            center=self.rng.choice([p for p in self.allied_players if p.hp>0] or self.allied_players).pos
            angle=self.rng.random()*360
            for attempt in range(72):
                pos=center+V(820,0).rotate(angle+attempt*5)
                if self.arena.contains(pos,45 if boss else 29):break
        pos=self.arena.constrain(V(pos),45 if boss else 25)
        kind=self.rng.choice(FAMILIES[self.arena.key][3][:min(4,1+self.waves.number//2)]) if kind is None else kind
        elite=False if elite is None else elite
        if boss: elite=False
        self.uid+=1; e=Enemy(self.uid,pos,kind,0,elite,boss);e.pos=self.arena.constrain(e.pos,e.radius);e.previous_pos=V(e.pos);tune(self,e); self.enemies.append(e)
        if not getattr(e,'trial_key',None):self.discovered.add(f'{self.arena.key}:{6 if boss else kind}')
        if boss:
            self.telemetry['boss_started']=self.time
            self.boss=e; self.boss_spawned=True; self.notice(e.name+' • ONDA '+str(self.waves.number),4.); self.sound('boss')
        return e
    def hit(self,e,damage,critical=True):
        if e.dead or e.puppet_left>0 or damage<=0 or (e.boss and e.phase_guard>0): return 0
        p=self.player; chance=min(.8,p.crit+(.15 if p.transformed and p.key=='rafael' else 0))
        crit=critical and self.rng.random()<chance; damage*=2 if crit else 1
        if e.boss:
            damage*=.8
            # Phase thresholds stop excess burst, while minimum phase duration prevents a single ultimate clearing all phases.
            floor=e.max_hp*({1:.67,2:.34}.get(e.phase,0))
            if e.phase_age<6: floor=max(floor,1.)
            damage=min(damage,max(0,e.hp-floor))
        actual=min(e.hp,damage); e.hp-=damage; e.hit=.1; self.total_damage+=actual; self.events['hits']+=1
        p.damage_dealt+=actual
        if actual>0: p.combat_left=2.
        p.gain_sigma(actual*.02)
        if actual>0 and len(self.texts)<75: self.texts.append(FloatText(V(e.pos)+V(0,-30),str(math.ceil(actual)),(255,210,102) if crit else (235,242,250),critical=crit))
        if e.hp<=0:
            e.dead=True;self.corpses.append(DefeatEcho(V(e.pos),e.kind,e.boss,.55,e.facing_left,self.arena.key));self.corpses[:]=self.corpses[-45:]
            self.kills+=1;p.kills+=1; self.particles_at(e.pos,CHARACTERS[p.key]['color'],10)
            p.gain_sigma(.8)
            if e.boss:
                self.telemetry['boss_seconds']=max(0,self.time-self.telemetry['boss_started'])
                if self.challenge:self.result='VICTORY';self.coins+=100;self.sound('victory')
                else:self.waves.clear(self)
            else:
                if e.elite:self.add_pickup(Pickup(V(e.pos),1,'chest',180))
                self.add_pickup(Pickup(V(e.pos),7 if e.elite else 3))
                if self.rng.random()<.05:self.add_pickup(Pickup(V(e.pos)+V(8,0),13,'health'))
        return actual
    def blast(self,pos,radius,damage,kind,root=False):
        for e in self.enemies:
            if not e.dead and e.pos.distance_squared_to(pos)<(radius+e.radius)**2:
                self.hit(e,damage)
                if kind=='glue': e.glue(2.2,.6+self.player.slow_bonus,root)
                if not e.boss:
                    e.pos+=unit(e.pos-pos)*(24 if self.player.transformed else 12)
                    if self.enemy_index is not None:self.enemy_index.move(e)
        color=(132,227,240) if kind=='glue' else (241,193,99) if kind=='pacoca' else (135,245,182)
        self.particles_at(pos,color,22,200)
    def fragments(self,pos,count,damage):
        for i in range(min(20,int(count))):
            self.add_projectile(Projectile(V(pos),V(330,0).rotate(360*i/max(1,count)),damage,'crumb',life=.6,radius=4))
    def dash(self):
        p=self.player
        if p.dash_cd>0 or self.transform_pause>0: return False
        p.dash_cd=2.4/max(1,p.cooldown); p.dash_left=.18; p.invulnerable=max(p.invulnerable,.23)
        self.weapon.dash(self); self.sound('dash'); return True
    def transform(self):
        if self.player.transform():
            if not self.telemetry["first_form"]:self.telemetry["first_form"]=self.time
            self.transform_pause=.55; self.weapon.passive_cd=1.; self.shake=.3; self.notice(self.player.form_name,2.5)
            from evolution_kit import transform
            transform(self)
            if self.player.key=='leozauxta': self.rhythm.start()
            self.particles_at(self.player.pos,CHARACTERS[self.player.key]['color'],65,260); self.sound('transform'); return True
        return False
    def ultimate(self):
        p=self.player
        if not p.transformed or p.ultimate_used or self.transform_pause>0: return False
        p.ultimate_used=True; p.ultimates+=1; self.weapon.ultimate(self); self.sound('ultimate')
        self.notice({'zatex':'SINFONIA DO VÉU','leozauxtaci':'CONVERGÊNCIA DAS QUATRO FORMAS','ippo':('DEMPSEY ROLL' if p.evolved else 'GAZELLE PUNCH'),'eren':'ASSALTO DO TITÃ','klein':('FIOS ESPIRITUAIS' if p.stage>=2 else 'TRUQUE FINAL'),'guxta':'COLAPSO DA LUA VERMELHA','leo':'O GRANDE DERRAMAMENTO','rafael':'PAÇOCA NUCLEAR','leozauxta':'TRIPLE SIGMA DANCE','davi':'COALA SMASH • 100%','walter':('ÚLTIMO PLANO' if p.evolved else 'REAÇÃO EM CADEIA'),'musashi':'DOIS CÉUS • UM CORTE','joe':'ÚLTIMO ROUND','thorfinn':'NÃO TENHO INIMIGOS','holden':'MERIDIANO DE SANGUE'}[p.key],3.)
        from evolution_kit import STAGES,profile
        if p.key in STAGES:self.notice(profile(p)[1],3.)
        return True
    def rhythm_tap(self,lane):
        if not self.player.transformed or self.player.key!='leozauxta' or self.transform_pause>0 or self.result:return False
        if not self.rhythm.tap(lane):return False
        p=self.player;p.dance_pose=lane+1
        # Every successful note reaches every currently living enemy; phase gates remain valid.
        self.blast(p.pos,6000,p.damage*.42,'token')
        self.add_area(Area(V(p.pos),380,.4,'wave'))
        targets=sorted((e for e in self.enemies if not e.dead),key=lambda e:e.pos.distance_squared_to(p.pos))[:3]
        for e in targets:self.add_area(Area(V(e.pos),85*p.bat_power,.7,'swarm',p.damage*.2*p.bat_power))
        self.sound('token');return True
    def hurt_player(self,damage):
        if self.player.transformed and self.rhythm.protected:return
        p=self.player
        if p.counter_left>0 and p.invulnerable<=0 and p.key in ('joe','ippo','thorfinn'):
            target=self.nearest(p.pos,220)
            if target:
                ascension.strike(self,p.pos,target.pos-p.pos,220*p.reach,36,p.damage*(1.2+p.counter_bonus),'joe_counter' if p.key=='joe' else 'deflect' if p.key=='thorfinn' else 'punch')
                p.counters+=1;p.counter_left=0.;self.sound('counter');damage*=.65
        if p.key=='klein' and p.guard_cd<=0 and p.invulnerable<=0:
            p.guard_cd=12.;p.invulnerable=.5;ascension.effect(self,'paper',p.pos,life=.7);return
        if p.key=='ippo' and p.transformed:damage*=.72
        actual=self.player.hurt(damage)
        if actual:
            self.shake=.15; self.sound('hit'); self.particles_at(self.player.pos,(235,100,143),8)
        if all(ally.hp<=0 for ally in self.allied_players) and self.result!='VICTORY': self.result='GAME_OVER'; self.sound('defeat')
    def enemy_update(self,e,dt):
        e.tick_status(dt); p=self.player; delta=p.pos-e.pos; distance=delta.length(); d=unit(delta)
        if e.puppet_mark>0 and not e.boss:
            e.puppet_mark=max(0,e.puppet_mark-dt)
            controller=next((a for a in self.allied_players if a.pid==e.puppet_owner and a.hp>0),None)
            if controller and controller.pos.distance_to(e.pos)<400:e.puppet_progress+=dt*(1+controller.puppet_bonus)
            else:e.puppet_progress=0
            if e.puppet_progress>=2.2:e.puppet_left=5.;e.puppet_mark=0;e.puppet_progress=0
        if e.puppet_left>0:
            e.puppet_left=max(0,e.puppet_left-dt);e.puppet_attack-=dt
            target=self.nearest(e.pos,650,{e.uid})
            if target:
                e.pos+=unit(target.pos-e.pos)*e.speed*1.5*dt
                if target.pos.distance_to(e.pos)<120 and e.puppet_attack<=0:
                    e.puppet_attack=.7
                    with self.acting(self.owner(e.puppet_owner)):
                        self.hit(target,self.player.damage*1.5);ascension.effect(self,'threads',e.pos,target.pos,life=.3)
            e.pos=self.arena.constrain(e.pos,e.radius);return
        if e.boss:
            e.phase_age+=dt
            if e.phase<3 and e.hp<=e.max_hp*({1:.67,2:.34}[e.phase]) and e.phase_age>=6:
                e.phase+=1; e.phase_age=0.; e.phase_guard=1.25; e.cooldown=1.8
                self.telegraphs[:]=[t for t in self.telegraphs if t.source is not e]
                e.windup_left=e.charge_left=0.
                self.notice(f'{e.name} • FASE {e.phase} / ESCUDO 1,25s',1.25)
                self.particles_at(e.pos,(243,110,176),55); self.shake=.4
            if e.phase_guard>0: return
        if e.charge_left>0:
            e.pos+=e.charge_dir*(420 if e.boss else 350)*dt
        elif e.root<=0 and e.windup_left<=0:
            direction=d; speed=e.speed*(e.slow_factor if e.slow>0 else 1)
            if e.boss:
                speed*=1+.2*(e.phase-1)
                if distance<230: direction=V(-d.y,d.x)*.5
            elif e.kind==1:
                direction=d if distance>380 else -d if distance<240 else V(-d.y,d.x)*.35
            elif e.kind==2: direction=unit(d+V(-d.y,d.x)*math.sin(self.time*5+e.uid)*.85)
            elif e.kind==4: direction=unit(d*.5+V(-d.y,d.x)*(.9 if distance<280 else .25))
            e.pos+=direction*speed*dt
        e.pos=self.arena.constrain(e.pos,e.radius)
        if e.cooldown<=0 and distance<850:
            if e.boss:
                pattern=e.action%4; e.action+=1; e.cooldown=3.-.6*(e.phase-1)
                if not getattr(e,'trial_key',None):
                    from boss_patterns import queue
                    queue(self,e,p,pattern)
                    if distance<p.radius+e.radius:self.hurt_player(e.damage)
                    return
                if getattr(e,'trial_key',None):
                    e.cooldown=max(1.2,2.8-e.phase*.35)
                    ascension.effect(self,'swarm' if e.trial_key=='leozauxta' else ('gravity','lightning','resonance','spill')[pattern],e.pos,radius=140,life=.7)
                    if e.trial_key=='leozauxtaci' and pattern==2:
                        for ally in self.allied_players:
                            for offset in (-150,0,150):self.telegraphs.append(Telegraph(self.arena.constrain(ally.pos+V(offset,0)),70,1.2,'hostile_blast',e.damage,e))
                        return
                if pattern==0: self.telegraphs.append(Telegraph(V(e.pos),90,.75,'boss_ring',e.damage,e))
                elif pattern==1: self.telegraphs.append(Telegraph(V(e.pos),e.radius,.8,'charge',e.damage,e,V(d)))
                elif pattern==2:
                    for i in range(e.phase):
                        self.telegraphs.append(Telegraph(V(p.pos)+p.facing*i*145,115,.95+i*.2,'hostile_blast',e.damage*1.4,e))
                else:
                    for i in range(4+e.phase):
                        self.telegraphs.append(Telegraph(e.pos+V(110,0).rotate(i*72),38,.9,'summon',0,e))
            elif e.kind==1:
                self.telegraphs.append(Telegraph(V(e.pos),22,.6,'ranged',e.damage,e,V(d))); e.cooldown=2.8
            elif e.kind==5:
                self.telegraphs.append(Telegraph(V(e.pos),e.radius,.75,'charge',e.damage,e,V(d))); e.cooldown=4.
        if e.kind in (0,2,3,4) and not e.boss and e.cooldown<=0 and distance<p.radius+e.radius+28:
            e.cooldown=1.4;e.attack_name='CONTACTO';self.telegraphs.append(Telegraph(V(e.pos),e.radius+30,.45,'enemy_melee',e.damage,e))
        if distance<p.radius+e.radius and (e.boss or e.charge_left>0):self.hurt_player(e.damage)
    def resolve_telegraph(self,t):
        if isinstance(t.source,Enemy) and t.source.dead: return
        if isinstance(t.source,Enemy):t.source.attack_left=max(t.source.attack_left,.35)
        if t.kind=='enemy_melee':
            for ally in self.allied_players:
                if ally.hp>0 and ally.pos.distance_to(t.pos)<t.radius+ally.radius:
                    with self.acting(ally):self.hurt_player(t.damage)
            return
        from boss_patterns import resolve
        if resolve(self,t):return
        if ascension.resolve_special(self,t):return
        p=self.player
        if t.kind=='whip_visual': return
        if t.kind=='charge':
            t.source.charge_dir=t.direction; t.source.charge_left=.6
        elif t.kind=='ranged':
            self.add_projectile(Projectile(V(t.pos),t.direction*255,t.damage,'hostile',life=4,hostile=True))
        elif t.kind=='boss_ring':
            n=10+4*t.source.phase
            for i in range(n): self.add_projectile(Projectile(V(t.source.pos),V(190+25*t.source.phase,0).rotate(360*i/n+self.time*20),t.damage,'hostile',life=5,hostile=True))
        elif t.kind=='hostile_blast':
            for ally in self.allied_players:
                if ally.hp>0 and ally.pos.distance_to(t.pos)<t.radius+ally.radius:
                    with self.acting(ally):self.hurt_player(t.damage)
            self.add_area(Area(V(t.pos),t.radius,.4,'danger_wave')); self.particles_at(t.pos,(239,86,149),30)
        elif t.kind=='summon': self.spawn(kind=self.rng.randrange(6),pos=t.pos,elite=False)
        elif t.kind in ('dance','dance_final'):
            pos=V(p.pos); self.events['dance_pulses']+=1
            self.blast(pos,t.radius,t.damage,'token'); self.add_area(Area(pos,t.radius,.4,'wave'))
            if t.kind=='dance':
                for i in range(12): self.add_projectile(Projectile(V(pos),V(480,0).rotate(i*30),p.damage,'token',pierce=2))
                self.add_area(Area(V(pos),170,1.2,'swarm',p.damage))
            self.shake=.25
        else:
            kind='glue' if t.kind=='glue_ultimate' else 'pacoca' if t.kind in ('rain','pacoca_ultimate') else 'token'
            self.blast(t.pos,t.radius,t.damage,kind,root=kind=='glue'); self.add_area(Area(V(t.pos),t.radius,.4,'wave'))
            if kind=='glue': self.add_area(Area(V(t.pos),t.radius,6.,'prison',p.damage*.25))
            if kind=='pacoca': self.fragments(t.pos,18 if 'ultimate' in t.kind else 5,p.damage*.65)
            if 'ultimate' in t.kind: self.shake=.4; self.hitstop=.035
    def projectile_update(self,q,dt):
        if q.dead: return
        travel=min(max(0,dt),max(0,q.life))
        q.life-=dt
        if travel<=0: q.dead=True; return
        if q.homing:
            target=self.nearest(q.pos,500,q.hit)
            if target: q.vel=q.vel.lerp(unit(target.pos-q.pos)*q.vel.length(),min(1,dt*5))
        previous=V(q.pos); q.pos+=q.vel*travel
        if q.hostile:
            for ally in self.allied_players:
                if ally.hp>0 and segment_distance(ally.pos,previous,q.pos)<ally.radius+q.radius:
                    with self.acting(ally):self.hurt_player(q.damage)
                    q.dead=True;break
            q.dead=q.dead or q.life<=0 or not self.arena.contains(q.pos)
            return
        # Snapshot avoids processing newly added fragments in this frame.
        minx=min(previous.x,q.pos.x)-q.radius;maxx=max(previous.x,q.pos.x)+q.radius
        miny=min(previous.y,q.pos.y)-q.radius;maxy=max(previous.y,q.pos.y)+q.radius
        nearby=self.enemy_index.query(minx,miny,maxx,maxy) if self.enemy_index is not None else self.enemies
        candidates=sorted((e for e in nearby if not e.dead and e.puppet_left<=0 and e.uid not in q.hit
            and minx-e.radius<e.pos.x<maxx+e.radius and miny-e.radius<e.pos.y<maxy+e.radius
            and segment_distance(e.pos,previous,q.pos)<e.radius+q.radius),key=lambda e:(e.pos.distance_squared_to(previous),e.uid))
        for e in candidates:
            if q.dead: break
            q.hit.add(e.uid); self.hit(e,q.damage)
            ascension.effect(self,'spark',e.pos,radius=22,life=.22)
            if q.kind in ('glue','bonder','jet'):
                e.glue(1.7,.5+self.player.slow_bonus)
                radius=(75 if q.kind=='bonder' else 32)*self.player.area*(1.4 if self.player.transformed else 1)
                self.add_area(Area(V(e.pos),radius,3.2,'glue',q.damage*.15))
                if q.kind=='bonder': self.blast(e.pos,radius,q.damage*.65,'glue')
                if q.kind=='jet' and not e.boss:
                    e.pos+=unit(q.vel)*32
                    if self.enemy_index is not None:self.enemy_index.move(e)
            elif q.kind=='flask':
                self.add_area(Area(V(e.pos),60*self.player.area,1.8,'chemical',q.damage*.22))
            elif q.kind in ('pacoca','stuffed'):
                self.fragments(e.pos,self.player.shards,q.damage*.25)
                if q.kind=='stuffed': self.blast(e.pos,90,q.damage*.7,'pacoca')
            self.particles_at(e.pos,CHARACTERS[self.player.key]['color'],4)
            if q.bounce>0:
                target=self.nearest(e.pos,360,q.hit)
                if target:
                    q.pos=V(e.pos); q.vel=unit(target.pos-q.pos)*q.vel.length(); q.bounce-=1; break
            if q.pierce>0: q.pierce-=1
            else: q.dead=True
        q.dead=q.dead or q.life<=0 or not self.arena.contains(q.pos)
    def update(self,dt,movement=None):
        if self.result: return
        if movement is None:movement=V()
        dt=min(.05,max(0,dt)); self.message_left=max(0,self.message_left-dt); self.shake=max(0,self.shake-dt)
        if self.transform_pause>0:
            self.transform_pause=max(0,self.transform_pause-dt); return
        if self.hitstop>0: self.hitstop=max(0,self.hitstop-dt); return
        self.time+=dt; p=self.player
        from expedition import tick as objectives_tick
        objectives_tick(self,dt)
        for body in self.corpses:body.life-=dt
        self.corpses[:]=[body for body in self.corpses if body.life>0]
        inputs=movement if isinstance(movement,dict) else {p.pid:movement}
        for ally in self.allied_players:
            if ally.hp<=0:
                nearby=any(a is not ally and a.hp>0 and a.pos.distance_to(ally.pos)<95 for a in self.allied_players)
                ally.revive_progress=ally.revive_progress+dt if nearby else 0.
                if ally.revive_progress>=3:
                    ally.hp=ally.max_hp*.4;ally.invulnerable=2.;ally.revive_progress=0.;self.notice('ALIADO REANIMADO',2.)
                continue
            move=inputs.get(ally.pid,V())
            if ally.key=='leozauxta' and ally.transformed:move=V()
            ally.terrain_speed=self.arena.speed_at(ally.pos);ally.update(dt,move)
            self.rhythms[ally.pid].update(ally.form_age,ally.key=='leozauxta' and ally.transformed)
            if ally.key=='walter' and not ally.evolved and self.time>=150 and not ally.transformed:
                ally.evolved=True;ally.base_damage*=1.15;self.notice('HEISENBERG • DIGA MEU NOME',3.);self.sound('level')
            ally.pos=self.arena.constrain(ally.pos,ally.radius)
        for fx in self.effects:fx.life-=dt
        self.effects[:]=[fx for fx in self.effects if fx.life>0]
        if self.waves.rest>0:
            self.waves.update(self,dt)
            return
        self.hazard_cd-=dt
        if self.hazard_cd<=0:
            self.hazard_cd=self.arena.hazard_interval
            for pos,radius in self.arena.hazards(p.pos,self.time):
                self.telegraphs.append(Telegraph(V(pos),radius,1.4,'hostile_blast',18))
        if not self.challenge:self.waves.update(self,dt)
        if self.result:return
        for ally in self.allied_players:
            if ally.hp<=0:continue
            with self.acting(ally):
                self.weapon.update(self,dt)
                if self.result:return
                ascension.tick(self,dt,age_effects=False)
                if self.result:return
        for e in list(self.enemies):
            if not e.dead:
                target=min((a for a in self.allied_players if a.hp>0),key=lambda a:a.pos.distance_squared_to(e.pos),default=p)
                with self.acting(target):self.enemy_update(e,dt)
                delta=e.pos-e.previous_pos
                e.walking=delta.length_squared()>.001
                if abs(delta.x)>.001:e.facing_left=delta.x<0
                e.previous_pos=V(e.pos)
        pending=self.telegraphs; self.telegraphs=OwnedTelegraphs(self)
        for t in pending:
            t.delay-=dt
            with self.acting(self.owner(t.owner)):
                if t.delay<=0: self.resolve_telegraph(t)
                else: self.telegraphs.append(t)
            if self.result:return
        for a in self.areas:
            a.life-=dt; a.tick-=dt
            if a.kind=='swarm':
                target=self.nearest(a.pos,650); destination=target.pos if target else self.owner(a.owner).pos
                a.pos+=unit(destination-a.pos)*min(180*dt,a.pos.distance_to(destination))
            if a.tick<=0 and a.damage>0:
                a.tick=.45
                for e in self.enemies:
                    if not e.dead and e.pos.distance_squared_to(a.pos)<(a.radius+e.radius)**2:
                        with self.acting(self.owner(a.owner)):
                            self.hit(e,a.damage,False)
                            if a.kind in ('glue','prison'): e.glue(.7,.55+self.player.slow_bonus,a.kind=='prison')
        from spatial import EnemyGrid
        self.enemy_index=EnemyGrid(self.enemies)
        try:
            for q in list(self.projectiles):
                with self.acting(self.owner(q.owner)):self.projectile_update(q,dt)
        finally:self.enemy_index=None
        if self.result:return
        for pickup in self.pickups:
            if pickup.life<=0:continue
            collector=min((a for a in self.allied_players if a.hp>0),key=lambda a:a.pos.distance_squared_to(pickup.pos),default=p)
            pickup.life-=dt; distance=pickup.pos.distance_to(collector.pos)
            if pickup.life<=0:continue
            if distance<collector.magnet: pickup.pos+=unit(collector.pos-pickup.pos)*min(distance,510*dt)
            if pickup.pos.distance_to(collector.pos)<collector.radius+12:
                self.collect_pickup(pickup,collector)
                collector.gain_sigma(.15)
                pickup.life=0; self.events['pickups']+=1
        for x in self.particles: x.life-=dt; x.pos+=x.vel*dt; x.vel*=max(0,1-dt*3)
        for x in self.texts: x.life-=dt; x.pos.y-=40*dt
        self.enemies=[e for e in self.enemies if not e.dead]
        self.projectiles=[q for q in self.projectiles if not q.dead]
        self.areas=[a for a in self.areas if a.life>0]
        self.pickups=[q for q in self.pickups if q.life>0]
        self.particles=[q for q in self.particles if q.life>0]
        self.texts=[q for q in self.texts if q.life>0]
        for e in self.enemies:e.pos=self.arena.constrain(e.pos,e.radius)
        if all(a.hp<=0 for a in self.allied_players) and not self.result: self.result='GAME_OVER'
