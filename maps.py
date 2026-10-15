"""Deterministic arena terrain. All scenery is traversable; colored terrain affects pace.
The academy uses the original user-supplied island image as its background.
"""
import math
import random
import pygame as pg
from arena_art import expansion_map
from entities import V
MAPS={
 'crypt':('CRIPTA DO COLAPSO','Pedra, velas e selos instáveis.','Explosões rituais a cada 12s.'),
 'usj':('U.A. • ACADEMIA','Campus em pixel art e vilões da U.A.','Explore a cidade; avisos de perigo a cada 10s.'),
 'city':('CIDADE EM RUÍNAS','Avenidas vazias sob uma noite de cinzas.','Corra nas avenidas; bombardeio a cada 10s.'),
}
MAPS.update(ring=('GINÁSIO • NOITE DE LUTA','Tablado, cordas e luzes de ringue.','Sinos de perigo a cada 14s.'),
            walls=('DISTRITO DAS MURALHAS','Ruas de pedra e portões rompidos.','Estilhaços em linha a cada 12s.'),
            fog=('BACKLUND • NEBLINA','Lampiões e praças de rituais.','Selos alternados a cada 13s.'))
# Campus image fits height; black side gutters are outside the arena.
BOUNDARY=[V(195,60),V(3405,60),V(3405,3540),V(195,3540)]

class Arena:
    def __init__(self,key):
        if key not in MAPS: raise ValueError('Mapa desconhecido: '+str(key))
        self.key=key; self.name=MAPS[key][0]; self.hazard_interval={'crypt':12.,'usj':10.,'city':10.,'ring':14.,'walls':12.,'fog':13.}[key]
        from settings import BASE_DIR
        self.generated_floor=(BASE_DIR/'assets/art/terrain_atlas.png').exists()
    def zone_at(self,pos):
        if self.key!='usj': return self.name
        x,y=pos.x/3600,pos.y/3600
        if x>.68 and y<.38: return 'ZONA DE RUÍNAS'
        if x<.32 and y<.68: return 'CAMPO DE TREINAMENTO'
        if y>.74: return 'PORTÃO PRINCIPAL'
        if x>.66: return 'DISTRITO URBANO'
        return 'PRAÇA DA U.A.'
    def speed_at(self,pos):
        if self.key=='usj':
            if V(pos).distance_to(V(3180,2080))<130: return .9
            return 1.
        if self.key=='city':
            period,phase,half,width=(900,450,450,135) if self.generated_floor else (600,0,300,90)
            if abs((pos.x+phase)%period-half)<width or abs((pos.y+phase)%period-half)<width:return 1.08
        return 1.
    @property
    def bounds(self):
        # This rectangle is also the inner face of the visible boundary walls.
        return pg.Rect(219 if self.key=='usj' else 96,96,3162 if self.key=='usj' else 3408,3408)
    def contains(self,pos,radius=0):
        b=self.bounds
        return b.left+radius<=pos.x<=b.right-radius and b.top+radius<=pos.y<=b.bottom-radius
    def constrain(self,pos,radius=15):
        b=self.bounds
        return V(max(b.left+radius,min(b.right-radius,pos.x)),max(b.top+radius,min(b.bottom-radius,pos.y)))
    def hazards(self,pos,time):
        if self.key=='ring':return [(V(pos)+V(140,0).rotate(time*10),100)]
        if self.key=='walls':return [(V(pos)+V(0,i*180),75) for i in (-1,0,1)]
        if self.key=='fog':return [(V(pos)+V(160,0).rotate(time*12+i*180),85) for i in range(2)]
        if self.key=='crypt': return [(V(pos),90)]
        if self.key=='city': return [(V(pos)+V(i*175,0),80) for i in (-1,0,1)]
        count=2 if self.zone_at(pos)=='ZONA DE RUÍNAS' else 1
        return [(self.constrain(V(pos)+V(i*210,0).rotate(time*20)),95) for i in range(count)]

def make_map(key,tile):
    """Cached background only, independent of combat RNG and framerate."""
    from visual_assets import terrain
    ground=terrain(key)
    if ground is not None:
        out=pg.Surface((3600,3600)).convert()
        for y in range(-450,3600,900):
            for x in range(-450,3600,900):out.blit(ground,(x,y))
        return out
    if key in ('ring','walls','fog'):return expansion_map(key)
    out=pg.Surface((3600,3600)).convert(); rng=random.Random(518)
    if key=='crypt':
        for y in range(0,3600,tile.get_height()):
            for x in range(0,3600,tile.get_width()): out.blit(tile,(x,y))
        return out
    if key=='usj':
        from settings import BASE_DIR
        source=pg.image.load(str(BASE_DIR/'assets/art/hero_map.png')).convert()
        width=round(source.get_width()*3600/source.get_height())
        out.fill((18,27,31));out.blit(pg.transform.scale(source,(width,3600)),((3600-width)//2,0))
        return out
    out.fill((26,28,32))
    if key=='city':
        # Low, shattered foundations leave every road and block traversable.
        for y in range(0,3600,600):
            for x in range(0,3600,600):
                pg.draw.rect(out,(42,45,48),(x+210,y,180,600))
                pg.draw.rect(out,(42,45,48),(x,y+210,600,180))
                for k in range(0,600,72):
                    pg.draw.rect(out,(135,115,70),(x+297,y+k,5,32));pg.draw.rect(out,(135,115,70),(x+k,y+297,32,5))
                for dx,dy in ((30,30),(415,30),(30,415),(415,415)):
                    rect=pg.Rect(x+dx,y+dy,150,150)
                    pg.draw.rect(out,(51,47,46),rect);pg.draw.rect(out,(78,72,63),rect,3)
                    for i in range(4):
                        xx=rect.x+rng.randrange(140); yy=rect.y+rng.randrange(140)
                        pg.draw.line(out,(22,23,25),(xx,yy),(xx+35,yy-22),5)
                for i in range(10):
                    xx=x+rng.randrange(600);yy=y+rng.randrange(600)
                    pg.draw.line(out,(75,71,63),(xx,yy),(xx+12,yy+7),2)
                for i in range(5):pg.draw.rect(out,(126,123,106),(x+220+i*32,y+175,17,28))
    # Reuse the stone's photographic microtexture as material shading, preserving zone colors.
    material=tile.copy();material.fill((155,155,155),special_flags=pg.BLEND_RGB_ADD)
    for y in range(0,3600,material.get_height()):
        for x in range(0,3600,material.get_width()):out.blit(material,(x,y),special_flags=pg.BLEND_RGB_MULT)
    for i in range(220):
        x=rng.randrange(120,3480);y=rng.randrange(120,3480)
        pts=[(x,y),(x+20,y-7),(x+31,y+5),(x+55,y-14)]
        pg.draw.lines(out,(30,32,30),False,pts,2)
    # Fine deterministic grain prevents large flat digital color fields.
    for i in range(45000):
        x=rng.randrange(3600);y=rng.randrange(3600);c=out.get_at((x,y));d=rng.choice((-9,8))
        out.set_at((x,y),tuple(max(0,min(255,v+d)) for v in c[:3]))
    pg.draw.rect(out,(119,111,87),(60,60,3480,3480),5)
    return pg.transform.scale(pg.transform.scale(out,(900,900)),(3600,3600))
