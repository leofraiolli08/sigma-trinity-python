"""Production VFX sprites. All transforms are bounded, cached and render-only."""
from collections import OrderedDict
import math
import pygame as pg
from settings import BASE_DIR
from entities import V

BASE_FX=('punch','slash','lightning','flame','chemical','crystal','vortex','cards',
          'note','token','pacoca','glue','bullet','nuclear','air','aura')
IMPACT_FX=('stomp','spark','swarm','gravity','spill','crumb_blast','resonance','threads_glow')
ULTIMATE_FX=tuple(f'ultimate_{key}_{stage}' for key in ('ippo','eren','klein','musashi','joe','thorfinn','holden') for stage in range(4))
FX_NAMES=BASE_FX+IMPACT_FX+ULTIMATE_FX
SEQUENCE_NAMES=("punch","slash","cards","bullet","aura","lightning","glue","pacoca","swarm","chemical","vortex","resonance")
PROJECTILES={'glue':'glue','bonder':'glue','jet':'glue','pacoca':'pacoca','stuffed':'pacoca',
             'crumb':'pacoca','token':'token','air':'air','shoot_style':'lightning',
             'flask':'chemical','bullet':'bullet','hostile':'bullet','card':'cards',
             'air_bullet':'air','flame':'flame','gravity':'gravity','laser':'lightning',
             'boomerang':'slash','note':'note','holden_bullet':'bullet'}
EFFECTS={'punch':'punch','uppercut':'punch','slash':'slash','musashi_slash':'slash',
         'death_line':'slash','lightning':'lightning','chemical':'chemical','flame':'flame',
         'crystal':'crystal','vortex':'gravity','paper':'cards','cards':'cards','seal':'resonance',
         'soul_aura':'aura','spill':'spill','nuclear':'nuclear','stomp':'stomp',
         'spark':'spark','muzzle':'bullet','blast':'nuclear','impact':'spark','crumb_blast':'crumb_blast','swarm':'swarm','resonance':'resonance'}

EFFECTS.update(joe_counter='punch',joe_jab='punch',counter='punch',dagger_cut='slash',deflect='slash',rifle_flash='bullet',vinland_aura='aura',joe_guard='aura',dominion='aura',vortex='vortex',spill='glue',crumb_blast='pacoca')

