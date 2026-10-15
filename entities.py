from dataclasses import dataclass, field
import math
import pygame as pg
from settings import CHARACTERS
V=pg.Vector2

def unit(v,fallback=(1,0)):
    return v.normalize() if v.length_squared()>1e-10 else V(fallback)

def segment_distance(p,a,b):
    d=b-a
    if d.length_squared()==0: return p.distance_to(a)
    t=max(0,min(1,(p-a).dot(d)/d.length_squared()))
    return p.distance_to(a+d*t)

class Player:
    def __init__(self,key):
        c=CHARACTERS[key]; self.key=key; self.pos=V(1800,1800); self.facing=V(1,0); self.facing_left=False
        self.base_hp=float(c['hp']); self.hp=self.base_hp; self.base_damage=c['damage']; self.base_speed=c['speed']
        self.crit=c['crit']; self.power=1.; self.haste=1.; self.reach=1.; self.speed_bonus=1.
        self.armor=10 if key=='leo' else 0; self.shots=1; self.magnet=105.; self.regen=.15
        self.cooldown=1.; self.area=1.; self.slow_bonus=0.; self.form_power=1.; self.shards=3; self.bat_power=1.; self.triple=0; self.dance=1.
        self.level=1; self.xp=0.; self.pending=0; self.sigma=0.; self.form_left=0.; self.form_age=0.; self.ultimate_used=False
        self.invulnerable=0.; self.dash_cd=0.; self.dash_left=0.; self.attack_pose=0.; self.walking=False
        self.attack_animation_left=0.;self.hurt_flash=0.
        self.form_recovery=0.; self.energy_budget=0.; self.combat_left=0.; self.terrain_speed=1.; self.smash_power=1.; self.whip_power=1.
        self.evolved=False; self.chemistry=1.; self.dance_pose=0; self.soul_mode='self'
        # Aura state is local today, but keeps the same contract future allied players will use.
        self.aura_left=0.; self.aura_power=0.; self.aura_speed=0.; self.aura_regen=0.; self.aura_armor=0.
        self.upgrades={}; self.transforms=0; self.ultimates=0
        self.aim=V(1,0); self.stage=0; self.guard_cd=0.; self.aux={}; self.evolutions=set(); self.passives=set(); self.rerolls=3
        self.allowed_items=None;self.pid=0;self.revive_progress=0.
        self.damage_dealt=0.;self.damage_taken=0.;self.kills=0
        self.specialization="";self.specialization_rank=0;self.counter_bonus=0.;self.puppet_bonus=0.;self.support_bonus=0.
        self.counter_left=0.;self.counters=0;self.run_rule="standard";self.clip_seen=set();self.short_cinema=True
    @property
    def transformed(self): return self.form_left>0
    @property
    def max_hp(self): return self.base_hp+(60 if self.key=='leozauxta' and self.transformed else 0)
    @property
    def damage(self): return self.base_damage*self.power*(1+self.aura_power)*((1+.9*self.form_power) if self.transformed else 1)
    @property
    def radius(self): return 30 if self.key=='eren' and self.transformed else 27 if self.key=='leozauxta' and self.transformed else 15
    @property
    def threshold(self): return 10+self.level*7
    def xp_gain(self,n):
        self.xp+=n
        while self.xp>=self.threshold:
            self.xp-=self.threshold; self.level+=1; self.pending+=1
    def transform(self):
        if self.run_rule=='noform' or self.sigma<100 or self.transformed or self.form_recovery>0: return False
        self.sigma=0; self.form_left=14.; self.form_age=0; self.ultimate_used=False; self.transforms+=1
        self.hp=min(self.max_hp,self.hp+18); self.invulnerable=max(self.invulnerable,.7)
        return True
    @property
    def display_name(self):
        from legends import NAMES
        if self.key in NAMES:return NAMES[self.key][self.stage]
        if self.key=='klein': return ('KLEIN • MÁGICO','GEHRMAN • SEM ROSTO','KLEIN • MARIONETISTA')[self.stage]
        if self.key=='ippo' and self.evolved:return 'IPPO • CAMPEÃO'
        if self.key=='eren' and self.evolved:return 'EREN • VETERANO'
        if self.key=='musashi': return ('MUSASHI • VAGANTE','MUSASHI • CAMINHO DA ESPADA','MUSASHI • CAMINHO DA MORTE','MUSASHI • CAMINHO DA ALMA')[self.stage]
        return 'HEISENBERG' if self.key=='walter' and self.evolved else CHARACTERS[self.key]['name']
    @property
    def form_name(self):
        from evolution_kit import STAGES,profile
        if self.key in STAGES:
            name=profile(self)[0]
            return name+(' • '+('EGO' if self.soul_mode=='self' else 'VÍNCULO') if self.key=='musashi' and self.stage==3 else '')
        return ('FELINA' if self.evolved else 'TRAJE HAZMAT') if self.key=='walter' else ('MUSHIN • '+('EGO' if self.soul_mode=='self' else 'VÍNCULO') if self.key=='musashi' else CHARACTERS[self.key]['form'])
    def sprite(self,time):
        if self.key in ('ippo','eren','klein','musashi','joe','thorfinn','holden'):
            from pixel_characters import sprite_name
            return sprite_name(self,time)
        if self.key in ('zatex','leozauxtaci'):return f'{self.key}_{"form" if self.transformed else "base"}_{int(time*8)%4}'
        if self.key=='walter':
            group=('felina' if self.evolved else 'hazmat') if self.transformed else ('heisenberg' if self.evolved else 'walter')
            return f'{group}_{int(time*6)%2}'
        frame=int(time*8)%4
        if self.transformed:
            if self.key=='leozauxta': return f'titan_{(int(self.form_age*6)+self.dance_pose)%6}'
            return f'{dict(leo="leo_calvo",rafael="pacoca",davi="full_cowl",guxta="red_moon")[self.key]}_{frame}'
        if self.key=='leozauxta': return f'leozauxta_{frame}'
        if self.dash_left>0: return self.key+'_dash'
        if self.attack_pose>0: return self.key+'_attack'
        return f'{self.key}_{"walk" if self.walking else "idle"}_{frame if self.walking else frame%2}'
    def gain_sigma(self,amount):
        if self.transformed or self.form_recovery>0: return
        gain=min(max(0,amount),self.energy_budget)
        self.sigma=min(100,self.sigma+gain); self.energy_budget-=gain
    def update(self,dt,movement):
        self.form_recovery=max(0,self.form_recovery-dt)
        self.aura_left=max(0,self.aura_left-dt)
        if self.aura_left==0:self.aura_power=self.aura_speed=self.aura_regen=self.aura_armor=0.
        self.guard_cd=max(0,self.guard_cd-dt)
        self.counter_left=max(0,self.counter_left-dt)
        # A one-second reservoir preserves credit between discrete weapon shots.
        self.energy_budget=min(2.5,self.energy_budget+dt*2.5) if not self.transformed and self.form_recovery<=0 else 0.
        if self.combat_left>0: self.gain_sigma(.7*min(dt,self.combat_left))
        self.combat_left=max(0,self.combat_left-dt)
        self.invulnerable=max(0,self.invulnerable-dt); self.dash_cd=max(0,self.dash_cd-dt)
        self.attack_pose=max(0,self.attack_pose-dt)
        self.attack_animation_left=max(0,self.attack_animation_left-dt)
        self.hurt_flash=max(0,self.hurt_flash-dt)
        self.walking=movement.length_squared()>0
        if self.walking:
            self.facing=unit(movement)
            # Vertical movement keeps the last horizontal look direction.
            if abs(movement.x)>1e-8: self.facing_left=movement.x<0
        if self.form_left>0:
            self.form_age+=dt; self.form_left=max(0,self.form_left-dt)
            self.hp=min(self.hp,self.max_hp)
            if self.form_left==0: self.form_recovery=10.; self.energy_budget=0.
        speed=self.base_speed*self.speed_bonus*(1+self.aura_speed)*self.terrain_speed*(1.1 if self.transformed and self.key=='rafael' else 1)
        if self.dash_left>0:
            self.pos+=self.facing*speed*3.4*dt; self.dash_left=max(0,self.dash_left-dt)
        elif self.walking: self.pos+=unit(movement)*speed*dt
        self.pos.x=max(60,min(3540,self.pos.x)); self.pos.y=max(60,min(3540,self.pos.y))
        self.hp=min(self.max_hp,self.hp+(self.regen+self.aura_regen)*dt)
    def hurt(self,amount):
        if amount<=0 or self.invulnerable>0 or self.hp<=0: return 0
        armor=self.armor+self.aura_armor+(30 if self.transformed else 0)
        damage=min(self.hp,amount*(1-min(.7,armor/(100+armor))))
        self.hp=max(0,self.hp-damage); self.invulnerable=.45
        self.damage_taken+=damage
        self.hurt_flash=.28
        return damage

