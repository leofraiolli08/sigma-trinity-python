"""Pixel rendering and explicit cells from the supplied U.A. atlas.
Original files remain untouched. Background transparency is resolved when loading.
"""
from collections import deque
import math
import pygame as pg
from entities import V
# Coordinates exclude captions and detached attack examples.
GROUPS={
 'nomu':[(8,53,53,59),(66,51,56,61),(128,51,56,61),(187,45,72,67)],
 'villain':[(10,145,52,72),(70,145,51,72),(127,145,59,72),(188,145,64,72)],
 'assassin':[(287,145,59,72),(351,145,58,72),(415,145,68,72),(496,145,65,72)],
 'twice':[(9,252,48,66),(62,252,36,66),(99,252,51,66),(155,252,49,66),(209,252,45,66)],
 'dabi':[(287,250,44,70),(382,250,44,70),(429,250,57,70)],
 'spinner':[(9,360,62,67),(77,360,65,67),(147,360,83,67)],
 'toga':[(284,358,51,69),(341,358,49,69),(402,358,51,69),(464,358,46,69)],
 'stain':[(6,452,75,81),(83,452,64,81),(149,452,65,81)],
 'compress':[(285,453,65,82),(350,453,60,82),(410,453,63,82),(486,453,73,82)],
 'muscular':[(5,562,72,80),(79,562,61,80),(144,562,72,80)],
 'giant':[(282,562,68,82),(354,562,89,82),(448,562,119,82)],
 'corrupt':[(5,680,63,81),(72,680,66,81),(141,680,48,81),(191,680,63,81)],
 'drone':[(282,686,68,72),(353,686,68,72),(425,686,75,72),(508,686,58,72)],
 'robot':[(5,795,76,84),(83,795,73,84),(161,795,63,84)],
 'boss':[(285,0,176,112),(464,0,101,112)],
}
VARIANTS={0:('villain','nomu','corrupt'),1:('dabi','compress'),2:('twice','toga'),3:('muscular','giant','robot'),4:('drone',),5:('spinner','stain','assassin')}