class ArtVFX:
    def __init__(self,path=None):
        self.images={};self.sequences={};self.cache=OrderedDict();self.max_cache=320
        default=path is None
        path=path or BASE_DIR/'assets/art/combat_fx_atlas.png'
        self.load_sheet(path,BASE_FX,4,4)
        if default:
            self.load_sheet(BASE_DIR/'assets/art/impact_fx_atlas.png',IMPACT_FX,4,2)
            self.load_sequences(BASE_DIR/'assets/art/animated_fx.png')
            self.load_sheet(BASE_DIR/'assets/art/ultimate_signatures.png',ULTIMATE_FX,4,7)
    def load_sheet(self,path,names,cols,rows):
        if not path.exists():return
        try:sheet=pg.image.load(str(path)).convert_alpha()
        except (pg.error,OSError):return
        w,h=sheet.get_size();cw,ch=w//cols,h//rows
        for i,name in enumerate(names):
            cell=sheet.subsurface((i%cols*cw,i//cols*ch,cw,ch)).copy()
            box=cell.get_bounding_rect(min_alpha=32)
            if box.width and box.height:
                src=cell.subsurface(box).copy()
                target=80;self.images[name]=pg.transform.scale(src,(target,max(1,round(src.get_height()*target/src.get_width()))))
    def load_sequences(self,path):
        if not path.exists():return
        try:sheet=pg.image.load(str(path)).convert_alpha()
        except (pg.error,OSError):return
        w,h=sheet.get_size()
        for row,name in enumerate(SEQUENCE_NAMES):
            frames=[]
            for col in range(4):
                a,b=round(col*w/4),round((col+1)*w/4);c,d=round(row*h/12),round((row+1)*h/12)
                cell=sheet.subsurface((a,c,b-a,d-c)).copy()
                frames.append(pg.transform.scale(cell,(80,max(1,round(cell.get_height()*80/cell.get_width())))))
            self.sequences[name]=frames
    def stamp(self,layer,name,point,width,angle=0,alpha=220,tint=None,frame=None):
        if name not in self.images and name not in self.sequences:return False
        width=max(4,min(144,round(width/4)*4));angle=round(angle/30)*30%360
        key=(name,width,angle,tint,frame)
        im=self.cache.get(key)
        if im is None:
            src=self.sequences[name][frame if frame is not None else 1] if name in self.sequences else self.images[name];height=max(1,round(src.get_height()*width/src.get_width()))
            im=pg.transform.scale(src,(width,height))
            if tint:
                im.fill((*tint,255),special_flags=pg.BLEND_RGBA_MULT)
            if angle:im=pg.transform.rotate(im,angle)
            self.cache[key]=im
            if len(self.cache)>self.max_cache:self.cache.popitem(last=False)
        else:self.cache.move_to_end(key)
        im.set_alpha(max(0,min(255,int(alpha))))
        layer.blit(im,im.get_rect(center=(round(point[0]),round(point[1]))))
        return True
    def projectile(self,fx,q,pos,time):
        name=PROJECTILES.get(q.kind)
        if name is None:return False
        a=V(fx.point(pos));d=q.vel.normalize() if q.vel.length_squared() else V(1,0)
        if not(-40<a.x<360 and -40<a.y<220):return True
        width=7 if q.kind=='crumb' else 13 if q.hostile else 18 if q.kind in ('stuffed','bonder','shoot_style') else 14
        # Short, low-opacity trail, never larger than the actual leading sprite.
        if fx.quality!='low':
            self.stamp(fx.layer,name,a-d*5,width*.65,-d.as_polar()[1],65)
        angle=-d.as_polar()[1]
        if name in ('token','vortex','gravity','cards'):angle=time*180
        tint=(255,90,120) if q.hostile else None
        return self.stamp(fx.layer,name,a,width,angle,245,tint)
    def effect(self,fx,e,xy,time):
        name=getattr(e,'art','') or (e.kind if e.kind.startswith('ultimate_') else EFFECTS.get(e.kind))
        if name is None:return False
        a=V(fx.point(xy(e.pos)));b=V(fx.point(xy(e.end)))
        progress=max(0,min(1,1-e.life/max(.001,e.duration)))
        directional=e.kind in ('punch','uppercut','slash','musashi_slash','death_line','lightning','crystal','muzzle','joe_jab','counter','dagger_cut','deflect','rifle_flash')
        delta=b-a;distance=delta.length();angle=-delta.as_polar()[1] if distance>.1 else 0
        point=a.lerp(b,.55+progress*.18) if directional else a
        width=max(18,min(112,distance*(.65+progress*.2))) if directional else max(20,min(128,e.radius/2*(.7+progress*.3)))
        if e.kind=='spark':width=12+progress*7
        if e.kind in ('vortex','cards','seal','soul_aura'):angle=time*(45 if e.kind=='vortex' else 12)
        alpha=int((215 if width<65 else 155)*(1-progress)**.65)
        tint=(245,140,170) if e.kind=='death_line' else None
        if not(-150<point.x<470 and -150<point.y<330):return True
        return self.stamp(fx.layer,name,point,width,angle,alpha,tint,min(3,int(progress*4)) if name in self.sequences else None)

def terrain(key):
    """Load a generated floor tile; caller builds and caches the full world once."""
    path=BASE_DIR/'assets/art/terrain_atlas.png'
    if key not in ('city','ring','walls','fog') or not path.exists():return None
    try:sheet=pg.image.load(str(path)).convert()
    except (pg.error,OSError):return None
    i=('city','ring','walls','fog').index(key);w,h=sheet.get_size();cw,ch=w//2,h//2
    cell=sheet.subsurface((i%2*cw,i//2*ch,cw,ch))
    # One world pixel cluster = 3 screen pixels. Characters stay smooth and untouched.
    return pg.transform.scale(pg.transform.scale(cell,(300,300)),(900,900))
