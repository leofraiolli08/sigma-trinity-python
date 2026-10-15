"""Pixel VFX: shapes are authored in code, separated from simulation randomness."""
import math
import pygame as pg
from entities import V

def draw(fx,e,xy,time):
    if fx.art.effect(fx,e,xy,time):return
    if e.kind in ('punch','uppercut'):
        # Boxer blows read as motion/impact rather than supernatural fireballs.
        a=V(fx.point(xy(e.pos)));b=V(fx.point(xy(e.end)))
        d=(b-a).normalize() if b!=a else V(1,0);side=V(-d.y,d.x)
        progress=max(0,min(1,1-e.life/e.duration));center=a.lerp(b,.5+progress*.5)
        alpha=round(230*(1-progress));ink=(244,235,218,alpha)
        for offset in (-3,0,3):pg.draw.line(fx.layer,ink,a+d*3+side*offset,center-d*3+side*offset,1)
        pg.draw.polygon(fx.layer,(*e.color,alpha),[center+d*4,center+side*3,center-d*3,center-side*3],1)
        fx.art.stamp(fx.layer,'spark',center,12,alpha=alpha)
        return
    if fx.art.effect(fx,e,xy,time):return
    layer=fx.layer;a=V(fx.point(xy(e.pos)));b=V(fx.point(xy(e.end)))
    t=1-e.life/e.duration;r=max(2,e.radius/4);alpha=int(230*(1-t*.7));c=(*e.color,alpha);white=(255,246,216,alpha)
    if not(-r-80<a.x<400+r and -r-80<a.y<260+r) and not(-100<b.x<420 and -100<b.y<280):return
    kind=e.kind
    if kind in ('lightning','threads','cable'):
        points=[a.lerp(b,i/8)+V(0,math.sin(i*8+time*23)*(3 if kind=='lightning' else 1)) for i in range(9)]
        if kind=='threads':
            for offset in (-3,0,3):pg.draw.lines(layer,c,False,[v+V(offset,0) for v in points],1)
            fx.art.stamp(layer,'threads_glow',b,18,alpha=150)
        else:
            pg.draw.lines(layer,(*e.color,65),False,points,4);pg.draw.lines(layer,c,False,points,2);pg.draw.lines(layer,white,False,points,1)
    elif kind in ('punch','uppercut','slash','crystal','musashi_slash','death_line'):
        d=(b-a).normalize() if b!=a else V(1,0);side=V(-d.y,d.x);center=a.lerp(b,.4+t*.6)
        if kind in ('punch','uppercut'):
            pg.draw.line(layer,(*e.color,80),a,center,7)
            pg.draw.polygon(layer,c,[center+d*7,center+d*3+side*5,center-d*4+side*4,center-d*4-side*4,center+d*3-side*5])
            pg.draw.line(layer,white,center+side*3,center+d*5,2)
        elif kind=='crystal':
            for i in range(5):
                p=a.lerp(b,i/4);h=(5+i%3)*max(.3,1-t)
                pg.draw.polygon(layer,c,[p+V(-4,2),p+V(0,-h),p+V(4,2)]);pg.draw.line(layer,white,p,p+V(0,-h),1)
        elif kind=='death_line':
            pg.draw.line(layer,(*e.color,90),a,b,8)
            pg.draw.line(layer,c,a,b,3)
            for i in range(4):
                cut=a.lerp(b,(i+1)/5);pg.draw.line(layer,white,cut-side*6,cut+side*6,1)
        else:
            pts=[a+d*(r*.7+math.cos(v)*r)+side*math.sin(v)*r for v in (-1.3,-.8,-.3,.3,.8,1.3)]
            pg.draw.lines(layer,c,False,pts,3);pg.draw.lines(layer,white,False,[p+d*2 for p in pts],1)
    elif kind in ('spark','muzzle'):
        for i in range(6):
            d=V(1,0).rotate(i*60);pg.draw.line(layer,c,a+d*(2+t*5),a+d*(5+t*11),1)
        pg.draw.rect(layer,white,(a.x-1,a.y-1,3,3))
    elif kind in ('paper','cards'):
        for i in range(9):
            p=a+V((4+t*r),0).rotate(i*40+time*30)
            pg.draw.polygon(layer,c,[p+V(-2,-4),p+V(3,-3),p+V(2,4),p+V(-3,3)])
            pg.draw.line(layer,white,p+V(0,-2),p+V(0,2))
    elif kind in ('vortex','seal','soul_aura'):
        for j in range(3):
            rr=max(2,r*(1-t*.7)*(1-j*.23));points=[a+V(rr,0).rotate(i*60+time*65*(1 if j%2 else -1)) for i in range(6)]
            pg.draw.polygon(layer,c,points,1);pg.draw.circle(layer,(*e.color,45),a,int(rr),1)
        if kind=='vortex':pg.draw.circle(layer,(17,9,28,210),a,max(3,int(r*.2*(1-t))))
        if kind=='soul_aura':
            for i in range(8):
                point=a+V(r*(.8-t*.3),0).rotate(i*45+time*55)
                pg.draw.circle(layer,white,point,2)
    elif kind=='drone':
        pg.draw.polygon(layer,c,[a+V(-4,0),a+V(0,-3),a+V(4,0),a+V(0,3)],1)
        pg.draw.line(layer,white,a+V(-6,-2),a+V(6,-2),1)
    elif kind=='afterimage':
        for i in range(4):pg.draw.ellipse(layer,(*e.color,int(alpha*(1-i/5))),(a.x-i*4,a.y-14,6,14),1)
    else:
        # Per-pattern silhouettes: rippling spill, blast debris, rising fire/steam.
        rr=max(2,int(r*(.2+t*.8)))
        if kind=='spill':
            for i in range(9):
                p=a+V(rr*.65,0).rotate(i*40);pg.draw.ellipse(layer,c,(p.x-rr*.35,p.y-rr*.22,rr*.7,rr*.44),2)
        elif kind in ('chemical','flame'):
            for i in range(7):
                p=a+V(math.sin(i*11)*r*.6,-t*r*.7+(i%3)*3)
                pg.draw.polygon(layer,c,[p+V(-3,4),p+V(0,-6-i%3),p+V(4,4)],1)
        else:
            pg.draw.ellipse(layer,c,(a.x-rr,a.y-rr*.5,rr*2,rr),2)
            for i in range(12):
                p=a+V(rr,0).rotate(i*30);pg.draw.rect(layer,c,(p.x,p.y,2+i%2,2))
            if kind=='nuclear':
                pg.draw.line(layer,(*e.color,95),a,a+V(0,-r*(1-t)),max(2,int(r*.18)))
                pg.draw.ellipse(layer,c,(a.x-rr*.55,a.y-r*(1-t)-rr*.2,rr*1.1,rr*.4),2)

