"""Original pixel art, drawn at native resolution; no remote resources."""
import math
import random
import struct
import wave
import logging
import pygame as pg
from art_assets import load_art
from settings import BASE_DIR
OUTLINE = (12, 15, 27)
SKIN = (205, 147, 108)
LIGHT = (242, 192, 145)

def rect(s,c,r): pg.draw.rect(s,c,r)
def head(s,x,y,hair=0,glasses=False,bald=False):
    rect(s,OUTLINE,(x-1,y-1,16,17)); rect(s,SKIN,(x,y,14,15))
    rect(s,LIGHT,(x+2,y+1,10,10)); rect(s,(170,108,83),(x+12,y+5,2,8))
    if not bald:
        colors=[(33,27,31),(54,39,35),(26,23,30)]
        rect(s,colors[hair],(x-1,y-3,16,6))
        for a in range(0,14,3): rect(s,colors[hair],(x+a,y-5+(a%3),3,4+(a%2)))
        if hair==1: pg.draw.polygon(s,colors[hair],[(x,y),(x+14,y),(x+3,y+6)])
    else:
        rect(s,(255,225,182),(x+3,y+1,5,2)); rect(s,(56,31,33),(x+2,y+10,11,3))
        rect(s,(56,31,33),(x+1,y+12,3,2)); rect(s,(56,31,33),(x+11,y+12,3,2))
    if glasses:
        pg.draw.rect(s,OUTLINE,(x,y+5,6,5),1); pg.draw.rect(s,OUTLINE,(x+8,y+5,6,5),1)
        rect(s,OUTLINE,(x+6,y+6,2,1)); rect(s,(178,222,230),(x+1,y+6,2,1))
    else:
        rect(s,OUTLINE,(x+3,y+6,2,2)); rect(s,OUTLINE,(x+10,y+6,2,2))
    if not bald: rect(s,(122,64,65),(x+5,y+12,5,1))

def human(kind,frame=0,bald=False,pose='walk'):
    s=pg.Surface((48,64),pg.SRCALPHA)
    bob=[0,1,0,-1][frame%4]; stride=[-2,0,2,0][frame%4]
    shirt=(31,48,74) if kind=='leo' else ((210,223,239) if kind=='rafael' else (34,33,43))
    pants=(23,28,39) if kind=='leo' else (58,77,100)
    if kind=='member2': shirt=(53,39,38)
    y=22+bob
    rect(s,OUTLINE,(13,y,24,24)); rect(s,shirt,(15,y+1,20,21))
    rect(s,tuple(min(255,c+19) for c in shirt),(17,y+2,5,18))
    rect(s,pants,(16,44+bob,8,14+stride)); rect(s,pants,(27,44+bob,8,14-stride))
    rect(s,(16,19,29),(14,56+bob+stride,10,4)); rect(s,(16,19,29),(27,56+bob-stride,10,4))
    armshift=-6 if pose=='attack' else stride
    rect(s,OUTLINE,(8,y+1,7,17)); rect(s,shirt,(9,y+1,5,7)); rect(s,SKIN,(9,y+8,5,9))
    rect(s,OUTLINE,(35,y+1+armshift,7,18)); rect(s,shirt,(36,y+1+armshift,5,7)); rect(s,LIGHT,(36,y+8+armshift,5,9))
    if kind=='leo':
        pg.draw.lines(s,(174,194,211),False,[(18,y+3),(24,y+11),(30,y+3)],1)
        rect(s,(233,241,244),(23,y+10,3,3)); rect(s,(158,239,239),(36,y+11+armshift,7,8)); rect(s,(62,185,204),(38,y+9+armshift,3,3))
    elif kind=='rafael': rect(s,(217,167,88),(36,y+10+armshift,8,7))
    else: rect(s,(95,235,150),(37,y+12+armshift,5,5))
    head(s,17,8+bob,1 if kind=='member0' else 2 if kind=='member2' else 0,kind=='rafael',bald)
    if pose=='dash': pg.draw.lines(s,(108,231,242),False,[(1,38),(7,38),(3,44),(9,44)],1)
    return s

