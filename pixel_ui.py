"""AI bitmap icons and crisp text, shared by gameplay and menus."""
import pygame as pg

SPEC_ORDER=('leo','rafael','leozauxta','davi','walter','guxta','ippo','eren','klein','zatex','leozauxtaci','musashi','joe','thorfinn','holden')
ICONS=('damage','speed','base_hp','armor','crit','rate','range','shots','magnet','regen','cooldown','area','form_power','coin','luck','knives','lightning','seals','drone','boomerang','bell','embers','rerolls','team','control')
SPEC_ROW_EDGES=(0,112,204,303,398,492,591,692,791,891,986,1090,1195,1304,1406,1536)
ALIASES={'power':'damage','health':'base_hp','heal':'regen','haste':'rate','pickup':'magnet','gold':'coin','dash':'speed','sword':'damage','shield':'armor','speed_bonus':'speed','reach':'range','slow_bonus':'control','shards':'shots','bat_power':'spec_leozauxta_1','triple':'spec_leozauxta_0','dance':'spec_leozauxta_1','chemistry':'spec_walter_0','smash_power':'spec_davi_0','whip_power':'spec_davi_1'}

def load(root):
    images={}
    for filename,cols,rows,names in [('spec_icons.png',3,15,tuple(f'spec_{k}_{lane}' for k in SPEC_ORDER for lane in range(3))),('upgrade_icons.png',5,5,ICONS),('signature_icons_v10.png',4,1,('spec_joe_0','spec_joe_1','spec_joe_2','spec_musashi_2'))]:
        path=root/'art'/filename
        if not path.exists():continue
        sheet=pg.image.load(str(path)).convert_alpha();w,h=sheet.get_size()
        for i,name in enumerate(names):
            col,row=i%cols,i//cols
            # The specialization illustrator used a narrower centered icon field.
            a,b=(round((.214+col*.191)*w),round((.214+(col+1)*.191)*w)) if cols==3 else (round(col*w/cols),round((col+1)*w/cols))
            c,d=(round(SPEC_ROW_EDGES[row]*h/1536),round(SPEC_ROW_EDGES[row+1]*h/1536)) if cols==3 else (round(row*h/rows),round((row+1)*h/rows))
            cell=sheet.subsurface((a,c,b-a,d-c)).copy();box=cell.get_bounding_rect(min_alpha=72)
            if box.width and box.height:
                src=cell.subsurface(box);factor=48/max(box.width,box.height)
                target=pg.transform.scale(src,(max(1,round(box.width*factor)),max(1,round(box.height*factor))))
                canvas=pg.Surface((56,56),pg.SRCALPHA);canvas.blit(target,target.get_rect(center=(28,28)))
                images['ui_'+name]=canvas
    for alias,name in ALIASES.items():
        if 'ui_'+name in images:images['ui_'+alias]=images['ui_'+name]
    return images

class PixelFont:
    """Rasterize once at half size, then nearest-neighbor upscale; keep layout metrics."""
    def __init__(self,path,size):
        self.font=pg.font.Font(str(path) if path.exists() else None,max(6,round(size*.73/2)))
    def render(self,text,antialias,color,background=None):
        image=self.font.render(text,False,color,background)
        return pg.transform.scale(image,(image.get_width()*2,image.get_height()*2))
    def size(self,text):return tuple(v*2 for v in self.font.size(text))
    def metrics(self,text):return self.font.metrics(text)
    def get_height(self):return self.font.get_height()*2
    def get_linesize(self):return self.font.get_linesize()*2
