"""Finite waves and an optional endless continuation. No file I/O."""
from entities import V

class Waves:
    def __init__(self):
        self.number=1;self.remaining=12;self.completed=0;self.rest=0.;self.endless=False;self.started=False
    @property
    def boss_wave(self):return self.number%10==0
    def begin(self,s):
        self.started=True;s.boss_spawned=False;s.boss=None
        self.remaining=0 if self.boss_wave else min(100,8+self.number*4)
        s.spawn_cd=.25
        if self.boss_wave:s.spawn(boss=True)
        s.notice(('CHEFE • ' if self.boss_wave else 'ONDA ')+str(self.number),2.)
    def clear(self,s):
        if self.completed>=self.number:return
        self.completed=self.number;s.coins+=int((8+self.number*2+(45 if self.boss_wave else 0))*(1.25 if s.run_rule=='elite' else 1))
        # Collect earned loot instead of abandoning it when the next wave starts.
        for item in s.pickups:
            s.collect_pickup(item)
        s.pickups.clear();s.projectiles.clear();s.telegraphs.clear();s.areas.clear();s.enemies.clear()
        if s.enemy_index is not None:s.enemy_index.clear()
        for ally in s.allied_players:
            ally.hp=min(ally.max_hp,ally.hp+ally.max_hp*(.4 if ally.hp<=0 else .06));ally.revive_progress=0.
        self.rest=2.5;s.notice('ONDA CONCLUÍDA • RECOMPENSA GARANTIDA',2.5)
        if self.number==10 and not self.endless:s.result='VICTORY';s.sound('victory')
    def continue_endless(self,s):
        if s.result!='VICTORY' or self.number!=10 or self.endless:return False
        self.endless=True;s.result=None;s.hitstop=0;s.transform_pause=0
        self.rest=2.5;return True
    def update(self,s,dt):
        if not self.started:self.begin(s)
        if self.rest>0:
            self.rest=max(0,self.rest-dt)
            if self.rest==0:self.number+=1;self.begin(s)
            return
        if self.boss_wave:
            if s.boss and s.boss.dead:self.clear(s)
            return
        s.spawn_cd-=dt
        if self.remaining and s.spawn_cd<=0:
            elite=(self.remaining==1 and self.number%3==0) or (s.run_rule=='elite' and self.remaining%5==0)
            e=s.spawn(elite=elite)
            if e:self.remaining-=1
            s.spawn_cd=max(.22,.85-self.number*.025)
        if self.remaining==0 and not any(not e.dead for e in s.enemies):self.clear(s)

FAMILIES={
 'crypt':('Legião sepulcral','REI DO OSSUÁRIO',(149,124,194),(0,2,4,5),1.,1.),
 'usj':('Vilões da academia','NOMU SUPREMO',(103,196,167),(0,1,3,5),1.05,.95),
 'city':('Máquinas do colapso','COLOSSO DE SUCATA',(125,175,211),(1,3,4,5),1.15,.88),
 'ring':('Pugilistas possuídos','CAMPEÃO DO VAZIO',(230,147,105),(0,2,3,5),.9,1.12),
 'walls':('Titãs errantes','TITÃ DO PORTÃO',(195,143,114),(0,2,3,5),1.25,.82),
 'fog':('Entidades da neblina','ARCONTE SEM ROSTO',(181,156,225),(1,2,4,5),.92,1.05),
}

def tune(s,e):
    w=s.waves.number;family=FAMILIES[s.arena.key]
    # Endless difficulty grows through health/damage, with bounded speed and population.
    scale=1+max(0,w-1)*.075+max(0,w-10)*.1
    e.max_hp=(15000*(1+max(0,w-10)*.12) if e.boss else e.max_hp*family[4]*scale)
    e.max_hp*=1+.65*(len(s.allied_players)-1)
    e.hp=e.max_hp;e.speed*=family[5]*min(1.45,1+max(0,w-10)*.008)
    e.damage*=1+max(0,w-1)*.025
    if e.boss:e.name=family[1]
