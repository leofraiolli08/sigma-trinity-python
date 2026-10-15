"""Short, individually choreographed cinematics; no combat randomness or video dependency."""
import math
import pygame as pg
from entities import V
from settings import BASE_DIR,CHARACTERS,INK,GOLD,MUTED

PROFILES={
 'leo':('CALVO ABSOLUTO','O GRANDE DERRAMAMENTO','spill','rain'),
 'rafael':('PAÇOCA ASCENDIDA','PAÇOCA NUCLEAR','crumb_blast','meteor'),
 'leozauxta':('TITÃ SIGMA TRÍPLICE','TRIPLE SIGMA DANCE','swarm','dance'),
 'davi':('FULL COWL','COALA SMASH • 100%','lightning','impact'),
 'walter':('TRAJE HAZMAT','REAÇÃO EM CADEIA','chemical','chain'),
 'guxta':('LUA VERMELHA','COLAPSO GRAVITACIONAL','gravity','collapse'),
 'ippo':('PEEK-A-BOO','DEMPSEY ROLL','punch','boxing'),
 'eren':('TITÃ DE ATAQUE','ASSALTO DO TITÃ','stomp','titan'),
 'klein':('O VÉU SEM ROSTO','FIOS ESPIRITUAIS','cards','puppet'),
 'zatex':('MAESTRO DO VÉU','SINFONIA DO VÉU','resonance','symphony'),
 'leozauxtaci':('CONVERGÊNCIA FINAL','QUATRO ASSINATURAS','aura','convergence'),
 'musashi':('MUSHIN','DOIS CÉUS • UM CORTE','slash','iaido'),
 'joe':('ESPÍRITO DE LUTA','ÚLTIMO ROUND','punch','counter'),
 'thorfinn':('VINLAND','NÃO TENHO INIMIGOS','aura','vinland'),
 'holden':('A DANÇA DO JUIZ','MERIDIANO DE SANGUE','bullet','salvo'),
}

class Cinematic:
    def __init__(self,key,kind='transform',sprite=None,stage=0,evolved=False,pid=0):
        self.key=key;self.kind=kind;self.sprite=sprite or 'portrait_'+key+'_form'
        self.stage=stage;self.evolved=evolved;self.pid=pid;self.age=0.;self.duration=6.5 if kind=='fusion' else 3.2 if kind=='trial' else 1.65 if kind=='ultimate' else 1.8
    @classmethod
    def player(cls,p,kind):
        c=cls(p.key,kind,p.sprite(0),p.stage,p.evolved,p.pid)
        from evolution_kit import stage_of
        c.stage=stage_of(p) if p.key=='walter' else p.stage
        token=f'{p.key}:{kind}:{c.stage}'
        if p.short_cinema and token in p.clip_seen:c.duration=.6
        p.clip_seen.add(token)
        return c
    def update(self,dt):self.age=min(self.duration,self.age+max(0,dt));return self.age>=self.duration
    def wire(self):return {k:getattr(self,k) for k in ('key','kind','sprite','stage','evolved','pid','age','duration')}
    @classmethod
    def read(cls,data):
        if not isinstance(data,dict) or data.get('key') not in CHARACTERS or data.get('kind') not in ('fusion','trial','transform','ultimate'):raise ValueError('Cutscene inválida')
        if type(data.get('stage')) is not int or not 0<=data['stage']<=3 or type(data.get('pid')) is not int or not 0<=data['pid']<4 or type(data.get('evolved')) is not bool:raise ValueError('Personagem da cutscene inválido')
        if not isinstance(data.get('sprite'),str) or len(data['sprite'])>96 or type(data.get('age')) not in (int,float) or not math.isfinite(data['age']) or data['age']<0:raise ValueError('Quadro da cutscene inválido')
        c=cls(data['key'],data['kind'],data['sprite'],data['stage'],data['evolved'],data['pid']);duration=data.get('duration')
        if type(duration) not in (int,float) or not math.isfinite(duration) or not .4<=duration<=6.5:raise ValueError('Duração de cutscene inválida')
        c.duration=duration;c.age=min(c.duration,data['age']);return c
    def title(self):
        if self.kind=='fusion':return 'LEOZAUXTACI COALA'
        if self.kind=='trial':return 'LEOZAUXTA • O DESAFIO'
        from evolution_kit import STAGES
        if self.key in STAGES:
            stage=int(self.evolved) if self.key in ('ippo','eren','walter') else self.stage
            return STAGES[self.key][stage][self.kind=='ultimate']
        title=PROFILES[self.key][self.kind=='ultimate']
        if self.key=='walter' and self.evolved:title='FELINA' if self.kind=='transform' else 'ÚLTIMO PLANO'
        if self.key=='ippo' and self.kind=='ultimate' and not self.evolved:title='GAZELLE PUNCH'
        if self.key=='klein' and self.kind=='ultimate' and self.stage<2:title='TRUQUE FINAL'
        if self.key=='musashi' and self.kind=='transform':title=('INSTINTO','CAMINHO DA ESPADA','CAMINHO DA MORTE','CAMINHO DA ALMA')[self.stage]
        return title

