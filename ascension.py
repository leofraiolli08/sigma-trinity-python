"""Solo expansion: distinct combat patterns, deterministic VFX and build weapons."""
import math
from dataclasses import dataclass
from entities import V, Projectile, Area, Telegraph, unit, segment_distance
from weapons import Weapon, WEAPONS

@dataclass
class Effect:
    kind: str
    pos: V
    end: V
    color: tuple
    life: float=.35
    duration: float=.35
    radius: float=70
    art: str=''

COLORS={'leo':(125,218,222),'rafael':(244,193,94),'leozauxta':(128,239,150),
        'davi':(92,235,163),'walter':(103,198,235),'guxta':(224,99,140),
        'ippo':(255,159,101),'eren':(164,214,179),'klein':(202,162,248)}
COLORS.update(zatex=(179,150,235),leozauxtaci=(237,204,141))
COLORS['musashi']=(229,199,141)
COLORS.update(joe=(232,122,94),thorfinn=(179,203,160),holden=(215,193,159))

def effect(s,kind,pos,end=None,radius=70,life=.35,color=None):
    if len(s.effects)>=90:s.effects.pop(0)
    from evolution_kit import STAGES,signature,stage_of
    primary={'ippo':('punch','uppercut'),'eren':('punch','stomp','crystal'),
             'klein':('cards',),'musashi':('musashi_slash','death_line','soul_aura'),
             'joe':('joe_counter','joe_jab'),'thorfinn':('dagger_cut','deflect','vinland_aura'),
             'holden':('rifle_flash',)}
    illustrated=kind in primary.get(s.player.key,())
    art=signature(s.player.key,stage_of(s.player)) if illustrated and s.player.key in STAGES and s.player.key!='walter' else ''
    s.effects.append(Effect(kind,V(pos),V(end if end is not None else pos),color or COLORS[s.player.key],life,life,radius,art))

def strike(s,origin,direction,reach,width,damage,kind='slash'):
    s.player.attack_animation_left=.28
    end=origin+unit(direction)*reach
    effect(s,kind,origin,end,radius=width)
    for e in s.enemies:
        if not e.dead and segment_distance(e.pos,origin,end)<width+e.radius:
            s.hit(e,damage)
            if not e.boss:
                e.pos=s.arena.constrain(e.pos+unit(direction)*12,e.radius)
                if s.enemy_index is not None:s.enemy_index.move(e)

class IppoWeapon(Weapon):
    name='JAB / DIRETO'; kind='punch'; sound='hit'; speed=0
    def __init__(self):super().__init__();self.combo=0
    def attack_limit(self,p):return 150*p.reach
    def fire(self,s,target):
        p=s.player
        if target.pos.distance_to(p.pos)>150*p.reach:return
        self.combo+=1
        finisher=self.combo%(2 if p.evolved else 3)==0
        strike(s,p.pos,unit(target.pos-p.pos),(140 if p.evolved else 125)*p.reach,32*p.area,p.damage*(1.7 if finisher else 1.2),'uppercut' if finisher and not p.evolved else 'punch')
        if finisher:target.glue(.7,.45)
        s.sound('hit')
    def skill(self,s,target):
        p=s.player
        if target and target.pos.distance_to(p.pos)<210*p.reach:
            d=unit(target.pos-p.pos)
            if self.skill_index%2:
                strike(s,p.pos,d,180*p.reach,48,p.damage*3.4,'uppercut');s.notice('GAZELLE PUNCH',.8)
            else:
                strike(s,p.pos,d,135*p.reach,45,p.damage*2.6,'punch');target.glue(1.8,.55);s.notice('LIVER BLOW',.8)
    def passive(self,s):
        if s.player.transformed:s.player.invulnerable=max(s.player.invulnerable,.15)
    def dash(self,s):
        p=s.player;p.counter_left=max(p.counter_left,.55);effect(s,'afterimage',p.pos,p.pos+p.facing*80)
    def ultimate(self,s):
        from evolution_kit import ultimate
        return ultimate(s)

