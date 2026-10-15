"""High-resolution art overlay; animation is cached at load time.
PNG originals retain their alpha. Missing art leaves the procedural fallback usable.
"""
import math
import logging
import pygame as pg


def trim(s):
    box=s.get_bounding_rect(min_alpha=8)
    return s.subsurface(box).copy() if box.width and box.height else s


def fit(s,box):
    factor=min(box[0]/s.get_width(),box[1]/s.get_height())
    return pg.transform.smoothscale(s,(max(1,round(s.get_width()*factor)),max(1,round(s.get_height()*factor))))


def animate(s,index,total=6,mode='idle'):
    # Runtime paper-puppet animation; the reference's facial pixels are not regenerated.
    phase=index*math.tau/total
    angle=math.sin(phase)*(7 if mode=='dance' else 2 if mode=='walk' else .6)
    scale_y=1-(.03*(1+math.cos(phase)) if mode=='dance' else .015*abs(math.sin(phase)))
    im=pg.transform.smoothscale(s,(s.get_width(),int(s.get_height()*scale_y)))
    im=pg.transform.rotozoom(im,angle,1)
    canvas=pg.Surface((int(s.get_width()*1.22),int(s.get_height()*1.1)),pg.SRCALPHA)
    foot=canvas.get_height()-int(abs(math.sin(phase))*s.get_height()*(.032 if mode=='dance' else .012))
    canvas.blit(im,im.get_rect(midbottom=(canvas.get_width()//2,foot)))
    return canvas


def load_art(root):
    art=root/'art'; images={}; logical={}; sources={}
    for key in ('leo','rafael','leozauxta','guxta','guxta_form','leo_form','rafael_form','leozauxta_form','floor','enemies'):
        path=art/(key+'.png')
        if not path.exists(): continue
        try: sources[key]=pg.image.load(str(path)).convert_alpha()
        except (OSError,pg.error) as exc: logging.warning('Arte ausente/inválida: %s: %s',key,exc)
    atlas=art/'davi_atlas.png'
    if atlas.exists():
        try:
            sheet=pg.image.load(str(atlas)).convert_alpha(); w,h=sheet.get_size()
            sources['davi']=sheet.subsurface((0,0,w//2,h)).copy()
            sources['davi_form']=sheet.subsurface((w//2,0,w-w//2,h)).copy()
        except (OSError,pg.error) as exc: logging.warning('Arte Davi inválida: %s',exc)
    def put(name,s,size): images[name]=s; logical[name]=size
    for key in ('leo','rafael','leozauxta','davi','guxta'):
        if key not in sources: continue
        src=trim(sources[key]); src=fit(src,(520,700)); width=src.get_width()/src.get_height()
        h=87 if key!='leozauxta' else 105; w=round(h*width)
        put('portrait_'+key,src,(w,h))
        for i in range(4):
            frame=animate(src,i,4,'walk'); name=f'{key}_walk_{i}' if key!='leozauxta' else f'leozauxta_{i}'
            put(name,frame,(int(w*1.22),int(h*1.1)))
        for i in range(2): put(f'{key}_idle_{i}',animate(src,i,2),(int(w*1.22),int(h*1.1)))
        for pose in ('attack','dash','transform','idle','walk'): put(f'{key}_{pose}',animate(src,1,4,'walk'),(int(w*1.22),int(h*1.1)))
    for key,prefix,count,h in [('leo','leo_calvo',4,100),('rafael','pacoca',4,95),('leozauxta','titan',6,140),('davi','full_cowl',4,108),('guxta','red_moon',4,112)]:
        if key+'_form' not in sources: continue
        src=fit(trim(sources[key+'_form']),(600,760)); w=round(h*src.get_width()/src.get_height())
        put('portrait_'+key+'_form',src,(w,h))
        for i in range(count): put(f'{prefix}_{i}',animate(src,i,count,'dance' if key=='leozauxta' else 'walk'),(int(w*1.22),int(h*1.1)))
        for pose in ('idle','attack','walk'): put(prefix+'_'+pose,animate(src,0),(int(w*1.22),int(h*1.1)))
    for key in ('ippo','eren','klein','musashi'):
        path=art/(key+'_atlas.png')
        if not path.exists():continue
        try:
            sheet=pg.image.load(str(path)).convert_alpha();sw,sh=sheet.get_size()
            for stage in range(4):
                cell=sheet.subsurface(((stage%2)*(sw//2),(stage//2)*(sh//2),sw//2,sh//2)).copy()
                # Remove detached fragments from neighboring atlas cells.
                bodies=pg.mask.from_surface(cell,8).connected_components(80)
                if bodies:
                    body=max(bodies,key=lambda m:m.count())
                    matte=body.to_surface(setcolor=(255,255,255,255),unsetcolor=(0,0,0,0))
                    cell.blit(matte,(0,0),special_flags=pg.BLEND_RGBA_MULT)
                src=fit(trim(cell),(420,650));h=125 if key in ('eren','musashi') and stage>=2 else 102 if key=='musashi' else 88
                w=round(h*src.get_width()/src.get_height())
                for i in range(4):put(f'{key}_stage{stage}_{i}',animate(src,i,4,'walk'),(int(w*1.22),int(h*1.1)))
                if stage in (0,2) or (key=='musashi' and stage==3):put('portrait_'+key+('_form' if stage else ''),src,(w,h))
                sources[f'{key}_stage{stage}']=src
        except (OSError,pg.error) as exc:logging.warning('Atlas %s indisponível: %s',key,exc)
    for key in ('zatex','leozauxtaci'):
        path=art/(key+'_atlas.png')
        if not path.exists():continue
        sheet=pg.image.load(str(path)).convert_alpha();sw,sh=sheet.get_size()
        for stage,group in enumerate(('base','form')):
            src=fit(trim(sheet.subsurface((stage*(sw//2),0,sw//2,sh)).copy()),(420,650))
            sources[key+('_form' if stage else '')]=src
            h=(125 if key=='leozauxtaci' else 95)+(10 if stage else 0);w=round(h*src.get_width()/src.get_height())
            put('portrait_'+key+('_form' if stage else ''),src,(w,h))
            for i in range(4):put(f'{key}_{group}_{i}',animate(src,i,4,'walk'),(int(w*1.22),int(h*1.1)))
    return images,logical,sources
