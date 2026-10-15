"""Exclusive three-rank specialization, with explicit first-choice tradeoffs."""
from settings import CHARACTERS
LABELS={
 'ippo':('Pressão contínua','Contra-atacante','Resistência do ringue'),
 'klein':('Cartomante','Fios espirituais','Ilusionista'),
 'musashi':('Corte decisivo','Passo vazio','Protetor da alma'),
 'joe':('Sem guarda','Cross Counter','Último fôlego'),
 'thorfinn':('Passos de Vinland','Deflexão','Protetor'),
 'holden':('Mira implacável','Domínio','O dançarino'),
 'leo':('Cola industrial','Prisão móvel','Guardião'),
 'rafael':('Farelo fatal','Ricochete','Reserva crocante'),
 'davi':('Smash concentrado','Shoot Style','Resgate'),
 'eren':('Lâminas fatais','Manobra tridimensional','Endurecimento'),
 'walter':('Reação concentrada','Plano calculado','Sobrevivente'),
 'guxta':('Colapso','Órbita','Campo protetor'),
 'zatex':('Solo','Cadência','Coro do véu'),
 'leozauxta':('Rajada tríplice','Dança acelerada','Trio resistente'),
 'leozauxtaci':('Convergência ofensiva','Convergência veloz','Convergência protetora'),
}
SPECS={}
for key in CHARACTERS:
 for lane,name in enumerate(LABELS[key]):
  changes=({'power':.18,'reach':.1,'speed_bonus':-.08},{'haste':.18,'cooldown':.12,'power':-.10},{'armor':12,'regen':.35,'power':-.12})[lane]
  SPECS[f'spec_{key}_{lane}']=(key,name,lane,changes)
def eligible(p,sid):
 spec=SPECS.get(sid)
 return bool(spec and spec[0]==p.key and p.level>=4 and p.specialization in ('',sid) and p.specialization_rank<3)
def apply(p,sid):
 if not eligible(p,sid):return False
 _,_,lane,changes=SPECS[sid];first=not p.specialization
 for stat,delta in changes.items():
  if delta>0 or first:setattr(p,stat,getattr(p,stat)+delta)
 p.specialization=sid;p.specialization_rank+=1
 if p.key in ('ippo','joe','thorfinn') and lane==1:p.counter_bonus+=.2
 if p.key=='klein' and lane==1:p.puppet_bonus+=.4
 if p.key in ('musashi','thorfinn') and lane==2:p.support_bonus+=.15
 return True
def label(p):return SPECS[p.specialization][1] if p.specialization in SPECS else 'Escolha no nível 4'