class ErenWeapon(Weapon):
    name='LÂMINAS / TITÃ';kind='blade';sound='shot';speed=700
    def attack_limit(self,p):return (230 if p.transformed else 180)*p.reach+40
    def fire(self,s,target):
        p=s.player;d=unit(target.pos-p.pos)
        reach=(230 if p.transformed else 180)*p.reach
        if target.pos.distance_to(p.pos)>reach+40:return
        for angle in (-22,22):strike(s,p.pos,d.rotate(angle),reach,42 if p.transformed else 25,p.damage*.95,'crystal' if p.transformed and p.evolved else 'punch' if p.transformed else 'slash')
    def skill(self,s,target):
        p=s.player
        if not target:return
        if p.transformed:
            s.blast(p.pos,200*p.area,p.damage*2.2,'titan');effect(s,'stomp',p.pos,radius=200*p.area,life=.7)
        else:
            d=unit(target.pos-p.pos);end=s.arena.constrain(p.pos+d*min(180,target.pos.distance_to(p.pos)),p.radius)
            effect(s,'cable',p.pos,target.pos,life=.4)
            strike(s,p.pos,d,260,40,p.damage*2.3);p.pos=end;p.invulnerable=max(p.invulnerable,.3)
    def passive(self,s):
        if s.player.transformed:s.player.hp=min(s.player.max_hp,s.player.hp+1.1)
    def dash(self,s):
        p=s.player;strike(s,p.pos,p.facing,170,35,p.damage,'slash')
    def ultimate(self,s):
        from evolution_kit import ultimate
        return ultimate(s)

