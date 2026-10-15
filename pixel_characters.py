"""AI-authored base poses and independent animation sheets for each evolved form."""
import logging
import statistics
import pygame as pg
from authored_atlas import poses
KEYS=('ippo','eren','klein','musashi','joe','thorfinn','holden')
ATTACK_DURATION=.28

def export_frames(root,images):
    folder=root/'sprites'/'characters'
    for name,frame in images.items():
        path=folder/(name+'.png')
        try:
            if path.exists():
                cached=pg.image.load(str(path))
                if cached.get_size()==frame.get_size() and pg.image.tobytes(cached,'RGBA')==pg.image.tobytes(frame,'RGBA'):continue
            folder.mkdir(parents=True,exist_ok=True);pg.image.save(frame,str(path))
        except (pg.error,OSError) as exc:logging.warning('Quadro %s disponível somente em memória: %s',name,exc)

def stage_for(player):
    # Legacy base sheet rows remain stable for saves, gallery and tests.
    if player.key in ('joe','thorfinn','holden'):return 3 if player.transformed else player.stage
    if player.key=='musashi':return player.stage
    if player.key=='klein':
        if player.stage>=2:return 3
        return 2 if player.transformed else player.stage
    return 2+int(player.evolved) if player.transformed else int(player.evolved)

def sprite_name(player,time):
    prefix=f'{player.key}_stage{stage_for(player)}'
    if player.transformed:
        from evolution_kit import stage_of
        prefix=f'{player.key}_form{stage_of(player)}'
    left=getattr(player,'attack_animation_left',0.)
    if left>0:
        frame=min(3,max(0,int((ATTACK_DURATION-left)/ATTACK_DURATION*4)))
        return f'{prefix}_attack_{frame}'
    frame=int(time*10)%4 if player.walking or player.dash_left>0 else 1
    return f'{prefix}_walk_{frame}'

def legacy_rows(sheet,key):
    sw,sh=sheet.get_size();rows=[]
    for stage in range(4):
        cells=[]
        for col in range(8):
            x0,x1=round(col*sw/8),round((col+1)*sw/8);y0,y1=round(stage*sh/4),round((stage+1)*sh/4)
            cell=sheet.subsurface((x0,y0,x1-x0,y1-y0)).copy()
            bodies=pg.mask.from_surface(cell,24).connected_components(40)
            if not bodies:raise ValueError(f'Quadro vazio: {stage}/{col}')
            body=max(bodies,key=lambda mask:mask.count())
            cell.blit(body.to_surface(setcolor=(255,255,255,255),unsetcolor=(0,0,0,0)),(0,0),special_flags=pg.BLEND_RGBA_MULT);cells.append(cell)
        boxes=[cell.get_bounding_rect(min_alpha=24) for cell in cells]
        height=76 if key=='eren' and stage>=2 else 54
        factor=height/statistics.median(b.height for b in boxes[:4])
        width=round(max(c.get_width() for c in cells)*factor)+4;h=round(max(b.height for b in boxes)*factor)+6
        frames=[]
        for cell,box in zip(cells,boxes):
            size=(max(1,round(cell.get_width()*factor)),max(1,round(cell.get_height()*factor)))
            frame=pg.Surface((width,h),pg.SRCALPHA);frame.blit(pg.transform.scale(cell,size),((width-size[0])//2,h-3-round(box.bottom*factor)));frames.append(frame)
        rows.append(frames)
    return rows

def wide_rows(sheet,stages,height=54):
    rows=poses(sheet,stages*2,4,[height]*(stages*2),group_rows=2)
    return [rows[i*2]+rows[i*2+1] for i in range(stages)]

def load(root):
    from evolution_kit import STAGES
    images={};logical={};sources={};status={}
    def register(prefix,frames,aliases=False):
        for col,frame in enumerate(frames):
            name=f'{prefix}_{"walk" if col<4 else "attack"}_{col%4}';images[name]=frame;logical[name]=frame.get_size()
            if aliases and col<4:images[f'{prefix}_{col}']=frame;logical[f'{prefix}_{col}']=frame.get_size()
        sources[prefix]=frames[1]
    for key in KEYS:
        status[key]='fallback'
        try:
            sheet=pg.image.load(str(root/'art'/f'{key}_animation.png')).convert_alpha()
            rows=wide_rows(sheet,4) if key=='musashi' else legacy_rows(sheet,key)
            for stage,frames in enumerate(rows):register(f'{key}_stage{stage}',frames,True)
            images['portrait_'+key]=rows[0][1];logical['portrait_'+key]=rows[0][1].get_size()
            status[key]='animated'
        except (pg.error,OSError,ValueError) as exc:logging.warning('Animação %s: %s',key,exc);continue
        try:
            sheet=pg.image.load(str(root/'art'/f'{key}_forms.png')).convert_alpha()
            stages=len(STAGES[key]);height=76 if key=='eren' else 54
            forms=wide_rows(sheet,stages,height) if key in ('musashi','ippo') else poses(sheet,stages,heights=[height]*stages)
            for stage,frames in enumerate(forms):register(f'{key}_form{stage}',frames)
            images['portrait_'+key+'_form']=forms[-1][1];logical['portrait_'+key+'_form']=forms[-1][1].get_size()
        except (pg.error,OSError,ValueError) as exc:logging.warning('Transformações %s: %s',key,exc)
    return images,logical,sources,status
