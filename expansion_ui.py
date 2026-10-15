from settings import CHARACTERS,INK,MUTED,GOLD,CYAN
from maps import MAPS
from ascension import RECIPES

def roster(g):
    # One roster implementation keeps pagination and secret visibility consistent.
    from interface import roster as draw_roster
    return draw_roster(g)

def arenas(g):
    from ui_design import header,badge,wrap
    r=g.render;header(r,'Escolha onde o colapso começa','1–6 ou clique • '+CHARACTERS[g.selected]['name'],'SELEÇÃO DE ARENA')
    for i,(key,(name,desc,rule)) in enumerate(MAPS.items()):
        x=34+(i%3)*415;y=166+(i//3)*243;r.panel((x,y,383,228),(26,24,34),(76,62,76))
        r.canvas.blit(r.map_preview(key,(369,96)),(x+7,y+7))
        badge(r,'0'+str(i+1),x+15,y+14,GOLD)
        r.text(name,x+16,y+116,24,GOLD)
        r.text(desc,x+16,y+146,17,MUTED)
        r.text(rule,x+16,y+169,17,CYAN)
        g.button((x+14,y+194,355,27),'ENTRAR / '+str(i+1),'map:'+key,GOLD)
    g.button((34,671,184,32),'VOLTAR','play',MUTED)

def build(g):
    from ui_design import header,icon,pips,wrap
    import upgrades
    r=g.render;p=g.session.player;r.dim()
    from specializations import label
    header(r,'Sua build, sua assinatura',label(p)+f' • GRAU {p.specialization_rank} • 6 famílias de passivas','ARSENAL DA EXPEDIÇÃO')
    r.panel((36,169,755,66),(26,24,34),CYAN,2)
    icon(r,'sword',70,201,CYAN,29);r.text('ASSINATURA',100,182,15,MUTED);r.text(g.session.weapon.name,100,203,25,INK)
    for i,(key,(name,passive,evolved)) in enumerate(RECIPES.items()):
        y=247+i*52;level=p.aux.get(key,0);done=key in p.evolutions;color=GOLD if done else CYAN if level else MUTED
        r.panel((36,y,755,47),(26,24,34),(68,61,76));icon(r,key,70,y+24,color,24)
        r.text(evolved if done else name,100,y+5,21,color)
        support=next(u.name for u in upgrades.UPGRADES if u.id==passive)
        status='EVOLUÍDA' if done else 'PRONTA PARA BAÚ' if level>=4 and p.upgrades.get(passive,0)>0 else 'Nv.4 + '+support+' + baú'
        if p.allowed_items is not None and key not in p.allowed_items and not level:status='LIBERE NO MENU / ARSENAL E MISSÕES'
        if p.run_rule=='signature':status='INDISPONÍVEL / ASSINATURA PURA'
        r.text(status,100,y+27,16,MUTED);pips(r,667,y+21,level,4,color,20)
    r.panel((816,169,427,450),(26,24,34),(68,61,76))
    r.text('ATRIBUTOS',840,190,20,GOLD)
    for i,(label,value) in enumerate((('VIDA',f'{int(p.max_hp)}'),('DANO BASE',f'{p.base_damage*p.power:.1f}'),('CRÍTICO',f'{p.crit*100:.0f}%'))):
        r.text(label,840,228+i*27,18,MUTED);r.text(value,1124,228+i*27,19,INK)
    r.text('MELHORIAS ATIVAS',840,327,19,CYAN)
    rows=[(u,p.upgrades[u.id]) for u in upgrades.UPGRADES if u.id in p.upgrades and u.stat!='aux']
    pages=max(1,(len(rows)+8)//9);g.build_page%=pages
    for i,(u,level) in enumerate(rows[g.build_page*9:g.build_page*9+9]):r.text(u.name,840,364+i*23,18,INK);r.text(str(level),1197,364+i*23,18,GOLD)
    if not rows:r.text('Sua jornada está apenas começando.',840,369,19,MUTED)
    if pages>1:g.button((840,583,378,26),f'MAIS MELHORIAS / {g.build_page+1} DE {pages}','build_next',CYAN)
    r.text('Menu local: os aliados continuam jogando.' if g.net else 'O tempo está pausado enquanto você consulta sua build.',640,649,19,MUTED,True)
    g.button((460,677,360,30),'CONTINUAR','resume',GOLD)
