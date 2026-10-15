"""Code-native pixel environments. Decorative geometry is traversable."""
import pygame as pg
import random

def expansion_map(key):
    rng=random.Random(910);s=pg.Surface((900,900));s.fill({'ring':(28,24,29),'walls':(51,51,48),'fog':(22,30,37)}[key])
    for y in range(0,900,12):
        for x in range(0,900,18):
            n=rng.randrange(8);c=(45+n,39+n,38+n) if key=='ring' else (62+n,62+n,55+n) if key=='walls' else (30+n,41+n,47+n)
            pg.draw.rect(s,c,(x+(9 if y%24 else 0),y,17,11))
    if key=='ring':
        for cy in (150,450,750):
            for cx in (150,450,750):
                pg.draw.rect(s,(11,14,21),(cx-111,cy-111,222,222))
                pg.draw.rect(s,(50,65,82),(cx-100,cy-100,200,200))
                pg.draw.rect(s,(77,89,102),(cx-95,cy-95,190,190),2)
                pg.draw.circle(s,(60,77,97),(cx,cy),55,3)
                for r,c in ((103,(176,79,74)),(108,(159,151,137))):pg.draw.rect(s,c,(cx-r,cy-r,2*r,2*r),1)
                for dx in (-107,107):
                    for dy in (-107,107):pg.draw.rect(s,(212,178,99),(cx+dx-3,cy+dy-3,7,7))
                # Corner mats have openings; no invisible collision is suggested.
                for dx in (-75,75):pg.draw.rect(s,(36,44,53),(cx+dx-9,cy-12,18,24))
                for k in range(35):
                    xx=cx+rng.randrange(-85,86);yy=cy+rng.randrange(-85,86)
                    pg.draw.line(s,(55,69,85),(xx,yy),(xx+4,yy),1)
                for dx in (-126,126):
                    for dy in (-70,-35,0,35,70):
                        pg.draw.rect(s,(51,40,43),(cx+dx-4,cy+dy-5,8,10));pg.draw.line(s,(110,68,56),(cx+dx-3,cy+dy-5),(cx+dx+2,cy+dy-5))
    elif key=='walls':
        for x in (80,390,700):
            for y in (80,390,700):
                for dx,dy in ((0,0),(130,0),(0,140),(140,140)):
                    pg.draw.rect(s,(68,61,51),(x+dx,y+dy,85,60))
                    pg.draw.polygon(s,(109,64,48),[(x+dx-5,y+dy),(x+dx+42,y+dy-35),(x+dx+90,y+dy)])
                    pg.draw.line(s,(143,88,58),(x+dx+5,y+dy-3),(x+dx+42,y+dy-28),2)
                    for ry in range(4,28,5):
                        reach=int((30-ry)*1.3);pg.draw.line(s,(82,49,42),(x+dx+42-reach,y+dy-ry),(x+dx+42+reach,y+dy-ry))
                    for row in range(8,58,8):
                        pg.draw.line(s,(79,70,56),(x+dx+2,y+dy+row),(x+dx+82,y+dy+row))
                    for wx in (12,52):pg.draw.rect(s,(36,41,39),(x+dx+wx,y+dy+16,17,24))
                    pg.draw.rect(s,(105,90,65),(x+dx+33,y+dy+33,18,27));pg.draw.line(s,(42,40,35),(x+dx+42,y+dy+34),(x+dx+42,y+dy+59))
        for y in (25,865):
            pg.draw.rect(s,(110,108,93),(10,y,880,16))
            for x in range(10,900,28):pg.draw.rect(s,(143,139,117),(x,y-5,18,8))
            pg.draw.rect(s,(48,50,47),(415,y-5,70,30))
    else:
        for x in range(90,900,180):
            pg.draw.rect(s,(47,53,56),(x-18,0,36,900))
            for y in range(90,900,180):
                pg.draw.rect(s,(47,53,56),(0,y-18,900,36))
                pg.draw.circle(s,(73,61,93),(x+48,y+48),28,1)
                pg.draw.polygon(s,(91,73,111),[(x+48,y+20),(x+72,y+62),(x+24,y+62)],1)
                pg.draw.rect(s,(15,19,24),(x-29,y-15,3,25))
                pg.draw.rect(s,(112,93,61),(x-32,y-23,9,10))
                pg.draw.rect(s,(238,204,132),(x-30,y-21,5,6))
        for i in range(110):
            x=rng.randrange(900);y=rng.randrange(900)
            pg.draw.line(s,(48,61,67),(x,y),(x+rng.randrange(8,35),y),1)
    # Small debris and scuffs prevent sterile flat surfaces without photographic noise.
    for i in range(1700):
        x=rng.randrange(900);y=rng.randrange(900);base=s.get_at((x,y))
        c=tuple(max(0,v-9) for v in base[:3])
        pg.draw.line(s,c,(x,y),(x+rng.randrange(1,4),y),1)
    for i in range(60):
        x=rng.randrange(20,880);y=rng.randrange(20,880)
        if key!='ring':
            pg.draw.lines(s,(29,33,34),False,[(x,y),(x+6,y-3),(x+11,y+1),(x+16,y-4)],1)
    return pg.transform.scale(s,(3600,3600)).convert()
