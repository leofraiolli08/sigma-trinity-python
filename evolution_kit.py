"""Stage-specific crossover choreography; names are adaptations, not canon power levels."""
from entities import V,Projectile,Telegraph,unit

# transformation, ultimate, cinematic motif, cinematic choreography
STAGES={
 'ippo':(('PEEK-A-BOO • IMPULSO','GAZELLE PUNCH','punch','boxing'),
         ('CAMPEÃO • RITMO INFINITO','DEMPSEY ROLL','punch','boxing')),
 'eren':(('TITÃ DE ATAQUE','ASSALTO DO TITÃ','stomp','titan'),
         ('TITÃ • ENDURECIMENTO','RUPTURA CRISTALINA','crystal','titan')),
 'klein':(('MÁGICO • SALTO FLAMEJANTE','TRUQUE FLAMEJANTE','flame','chain'),
          ('SEM ROSTO • GEHRMAN SPARROW','DISPARO DO SEM ROSTO','cards','salvo'),
          ('MARIONETISTA • CONTROLE','FIOS DO CORPO ESPIRITUAL','threads_glow','puppet')),
 'musashi':(('INSTINTO • SAQUE','UM ÚNICO CORTE','slash','iaido'),
            ('ESPADA • NITEN ICHI-RYŪ','DOIS CÉUS • UM CORTE','slash','iaido'),
            ('MORTE • RESOLUÇÃO','LINHA DECISIVA','slash','iaido'),
            ('ALMA • SÁBIO DO BOKKEN','O CORTE SEM ÓDIO','aura','vinland')),
 'joe':(('VAGANTE • GUARDA DE COMBATE','TRÊS GOLPES PARA AMANHÃ','punch','boxing'),
        ('PESO-GALO • CROSS COUNTER','TRIPLO CROSS COUNTER','punch','counter'),
        ('SEM GUARDA • ÚLTIMO FÔLEGO','ÚLTIMO ROUND','punch','counter')),
 'thorfinn':(('VINGANÇA • DUAS ADAGAS','FLANCO DO VINGADOR','slash','iaido'),
             ('RENASCER • RESILIÊNCIA','CEM GOLPES • RESISTIR','aura','counter'),
             ('EXPLORADOR • DEFLEXÃO','PASSAGEM SEGURA','aura','vinland'),
             ('VINLAND • MÃOS ABERTAS','NÃO TENHO INIMIGOS','aura','vinland')),
 'holden':(('NATURALISTA • OBSERVADOR','MIRA DO JUIZ','bullet','salvo'),
           ('ATIRADOR • SALVA','MERIDIANO DE SANGUE','bullet','salvo'),
           ('ESTRATEGISTA • DOMÍNIO','O MAPA DA GUERRA','bullet','salvo'),
           ('A DANÇA DO JUIZ','A ÚLTIMA DANÇA','bullet','dance')),
 'walter':(('TRAJE HAZMAT','REAÇÃO EM CADEIA','chemical','chain'),
           ('FELINA','ÚLTIMO PLANO','bullet','salvo')),
}
def stage_of(p):
    if p.key in ('ippo','eren','walter'):return int(p.evolved)
    return max(0,min(len(STAGES.get(p.key,(None,)))-1,p.stage))
def profile(p):return STAGES[p.key][stage_of(p)]
def signature(key,stage):
    # Only two Ippo/Eren and three Joe/Klein rows are playable; spare VFX are unused.
    return f'ultimate_{key}_{stage}'

def transform(s):
    """Distinct temporary opening bonuses; expiration uses the existing aura contract."""
    p=s.player;stage=stage_of(p)
    from ascension import effect
    if p.key=='ippo':
        p.counter_left=max(p.counter_left,.8+stage*.5)
        s.apply_ally_aura(p,0,5,power=.05 if stage else 0,speed=.12 if stage else .06)
    elif p.key=='eren':
        s.apply_ally_aura(p,0,5,armor=20 if stage else 8,regen=.4 if stage else .2)
    elif p.key=='klein':
        p.invulnerable=max(p.invulnerable,1.1 if stage==1 else .7)
        s.apply_ally_aura(p,0,5,speed=.12 if stage==0 else .06,armor=8 if stage==2 else 0)
    elif p.key=='musashi':
        radius=310 if stage==3 and p.soul_mode=='bond' else 0
        s.apply_ally_aura(p,radius,5,power=.16 if stage==2 else .09,
                          speed=.12 if stage==0 else .05,armor=12 if stage==3 else 4)
    elif p.key=='joe':
        p.counter_left=max(p.counter_left,.6+stage*.45)
        s.apply_ally_aura(p,0,5,armor=8 if stage==2 else 0,speed=.06 if stage==0 else 0)
    elif p.key=='thorfinn':
        s.apply_ally_aura(p,0 if stage<2 else 300,5,armor=6+stage*4,regen=stage*.15,speed=.1 if stage==0 else .04)
    elif p.key=='holden':
        s.apply_ally_aura(p,0,5,power=.06 if stage in (0,2) else 0,speed=.12 if stage==3 else 0)
    if p.key in STAGES and p.key!='walter':effect(s,signature(p.key,stage),p.pos,radius=155,life=.75)