class Enemy:
    def __init__(self,uid,pos,kind,time=0,elite=False,boss=False):
        self.uid=uid; self.pos=V(pos); self.kind=kind; self.elite=elite; self.boss=boss; self.dead=False
        self.facing_left=False;self.previous_pos=V(pos)
        self.radius=43 if boss else (24 if kind in (3,5) else 17)*(1.2 if elite else 1)
        self.max_hp=15000 if boss else [42,36,25,115,32,145][kind]*(1+time/170)*(2 if elite else 1)
        self.hp=self.max_hp; self.speed=(73 if boss else [89,61,131,63,111,56][kind])*(1+min(.35,time/900))
        self.damage=(26 if boss else [10,10,8,17,9,21][kind])*(1.3 if elite else 1)
        self.slow=0.; self.slow_factor=1.; self.root=0.; self.root_immunity=0.; self.hit=0.
        self.phase_guard=0.; self.phase_age=0.; self.cooldown=2.; self.phase=1; self.action=0; self.charge_left=0.; self.charge_dir=V(1,0)
        self.puppet_mark=0.;self.puppet_progress=0.;self.puppet_left=0.;self.puppet_attack=0.;self.puppet_owner=0
        self.attack_name=''
        self.windup_left=0.;self.attack_left=0.;self.walking=False
    def tick_status(self,dt):
        for name in ('slow','root','root_immunity','hit','cooldown','charge_left','phase_guard','windup_left','attack_left'): setattr(self,name,max(0,getattr(self,name)-dt))
    def glue(self,duration,strength,root=False):
        self.slow=max(self.slow,duration); self.slow_factor=max(.75 if self.boss else .22,1-strength)
        if root and not self.boss and self.root_immunity<=0:
            self.root=.7; self.root_immunity=2.5

@dataclass
class Projectile:
    pos: V
    vel: V
    damage: float
    kind: str
    life: float=2.3
    radius: float=8
    pierce: int=0
    bounce: int=0
    homing: bool=False
    hostile: bool=False
    hit: set=field(default_factory=set)
    dead: bool=False
    owner: int=0

@dataclass
class Area:
    pos: V
    radius: float
    life: float
    kind: str
    damage: float=0
    tick: float=0
    owner: int=0

@dataclass
class Telegraph:
    pos: V
    radius: float
    delay: float
    kind: str
    damage: float
    source: object=None
    direction: object=None
    owner: int=0
    total_delay: float=0.
    reach: float=0.
    spread: float=0.
    count: int=0

@dataclass
class Pickup:
    pos: V
    value: float
    kind: str='xp'
    life: float=75

@dataclass
class Particle:
    pos: V
    vel: V
    life: float
    color: tuple
    size: int=3

@dataclass
class FloatText:
    pos: V
    text: str
    color: tuple
    life: float=.65
    critical: bool=False

@dataclass
class DefeatEcho:
    pos: V
    kind: int
    boss: bool=False
    life: float=.55
    facing_left: bool=False
    theme: str='crypt'
