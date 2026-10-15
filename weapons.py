import math
from entities import V, Projectile, Area, Telegraph, unit

class Weapon:
    name=''
    def __init__(self): self.attack_cd=0.; self.skill_cd=2.; self.passive_cd=1.; self.skill_index=0
    def attack_limit(self,p):return p.reach*720*(1.25 if p.transformed else 1)
    def update(self,s,dt):
        p=s.player; self.attack_cd-=dt; self.skill_cd-=dt; self.passive_cd-=dt
        target=s.nearest(p.pos,p.reach*720*(1.25 if p.transformed else 1))
        if target:p.aim=unit(target.pos-p.pos)
        attack_target=s.nearest(p.pos,self.attack_limit(p))
        if attack_target and self.attack_cd<=0:
            p.aim=unit(attack_target.pos-p.pos)
            self.fire(s,attack_target); self.attack_cd=.56/max(.3,p.haste)/(1.3 if p.transformed else 1); p.attack_pose=.16
            p.attack_animation_left=.28
        if self.skill_cd<=0:
            self.skill(s,target); self.skill_cd=3.6/max(.3,p.cooldown)/(1.2 if p.transformed else 1); self.skill_index+=1
        if self.passive_cd<=0:
            self.passive(s); self.passive_cd=1.
    def fire(self,s,target):
        p=s.player
        shots=[]
        for i in range(min(10,int(p.shots)+(2 if p.transformed else 0))):
            angle=(i-(min(10,int(p.shots)+(2 if p.transformed else 0))-1)/2)*8
            q=self.shoot(s,p.pos,unit(target.pos-p.pos).rotate(angle),p.damage)
            if q is not None:shots.append(q)
        s.sound(self.sound)
        return shots
    def shoot(self,s,pos,direction,damage,kind=None,**kw):
        p=s.player; speed=self.speed*(1.2 if p.transformed else 1)
        return s.add_projectile(Projectile(V(pos),direction*speed,damage,kind or self.kind,life=2.3*p.reach,**kw))
    def passive(self,s):
        # Base classes always provide their own meaningful passive.
        raise NotImplementedError
    def skill(self,s,target): raise NotImplementedError
    def ultimate(self,s): raise NotImplementedError
    def dash(self,s): raise NotImplementedError

class GlueWeapon(Weapon):
    name='COLA LÍQUIDA'; kind='glue'; sound='glue'; speed=450
    def skill(self,s,target):
        p=s.player; i=self.skill_index%3
        if i==0 and target:
            self.shoot(s,p.pos,unit(target.pos-p.pos),p.damage*2.4,'bonder',radius=14)
            s.notice('SUPER BONDER',1.)
        elif i==1 and target:
            d=unit(target.pos-p.pos)
            for angle in (-8,0,8): self.shoot(s,p.pos,d.rotate(angle),p.damage*1.25,'jet',pierce=5)
            s.notice('COLA PRESSURIZADA',1.)
        else:
            s.add_area(Area(V(p.pos),125*p.area,2.5,'prison',p.damage*.45)); s.notice('PRISÃO ADESIVA',1.)
    def passive(self,s):
        p=s.player
        s.add_area(Area(V(p.pos),52*p.area*(1.35 if p.transformed else 1),2.5,'glue',p.damage*.16))
        if p.transformed: s.blast(p.pos,110*p.area,p.damage*.6,'glue',root=True)
    def ultimate(self,s):
        s.telegraphs.append(Telegraph(V(s.player.pos),440*s.player.area,.85,'glue_ultimate',s.player.damage*7))
    def dash(self,s): s.add_area(Area(V(s.player.pos),65,4,'glue',s.player.damage*.3))