class KleinWeapon(Weapon):
    name='BALA DE AR / CARTAS';kind='card';sound='shot';speed=720
    def fire(self,s,target):
        p=s.player
        self.shoot(s,p.pos,unit(target.pos-p.pos),p.damage,'card' if self.skill_index%2 else 'air_bullet',pierce=1 if p.evolved else 0)
        for i in range(1,min(5,int(p.shots))):self.shoot(s,p.pos,unit(target.pos-p.pos).rotate((1 if i%2 else -1)*((i+1)//2)*12),p.damage*.7,'card',pierce=1)
    def skill(self,s,target):
        p=s.player
        if not target:return
        if p.stage>=2:
            targets=sorted((e for e in s.enemies if not e.dead),key=lambda e:e.pos.distance_squared_to(p.pos))[:3]
            for e in targets:
                effect(s,'threads',p.pos,e.pos,life=2.)
                e.glue(2.2,.7,True)
                if not e.boss:e.puppet_mark=3.;e.puppet_progress=0.;e.puppet_owner=p.pid
            s.notice('FIOS DO CORPO ESPIRITUAL',.9)
        else:
            # Flame attack is an adaptation of the Magician's fire control.
            for angle in (-16,0,16):self.shoot(s,p.pos,unit(target.pos-p.pos).rotate(angle),p.damage*1.2,'flame',pierce=2)
    def passive(self,s):
        if s.player.transformed:s.player.guard_cd=max(0,s.player.guard_cd-1)
    def dash(self,s):
        p=s.player;effect(s,'paper',p.pos,life=.7);effect(s,'flame',p.pos+p.facing*100,life=.6)
    def ultimate(self,s):
        from evolution_kit import ultimate
        return ultimate(s)

WEAPONS.update(ippo=IppoWeapon,eren=ErenWeapon,klein=KleinWeapon)

class ZatexWeapon(Weapon):
    name='RESSONÂNCIA DO VÉU';kind='note';sound='token';speed=560
    def fire(self,s,target):
        p=s.player;d=unit(target.pos-p.pos)
        for i in range(min(5,int(p.shots))):self.shoot(s,p.pos,d.rotate((i-(p.shots-1)/2)*9),p.damage,'note',pierce=1,homing=p.transformed)
        effect(s,'seal',p.pos,radius=34,life=.2)
    def skill(self,s,target):
        if not target:return
        p=s.player
        for angle in (-25,0,25):strike(s,p.pos,unit(target.pos-p.pos).rotate(angle),280*p.reach,25,p.damage*.8,'threads')
        target.glue(1.4,.45);s.sound('token')
    def passive(self,s):
        if s.player.transformed:
            p=s.player;effect(s,'seal',p.pos,radius=125,life=.4);s.blast(p.pos,125,p.damage*.4,'echo')
    def dash(self,s):effect(s,'afterimage',s.player.pos,life=.4)
    def ultimate(self,s):
        for i in range(3):s.telegraphs.append(Telegraph(V(s.player.pos),200+i*90,.25+i*.4,'resonance',s.player.damage*1.7))

class ConvergenceWeapon(Weapon):
    name='QUATRO ASSINATURAS';kind='note';sound='token';speed=600
    def __init__(self):
        super().__init__()
        from weapons import GlueWeapon,GuxtaWeapon,CoalaWeapon
        self.parts=[GlueWeapon(),GuxtaWeapon(),ZatexWeapon(),CoalaWeapon()];self.turn=0
    def fire(self,s,target):self.parts[self.turn%4].fire(s,target);self.turn+=1
    def skill(self,s,target):
        part=self.parts[self.skill_index%4];part.skill(s,target);part.skill_index+=1
    def passive(self,s):
        if s.player.transformed:self.parts[self.turn%4].passive(s)
    def dash(self,s):self.parts[3].dash(s);self.parts[0].dash(s)
    def ultimate(self,s):
        for i,part in enumerate(self.parts):
            start=len(s.telegraphs);part.ultimate(s)
            for t in s.telegraphs[start:]:t.delay+=i*.4

WEAPONS.update(zatex=ZatexWeapon,leozauxtaci=ConvergenceWeapon)

class MusashiWeapon(Weapon):
    """Grounded swordsmanship: the effects visualize timing and intent, not magic."""
    name='NITEN ICHI-RYŪ';kind='blade';sound='hit';speed=0
    def attack_limit(self,p):return 185*p.reach
    def fire(self,s,target):
        p=s.player
        if not target or target.pos.distance_to(p.pos)>185*p.reach:return
        d=unit(target.pos-p.pos);stage=p.stage
        strike(s,p.pos,d,150*p.reach,22,p.damage*1.28,'musashi_slash')
        if stage>=1: strike(s,p.pos,d.rotate(-36 if self.skill_index%2 else 36),175*p.reach,20,p.damage*.92,'musashi_slash')
        if stage>=2 and target.hp/target.max_hp<=.35:
            strike(s,p.pos,d,175*p.reach,18,p.damage*.75,'death_line')
        s.sound('hit')
    def skill(self,s,target):
        p=s.player;stage=p.stage;d=unit((target.pos-p.pos) if target else p.aim)
        if stage==0:
            strike(s,p.pos,d,270*p.reach,20,p.damage*2.8,'musashi_slash')
            p.pos=s.arena.constrain(p.pos+d*95,p.radius);p.invulnerable=max(p.invulnerable,.18)
            s.notice('SAQUE INSTINTIVO',.8)
        elif stage==1:
            for angle in (-26,0,26):strike(s,p.pos,d.rotate(angle),250*p.reach,24,p.damage*1.55,'musashi_slash')
            p.invulnerable=max(p.invulnerable,.12);s.notice('NITEN ICHI-RYŪ',.8)
        elif stage==2:
            for angle in (-18,0,18):strike(s,p.pos,d.rotate(angle),310*p.reach,17,p.damage*1.45,'death_line')
            if target and target.hp/target.max_hp<=.4: strike(s,p.pos,d,330*p.reach,23,p.damage*2.4,'death_line')
            s.notice('CAMINHO DA MORTE',.8)
        elif p.soul_mode=='self':
            s.apply_ally_aura(p,0,3.5,power=.24,speed=.16,regen=.55,armor=8)
            effect(s,'soul_aura',p.pos,radius=92,life=.7);s.notice('ALMA • EGO',.8)
        else:
            affected=s.apply_ally_aura(p,275,3.5,power=.12,speed=.12,regen=.36,armor=5)
            effect(s,'soul_aura',p.pos,radius=275,life=.7);s.notice(f'ALMA • VÍNCULO  {affected} ALIADO(S)',.8)
    def passive(self,s):
        p=s.player
        if p.stage>=1 and p.transformed:p.invulnerable=max(p.invulnerable,.055)
        if p.stage>=3 and p.soul_mode=='bond':
            s.apply_ally_aura(p,275,1.15,power=.07,speed=.07,regen=.18,armor=3)
            effect(s,'soul_aura',p.pos,radius=275,life=.28)
    def dash(self,s):
        p=s.player;strike(s,p.pos,p.facing,160*p.reach,20,p.damage*.9,'musashi_slash')
        effect(s,'afterimage',p.pos,p.pos-p.facing*70,life=.25)
    def ultimate(self,s):
        from evolution_kit import ultimate
        return ultimate(s)

WEAPONS.update(musashi=MusashiWeapon)

def resolve_special(s,t):
    from legends import resolve
    if resolve(s,t):return True
    p=s.player
    if t.kind=='musashi_cut':
        strike(s,t.pos,t.direction or p.aim,t.radius,25,t.damage,'musashi_slash')
        return True
    if t.kind=='resonance':
        for i in range(12):s.add_projectile(Projectile(V(p.pos),V(420,0).rotate(i*30),t.damage*.35,'note',homing=True,pierce=1,life=1.2))
        effect(s,'seal',p.pos,radius=t.radius,life=.65);s.blast(p.pos,t.radius,t.damage,'echo');return True
    if t.kind in ('dempsey','gazelle_combo'):
        target=s.nearest(p.pos,240*p.reach)
        if target:
            strike(s,p.pos,unit(target.pos-p.pos),190*p.reach,62,t.damage,'punch' if t.kind=='dempsey' else 'uppercut');p.invulnerable=max(p.invulnerable,.08)
        else:effect(s,'punch',p.pos,p.pos+p.aim*150)
        return True
    if t.kind in ('titan_impact','puppet_impact'):
        s.blast(t.pos,t.radius,t.damage,'impact');effect(s,'crystal' if t.kind=='titan_impact' and p.evolved else 'stomp' if t.kind=='titan_impact' else 'threads',t.pos,radius=t.radius,life=.75);return True
    if t.kind=='coala_ultimate':
        strike(s,t.pos,p.aim,820,110*p.area,t.damage,'lightning');s.shake=.3;return True
    if t.kind=='remote_ultimate':
        # A sweeping, piercing machine-gun burst rather than repeated area nukes.
        target=s.nearest(p.pos)
        d=unit(target.pos-p.pos) if target else p.aim
        for angle in (-18,-9,0,9,18):s.add_projectile(Projectile(V(p.pos),d.rotate(angle)*1000,t.damage,'bullet',pierce=5))
        effect(s,'muzzle',p.pos,p.pos+d*80,life=.18);return True
    if t.kind=='guxta_ultimate':
        for e in s.enemies:
            if not e.dead and e.pos.distance_to(t.pos)<t.radius:
                if not e.boss:e.pos+=(t.pos-e.pos)*.65
                s.hit(e,t.damage);e.glue(2,.6)
        effect(s,'vortex',t.pos,radius=t.radius,life=1.2);return True
    if t.kind=='chem_ultimate':
        for i in range(7):
            pos=t.pos+V(100+i*28,0).rotate(i*137)
            s.add_area(Area(pos,110,4,'chemical',t.damage*.1))
            effect(s,'chemical',pos,radius=110,life=.9)
        return True
    if 'ultimate' in t.kind or t.kind in ('rain','storm'):
        motif='spill' if t.kind=='glue_ultimate' else 'crumb_blast' if t.kind in ('pacoca_ultimate','rain') else 'swarm' if t.kind=='storm' else 'cards'
        effect(s,motif,t.pos,radius=t.radius,life=.9)
    return False

RECIPES={'knives':('Lâminas orbitais','rate','Coroa cortante'),
         'lightning':('Condutor elétrico','range','Tempestade em cadeia'),
         'seals':('Selos arcanos','damage','Catedral de selos'),
         'drone':('Sentinela','cooldown','Dupla sentinela'),
         'boomerang':('Bumerangue','magnet','Órbita voraz')}
RECIPES.update(bell=('Sino do vazio','cooldown','Réquiem do vazio'),embers=('Brasas errantes','damage','Fênix errante'))

def tick(s,dt,age_effects=True):
    from legends import tick as legend_tick
    legend_tick(s)
    p=s.player
    if age_effects:
        for fx in s.effects:fx.life-=dt
        s.effects[:]=[fx for fx in s.effects if fx.life>0]
    if p.key=='musashi':
        stage=3 if p.level>=15 else 2 if p.level>=10 else 1 if p.level>=5 else 0
        while stage>p.stage and not p.transformed:
            p.stage+=1;p.evolved=True;p.base_damage*=1.10
            s.notice('EVOLUÇÃO: '+p.display_name,3);s.sound('level')
            effect(s,'soul_aura' if p.stage==3 else 'death_line' if p.stage==2 else 'musashi_slash',p.pos,radius=180,life=1.)
    else:
        stage=(2 if p.level>=9 else 1 if p.level>=5 else 0) if p.key=='klein' else int(p.level>=6)
        while p.key in ('ippo','eren','klein') and stage>p.stage and not p.transformed:
            p.stage+=1;p.evolved=True;p.base_damage*=1.12
            s.notice('EVOLUÇÃO: '+p.display_name,3);s.sound('level');effect(s,'spark' if p.key=='ippo' else 'stomp' if p.key=='eren' else 'cards',p.pos,radius=180,life=1.)
    for key,level in p.aux.items():
        s.aux_timers[key]=s.aux_timers.get(key,0)-dt
        if s.aux_timers[key]>0:continue
        evolved=key in p.evolutions; dmg=p.base_damage*p.power*(.35+.13*level)
        target=s.nearest(p.pos,700)
        if key=='knives':
            for i in range(4 if evolved else 2):
                pos=p.pos+V(100 if evolved else 75,0).rotate(s.time*160+i*(90 if evolved else 180))
                s.blast(pos,38,dmg*.5,'blade');effect(s,'slash',pos,pos+V(28,0),radius=25,life=.22)
            cd=.4
        elif key=='lightning':
            pos=V(p.pos);seen=set()
            for _ in range(5 if evolved else 2):
                e=s.nearest(pos,500,seen)
                if not e:break
                seen.add(e.uid);effect(s,'lightning',pos,e.pos,life=.35);s.hit(e,dmg);pos=V(e.pos)
            cd=2.3
        elif key=='seals':
            if target:
                radius=125 if evolved else 80
                s.add_area(Area(V(target.pos),radius,2.3,'seal',dmg*.3));effect(s,'seal',target.pos,radius=radius,life=2.3)
            cd=3.1
        elif key=='drone':
            if target:
                for i in range(2 if evolved else 1):
                    pos=p.pos+V(-40 if i==0 else 40,-45)
                    s.add_projectile(Projectile(pos,unit(target.pos-pos)*700,dmg,'laser',pierce=2 if evolved else 0))
                    effect(s,'drone',pos,radius=18,life=.4)
            cd=.8
        elif key=='bell':
            radius=(190 if evolved else 120)*p.area
            s.blast(p.pos,radius,dmg*(1.25 if evolved else .8),'echo')
            for enemy in s.enemies:
                if not enemy.dead and enemy.pos.distance_to(p.pos)<radius+enemy.radius:enemy.glue(1.3 if evolved else .6,.55,evolved)
            effect(s,'resonance',p.pos,radius=radius,life=.6);cd=2.4
        elif key=='embers':
            if target:
                direction=unit(target.pos-p.pos)
                for angle in ((-18,0,18) if evolved else (-10,10)):
                    s.add_projectile(Projectile(V(p.pos),direction.rotate(angle)*430,dmg*.7,'flame',life=2.1,pierce=2 if evolved else 0,homing=evolved))
            cd=1.5
        else:
            if target:s.add_projectile(Projectile(V(p.pos),unit(target.pos-p.pos)*440,dmg,'boomerang',pierce=5 if evolved else 2,bounce=3 if evolved else 1,homing=evolved))
            cd=1.7
        s.aux_timers[key]=cd/max(1,p.haste)

def chest(s):
    p=s.player;s.chests+=1
    ready=[key for key,level in p.aux.items() if level>=4 and p.upgrades.get(RECIPES[key][1],0)>0 and key not in p.evolutions]
    if ready:
        key=ready[0];p.evolutions.add(key);s.notice('ARMA EVOLUÍDA: '+RECIPES[key][2].upper(),3.5)
        effect(s,'cards',p.pos,radius=220,life=1)
    else:
        from upgrades import choices, apply
        offer=choices(p,s.rng);apply(p,offer[0]);s.notice('BAÚ: '+offer[0][0].name.upper(),2.5)
    s.coins+=15;s.sound('level')

from legends import JoeWeapon,ThorfinnWeapon,HoldenWeapon
WEAPONS.update(joe=JoeWeapon,thorfinn=ThorfinnWeapon,holden=HoldenWeapon)