def pacoca(frame=0):
    s=pg.Surface((56,64),pg.SRCALPHA); y=9+(frame%2)
    rect(s,OUTLINE,(8,y,40,43)); rect(s,(165,104,51),(10,y+2,36,39)); rect(s,(220,169,87),(12,y+3,30,34))
    rect(s,(245,204,125),(13,y+3,27,4))
    for i in range(24):
        x=13+(i*13)%28; yy=y+9+(i*17)%26
        rect(s,[(190,128,63),(245,199,114)][i%2],(x,yy,2,2))
    for x in (14,30): pg.draw.rect(s,OUTLINE,(x,y+12,12,9),2)
    rect(s,OUTLINE,(26,y+15,4,2)); rect(s,OUTLINE,(22,y+27,13,2))
    rect(s,(237,192,121),(3,y+25,6,12)); rect(s,(237,192,121),(47,y+23,6,12))
    for x,st in [(15,frame%3),(34,-frame%3)]: rect(s,OUTLINE,(x,y+41,8,9+st))
    return s

def trio(frame=0):
    s=pg.Surface((92,68),pg.SRCALPHA)
    s.blit(human('member0',frame),(0,5)); s.blit(human('member2',frame+1),(43,2)); s.blit(human('member1',frame),(23,0))
    return s

def titan(frame=0):
    s=pg.Surface((128,136),pg.SRCALPHA); swing=[-5,-2,3,6,2,-3][frame%6]; y=49
    pg.draw.polygon(s,OUTLINE,[(27+swing,y),(100+swing,y),(96,107),(36,107)])
    pg.draw.polygon(s,(47,42,65),[(30+swing,y+3),(97+swing,y+3),(91,103),(40,103)])
    pg.draw.polygon(s,(92,73,119),[(48+swing,52),(67+swing,63),(83+swing,53),(82,90),(48,90)])
    pg.draw.lines(s,(126,245,171),False,[(47+swing,63),(76+swing,63),(55+swing,77),(79+swing,77)],3)
    for x,shift in [(15,swing*2),(98,-swing*2)]:
        rect(s,OUTLINE,(x,y+shift,19,42)); rect(s,(160,114,94),(x+3,y+shift+3,13,35)); rect(s,LIGHT,(x+4,y+shift+31,12,9))
    for x,shift in [(37,swing),(76,-swing)]:
        rect(s,(24,28,46),(x,102,17,23+shift)); rect(s,(165,184,204),(x-3,122+shift,23,7))
    for x,yy,h in [(32+swing,29,1),(57+swing,21,0),(81+swing,30,2)]: head(s,x,yy,h)
    return s

def enemy(kind,frame=0):
    s=pg.Surface((40,48),pg.SRCALPHA); c=[(219,82,126),(119,137,180),(138,204,89),(185,144,72),(158,107,225),(122,140,170)][kind]
    if kind==2:
        pg.draw.ellipse(s,OUTLINE,(4,21,33,23)); pg.draw.ellipse(s,c,(6,23,29,18)); rect(s,(192,247,131),(10,25,8,3))
    elif kind==4:
        pg.draw.polygon(s,c,[(20,23),(3,11+frame*3),(0,29),(11,26),(20,39),(28,26),(39,29),(36,11+frame*3)])
    else:
        rect(s,OUTLINE,(9,18,24,25)); rect(s,c,(11,20,20,20)); rect(s,(30,33,50),(11,39,8,7)); rect(s,(30,33,50),(25,39,8,7))
        rect(s,OUTLINE,(9,4,23,19)); rect(s,c,(11,6,19,15))
        if kind==3: rect(s,(223,191,104),(3,26,9,14))
        if kind==5:
            rect(s,(196,208,222),(30,7,4,30)); rect(s,(182,128,65),(26,33,12,3)); rect(s,(39,42,65),(8,8,26,5))
    for x in (13,24): rect(s,(255,234,211),(x,29 if kind==2 else 15,3,3))
    return s

