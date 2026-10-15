"""Expedition menus and concise progress/comparison feedback."""
import pygame as pg
from entities import V
from settings import INK,MUTED,GOLD,CYAN,GREEN,CHARACTERS
from ui_design import header,wrap,badge
from expedition import RULES,OBJECTIVES,completed
from monster_animation import THEMES

def comparison(p,u,rarity):
 if u.stat=='spec':return 'ESCOLHA EXCLUSIVA' if not p.specialization else 'VANTAGEM REFORÇADA'
 if u.stat=='aux':return f'ARMA / {p.aux.get(u.id[4:],0)} → {p.aux.get(u.id[4:],0)+1}'
 if u.stat=='heal':return f'VIDA / {p.hp:.0f} → {min(p.max_hp,p.hp+u.amount*rarity[1]):.0f}'
 before=getattr(p,u.stat,0);after=before+u.amount*(1 if u.stat in ('shots','triple','shards') else rarity[1])
 return f'{before:g} → {after:g}'
def challenges(g):
 r=g.render;header(r,'Escolha os termos da expedição','Quatro regras • seu progresso e suas recompensas são preservados.','NOVOS CAMINHOS')
 for i,(key,(name,desc)) in enumerate(RULES.items()):
  x=48+i%2*600;y=175+i//2*230;r.panel((x,y,575,211),(25,24,34),GOLD if key=='standard' else CYAN)
  badge(r,f'0{i+1}',x+20,y+19,GOLD);r.text(name.upper(),x+80,y+23,28,INK);wrap(r,desc,x+20,y+81,530,22,MUTED)
  best=g.save.data['challenge_records'].get(key,0);r.text(f'MELHOR ONDA / {best}',x+20,y+145,16,GOLD)
  g.button((x+295,y+149,260,42),'ESCOLHER','rule:'+key,CYAN)
 g.button((440,662,400,36),'VOLTAR AO MENU','menu',GOLD)
def bestiary(g):
 from maps import MAPS
 r=g.render;theme=THEMES[g.bestiary_page%6];known=set(g.save.data['bestiary'])
 header(r,'Criaturas do colapso',MAPS[theme][0]+' • Descobertas ao enfrentar os inimigos.','BESTIÁRIO')
 names=('PERSEGUIDOR','ATIRADOR','PESADO','INVESTIDA','ENXAME','CAPITÃO','CHEFE')
 for i in range(7):
  x=35+i%4*310;y=175+i//4*223;seen=f'{theme}:{i}' in known
  r.panel((x,y,285,207),(24,24,34),GOLD if i==6 else (66,61,72))
  if seen:
   name=f'{theme}_anim_{i}_{int(g.ui_time*7)%3}'
   if name in g.assets.images:
    w,h=g.assets.logical[name];r.sprite(name,(x+142,y+149),min(155/w,118/h))
  else:r.text('?',x+142,y+93,72,MUTED,True)
  r.text(names[i] if seen else 'DESCONHECIDO',x+142,y+171,19,INK if seen else MUTED,True)
 g.button((48,662,270,36),'VOLTAR AO MENU','menu',GOLD)
 g.button((881,662,350,36),f'PRÓXIMA ARENA • {g.bestiary_page+1}/6','bestiary_next',CYAN)
def objectives_world(r,s,xy):
 if s.challenge:return
 for node in s.objectives:
  if node['done'] or s.waves.number<node['available']:continue
  at=V(xy(V(node['x'],node['y'])))
  if not(-120<at.x<1400 and -120<at.y<840):continue
  pg.draw.circle(r.canvas,(32,63,66),at,110,2)
  pg.draw.circle(r.canvas,CYAN,at,19,2)
  for i in range(4):
   a=at+V(12,0).rotate(i*90+s.time*15);b=at+V(23,0).rotate(i*90+s.time*15);pg.draw.line(r.canvas,CYAN,a,b,2)
  if node['progress']:r.bar(at.x-45,at.y+29,90,5,node['progress']/8,GREEN)
  if s.player.pos.distance_to(V(node['x'],node['y']))<110:r.text('DEFENDA O PONTO',at.x,at.y-40,16,CYAN,True)
def tracker(r,s):
 if s.challenge:return
 count=completed(s);r.panel((1007,111,257,69),(19,20,29),(68,59,72))
 r.text(OBJECTIVES[s.arena.key][0],1020,124,16,CYAN)
 r.text(f'{count}/3 • OPCIONAL • +25 ESSÊNCIAS',1020,151,14,MUTED)
 if not s.rhythm.active:
  for n in s.objectives:
   if n['done'] or s.waves.number<n['available']:continue
   pt=(1144+round(n['x']/3600*112),539+round(n['y']/3600*112));pg.draw.circle(r.canvas,CYAN,pt,3,1)
