"""Literary/manga heroes; combat values and stages are crossover adaptations."""
from entities import V,Projectile,Telegraph,unit
from weapons import Weapon
NAMES={
 'joe':('JOE • VAGANTE','JOE • PESO-GALO','JOE • SEM GUARDA'),
 'thorfinn':('THORFINN • VINGANÇA','THORFINN • RENASCER','THORFINN • EXPLORADOR','THORFINN • VINLAND'),
 'holden':('HOLDEN • NATURALISTA','HOLDEN • ATIRADOR','HOLDEN • ESTRATEGISTA','HOLDEN • A DANÇA'),
}
ULTIMATES={'joe':'ÚLTIMO ROUND','thorfinn':'NÃO TENHO INIMIGOS','holden':'MERIDIANO DE SANGUE'}
def tick(s):
 p=s.player
 if p.key not in NAMES or p.transformed:return
 stage=sum(p.level>=n for n in ((6,12) if p.key=='joe' else (5,10,15)))
 while p.stage<stage:
  p.stage+=1;p.evolved=True;p.base_damage*=1.08
  if p.key=='thorfinn':p.armor+=5;p.regen+=.1
  s.notice('EVOLUÇÃO: '+p.display_name,3);s.sound('level')
class JoeWeapon(Weapon):
 name='JAB / CROSS COUNTER';kind='punch';sound='hit';speed=0
 def attack_limit(self,p):return 170*p.reach
 def fire(self,s,target):
  from ascension import strike
  p=s.player
  if target.pos.distance_to(p.pos)>self.attack_limit(p):return
  counter=p.counter_left>0
  strike(s,p.pos,target.pos-p.pos,(170 if p.stage==2 else 155)*p.reach,28*p.area,p.damage*(2.5+p.counter_bonus if counter else 1.25),'joe_counter' if counter else 'joe_jab')
  if p.stage==2 and not counter:strike(s,p.pos,unit(target.pos-p.pos).rotate(18),130*p.reach,22*p.area,p.damage*.25,'joe_jab')
  if counter:p.counter_left=0;p.counters+=1;s.sound('counter')
  else:s.sound('punch')
 def skill(self,s,target):
  from ascension import effect
  p=s.player;p.counter_left=max(p.counter_left,1.1);effect(s,'joe_guard',p.pos,radius=55,life=.45)
 def passive(self,s):
  if s.player.transformed:s.player.counter_left=max(s.player.counter_left,.45)
 def dash(self,s):
  from ascension import effect
  s.player.counter_left=max(s.player.counter_left,.75);effect(s,'afterimage',s.player.pos,life=.25)
 def ultimate(self,s):
     from evolution_kit import ultimate
     return ultimate(s)

class ThorfinnWeapon(Weapon):
 name='ADAGAS / DEFLEXÃO';kind='blade';sound='hit';speed=0
 def attack_limit(self,p):return 180*p.reach
 def fire(self,s,target):
  from ascension import strike
  p=s.player
  if target.pos.distance_to(p.pos)>self.attack_limit(p):return
  if p.stage==0:
   for angle in (-15,15):strike(s,p.pos,unit(target.pos-p.pos).rotate(angle),160*p.reach,18,p.damage*.85,'dagger_cut')
   s.sound('blade')
  else:strike(s,p.pos,target.pos-p.pos,165*p.reach,32,p.damage*1.45,'deflect');target.glue(.8,.4);s.sound('punch')
 def skill(self,s,target):
  p=s.player
  if p.stage==0 and target:
   from ascension import strike
   strike(s,p.pos,target.pos-p.pos,270*p.reach,23,p.damage*2.4,'dagger_cut')
  else:
   from ascension import effect
   s.apply_ally_aura(p,240,2.5,armor=12,regen=.45,speed=.08);effect(s,'vinland_aura',p.pos,radius=240,life=.6)
   for e in s.enemies:
    if not e.dead and e.pos.distance_to(p.pos)<220:e.glue(1.3,.5)
 def passive(self,s):
  if s.player.stage>=2:s.apply_ally_aura(s.player,240,1.1,armor=5,regen=.15)
 def dash(self,s):
  from ascension import effect
  p=s.player;p.counter_left=max(p.counter_left,.6);effect(s,'deflect',p.pos,p.pos+p.facing*80,life=.22)
 def ultimate(self,s):
     from evolution_kit import ultimate
     return ultimate(s)

class HoldenWeapon(Weapon):
 name='RIFLE / DOMÍNIO';kind='bullet';sound='rifle';speed=960
 def fire(self,s,target):
  from ascension import effect
  p=s.player;d=unit(target.pos-p.pos)
  for angle in (-5,5) if p.stage==1 else (0,):self.shoot(s,p.pos,d.rotate(angle),p.damage*(.8 if p.stage==1 else 1.45),'holden_bullet',pierce=1+int(p.stage>=2))
  if p.stage==3:target.glue(.6,.2)
  effect(s,'rifle_flash',p.pos,p.pos+d*72,life=.18);s.sound('rifle')
 def skill(self,s,target):
  if not target:return
  from ascension import effect
  p=s.player;radius=110*p.area
  for angle in (-8,8):self.shoot(s,p.pos,unit(target.pos-p.pos).rotate(angle),p.damage,'holden_bullet',pierce=2)
  for e in s.enemies:
   if e.pos.distance_to(target.pos)<radius:e.glue(1.5,.45)
  effect(s,'dominion',target.pos,radius=radius,life=.65)
 def passive(self,s):
  if s.player.transformed:
   for e in s.enemies:
    if not e.dead and e.pos.distance_to(s.player.pos)<160:e.glue(.8,.35)
 def dash(self,s):
  from ascension import effect
  effect(s,'dust',s.player.pos,life=.35)
 def ultimate(self,s):
     from evolution_kit import ultimate
     return ultimate(s)

def resolve(s,t):
 from ascension import effect,strike
 p=s.player
 if t.kind=='joe_round':
  target=s.nearest(p.pos,260*p.reach);strike(s,p.pos,unit(target.pos-p.pos) if target else p.aim,225*p.reach,42,t.damage,'joe_counter');p.invulnerable=max(p.invulnerable,.09);return True
 if t.kind=='vinland_pulse':s.blast(t.pos,t.radius,t.damage,'repel');effect(s,'vinland_aura',t.pos,radius=t.radius,life=.8);return True
 if t.kind=='holden_salvo':s.add_projectile(Projectile(V(p.pos),t.direction*1100,t.damage,'holden_bullet',pierce=5,life=1.8));effect(s,'rifle_flash',p.pos,p.pos+t.direction*90,life=.2);s.sound('rifle');return True
 return False