def boss(frame=0):
    s=pg.Surface((110,132),pg.SRCALPHA)
    pg.draw.polygon(s,(40,28,55),[(54,4),(90,39),(105,120),(55,108),(6,120),(20,39)])
    pg.draw.polygon(s,(98,54,96),[(55,12),(78,45),(84,108),(55,96),(26,108),(33,45)])
    pg.draw.polygon(s,(193,90,151),[(30,43),(13,32),(7,70),(28,61)])
    pg.draw.polygon(s,(193,90,151),[(80,43),(97,32),(103,70),(82,61)])
    rect(s,(20,18,34),(35,21,40,29)); rect(s,(244,112,171),(41,30,10,4)); rect(s,(244,112,171),(59,30,10,4))
    pg.draw.polygon(s,(242,149,210),[(55,53),(65,68),(55,84),(45,68)],2)
    for x in (34,55,76): pg.draw.line(s,(217,116,190),(x,90),(x,112+frame*2),2)
    return s

def attack(kind):
    s=pg.Surface((20,20),pg.SRCALPHA)
    if kind=='glue':
        rect(s,(36,132,163),(7,1,6,5)); rect(s,(176,248,238),(4,6,12,12)); rect(s,(81,191,206),(6,10,8,4))
    elif kind=='crumb' or kind=='pacoca':
        rect(s,(108,70,43),(3,4,14,13)); rect(s,(229,181,98),(4,5,12,10)); rect(s,(251,211,137),(5,6,10,3))
    elif kind=='token':
        pg.draw.polygon(s,(49,138,94),[(10,0),(19,6),(19,14),(10,20),(1,14),(1,6)])
        pg.draw.polygon(s,(141,255,162),[(10,2),(17,7),(17,13),(10,18),(3,13),(3,7)],2)
        pg.draw.lines(s,(214,255,219),False,[(7,6),(13,6),(7,13),(13,13)],2)
    else: pg.draw.circle(s,(249,104,166),(10,10),6); pg.draw.circle(s,(255,206,224),(10,10),3)
    return s

def generated():
    out={}
    for key in ('leo','rafael'):
        for i in range(4): out[f'{key}_walk_{i}']=human(key,i)
        for i in range(2): out[f'{key}_idle_{i}']=human(key,i)
        for pose in ('attack','dash','transform'): out[f'{key}_{pose}']=human(key,0,False,pose)
    for i in range(4):
        out[f'leo_calvo_{i}']=human('leo',i,True)
        out[f'pacoca_{i}']=pacoca(i)
        out[f'leozauxta_{i}']=trio(i)
    for i in range(3): out[f'member_{i}']=human(f'member{i}')
    for i in range(6): out[f'titan_{i}']=titan(i)
    for k in range(6):
        for i in range(2): out[f'enemy_{k}_{i}']=enemy(k,i)
    for i in range(2): out[f'boss_{i}']=boss(i)
    for k in ('glue','pacoca','crumb','token','hostile'): out[f'attack_{k}']=attack(k)
    out['leo_calvo_idle']=human('leo',0,True); out['leo_calvo_attack']=human('leo',0,True,'attack')
    for pose in ('idle','walk','attack'): out[f'pacoca_{pose}']=pacoca(1 if pose=='walk' else 0)
    out['rafael_idle']=human('rafael'); out['rafael_walk']=human('rafael',1)
    for i in range(4):
        out[f'davi_walk_{i}']=human('leo',i)
        out[f'full_cowl_{i}']=human('leo',i,True)
    for i in range(2): out[f'davi_idle_{i}']=human('leo',i)
    for pose in ('attack','dash','transform'): out['davi_'+pose]=human('leo',0,False,pose)
    for i in range(4):
        out[f'guxta_walk_{i}']=human('leo',i)
        out[f'red_moon_{i}']=human('leo',i,True)
    for i in range(2):out[f'guxta_idle_{i}']=human('leo',i)
    for pose in ('attack','dash','transform'):out['guxta_'+pose]=human('leo',0,False,pose)
    for key in ('walter','hazmat','heisenberg','felina'):
        for i in range(2):out[f'{key}_{i}']=human('leo',i)
    for key in ('ippo','eren','klein','musashi','joe','thorfinn','holden'):
        for stage in range(4):
            for frame in range(4):
                image=human('leo',frame,stage>=2);out[f'{key}_stage{stage}_{frame}']=image
                for pose in ('walk','attack'):out[f'{key}_stage{stage}_{pose}_{frame}']=image
    for key in ('zatex','leozauxtaci'):
        for group in ('base','form'):
            for i in range(4):out[f'{key}_{group}_{i}']=trio(i) if key=='leozauxtaci' else human('rafael',i)
    # Emergency offline aliases only; packaged authored sheets override every one.
    from evolution_kit import STAGES
    for key in ('ippo','eren','klein','musashi','joe','thorfinn','holden'):
        for stage in range(len(STAGES[key])):
            for pose in ('walk','attack'):
                for frame in range(4):out[f'{key}_form{stage}_{pose}_{frame}']=out[f'{key}_stage{min(stage,3)}_{pose}_{frame}']
    return out

