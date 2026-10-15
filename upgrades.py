from dataclasses import dataclass

@dataclass(frozen=True)
class Upgrade:
    id: str
    name: str
    description: str
    stat: str
    amount: float
    max_level: int=5
    character: str='all'

UPGRADES=[
 Upgrade('guxta_area','Campo gravitacional','+18% área de atração e repulsão','area',.18,4,'guxta'),
 Upgrade('guxta_form','Lua vermelha','+15% potência da transformação','form_power',.15,3,'guxta'),
 Upgrade('guxta_cd','Órbita rápida','+12% recarga das habilidades','cooldown',.12,4,'guxta'),
 Upgrade('walt_chem','Precisão química','+20% dano das reações','chemistry',.2,4,'walter'),
 Upgrade('walt_area','Controle de área','+15% área das reações','area',.15,4,'walter'),
 Upgrade('walt_plan','Plano calculado','+12% recarga de habilidades','cooldown',.12,4,'walter'),
 Upgrade('davi_smash','Delaware Smash','+20% força de Shoot Style e ultimate','smash_power',.2,4,'davi'),
 Upgrade('davi_whip','Blackwhip','+25% dano dos chicotes','whip_power',.25,4,'davi'),
 Upgrade('davi_cowl','Full Cowl','+15% potência da transformação','form_power',.15,3,'davi'),
 Upgrade('davi_speed','Shoot Style','+10% velocidade de movimento','speed_bonus',.1,3,'davi'),
 Upgrade('damage','Poder bruto','+15% dano base','power',.15),
 Upgrade('speed','Passo Sigma','+8% velocidade','speed_bonus',.08),
 Upgrade('hp','Reserva vital','+20 vida máxima e cura 20','base_hp',20),
 Upgrade('armor','Casca grossa','+8 armadura; resistência limitada','armor',8),
 Upgrade('crit','Olhar fatal','+5 pontos percentuais de crítico','crit',.05),
 Upgrade('rate','Ritmo acelerado','+12% velocidade de ataque','haste',.12),
 Upgrade('range','Horizonte','+15% alcance de ataques','reach',.15),
 Upgrade('shots','Mãos ocupadas','+1 projétil por rajada','shots',1,3),
 Upgrade('magnet','Ímã de aura','+35 alcance de coleta','magnet',35),
 Upgrade('regen','Segundo fôlego','+0,4 vida regenerada por segundo','regen',.4),
 Upgrade('cooldown','Fluxo contínuo','+15% recarga de habilidades','cooldown',.15),
 Upgrade('leo_power','Cola industrial','+22% dano base','power',.22,5,'leo'),
 Upgrade('leo_slow','Adesivo extremo','Cola reduz mais a velocidade','slow_bonus',.07,4,'leo'),
 Upgrade('leo_shots','Galão duplo','+1 recipiente por rajada','shots',1,3,'leo'),
 Upgrade('leo_area','Super Bonder','+20% área de cola','area',.2,4,'leo'),
 Upgrade('leo_form','Cabeça refletora','+20% potência da transformação','form_power',.2,3,'leo'),
 Upgrade('raf_power','Amendoim premium','+22% dano base','power',.22,5,'rafael'),
 Upgrade('raf_shots','Paçoca dupla','+1 paçoca por rajada','shots',1,3,'rafael'),
 Upgrade('raf_shards','Farelo balístico','+2 fragmentos por explosão','shards',2,4,'rafael'),
 Upgrade('raf_crit','Paçoca crocante','+8 pontos percentuais de crítico','crit',.08,4,'rafael'),
 Upgrade('raf_form','Embalagem divina','+20% potência da transformação','form_power',.2,3,'rafael'),
 Upgrade('trio_power','Robux premium','+22% dano base','power',.22,5,'leozauxta'),
 Upgrade('trio_shots','Pay to win','+1 moeda por rajada','shots',1,3,'leozauxta'),
 Upgrade('trio_bats','Bat overload','+25% dano e alcance do enxame','bat_power',.25,4,'leozauxta'),
 Upgrade('trio_triple','Triple account','+3 moedas na habilidade tripla','triple',3,3,'leozauxta'),
 Upgrade('trio_dance','Dance meta','+25% alcance das ondas da dança','dance',.25,4,'leozauxta'),
]
RARITIES=[('COMUM',1.0,(159,178,201)),('RARO',1.3,(73,197,239)),('ÉPICO',1.6,(204,119,242)),('LENDÁRIO',2.0,(255,201,90))]
from ascension import RECIPES
for key,(name,passive,evolution) in RECIPES.items():
    UPGRADES.append(Upgrade('aux_'+key,name,'Arma auxiliar. Nv.4 + '+{'rate':'Ritmo acelerado','range':'Horizonte','damage':'Poder bruto','cooldown':'Fluxo contínuo','magnet':'Ímã de aura'}[passive]+' + baú: '+evolution,'aux',1,4))

from specializations import SPECS
for sid,(key,name,lane,changes) in SPECS.items():
    summary=('+18% dano, +10% alcance; −8% movimento','+18% ataque, +12% habilidades; −10% dano','+12 armadura, +0,35 cura/s; −12% dano')[lane]
    UPGRADES.append(Upgrade(sid,name,summary+'. Perdas só na primeira escolha.','spec',1,3,key))

def eligible(player,u):
    if u.stat=='spec':
        from specializations import eligible as allowed
        return allowed(player,u.id)
    if u.character not in ('all',player.key) or player.upgrades.get(u.id,0)>=u.max_level:return False
    if u.stat=='shots' and player.key in ('ippo','eren','joe','thorfinn','musashi'):return False
    if u.stat=='aux' and player.run_rule=='signature':return False
    if u.stat=='aux' and player.allowed_items is not None and u.id[4:] not in player.allowed_items:return False
    if u.stat=='aux':return u.id[4:] in player.aux or len(player.aux)<5
    return u.stat=='heal' or u.stat in player.passives or len(player.passives)<6

def choices(player,rng):
    pool=[u for u in UPGRADES if eligible(player,u)]
    if player.level>=4 and not player.specialization:return [(u,RARITIES[1]) for u in pool if u.stat=='spec']
    if not pool: pool=[Upgrade('recovery','Reabastecimento','Cura 35 de vida','heal',35,999)]
    selected=rng.sample(pool,min(3,len(pool)))
    return [(u,RARITIES[1] if u.stat=='spec' else RARITIES[0] if u.stat=='aux' else rng.choices(RARITIES,weights=[60,27,10,3])[0]) for u in selected]

def apply(player,choice):
    u,rarity=choice
    if u.stat=='spec':
        from specializations import apply as commit
        if not commit(player,u.id):return False
        player.upgrades[u.id]=player.specialization_rank;return True
    amount=u.amount*(1 if u.stat in ('shots','triple','shards') else rarity[1])
    if not eligible(player,u) and u.stat!='heal':return False
    if u.stat=='aux':player.aux[u.id[4:]]=player.aux.get(u.id[4:],0)+1
    elif u.stat=='heal': player.hp=min(player.max_hp,player.hp+amount)
    else:
        player.passives.add(u.stat)
        setattr(player,u.stat,getattr(player,u.stat)+amount)
        if u.stat=='base_hp': player.hp=min(player.max_hp,player.hp+amount)
    player.upgrades[u.id]=player.upgrades.get(u.id,0)+1
    return True