class CinematicRenderer:
    def __init__(self):
        self.backgrounds=[];self.layer=pg.Surface((1280,720),pg.SRCALPHA)
        path=BASE_DIR/'assets/art/cinematic_atlas.png'
        if path.exists():
            sheet=pg.image.load(str(path)).convert();w,h=sheet.get_size()
            for i in range(3):
                image=sheet.subsurface((i*w//3,0,(i+1)*w//3-i*w//3,h))
                factor=max(1280/image.get_width(),720/image.get_height());image=pg.transform.scale(image,(round(image.get_width()*factor),round(image.get_height()*factor)))
                self.backgrounds.append(image.subsurface(image.get_rect().inflate(0,0).clip(pg.Rect((image.get_width()-1280)//2,(image.get_height()-720)//2,1280,720))).copy())
    def actor(self,r,name,x,y,height,alpha=255,flip=False):
        if name not in r.a.images:return
        im=r.a.images[name];scale=height/im.get_height()
        resize=pg.transform.scale if name in r.a.pixel_names or name.startswith(('walter','hazmat','heisenberg','felina','portrait_walter','portrait_heisenberg','portrait_felina')) else pg.transform.smoothscale
        im=resize(im,(max(1,round(im.get_width()*scale)),max(1,round(height))))
        if flip:im=pg.transform.flip(im,True,False)
        im.set_alpha(int(max(0,min(255,alpha))));r.canvas.blit(im,im.get_rect(midbottom=(round(x),round(y))))
    def draw(self,r,c,options=None):
        t=c.age;u=t/c.duration;color=CHARACTERS[c.key]['color'];motif,pattern=PROFILES[c.key][2:]
        from evolution_kit import STAGES,signature
        if c.key in STAGES:
            stage=int(c.evolved) if c.key in ('ippo','eren','walter') else c.stage
            motif,pattern=STAGES[c.key][stage][2:]
        bg=1 if c.kind=='fusion' else 2 if c.key in ('musashi','klein','zatex') else 0
        if self.backgrounds:r.canvas.blit(self.backgrounds[bg],(0,0))
        else:r.canvas.fill((10,14,22))
        self.layer.fill((2,6,14,110));r.canvas.blit(self.layer,(0,0))
        r.fx.begin()
        if c.kind=='fusion':
            merge=max(0,min(1,(t-1.5)/2.5));ease=merge*merge*(3-2*merge)
            if t<4.:
                self.actor(r,'portrait_leozauxta_form',335+305*ease,590,300,255*(1-merge*.5))
                self.actor(r,'portrait_davi_form',945-305*ease,590,320,255*(1-merge*.5),True)
                r.fx.art.stamp(r.fx.layer,'lightning',(235-75*ease,93),90+merge*40,t*100,245)
                r.fx.art.stamp(r.fx.layer,'swarm',(85+75*ease,93),80+merge*40,-t*75,240)
            else:self.actor(r,'portrait_leozauxtaci_form',640,595,320+min(1,(t-4)/.7)*65)
            # Fractures open, blocks lift, then collapse into the converging figures.
            for i in range(18):
                d=V(1,0).rotate(i*137);start=V(640,470)+d*(90+ease*500)
                pg.draw.line(r.canvas,(*color,),V(640,470),start,3)
                debris=start+V(math.sin(t*3+i)*18,-max(0,t-1)*25)
                pg.draw.polygon(r.canvas,(46+i%3*9,43,58),[debris+V(-18,0),debris+V(7,-24),debris+V(25,7),debris+V(0,20)])
                pg.draw.line(r.canvas,GOLD,debris+V(-18,0),debris+V(7,-24),2)
            r.fx.art.stamp(r.fx.layer,'aura',(160,112),max(30,130*math.sin(min(1,u)*math.pi)),t*50,210)
            subtitle='DUAS FORÇAS RASGAM A ARENA' if t<2 else 'O CENÁRIO NÃO SUPORTA A CONVERGÊNCIA' if t<4 else 'DERROTE A FUSÃO PARA REVELAR SUA ASSINATURA'
        else:
            ultimate=c.kind=='ultimate';progress=max(0,min(1,u*1.7));center=V(160,107)
            portrait='portrait_'+c.key+'_form' if c.kind=='trial' else c.sprite
            if c.key in ('musashi','walter') or c.key in ('ippo','eren','klein') and c.evolved:portrait=c.sprite
            slide=(1-(1-min(1,u*3))**3)
            x=640+(1-slide)*(350 if ultimate else -350)
            if pattern=='dance':x+=math.sin(t*12)*42
            if pattern=='counter':x+=math.sin(t*18)*45*(1-u)
            if pattern=='vinland':x+=math.sin(t*3)*12
            if pattern=='salvo':x+=math.sin(t*9)*18
            if pattern=='boxing' and ultimate:x+=math.sin(t*24)*80
            if pattern=='titan':height=210+min(1,u*2)*190
            else:height=320+progress*30
            self.actor(r,portrait,x,610,height)
            if not ultimate and c.kind!='trial' and u<.55:
                self.actor(r,'portrait_'+c.key,x,610,height,255*(1-u/.55))
            if pattern=='rain':
                for i in range(9):r.fx.art.stamp(r.fx.layer,motif,(30+i*33,(t*75+i*31)%165),35,-20,190)
            elif pattern=='meteor':
                for i in range(6):r.fx.art.stamp(r.fx.layer,motif,(35+i*48,35+(t*70+i*12)%105),35+progress*10,t*70,210)
            elif pattern=='dance':
                for i in range(4):r.fx.art.stamp(r.fx.layer,'swarm',(160+math.cos(t*4+i)*90,95+math.sin(t*4+i)*40),48,t*90+i*90,220)
            elif pattern=='impact':
                for i in range(5):r.fx.art.stamp(r.fx.layer,motif,(85+i*39,85+math.sin(t*14+i)*15),54,-i*40,220)
            elif pattern=='chain':
                for i in range(5):r.fx.art.stamp(r.fx.layer,'bullet' if c.evolved else 'chemical',(50+i*55,132-i*10),36+progress*12,-t*25,220)
            elif pattern=='collapse':
                radius=(1-progress)*105+30
                for i in range(8):r.fx.art.stamp(r.fx.layer,motif,center+V(radius,0).rotate(i*45+t*60),31,t*45,210)
            elif pattern=='counter':
                for i in range(5):r.fx.art.stamp(r.fx.layer,'punch',(76+i*40,98+math.sin(t*20+i)*18),34+i%2*10,180 if i%2 else 0,220)
            elif pattern=='vinland':
                for i in range(8):r.fx.art.stamp(r.fx.layer,'aura',center+V(70,0).rotate(i*45+t*28),25,0,150)
            elif pattern=='salvo':
                for i in range(7):r.fx.art.stamp(r.fx.layer,'bullet',(40+i*38,75+i%3*24),26,-12+i*4,220)
            elif pattern=='boxing':
                for i in range(6):r.fx.art.stamp(r.fx.layer,'punch',(75+i*34,100+math.sin(t*24+i)*25),36+i%2*10,180 if i%2 else 0,225)
            elif pattern=='titan':
                for i in range(5):r.fx.art.stamp(r.fx.layer,'crystal' if c.evolved else 'stomp',(60+i*50,140),50,0,215)
            elif pattern=='puppet':
                for i in range(9):
                    pg.draw.line(r.fx.layer,(*color,170),(160,28),(55+i*27,140),1)
                    r.fx.art.stamp(r.fx.layer,motif,(55+i*27,140),17,t*90,240)
            elif pattern=='symphony':
                for i in range(6):r.fx.art.stamp(r.fx.layer,'note' if ultimate else 'resonance',center+V(60+10*i,0).rotate(i*60+t*45),32,t*35,215)
            elif pattern=='convergence':
                for i,name in enumerate(('glue','gravity','resonance','lightning')):r.fx.art.stamp(r.fx.layer,name,center+V(70,0).rotate(i*90+t*70),55,t*30,220)
            else:
                # Musashi: a held silhouette, ink streaks, then a single decisive cut.
                for i in range(2+c.stage):r.fx.art.stamp(r.fx.layer,'slash',(90+i*38,95+(i%2)*30),80,(-20 if ultimate else 50)+i*25,220)
                if c.stage==3:r.fx.art.stamp(r.fx.layer,'aura',center,100,t*25,145)
            emblem=signature(c.key,stage) if c.key in STAGES and c.key!='walter' else motif
            r.fx.art.stamp(r.fx.layer,emblem,center,65+progress*50,0,170 if ultimate else 100)
            subtitle='O DESAFIO COMEÇA • ENFRENTE A ASSINATURA' if c.kind=='trial' else ('ASSINATURA • '+CHARACTERS[c.key]['name']) if ultimate else 'AURA EM ASCENSÃO • '+CHARACTERS[c.key]['name']
        r.fx.present(r.canvas)
        flash=abs(t-3.85)<.1 if c.kind=='fusion' else abs(u-.55)<.035
        if flash and (options or {}).get('flashes',True):
            self.layer.fill((*color,170));r.canvas.blit(self.layer,(0,0))
        pg.draw.rect(r.canvas,(4,7,12),(0,0,1280,74));pg.draw.rect(r.canvas,(4,7,12),(0,625,1280,95))
        r.text(subtitle,640,39,22,color,True)
        r.text(c.title(),640,654,38,INK,True);r.text('ENTER • PULAR',1188,699,16,MUTED,True)
        r.bar(40,715,1200,3,u,color)