SOUNDS={'shot':620,'glue':280,'pacoca':440,'token':880,'bats':180,'dash':360,'hit':110,'level':1040,'transform':220,'ultimate':90,'boss':65,'victory':1320,'defeat':140,'punch':145,'blade':1850,'rifle':80,'counter':900,'objective':1240}
class AssetManager:
    def __init__(self, root=BASE_DIR/'assets'):
        self.images={}; self.scaled={}; self.fonts={}; self.sounds={}; self.art_names=set(); self.logical={}; self.sources={}
        self.art_status={}
        self.font_root=root/'fonts'
        for sub in ('sprites/characters','sprites/enemies','sprites/bosses','sprites/attacks','sprites/effects','sprites/ui','sounds'):
            try: (root/sub).mkdir(parents=True,exist_ok=True)
            except OSError as exc: logging.warning('Assets em memória: %s',exc)
        from pixel_characters import load as load_animations,export_frames,KEYS
        animations,animation_sizes,animation_sources,self.animation_status=load_animations(root)
        export_frames(root,animations)
        for name,s in generated().items():
            s=animations.get(name,s)
            category='enemies' if name.startswith('enemy') else 'bosses' if name.startswith('boss') else 'attacks' if name.startswith('attack') else 'characters'
            path=root/'sprites'/category/(name+'.png')
            if path.exists():
                try: s=pg.image.load(str(path))
                except (pg.error,OSError):
                    logging.warning('Sprite inválido regenerado: %s',path)
                    try: pg.image.save(s,str(path))
                    except (pg.error,OSError): pass
            else:
                try: pg.image.save(s,str(path))
                except (pg.error,OSError) as exc: logging.warning('Sprite em memória: %s',exc)
            self.images[name]=s
        art, self.logical, self.sources = load_art(root)
        self.images.update(art); self.art_names=set(art)
        from pixel_style import load_atlas,load_generated
        ua,sizes=load_atlas(root);self.images.update(ua);self.logical.update(sizes)
        self.art_status['usj']='generated' if ua else 'fallback'
        new,sizes=load_generated(root);self.images.update(new);self.logical.update(sizes)
        self.art_status['crypt']='generated' if 'enemy_0_0' in new else 'fallback'
        from monster_art import load
        new,sizes=load(root,self.art_status);self.images.update(new);self.logical.update(sizes)
        new,sizes,sources=animations,animation_sizes,animation_sources
        self.images.update(new);self.logical.update(sizes);self.sources.update(sources)
        self.pixel_names=set(new)
        from pixel_ui import load as load_ui
        icons=load_ui(root);self.images.update(icons);self.pixel_names.update(icons)
        self.logical.update({name:image.get_size() for name,image in icons.items()})
        from monster_animation import load as load_monsters,export_frames as export_monsters
        monsters,monster_sizes,self.monster_animation_status=load_monsters(root)
        export_monsters(root,monsters);self.images.update(monsters);self.logical.update(monster_sizes);self.pixel_names.update(monsters)
        self.art_names.difference_update(new)
        # Keep the old procedural art usable for incomplete development trees.
        # Packaged builds refuse missing/altered sheets during the installation check.
        for key in KEYS:
            for stage in range(4):
                for pose in ('walk','attack'):
                    for frame in range(4):
                        name=f'{key}_stage{stage}_{pose}_{frame}'
                        if name not in self.images:
                            legacy=f'{key}_stage{stage}_{frame}';self.images[name]=self.images[legacy]
                            self.logical[name]=self.logical.get(legacy,self.images[legacy].get_size())
        if 'titan_0' in self.images:
            for lane in range(4):
                for frame in range(6):
                    src=self.images[f'titan_{frame}'];w,h=src.get_size()
                    pose=pg.transform.rotozoom(src,(-9,0,9,0)[lane],1)
                    if lane==1:pose=pg.transform.smoothscale(pose,(pose.get_width(),int(pose.get_height()*.8)))
                    if lane==3:pose=pg.transform.flip(pose,True,False)
                    name=f'dance_{lane}_{frame}';self.images[name]=pose;self.logical[name]=(int(140*pose.get_width()/pose.get_height()),140 if lane!=1 else 115);self.art_names.add(name)
        for name,freq in SOUNDS.items():
            path=root/'sounds'/(name+'.wav')
            try:
                if not path.exists():
                    duration=.10 if name in ('shot','hit','glue','pacoca','token') else .38
                    with wave.open(str(path),'wb') as wav:
                        wav.setparams((1,2,22050,0,'NONE','not compressed'))
                        samples=[]
                        for i in range(int(22050*duration)):
                            t=i/22050; envelope=(1-t/duration)**2
                            value=math.sin(2*math.pi*freq*t*(1+.5*t/duration))*envelope*.22
                            if name in ('punch','blade','rifle','counter','objective'):
                                noise=math.sin(i*12.9898+freq)*math.cos(i*78.233)
                                value=(value*.4+noise*envelope*(.28 if name in ('punch','rifle') else .1))
                            samples.append(struct.pack('<h',int(32767*value)))
                        wav.writeframes(b''.join(samples))
                if pg.mixer.get_init(): self.sounds[name]=pg.mixer.Sound(str(path))
            except (OSError,pg.error,wave.Error) as exc: logging.warning('Som indisponível: %s',exc)
    def sprite(self,name,scale=1):
        key=(name,scale)
        if key not in self.scaled:
            s=self.images[name]; w,h=self.logical.get(name,s.get_size())
            resize=pg.transform.smoothscale if name in self.art_names else pg.transform.scale
            self.scaled[key]=resize(s,(max(1,int(w*scale)),max(1,int(h*scale))))
        return self.scaled[key]
    def font(self,size):
        if size not in self.fonts:
            path=self.font_root/('DejaVuSans-Bold.ttf' if size>=24 else 'DejaVuSans.ttf')
            from pixel_ui import PixelFont
            self.fonts[size]=PixelFont(path,size)
        return self.fonts[size]
    def play(self,name,volume=.5):
        if name in self.sounds and pg.mixer.get_init():
            try:
                self.sounds[name].set_volume(volume); self.sounds[name].play()
            except pg.error as exc:
                logging.warning('Saída de áudio indisponível: %s',exc)