class PacocaWeapon(Weapon):
    name='PAÇOCA BALÍSTICA'; kind='pacoca'; sound='pacoca'; speed=600
    def fire(self,s,target):
        shots=super().fire(s,target)
        # Alternating ricochet rounds have bounded bounces and a shared hit set.
        if shots:shots[-1].bounce=2
    def skill(self,s,target):
        p=s.player
        if self.skill_index%2==0:
            targets=sorted((e for e in s.enemies if not e.dead),key=lambda e:e.pos.distance_squared_to(p.pos))[:5]
            for e in targets: s.telegraphs.append(Telegraph(V(e.pos),65,.65,'rain',p.damage*2))
            s.notice('CHUVA DE PAÇOCA',1.)
        elif target:
            self.shoot(s,p.pos,unit(target.pos-p.pos),p.damage*2.7,'stuffed',radius=13)
            s.notice('PAÇOCA RECHEADA',1.)
    def passive(self,s):
        if s.player.transformed: s.fragments(s.player.pos,8,s.player.damage*.55)
    def ultimate(self,s):
        s.telegraphs.append(Telegraph(V(s.player.pos),470,.85,'pacoca_ultimate',s.player.damage*9))
    def dash(self,s): s.fragments(s.player.pos,6,s.player.damage*.35)

class TrioWeapon(Weapon):
    name='ROBUX BARRAGE'; kind='token'; sound='token'; speed=510
    def fire(self,s,target):
        shots=super().fire(s,target)
        if shots:shots[-1].homing=True;shots[-1].pierce=1
    def skill(self,s,target):
        p=s.player; idx=self.skill_index%3
        if idx==0:
            s.add_area(Area(V(p.pos),115*p.bat_power*(1.4 if p.transformed else 1),3.0,'swarm',p.damage*.65*p.bat_power)); s.sound('bats'); s.notice('SIGMA BAT SWARM',1.)
        elif idx==1:
            for e in sorted((e for e in s.enemies if not e.dead),key=lambda e:e.pos.distance_squared_to(p.pos))[:6]:
                s.telegraphs.append(Telegraph(V(e.pos),75,.7,'storm',p.damage*2.2))
            s.notice('ROBUX STORM',1.)
        elif target:
            d=unit(target.pos-p.pos)
            for member in (-1,0,1):
                for n in range(3+int(p.triple/3)):
                    self.shoot(s,p.pos+V(member*20,0),d.rotate(member*12+(n-1)*5),p.damage*.85,pierce=1,bounce=1,homing=(member==0))
            s.notice('TRIPLE INVESTMENT',1.)
    def passive(self,s):
        if s.player.transformed:
            p=s.player; s.blast(p.pos,150*p.dance,p.damage*.9,'token')
            s.add_area(Area(V(p.pos),150*p.dance,.35,'wave',0))
    def ultimate(self,s):
        p=s.player
        for n in range(5): s.telegraphs.append(Telegraph(V(p.pos),170+n*65,.4+n*.45,'dance',p.damage*2.2,source=p))
        s.telegraphs.append(Telegraph(V(p.pos),640,2.85,'dance_final',p.damage*7,source=p))
    def dash(self,s): s.add_area(Area(V(s.player.pos),95,1.1,'swarm',s.player.damage*.65))

WEAPONS={'leo':GlueWeapon,'rafael':PacocaWeapon,'leozauxta':TrioWeapon}


class CoalaWeapon(Weapon):
    name='ONE FOR COALA'; kind='air'; sound='shot'; speed=720
    def shoot(self,s,pos,direction,damage,kind=None,**kw):
        kw.setdefault('pierce',1)
        super().shoot(s,pos,direction,damage,kind,**kw)
    def skill(self,s,target):
        p=s.player
        if not target: return
        if self.skill_index%2==0:
            # Long-range kick impact is a narrow shockwave, requiring positioning.
            self.shoot(s,p.pos,unit(target.pos-p.pos),p.damage*3*p.smash_power,'shoot_style',radius=17,pierce=4)
            s.notice('SHOOT STYLE',1.)
        else:
            for e in sorted((e for e in s.enemies if not e.dead),key=lambda e:e.pos.distance_squared_to(p.pos))[:3]:
                if e.pos.distance_to(p.pos)>430*p.reach: continue
                s.hit(e,p.damage*1.4*p.whip_power)
                e.glue(1.4,.6,True)
                if not e.boss: e.pos+=(p.pos-e.pos)*.3
                s.telegraphs.append(Telegraph(V(e.pos),18,.22,'whip_visual',0,source=p))
            s.notice('BLACKWHIP',1.)
    def passive(self,s):
        if s.player.transformed:
            p=s.player; s.blast(p.pos,100*p.area,p.damage*.5,'air')
            s.add_area(Area(V(p.pos),100*p.area,.4,'wave'))
    def ultimate(self,s):
        p=s.player
        s.telegraphs.append(Telegraph(V(p.pos),360*p.area,.7,'coala_ultimate',p.damage*8*p.smash_power))
    def dash(self,s):
        p=s.player
        self.shoot(s,p.pos,V(p.facing),p.damage*1.4,'shoot_style',radius=14,pierce=3)