def projectile(fx,q,pos,time):
    kinds=('card','air_bullet','flame','gravity','laser','boomerang','note')
    if q.kind not in kinds:return False
    a=V(fx.point(pos));s=fx.layer;d=q.vel.normalize() if q.vel.length_squared() else V(1,0);side=V(-d.y,d.x)
    c={'note':(183,159,245),'card':(223,193,246),'air_bullet':(186,215,235),'flame':(248,165,84),'gravity':(228,112,164),'laser':(130,218,235),'boomerang':(242,205,122)}[q.kind]
    for i in range(1,5):pg.draw.rect(s,(*c,150-i*25),(*(a-d*i*3),2,2))
    if q.kind=='note':
        pg.draw.circle(s,c,a,4,1);pg.draw.line(s,c,a+V(2,0),a+V(2,-8),2);pg.draw.line(s,c,a+V(2,-8),a+V(6,-6),2)
    elif q.kind=='card':
        d=V(1,0).rotate(time*600);side=V(-d.y,d.x)
        pg.draw.polygon(s,c,[a+d*4+side*2,a-d*4+side*2,a-d*4-side*2,a+d*4-side*2],1);pg.draw.circle(s,(246,226,178),a,1)
    elif q.kind=='gravity':
        pg.draw.circle(s,(*c,70),a,7);pg.draw.circle(s,c,a,5,1);pg.draw.circle(s,(24,13,35),a,3)
    elif q.kind=='boomerang':
        d=V(1,0).rotate(time*550);side=V(-d.y,d.x);pg.draw.lines(s,c,False,[a+d*5,a-side*3,a-d*5],2)
    elif q.kind=='flame':pg.draw.polygon(s,c,[a+d*4,a-d*6+side*3,a-d*3,a-d*6-side*3])
    else:
        pg.draw.line(s,(*c,80),a-d*10,a,4);pg.draw.line(s,c,a-d*8,a,2);pg.draw.line(s,(251,255,244),a-d*4,a,1)
    return True
