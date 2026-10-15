"""Optional capture objectives, rule challenges and run telemetry."""
from entities import V,Pickup
RULES={
 'standard':('Expedição','Arsenal completo. Ondas 1–10 e infinito.'),
 'signature':('Assinatura pura','Sem armas auxiliares. Domine o kit do personagem.'),
 'noform':('Força humana','Transformações desativadas. +20% dano base.'),
 'elite':('Cerco de elites','Mais elites. +25% moedas das ondas.'),
}
OBJECTIVES={
 'crypt':('SELAR OS ALTARES','Interrompa os rituais nas três pedras.'),
 'usj':('DEFENDER A ACADEMIA','Mantenha os vilões longe dos postos.'),
 'city':('DESLIGAR AS MÁQUINAS','Desative as três fontes de bombardeio.'),
 'ring':('TOCAR OS SINOS','Conquiste os três cantos do ringue.'),
 'walls':('FECHAR OS PORTÕES','Proteja os pontos de reconstrução.'),
 'fog':('DISSIPAR A NEBLINA','Purifique as três lanternas rituais.'),
}
def setup(s,rule='standard'):
 if rule not in RULES:raise ValueError('Regra de expedição inválida')
 s.run_rule=rule;s.objectives=[];s.discovered=set();s.telemetry={'first_form':0.,'boss_started':0.,'boss_seconds':0.}
 for i,offset in enumerate((V(-440,-270),V(430,-180),V(0,490))):
  pos=s.arena.constrain(V(1800,1800)+offset,100)
  s.objectives.append(dict(x=pos.x,y=pos.y,progress=0.,done=False,available=2+i*2))
 configure(s.player,rule)
def configure(p,rule):
 p.run_rule=rule
 if rule=='noform':p.power+=.2
def tick(s,dt):
 if s.challenge or s.result:return
 for node in s.objectives:
  if node['done'] or s.waves.number<node['available']:continue
  pos=V(node['x'],node['y']);allies=[p for p in s.allied_players if p.hp>0 and p.pos.distance_to(pos)<110]
  if not allies:continue
  contested=any(not e.dead and e.puppet_left<=0 and e.pos.distance_to(pos)<125 for e in s.enemies)
  node['progress']=min(8.,node['progress']+dt*(.25 if contested else 1.)*(1+.25*(len(allies)-1)))
  if node['progress']>=8.:
   node['done']=True;s.coins+=25;s.add_pickup(Pickup(pos,18,'xp'));s.add_pickup(Pickup(pos,18,'health'))
   if all(n['done'] for n in s.objectives):s.add_pickup(Pickup(pos,1,'chest',180))
   s.notice('OBJETIVO CONCLUÍDO • +25 ESSÊNCIAS',2.);s.sound('objective')
def completed(s):return sum(n['done'] for n in s.objectives)
def track_lines(data):
 from missions import MISSIONS,unlocked
 owned=unlocked(data);stats=data['mission_stats']
 pending=[f'{name}: {min(goal,stats.get(stat,0))}/{goal}' for key,(name,_,stat,goal) in MISSIONS.items() if key not in owned]
 return pending[:2] or ['Arsenal completo • explore as arenas e o infinito.']