def ultimate(s):
    p=s.player;stage=stage_of(p)
    from ascension import effect,strike
    effect(s,signature(p.key,stage),p.pos,p.pos+p.aim*90,radius=250,life=.95)
    if p.key=='ippo':
        for i in range(10 if stage else 3):
            s.telegraphs.append(Telegraph(V(p.pos),200,.1+i*.14,'dempsey' if stage else 'gazelle_combo',p.damage*(1.25 if stage else 3),source=p))
    elif p.key=='eren':
        count=7 if stage else 5
        for i in range(count):
            pos=p.pos+(V(175,0).rotate(i*360/count) if stage else p.aim*(90+i*90))
            s.telegraphs.append(Telegraph(s.arena.constrain(pos,25),145 if stage else 115,.25+i*.13,'titan_impact',p.damage*(2 if stage else 2.6)))
        if stage:s.apply_ally_aura(p,0,4,armor=25)
    elif p.key=='klein':
        if stage==0:
            for i in range(12):s.add_projectile(Projectile(V(p.pos),V(490,0).rotate(i*30),p.damage*2,'flame',pierce=2))
            p.invulnerable=max(p.invulnerable,.5)
        elif stage==1:
            for angle in (-12,-6,0,6,12):
                s.add_projectile(Projectile(V(p.pos),p.aim.rotate(angle)*900,p.damage*3.8,'air_bullet',pierce=4))
            effect(s,'paper',p.pos,radius=120,life=.8);p.invulnerable=max(p.invulnerable,1.)
        else:
            for e in sorted((e for e in s.enemies if not e.dead),key=lambda e:e.pos.distance_squared_to(p.pos))[:8]:
                e.glue(3.5,.75,True);effect(s,'threads',p.pos,e.pos,life=2.8)
                if not e.boss:e.puppet_mark=3.5;e.puppet_progress=1.;e.puppet_owner=p.pid
                s.telegraphs.append(Telegraph(V(e.pos),125,1.2,'puppet_impact',p.damage*2))
    elif p.key=='musashi':
        cuts=((0,.22,0,6.),) if stage==0 else ((-35,.15,0,2.6),(35,.3,0,2.6),(0,.55,80,3.)) if stage==1 else ((0,.75,0,10.),) if stage==2 else ((0,.45,0,4.5),)
        for angle,delay,offset,multiplier in cuts:
            s.telegraphs.append(Telegraph(V(p.pos)+p.aim*offset,(380 if stage==2 else 310)*p.reach,delay,'musashi_cut',p.damage*multiplier,source=p,direction=p.aim.rotate(angle)))
        if stage==3:
            s.apply_ally_aura(p,310 if p.soul_mode=='bond' else 0,6,power=.17 if p.soul_mode=='bond' else .34,armor=12,regen=.6,speed=.15)
    elif p.key=='joe':
        delays=((.12,.28,.44),(.3,.75,1.2),tuple(.15+i*.17 for i in range(7)))[stage]
        for delay in delays:s.telegraphs.append(Telegraph(V(p.pos),225,delay,'joe_round',p.damage*(2.1 if stage==0 else 3. if stage==1 else 2.),source=p))
        p.counter_left=(.7,2.2,1.4)[stage]
        if stage==2:s.apply_ally_aura(p,0,4,armor=15,regen=.5)
    elif p.key=='thorfinn':
        if stage==0:
            for angle in (-24,24,0):strike(s,p.pos,p.aim.rotate(angle),290*p.reach,28,p.damage*2.5,'dagger_cut')
            p.invulnerable=max(p.invulnerable,.45)
        else:
            radius=(0,260,380,550)[stage]
            s.apply_ally_aura(p,radius,6,armor=12+stage*5,regen=.3*stage,speed=.08)
            for e in s.enemies:
                if not e.dead and e.pos.distance_to(p.pos)<radius+e.radius:
                    e.glue(2.+stage,.5+.05*stage,True)
                    if not e.boss:
                        e.pos=s.arena.constrain(e.pos+unit(e.pos-p.pos)*65,e.radius)
                        if s.enemy_index is not None:s.enemy_index.move(e)
            if stage==1:p.invulnerable=max(p.invulnerable,1.2);p.counter_left=1.5
            if stage==3:
                for ally in s.allied_players:
                    if ally.hp>0 and ally.pos.distance_to(p.pos)<=radius:ally.hp=min(ally.max_hp,ally.hp+24)
    elif p.key=='holden':
        angles=((0,),tuple((i-3.5)*9 for i in range(8)),(-5,0,5),tuple(i*30 for i in range(12)))[stage]
        for i,angle in enumerate(angles):
            s.telegraphs.append(Telegraph(V(p.pos),550,.2+i*(.4 if stage==2 else .13),'holden_salvo',p.damage*(8 if stage==0 else 3.5 if stage==2 else 1.),source=p,direction=p.aim.rotate(angle)))
        if stage==2:
            for e in s.enemies:
                if not e.dead and e.pos.distance_to(p.pos)<500:e.glue(2,.55)
