"""Only ordinary item missions are public. Character secrets are never listed here."""
MISSIONS={
 'lightning':('Condutor elétrico','Complete a onda 3.','wave',3),
 'seals':('Selos arcanos','Abra 2 baús no total.','chests',2),
 'drone':('Sentinela','Derrote 250 inimigos no total.','kills',250),
 'boomerang':('Bumerangue','Use 3 transformações no total.','transforms',3),
 'bell':('Sino do vazio','Derrote seu primeiro chefe.','victories',1),
 'embers':('Brasas errantes','Complete a onda 8.','wave',8),
}
def unlocked(data):
    stats=data.get('mission_stats',{})
    return {'knives'}|{k for k,(_,_,stat,n) in MISSIONS.items() if stats.get(stat,0)>=n}

def draw(g):
    from settings import INK,MUTED,GOLD,CYAN,GREEN
    from ui_design import header,icon,badge,wrap
    r=g.render;d=g.save.data;owned=unlocked(d)
    header(r,'Uma missão. Uma nova possibilidade.','Cumpra objetivos e amplie as armas disponíveis nas próximas partidas.','ARSENAL / MISSÕES')
    for i,(key,(name,desc,stat,n)) in enumerate(MISSIONS.items()):
        x=40+(i%3)*409;y=185+(i//3)*216;done=key in owned;color=GREEN if done else CYAN
        r.panel((x,y,382,193),(26,24,34),color if done else (71,61,78),2 if done else 1)
        r.panel((x+20,y+22,63,63),(17,19,29),color);icon(r,key,x+51,y+53,color,34)
        r.text(name,x+104,y+24,23,INK);wrap(r,desc,x+104,y+64,251,18,MUTED,22)
        value=min(n,d['mission_stats'].get(stat,0));r.bar(x+20,y+130,342,7,value/n,color)
        r.text('DISPONÍVEL NO ARSENAL' if done else 'MISSÃO EM ANDAMENTO',x+20,y+154,17,color)
        r.text(f'{value} / {n}',x+296,y+154,18,INK)
    r.text('Lâminas orbitais estão disponíveis desde o início. Seu progresso é salvo por onda.',640,643,20,MUTED,True)
    g.button((465,679,350,30),'VOLTAR','menu',GOLD)