def cut_cell(sheet,rect):
    im=sheet.subsurface(rect).copy().convert_alpha();w,h=im.get_size()
    # Remove only border-connected dark atlas backdrop, retaining enclosed dark clothing.
    seen=set();queue=deque([(x,0) for x in range(w)]+[(x,h-1) for x in range(w)]+[(0,y) for y in range(h)]+[(w-1,y) for y in range(h)])
    while queue:
        x,y=queue.popleft()
        if (x,y) in seen or not(0<=x<w and 0<=y<h):continue
        seen.add((x,y));r,g,b,a=im.get_at((x,y))
        # The supplied sheet has a subtly varying near-black backdrop, including
        # red-tinted patches. The old color ordering left these patches opaque.
        if r<=22 and g<=24 and b<=31 and b-r>=5 and b-g>=4:
            im.set_at((x,y),(0,0,0,0));queue.extend(((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
    components=pg.mask.from_surface(im,8).connected_components(20)
    if components:
        body=max(components,key=lambda m:m.count())
        matte=body.to_surface(setcolor=(255,255,255,255),unsetcolor=(0,0,0,0))
        im.blit(matte,(0,0),special_flags=pg.BLEND_RGBA_MULT)
    box=im.get_bounding_rect(min_alpha=8)
    return im.subsurface(box).copy() if box.width and box.height else im

def load_atlas(root):
    path=root/'art/ua_monsters.png'
    if not path.exists():return {},{}
    sheet=pg.image.load(str(path)).convert_alpha();images={};sizes={}
    for group,boxes in GROUPS.items():
        frames=[cut_cell(sheet,pg.Rect(*r)) for r in boxes]
        # Same canvas and same source scale prevent frame-to-frame size pumping.
        w=max(f.get_width() for f in frames);h=max(f.get_height() for f in frames)
        for i,frame in enumerate(frames):
            canvas=pg.Surface((w,h),pg.SRCALPHA);canvas.blit(frame,frame.get_rect(midbottom=(w//2,h)))
            name=f'ua_{group}_{i}';images[name]=canvas
            target=108 if group=='boss' else 66 if group in ('giant','muscular','robot') else 54
            sizes[name]=(round(w*target/h),target)
    return images,sizes

def enemy_sprite(enemy,time,arena):
    if getattr(enemy,'trial_key',None):return 'portrait_'+enemy.trial_key+'_form'
    if arena in ('city','ring','walls','fog'):return f'{arena}_boss_{int(time*4)%2}' if enemy.boss else f'{arena}_enemy_{enemy.kind}_{int(time*6)%2}'
    if arena!='usj':return f'boss_{int(time*4)%2}' if enemy.boss else f'enemy_{enemy.kind}_{int(time*6)%2}'
    groups=('boss',) if enemy.boss else VARIANTS[enemy.kind]
    group=groups[(enemy.uid//6)%len(groups)]
    return f'ua_{group}_{int(time*7+enemy.uid)%len(GROUPS[group])}'

def floor_tile():
    import random
    r=random.Random(16);tile=pg.Surface((96,96));tile.fill((22,24,34))
    for y in range(0,96,16):
        for x in range(-12,96,24):
            xx=x+(12 if y//16%2 else 0);col=r.choice(((42,43,58),(48,47,63),(37,40,52)))
            pg.draw.rect(tile,col,(xx+1,y+1,22,14));pg.draw.line(tile,(65,63,77),(xx+2,y+2),(xx+20,y+2))
            for _ in range(3):pg.draw.rect(tile,(29,33,42),(xx+r.randrange(3,21),y+r.randrange(4,13),2,1))
    return pg.transform.scale(tile,(192,192))

class PixelEffects:
    def __init__(self):
        from visual_assets import ArtVFX
        self.layer=pg.Surface((320,180),pg.SRCALPHA);self.output=pg.Surface((1280,720),pg.SRCALPHA)
        self.art=ArtVFX();self.quality='full'
    def begin(self):self.layer.fill((0,0,0,0))
    def point(self,pos):return (round(pos[0]/4),round(pos[1]/4))
    def present(self,canvas):
        # Scale only the occupied rectangle. Empty ground-effects passes cost no full-screen blit.
        rect=self.layer.get_bounding_rect(min_alpha=1)
        if not rect.width or not rect.height:return
        target=pg.Rect(rect.x*4,rect.y*4,rect.width*4,rect.height*4)
        pg.transform.scale(self.layer.subsurface(rect),target.size,self.output.subsurface(target))
        canvas.blit(self.output,target,area=target)
    def projectile(self,q,pos,time,academy=False):
        if self.art.projectile(self,q,pos,time):return
        from combat_art import projectile
        if projectile(self,q,pos,time):return
        x,y=self.point(pos);d=q.vel.normalize() if q.vel.length_squared() else V(1,0)
        color=(100,235,225) if q.kind in ('glue','bonder','jet') else (183,239,113) if q.kind=='flask' else (255,183,79) if q.kind in ('pacoca','stuffed','crumb') else (117,251,146) if q.kind in ('token','air','shoot_style') else (66,153,255) if q.kind=='bullet' else (249,92,121)
        length=8 if q.kind in ('shoot_style','bullet') else 6 if q.kind in ('bonder','stuffed') else 5
        for n in range(length,0,-1):
            at=(round(x-d.x*n*2),round(y-d.y*n*2)); alpha=35+int(180*(1-n/(length+1)))
            pg.draw.rect(self.layer,(*color,alpha),(*at,2 if n<length-2 else 1,2 if n<length-2 else 1))
        if q.kind in ('air','shoot_style','hostile','bullet'):
            width=3 if q.kind=='shoot_style' else 2
            pts=[(x-10*d.x,y-10*d.y),(x-4*d.x+d.y*width,y-4*d.y-d.x*width),(x,y),(x-4*d.x-d.y*width,y-4*d.y+d.x*width)]
            pg.draw.lines(self.layer,(*color,210),False,pts,width)
            pg.draw.rect(self.layer,(235,255,229),(x-2,y-2,4,4))
            if q.kind=='shoot_style':
                for sign in (-1,1): pg.draw.line(self.layer,(189,255,217),(x-8*d.x+sign*d.y*4,y-8*d.y-sign*d.x*4),(x-2*d.x+sign*d.y*5,y-2*d.y-sign*d.x*5),1)
        elif q.kind=='token':
            spin=int(time*18)%2
            pg.draw.polygon(self.layer,(25,72,49),[(x,y-5),(x+5,y),(x,y+5),(x-5,y)])
            pg.draw.polygon(self.layer,color,[(x,y-4),(x+4,y),(x,y+4),(x-4,y)],1)
            pg.draw.line(self.layer,(229,255,172),(x-2 if spin else x,y),(x+2 if spin else x,y) if spin else (x,y+2))
        elif q.kind in ('pacoca','stuffed','crumb'):
            radius=1 if q.kind=='crumb' else (4 if q.kind=='stuffed' else 3)
            pg.draw.rect(self.layer,(96,48,34),(x-radius-1,y-radius-1,radius*2+2,radius*2+2))
            pg.draw.rect(self.layer,color,(x-radius,y-radius,radius*2,radius*2));pg.draw.rect(self.layer,(255,236,165),(x-radius,y-radius,radius*2,1))
            pg.draw.rect(self.layer,(194,105,54),(x+radius-1,y+radius-1,2,2))
        elif q.kind=='flask':
            pg.draw.circle(self.layer,(66,100,48), (x,y+1),5)
            pg.draw.circle(self.layer,color,(x,y+1),4)
            pg.draw.rect(self.layer,(230,255,181),(x-1,y-5,3,3))
            for i in range(3):
                bx=x+int(math.sin(time*9+i)*4);by=y-5-i*2
                pg.draw.rect(self.layer,(214,255,165),(bx,by,1,1))
        else:
            pg.draw.circle(self.layer,(*color,70),(x,y),6);pg.draw.circle(self.layer,(24,96,114),(x,y),4);pg.draw.circle(self.layer,color,(x,y),3);pg.draw.rect(self.layer,(235,255,252),(x-1,y-2,2,1))
    def attack_cast(self,pos,direction,key,pose,time):
        if key in ('ippo','eren','musashi'):return  # The actual strike already draws its impact.
        x,y=self.point(pos);d=direction.normalize() if direction.length_squared() else V(1,0);side=V(-d.y,d.x)
        from ascension import COLORS
        color=COLORS[key]
        power=max(0,min(1,pose/.16)); end=V(x,y)+d*(10+power*4)
        for offset in (-2,0,2):
            a=V(x,y)+side*offset;pg.draw.line(self.layer,(*color,120+int(power*100)),a,end+side*offset,1)
        pg.draw.circle(self.layer,(*color,100),(round(end.x),round(end.y)),4)
        pg.draw.rect(self.layer,(245,255,236),(round(end.x)-1,round(end.y)-1,3,3))
    def wave(self,pos,radius,life,color):
        center=self.point(pos);rr=max(1,round(radius/4*(1-min(1,life/.4))))
        pg.draw.circle(self.layer,(*color,210),center,rr,2)
        if rr>4:pg.draw.circle(self.layer,(*color,80),center,rr-3,1)
        for i in range(16):
            d=V(rr+2+(i%3),0).rotate(i*22.5);pg.draw.rect(self.layer,(*color,220),(round(center[0]+d.x),round(center[1]+d.y),2,2))


def isolated_figures(path):
    sheet=pg.image.load(str(path)).convert_alpha()
    masks=sorted(pg.mask.from_surface(sheet,20).connected_components(100),key=lambda m:m.count(),reverse=True)[:8]
    # Connected alpha isolates irregular sprites even when their bounding boxes overlap.
    pieces=[]
    for mask in masks:
        rect=mask.get_bounding_rects()[0];im=sheet.subsurface(rect).copy()
        matte=mask.to_surface(setcolor=(255,255,255,255),unsetcolor=(0,0,0,0)).subsurface(rect)
        im.blit(matte,(0,0),special_flags=pg.BLEND_RGBA_MULT);pieces.append((rect,im))
    top=sorted(pieces,key=lambda pair:pair[0].centery)[:4];bottom=[x for x in pieces if all(x is not a for a in top)]
    return [im for rect,im in sorted(top,key=lambda pair:pair[0].centerx)+sorted(bottom,key=lambda pair:pair[0].centerx)]

def load_generated(root):
    images={};sizes={}
    path=root/'art/pixel_monsters.png'
    if path.exists():
        figures=isolated_figures(path)
        for i,figure in enumerate(figures):
            height=[64,64,38,70,48,70,112,112][i]
            width=round(figure.get_width()*height/figure.get_height());im=pg.transform.scale(figure,(width,height))
            if i<6:
                for frame in range(2):
                    canvas=pg.Surface((width+4,height+3),pg.SRCALPHA);canvas.blit(im,(2,frame*2))
                    name=f'enemy_{i}_{frame}';images[name]=canvas;sizes[name]=canvas.get_size()
            else:
                name=f'boss_{i-6}';images[name]=im;sizes[name]=im.get_size()
    path=root/'art/walter_atlas.png'
    if path.exists():
        figures=isolated_figures(path)
        for i,figure in enumerate(figures):
            group=('walter','hazmat','heisenberg','felina')[i//2]
            height=86;width=round(figure.get_width()*height/figure.get_height());im=pg.transform.scale(figure,(width,height))
            name=f'{group}_{i%2}';images[name]=im;sizes[name]=im.get_size()
            if i%2==0:
                portrait='portrait_'+('walter' if group=='walter' else 'walter_form' if group=='hazmat' else group)
                images[portrait]=im;sizes[portrait]=im.get_size()
    return images,sizes
