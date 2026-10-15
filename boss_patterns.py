"""Six arena signatures. Every damaging attack is telegraphed before resolution."""
from entities import V,Telegraph,Projectile,unit,segment_distance
from waves import FAMILIES

HOSTILE_KINDS=frozenset(('charge','ranged','boss_ring','hostile_blast','summon','boss_fan','boss_sweep','enemy_melee'))

def queue(s,e,target,pattern):
    theme=s.arena.key;phase=e.phase
    living=[p for p in s.allied_players if p.hp>0]
    def mark(pos,radius,delay=1.15,kind='hostile_blast',damage=None,direction=None,**kw):
        t=Telegraph(s.arena.constrain(V(pos)),radius,delay,kind,e.damage if damage is None else damage,e,direction,**kw)
        s.telegraphs.append(t)
    def charge(delay=1.):mark(e.pos,e.radius,delay,'charge',direction=unit(target.pos-e.pos))
    def fan(count=7,spread=70):mark(e.pos,35,1.05,'boss_fan',direction=unit(target.pos-e.pos),count=count,spread=spread,reach=800)
    def sweep(pos,direction,length=470,width=35,delay=1.2):mark(pos,width,delay,'boss_sweep',direction=unit(direction),reach=length)
    def summon(count):
        for i in range(count):mark(e.pos+V(155,0).rotate(360*i/count),38,1.2,'summon',0)
    if theme=='crypt':
        e.attack_name=('CÍRCULO SEPULCRAL','AVANÇO DO OSSUÁRIO','SELOS DA CRIPTA','LEGIÃO DESPERTA')[pattern]
        if pattern==0:mark(e.pos,90,1.,'boss_ring')
        elif pattern==1:charge()
        elif pattern==2:
            for p in living:
                for i in range(phase):mark(p.pos+V((i-(phase-1)/2)*180,0),85,1.25+i*.18)
        else:summon(3+phase)
    elif theme=='usj':
        e.attack_name=('INVESTIDA NOMU','IMPACTO DE ABSORÇÃO','PRESSÃO DA ACADEMIA','REFORÇOS DA LIGA')[pattern]
        if pattern==0:charge(.95)
        elif pattern==1:
            mark(e.pos,155+phase*18,1.05,damage=e.damage*1.25)
            if phase>=2:
                for p in living:mark(p.pos,65,1.6)
        elif pattern==2:fan(5+phase*2,80)
        else:summon(2+phase)
    elif theme=='city':
        e.attack_name=('BOMBARDEIO QUADRICULADO','VARREDURA MECÂNICA','DISPARO DE SUCATA','ESCOLTA DO COLOSSO')[pattern]
        if pattern==0:
            for p in living:
                for i in range(2+phase):mark(p.pos+V((i-(1+phase)/2)*175,0),62,1.4+i*.12)
        elif pattern==1:sweep(e.pos,target.pos-e.pos,620,32+phase*5)
        elif pattern==2:fan(5+phase*2,95)
        else:summon(2+phase)
    elif theme=='ring':
        e.attack_name=('ENTRADA DE PRESSÃO','DIRETO DO VAZIO','GANCHO DEMOLIDOR','DESAFIANTES DO RINGUE')[pattern]
        if pattern==0:charge(.95)
        elif pattern==1:sweep(e.pos,target.pos-e.pos,315,40+phase*6,1.)
        elif pattern==2:mark(e.pos,125+phase*20,1.1,damage=e.damage*1.3)
        else:summon(1+phase)
    elif theme=='walls':
        e.attack_name=('PISÃO DO PORTÃO','FISSURA DAS MURALHAS','MARCHA TITÂNICA','TITÃS ERRANTES')[pattern]
        if pattern==0:mark(e.pos,180+phase*20,1.3,damage=e.damage*1.3)
        elif pattern==1:
            direction=unit(target.pos-e.pos)
            for i in range(phase):sweep(e.pos+V(-direction.y,direction.x)*(i-(phase-1)/2)*140,direction,580,30,1.25+i*.18)
        elif pattern==2:charge(1.15)
        else:summon(phase+1)
    else:
        e.attack_name=('SELOS ESPELHADOS','CARTAS DO ARCONTE','CORTE DO VÉU','ECOS DA NEBLINA')[pattern]
        if pattern==0:
            for p in living:
                for sign in (-1,1):mark(p.pos+V(sign*145,0),83,1.25)
                if phase==3:mark(p.pos,62,1.7)
        elif pattern==1:fan(5+phase*2,110)
        elif pattern==2:sweep(e.pos,target.pos-e.pos,550,28+phase*5,1.2)
        else:summon(1+phase)

def resolve(s,t):
    if t.kind not in ('boss_fan','boss_sweep'):return False
    if t.kind=='boss_fan':
        for i in range(t.count):
            angle=(i-(t.count-1)/2)*t.spread/max(1,t.count-1)
            s.add_projectile(Projectile(V(t.pos),V(t.direction).rotate(angle)*250,t.damage,'hostile',life=3.2,radius=6,hostile=True))
    else:
        end=t.pos+V(t.direction)*t.reach
        for ally in s.allied_players:
            if ally.hp>0 and segment_distance(ally.pos,t.pos,end)<t.radius+ally.radius:
                with s.acting(ally):s.hurt_player(t.damage)
        import ascension
        ascension.effect(s,'death_line',t.pos,end,radius=t.radius,life=.5,color=FAMILIES[s.arena.key][2])
    return True
