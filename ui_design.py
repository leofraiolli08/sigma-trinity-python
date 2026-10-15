"""Original compact dark-fantasy UI: warm brass, ink, readable cards and glyphs."""
import pygame as pg
from settings import INK,MUTED,GOLD,CYAN,GREEN,PINK

SURFACE=(25,25,34)
RAISED=(35,33,43)
EDGE=(69,64,74)

def header(r,title,subtitle='',eyebrow='EXPEDIÇÕES / ASCENSÃO'):
    r.text(eyebrow,40,58,16,GOLD)
    r.text(title,40,78,38,INK)
    if subtitle:r.text(subtitle,640,132,19,MUTED,True)

def wrap(r,text,x,y,width,size=21,color=MUTED,leading=None):
    line='';leading=leading or size+3
    for word in str(text).split():
        test=(line+' '+word).strip()
        if line and r.a.font(size).size(test)[0]>width:r.text(line,x,y,size,color);y+=leading;line=word
        else:line=test
    if line:r.text(line,x,y,size,color);y+=leading
    return y

def badge(r,label,x,y,color=GOLD):
    width=r.a.font(16).size(label)[0]+20
    pg.draw.rect(r.canvas,(12,14,21),(x,y,width,25))
    pg.draw.line(r.canvas,color,(x,y+24),(x+width,y+24),2)
    r.text(label,x+10,y+5,16,color)
    return width

def icon(r,kind,x,y,color=GOLD,size=24):
    """Tiny code-native glyphs, never font-dependent missing emoji."""
    name='ui_'+kind
    if name in r.a.images:
        r.sprite(name,(x,y+size//2),size/56)
        return
    s=size/24
    def pts(rows):return [(round(x+a*s),round(y+b*s)) for a,b in rows]
    def line(rows,width=2):pg.draw.lines(r.canvas,color,False,pts(rows),width)
    if kind in ('sword','damage','knives','boomerang'):
        line([(-8,8),(7,-7),(10,-10),(10,-5),(-6,10)]);line([(-8,3),(-3,8)]);line([(-11,11),(-6,6)],3)
    elif kind in ('health','base_hp','regen','heal'):
        pg.draw.polygon(r.canvas,color,pts([(-10,-5),(-5,-9),(0,-5),(5,-9),(10,-5),(9,1),(0,10),(-9,1)]))
    elif kind in ('lightning','power','shots','haste','dash'):
        pg.draw.polygon(r.canvas,color,pts([(2,-12),(-9,2),(-1,2),(-4,12),(10,-3),(2,-3)]))
    elif kind in ('coin','gold'):
        pg.draw.circle(r.canvas,color,(x,y),round(10*s),2);line([(0,-6),(0,6)],2);line([(-3,-3),(3,-3)])
    elif kind in ('magnet','luck','pickup'):
        line([(-9,-10),(-9,2),(-5,9),(5,9),(9,2),(9,-10)],3)
    elif kind in ('rerolls','speed','cooldown'):
        line([(-10,0),(-8,-6),(0,-10),(8,-5),(9,0)]);line([(5,-2),(9,2),(12,-3)])
        line([(10,4),(5,9),(-3,10),(-9,5)]);line([(-5,6),(-10,3),(-11,9)])
    elif kind=='team':
        for xx,yy in ((-7,1),(7,1),(0,-5)):
            pg.draw.circle(r.canvas,color,(x+round(xx*s),y+round(yy*s)),round(3*s))
            line([(xx-4,yy+7),(xx,yy+4),(xx+4,yy+7)])
    elif kind in ('seals','drone','control','shield'):
        pg.draw.polygon(r.canvas,color,pts([(0,-11),(10,-6),(8,5),(0,11),(-8,5),(-10,-6)]),2);line([(-4,0),(0,4),(5,-3)])
    elif kind=='bell':
        line([(-10,7),(-7,3),(-6,-5),(0,-9),(6,-5),(7,3),(10,7),(-10,7)])
        pg.draw.circle(r.canvas,color,(x,y+round(10*s)),max(1,round(2*s)))
    elif kind=='embers':
        pg.draw.polygon(r.canvas,color,pts([(-8,5),(-5,-3),(-2,1),(1,-12),(8,0),(8,6),(3,10),(-3,10)]),2)
    else:
        pg.draw.polygon(r.canvas,color,pts([(0,-11),(10,0),(0,11),(-10,0)]),2)
        pg.draw.circle(r.canvas,color,(x,y),round(3*s))

def pips(r,x,y,value,cap,color=GOLD,width=16):
    for i in range(cap):pg.draw.rect(r.canvas,color if i<value else (63,59,70),(x+i*(width+5),y,width,5))

def stat(r,rect,label,value,color=GOLD):
    x,y,w,h=rect;r.panel(rect,SURFACE,EDGE)
    r.text(label,x+18,y+15,16,MUTED);r.text(str(value),x+18,y+39,36,color)

def player_portrait(g,key,pos,box,form=False,animated=False):
    name='portrait_'+key+('_form' if form else '')
    if animated and key in ('ippo','eren','klein','musashi','joe','thorfinn','holden'):
        if form:
            from evolution_kit import STAGES
            stage=len(STAGES[key])-1
            name=f'{key}_form{stage}_attack_{int(g.ui_time*9)%4}'
            if name in g.assets.images:
                w,h=g.assets.logical[name];g.render.sprite(name,pos,min(box[0]/w,box[1]/h));return
        stage=3 if key in ('musashi','joe','thorfinn','holden') and form else 2 if form else 0
        pose='attack' if form else 'walk';name=f'{key}_stage{stage}_{pose}_{int(g.ui_time*(9 if form else 7))%4}'
    if name in g.assets.images:
        w,h=g.assets.logical[name];g.render.sprite(name,pos,min(box[0]/w,box[1]/h))
