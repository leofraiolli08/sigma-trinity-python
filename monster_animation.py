"""Normalized authored poses: walk, windup, attack, hit and defeat."""
import logging
import statistics
import pygame as pg
THEMES=('crypt','usj','city','ring','walls','fog')
def load(root):
 images={};sizes={};status={}
 for theme in THEMES:
  path=root/'art'/f'{theme}_animation.png';status[theme]='fallback'
  if not path.exists():continue
  try:
   sheet=pg.image.load(str(path)).convert_alpha();sw,sh=sheet.get_size()
   for row in range(7):
    cells=[]
    for col in range(8):
     a,b=round(col*sw/8),round((col+1)*sw/8);c,d=round(row*sh/7),round((row+1)*sh/7)
     cell=sheet.subsurface((a,c,b-a,d-c)).copy();components=pg.mask.from_surface(cell,24).connected_components(25)
     if not components:raise ValueError(f'Quadro vazio {row}/{col}')
     body=max(components,key=lambda m:m.count());cell.blit(body.to_surface(setcolor=(255,255,255,255),unsetcolor=(0,0,0,0)),(0,0),special_flags=pg.BLEND_RGBA_MULT);cells.append(cell)
    boxes=[c.get_bounding_rect(min_alpha=24) for c in cells];height=100 if row==6 else 68 if theme=='walls' else 48 if row==4 else 57
    factor=height/statistics.median(b.height for b in boxes[:3]);width=round(max(c.get_width() for c in cells)*factor)+4;h=round(max(b.height for b in boxes)*factor)+6
    for col,(cell,box) in enumerate(zip(cells,boxes)):
     size=(max(1,round(cell.get_width()*factor)),max(1,round(cell.get_height()*factor)));frame=pg.Surface((width,h),pg.SRCALPHA)
     frame.blit(pg.transform.scale(cell,size),((width-size[0])//2,h-3-round(box.bottom*factor)))
     name=f'{theme}_anim_{row}_{col}';images[name]=frame;sizes[name]=frame.get_size()
   status[theme]='animated'
  except (pg.error,OSError,ValueError) as exc:logging.warning('Animação %s: %s',theme,exc)
 # A dedicated sheet keeps the titan's fists and feet outside neighboring cells.
 path=root/'art'/'titan_boss_v10.png'
 if path.exists():
  try:
   from authored_atlas import poses
   rows=poses(pg.image.load(str(path)).convert_alpha(),2,4,[100,100],group_rows=2)
   authored=rows[0][:3]+rows[1][:2]+[rows[0][3],rows[1][2],rows[1][3]]
   # Keep defeat at the same body scale as walk rather than enlarging a crouch.
   for col,frame in enumerate(authored):
    name=f'walls_anim_6_{col}';images[name]=frame;sizes[name]=frame.get_size()
  except (pg.error,OSError,ValueError) as exc:logging.warning('Chefe titã: %s',exc)
 return images,sizes,status
def sprite_name(e,time,theme):
 if getattr(e,'trial_key',None):return 'portrait_'+e.trial_key+'_form'
 frame=6 if e.hit>0 else 3 if e.windup_left>0 else (4 if e.attack_left>.15 else 5) if e.attack_left>0 else int(time*8+e.uid)%3 if e.walking else 1
 return f'{theme}_anim_{6 if e.boss else e.kind}_{frame}'
def export_frames(root,images):
 folder=root/'sprites'/'enemies';folder.mkdir(parents=True,exist_ok=True)
 for name,frame in images.items():
  path=folder/(name+'.png')
  try:
   if path.exists():
    old=pg.image.load(str(path))
    if old.get_size()==frame.get_size() and pg.image.tobytes(old,'RGBA')==pg.image.tobytes(frame,'RGBA'):continue
   pg.image.save(frame,str(path))
  except (OSError,pg.error) as exc:logging.warning('Quadro %s apenas em memória: %s',name,exc)
