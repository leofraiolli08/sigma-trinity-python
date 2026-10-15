"""Small capped meta bonuses; no purchases and no network dependency."""
META={
 'power':('Determinação','+3% dano por nível',5,80,.03),
 'base_hp':('Vitalidade','+5 HP por nível',5,65,5),
 'magnet':('Coletor','+12 alcance de coleta',5,50,12),
 'regen':('Recuperação','+0,08 HP/s por nível',5,75,.08),
 'rerolls':('Planejamento','+1 rerrolagem por partida',2,120,1),
}
ACHIEVEMENTS={
 'first_run':('Primeiros passos','Conclua uma partida.',30),
 'hundred':('Abrir caminho','100 abates em uma partida.',50),
 'survivor':('Resistência','Sobreviva por 3 minutos.',60),
 'ascended':('Ascensão','Atinja o nível 10.',80),
 'transform':('Outra forma','Use uma transformação.',40),
 'ultimate':('Assinatura','Use uma ultimate.',40),
 'chest':('Tesouro','Abra um baú de elite.',50),
 'evolution':('Receita perfeita','Evolua uma arma auxiliar.',120),
 'victory':('Quebra do colapso','Derrote o chefe.',150),
 'traveler':('Viajante','Conclua partidas em 3 arenas.',100),
 'ippo':('Espírito de luta','Vença com Ippo.',100),
 'eren':('Além das muralhas','Vença com Eren.',100),
 'klein':('O mundo oculto','Vença com Klein.',100),
}
ACHIEVEMENTS.update(joe=('A chama do ringue','Vença com Joe Yabuki.',100),thorfinn=('Terra sem guerra','Vença com Thorfinn.',100),holden=('A dança não termina','Vença com Judge Holden.',100),objectives=('Domínio da arena','Conclua os três objetivos de uma arena.',100),rule=('Outra expedição','Vença com uma regra de desafio.',120))
from maps import MAPS
for key,(name,_,_) in MAPS.items():
    ACHIEVEMENTS['arena_'+key]=('Conquistar: '+name.title(),'Vença a onda 10 nesta arena.',75)
ACHIEVEMENTS.update(soul=('O caminho interior','Alcance o Caminho da Alma com Musashi.',100),
                    team=('Quatro assinaturas','Vença com quatro jogadores na sala.',120))

def meta_apply(data,player):
    for stat,(_,_,cap,_,amount) in META.items():
        setattr(player,stat,getattr(player,stat)+min(cap,data['meta'].get(stat,0))*amount)
    player.hp=player.max_hp

def cost(data,key):return META[key][3]*(data['meta'].get(key,0)+1)

def purchase(save,key):
    if key not in META:return False
    d=save.data;price=cost(d,key)
    if d['meta'].get(key,0)>=META[key][2] or d['coins']<price:return False
    old_coins=d['coins'];old_level=d['meta'].get(key)
    d['coins']-=price;d['meta'][key]=d['meta'].get(key,0)+1
    if save.save():return True
    d['coins']=old_coins
    if old_level is None:d['meta'].pop(key,None)
    else:d['meta'][key]=old_level
    return False

def finish(data,s,victory):
    checkpoint(data,s,victory,True)

def checkpoint(data,s,victory=False,finished=False):
    p=s.player;before=s.banked
    data['lifetime_kills']+=max(0,s.kills-before.get('kills',0))
    if (finished or victory) and s.arena.key not in data['visited']:data['visited'].append(s.arena.key)
    checks={'first_run':finished or victory,'hundred':s.kills>=100,'survivor':s.time>=180,
            'ascended':p.level>=10,'transform':p.transforms>0,'ultimate':p.ultimates>0,
            'chest':s.chests>0,'evolution':bool(p.evolutions),'victory':victory,
            'traveler':len(data['visited'])>=3,
            **{key:victory and p.key==key for key in ('ippo','eren','klein','joe','thorfinn','holden')}}
    checks.update({'arena_'+key:victory and s.arena.key==key for key in MAPS})
    checks.update(soul=p.key=='musashi' and p.stage>=3,team=victory and len(s.allied_players)==4)
    from expedition import completed
    checks.update(objectives=completed(s)==3,rule=victory and s.run_rule!='standard')
    total=int(s.kills//4+s.coins+(80 if s.victory_paid else 0))
    reward=max(0,total-before.get('income',0))
    for key,done in checks.items():
        if done and key not in data['achievements']:
            data['achievements'].append(key);s.awarded.append(key);reward+=ACHIEVEMENTS[key][2]
    stats=data['mission_stats']
    for key,value in (('kills',s.kills),('chests',s.chests),('transforms',p.transforms),('victories',int(s.victory_paid))):
        stats[key]=stats.get(key,0)+max(0,value-before.get(key,0));before[key]=value
    stats['wave']=max(stats.get('wave',0),s.waves.completed)
    before['income']=total;s.reward+=reward;data['coins']+=reward

def draw_menu(g):
    from settings import INK,MUTED,GOLD,CYAN,GREEN
    from ui_design import header,icon,pips,badge,wrap
    r=g.render;d=g.save.data;header(r,'Cada expedição deixa uma marca',f'{d["coins"]} essências • bônus permanentes com limites fixos','ARQUIVO DE ASCENSÃO')
    r.text('MELHORIAS PERMANENTES',39,170,18,GOLD);r.text('CONQUISTAS',593,170,18,CYAN)
    for i,(key,(name,desc,cap,_,_)) in enumerate(META.items()):
        y=203+i*82;level=d['meta'].get(key,0);price=cost(d,key)
        r.panel((32,y,530,72),(26,24,34));icon(r,key,65,y+33,GOLD,26)
        r.text(name,91,y+12,24,INK);r.text(desc,91,y+40,17,MUTED)
        pips(r,253,y+17,level,cap,GOLD,11)
        g.button((394,y+20,151,34),'MÁXIMO' if level>=cap else str(price)+' / COMPRAR','buy:'+key,GOLD,level<cap and d['coins']>=price)
    pages=(len(ACHIEVEMENTS)+6)//7;g.archive_page%=pages
    page=g.archive_page;rows=list(ACHIEVEMENTS.items())[page*7:page*7+7]
    for i,(key,(name,desc,reward)) in enumerate(rows):
        y=203+i*57;done=key in d['achievements'];r.panel((583,y,660,50),(26,24,34),GREEN if done else (62,56,71))
        icon(r,'shield',605,y+24,GREEN if done else MUTED,19)
        size=21
        while size>15 and r.a.font(size).size(name)[0]>505:size-=1
        r.text(name,627,y+7,size,GREEN if done else INK);r.text(desc,627,y+29,17,MUTED)
        r.text('OK' if done else '+'+str(reward),1189,y+17,18,GREEN if done else GOLD)
    g.button((886,620,357,34),f'CONQUISTAS / {page+1} DE {pages}','archive_next',CYAN)
    g.button((32,667,190,35),'VOLTAR','menu',MUTED)
    r.text(f'{len(d["achievements"])}/{len(ACHIEVEMENTS)} conquistadas • moedas e missões salvas por onda',798,684,18,MUTED,True)
