"""Four-lane rhythm chart in simulation time: pause/level-up freeze notes too."""
from dataclasses import dataclass
@dataclass
class Note:
    time: float
    lane: int
    judged: bool=False
class Rhythm:
    window=.16
    def __init__(self):
        self.active=False;self.notes=[];self.age=0.;self.combo=0;self.best=0;self.hits=0;self.misses=0;self.shield_until=0.;self.feedback='';self.feedback_until=0.
    def start(self):
        self.__init__();self.active=True
        pattern=(0,1,2,3,2,0,3,1,0,2,1,3,0,3,2,1)
        self.notes=[Note(1.+i*.48,pattern[i%len(pattern)]) for i in range(27)]
    @property
    def protected(self):return self.active and self.age<self.shield_until
    def fail(self):
        self.combo=0;self.misses+=1;self.shield_until=0;self.feedback='ERRO';self.feedback_until=self.age+.45
    def update(self,age,active):
        self.age=age;self.active=active
        if not active:self.shield_until=0;return
        for note in self.notes:
            if not note.judged and self.age-note.time>self.window:
                note.judged=True;self.fail()
    def tap(self,lane):
        if not self.active:return False
        candidates=[n for n in self.notes if not n.judged and n.lane==lane and abs(n.time-self.age)<=self.window]
        if not candidates:self.fail();return False
        note=min(candidates,key=lambda n:abs(n.time-self.age));note.judged=True
        self.combo+=1;self.hits+=1;self.best=max(self.best,self.combo);self.shield_until=self.age+.72
        self.feedback='PERFEITO' if abs(note.time-self.age)<=.075 else 'BOM';self.feedback_until=self.age+.4
        return True