WEAPONS['davi']=CoalaWeapon


class WalterWeapon(Weapon):
    name='REAÇÃO EM CADEIA';kind='flask';sound='shot';speed=440
    def fire(self,s,target):
        self.kind='bullet' if s.player.evolved and s.player.transformed else 'flask'
        super().fire(s,target)
    def skill(self,s,target):
        if not target:return
        p=s.player
        if p.evolved:
            for angle in (-12,0,12):self.shoot(s,p.pos,unit(target.pos-p.pos).rotate(angle),p.damage*1.3,'bullet',pierce=2)
            s.notice('PLANO CALCULADO',.8)
        else:
            s.add_area(Area(V(target.pos),110*p.area,2.4,'chemical',p.damage*.55*p.chemistry));s.notice('REAÇÃO CONTROLADA',.8)
    def passive(self,s):
        p=s.player
        if not p.transformed:return
        if p.evolved:
            target=s.nearest(p.pos)
            if target:
                self.shoot(s,p.pos,unit(target.pos-p.pos),p.damage*1.5,'bullet',pierce=4)
                s.add_area(Area(V(p.pos),32,.65,'turret'))
        else:s.add_area(Area(V(p.pos),95*p.area,1.3,'chemical',p.damage*.35*p.chemistry))
    def ultimate(self,s):
        p=s.player
        if p.evolved:
            for i in range(6):s.telegraphs.append(Telegraph(V(p.pos),480,.3+i*.28,'remote_ultimate',p.damage*1.5))
        else:s.telegraphs.append(Telegraph(V(p.pos),320*p.area,.8,'chem_ultimate',p.damage*7*p.chemistry))
    def dash(self,s):s.add_area(Area(V(s.player.pos),65,1.8,'chemical',s.player.damage*.2))
WEAPONS['walter']=WalterWeapon


class GuxtaWeapon(Weapon):
    name='PULSO GRAVITACIONAL';kind='gravity';sound='shot';speed=620
    def skill(self,s,target):
        p=s.player
        if not target:return
        center=V(target.pos); radius=150*p.area
        for e in s.enemies:
            if not e.dead and e.pos.distance_to(center)<radius:
                s.hit(e,p.damage*1.5)
                if not e.boss:e.pos+=(center-e.pos)*.45
        s.add_area(Area(center,radius,.45,'wave'))
        s.notice('ATRAÇÃO GRAVITACIONAL',.8)
    def passive(self,s):
        p=s.player
        if not p.transformed:return
        radius=145*p.area
        s.blast(p.pos,radius,p.damage*.65,'air')
        for e in s.enemies:
            if not e.dead and not e.boss and e.pos.distance_to(p.pos)<radius:
                e.pos+=unit(e.pos-p.pos)*55
        s.add_area(Area(V(p.pos),radius,.4,'wave'))
    def ultimate(self,s):
        p=s.player
        s.telegraphs.append(Telegraph(V(p.pos),400*p.area,.8,'guxta_ultimate',p.damage*7))
        s.notice('COLAPSO DA LUA VERMELHA',1.5)
    def dash(self,s):
        p=s.player;s.blast(p.pos,85,p.damage*.5,'air');s.add_area(Area(V(p.pos),85,.3,'wave'))
WEAPONS['guxta']=GuxtaWeapon
