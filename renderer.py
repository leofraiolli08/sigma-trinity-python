import math
import random
from collections import OrderedDict
import pygame as pg
from maps import make_map
from pixel_style import floor_tile,enemy_sprite,PixelEffects
from entities import V
from settings import WIDTH,HEIGHT,BG,INK,MUTED,CYAN,GOLD,GREEN,PINK,CHARACTERS,RUN_DURATION
from release_info import RELEASE_ID
from boss_patterns import HOSTILE_KINDS

class Renderer:
    @staticmethod
    def actor_flip(name,left):
        # Photos and atlas sprites have different native facing directions.
        native_left=name.startswith(('leo_walk','leo_idle','leo_attack','leo_dash','leo_transform','leo_calvo',
                                     'rafael','pacoca','guxta','red_moon','davi_walk','davi_idle','davi_attack','davi_dash'))
        return bool(left)!=native_left
    def __init__(self,assets):
        self.flashes=True
        self.a=assets; self.canvas=pg.Surface((WIDTH,HEIGHT)); self.tile=self.make_tile()
        self.overlay=pg.Surface((WIDTH,HEIGHT),pg.SRCALPHA)
        self.titles={}; self.vignette=self.make_vignette()
        self.fx=PixelEffects()
        self.map_surface=None; self.map_key=None; self.previews={}
        self.glows={}; self.flipped={}
        self.hit_sprites=OrderedDict()
        self.danger_fields=OrderedDict()
        self.text_cache=OrderedDict();self.preview_masters={};self.ui_dt=1/60
        self.damage_frame=pg.Surface((WIDTH,HEIGHT),pg.SRCALPHA)
        for inset in range(0,36,3):
            pg.draw.rect(self.damage_frame,(190,40,65,max(1,70-inset*2)),(inset,inset,WIDTH-inset*2,HEIGHT-inset*2),3)
        self.menu_back=pg.Surface((WIDTH,HEIGHT)).convert()
        self.menu_back.fill((15,16,23))
        for y in range(0,HEIGHT,32):
            for x in range(0,WIDTH,32):
                tone=(19,19,27) if (x//32+y//32)%2 else (17,18,25)
                pg.draw.rect(self.menu_back,tone,(x,y,30,30))
                pg.draw.rect(self.menu_back,(28,27,35),(x+2,y+2,2,2))
        for radius in (220,310,400):
            points=[V(1110,310)+V(radius,0).rotate(i*45) for i in range(8)]
            pg.draw.polygon(self.menu_back,(43,36,43),points,2)
        for radius in (40,100,180):
            glow=pg.Surface((radius*2,radius*2),pg.SRCALPHA)
            for rr in range(radius,0,-3):
                alpha=int(24*(1-rr/radius)**2)
                pg.draw.circle(glow,(181,114,50,alpha),(radius,radius),rr)
            self.glows[radius]=glow
    def text(self,text,x,y,size=24,color=INK,center=False):
        key=(str(text),size,tuple(color))
        s=self.text_cache.get(key)
        if s is None:
            s=self.a.font(size).render(str(text),True,color);self.text_cache[key]=s
            if len(self.text_cache)>768:self.text_cache.popitem(last=False)
        else:self.text_cache.move_to_end(key)
        r=s.get_rect(center=(x,y)) if center else s.get_rect(topleft=(x,y));self.canvas.blit(s,r);return r
    def title(self,text,x,y,size=48,color=INK,center=False):
        if size not in self.titles: self.titles[size]=pg.font.Font(None,size)
        self.text(text,x,y,size,color,center)
    def panel(self,rect,color=(22,22,24),border=(66,61,53),width=1):
        rect=pg.Rect(rect)
        x,y,w,h=rect;k=min(6,h//4)
        points=[(x+k,y),(x+w-k,y),(x+w-k,y+k),(x+w,y+k),(x+w,y+h-k),(x+w-k,y+h-k),(x+w-k,y+h),(x+k,y+h),(x+k,y+h-k),(x,y+h-k),(x,y+k),(x+k,y+k)]
        pg.draw.polygon(self.canvas,(7,8,15),[(xx,yy+3) for xx,yy in points])
        pg.draw.polygon(self.canvas,color,points);pg.draw.polygon(self.canvas,border,points,1)
        pg.draw.line(self.canvas,tuple(min(255,int(c*.6)+18) for c in border),(x+k+2,y+2),(x+w-k-2,y+2))
        if width>1:
            pg.draw.line(self.canvas,border,(x+k,y),(x+min(66,w-7),y),2)
            pg.draw.line(self.canvas,border,(x+w-min(36,w-7),y+h),(x+w-k,y+h),2)
    def bar(self,x,y,w,h,value,color,back=(37,34,32)):
        pg.draw.rect(self.canvas,back,(x,y,w,h),border_radius=0)
        if value>0:
            fill=max(1,int(w*max(0,min(1,value))));pg.draw.rect(self.canvas,color,(x,y,fill,h),border_radius=0)
            pg.draw.line(self.canvas,tuple(min(255,c+32) for c in color),(x+1,y+1),(x+max(1,fill-2),y+1))
    def make_tile(self):
        return floor_tile()
    def make_vignette(self):
        v=pg.Surface((320,180),pg.SRCALPHA)
        for y in range(180):
            for x in range(320):
                d=((x-160)/175)**2+((y-90)/113)**2
                v.set_at((x,y),(3,4,7,min(100,int(max(0,d-.25)*55))))
        return pg.transform.smoothscale(v,(WIDTH,HEIGHT))
    def floor(self,camera):
        size=self.tile.get_width()
        for gy in range(int(camera.y//size),int((camera.y+HEIGHT)//size)+1):
            for gx in range(int(camera.x//size),int((camera.x+WIDTH)//size)+1):
                self.canvas.blit(self.tile,(round(gx*size-camera.x),round(gy*size-camera.y)))
    def map_preview(self,key,size):
        cache=(key,size)
        if cache not in self.previews:
            if key not in self.preview_masters:
                world=self.map_surface if self.map_key==key else make_map(key,self.tile)
                self.preview_masters[key]=pg.transform.scale(world,(480,480))
            preview=pg.Surface(size);preview.fill((12,17,20))
            side=max(size);image=pg.transform.scale(self.preview_masters[key],(side,side))
            preview.blit(image,((size[0]-side)//2,(size[1]-side)//2));self.previews[cache]=preview
        return self.previews[cache]
    def background(self,t):
        self.canvas.blit(self.menu_back,(0,0))
        pg.draw.line(self.canvas,(62,51,63),(32,47),(1248,47))
        pg.draw.line(self.canvas,GOLD,(32,47),(113,47),2)
        self.text('S I G M A  /  T R I N I T Y',36,22,16,GOLD)
        self.text(f'{RELEASE_ID} / ASCENSÃO',1148,27,16,MUTED,True)
        for i in range(16):
            x=(i*173+int(t*(3+i%3)))%WIDTH;y=(i*79-int(t*(4+i%4)))%HEIGHT
            pg.draw.rect(self.canvas,(103,76,57),(x,y,2,2))
    def logo(self,x,y):
        self.title('SIGMA',x,y,92,INK,True)
        self.title('TRINITY',x,y+84,62,GOLD,True)
        self.text('C H A O S   A S C E N S I O N',x,y+150,20,MUTED,True)
    def sprite(self,name,pos,scale=1,center=True,flip_x=False,hit=False):
        img=self.a.sprite(name,scale)
        if flip_x:
            key=(name,scale)
            if key not in self.flipped: self.flipped[key]=pg.transform.flip(img,True,False)
            img=self.flipped[key]
        if hit:
            key=(name,scale,flip_x)
            if key not in self.hit_sprites:
                white=img.copy();white.fill((65,60,55,0),special_flags=pg.BLEND_RGBA_ADD)
                self.hit_sprites[key]=white
                if len(self.hit_sprites)>96:self.hit_sprites.popitem(last=False)
            img=self.hit_sprites[key]
        r=img.get_rect(midbottom=pos) if center else img.get_rect(topleft=pos); self.canvas.blit(img,r); return r
    def draw_world(self,s,options,hitboxes=False):
        self.fx.quality=options.get('effects','full')
        self.flashes=options.get('flashes',True)
        p=s.player; camera=getattr(p,'render_pos',p.pos)-V(WIDTH/2,HEIGHT/2+35)
        bounds=s.arena.bounds
        camera.x=max(bounds.left-64,min(bounds.right+64-WIDTH,camera.x))
        camera.y=max(bounds.top-220,min(bounds.bottom+100-HEIGHT,camera.y))
        # Render-only deterministic shake cannot change combat RNG or positions.
        if options['shake'] and s.shake>0: camera+=V(math.sin(s.time*117),math.cos(s.time*97))*s.shake*20
        def xy(pos): return (round(pos.x-camera.x),round(pos.y-camera.y))
        if self.map_key!=s.arena.key:
            self.map_surface=make_map(s.arena.key,self.tile); self.map_key=s.arena.key
            if s.arena.key in ('city','ring','walls','fog'):
                # Cache material shading once; busy floor tiles stop competing with actors.
                self.map_surface.fill((198,198,205),special_flags=pg.BLEND_RGB_MULT)
        self.canvas.fill((13,16,19)); self.canvas.blit(self.map_surface,(-int(camera.x),-int(camera.y)))
        if s.arena.key=='crypt':
            # Ruined stone landmarks and candles are decorative, never invisible obstacles.
            origin=xy(V(1800,1800))
            for rad in (238,249,290):
                pg.draw.ellipse(self.canvas,(70,58,43),(origin[0]-rad,origin[1]-rad*.62,rad*2,rad*1.24),2)
            for i in range(12):
                v=V(274,0).rotate(i*30); v.y*=.62; at=(int(origin[0]+v.x),int(origin[1]+v.y))
                pg.draw.line(self.canvas,(82,64,43),(at[0]-3,at[1]-7),(at[0]+3,at[1]+7),2)
            for gy in range(int(camera.y//490),int((camera.y+HEIGHT)//490)+1):
                for gx in range(int(camera.x//580),int((camera.x+WIDTH)//580)+1):
                    x,y=xy(V(gx*580+90,gy*490+65))
                    if (gx+gy)%3==0 and 'obelisk' in self.a.images:
                        self.sprite('obelisk',(x,y),.9)
                    else:
                        for i in range(3):
                            xx=x+i*12;yy=y+(i%2)*7
                            self.canvas.blit(self.glows[40],(xx-40,yy-54))
                            pg.draw.rect(self.canvas,(113,104,84),(xx,yy-12,4,12))
                            flame=3+int(math.sin(s.time*6+i)*1)
                            pg.draw.ellipse(self.canvas,(207,155,75),(xx,yy-15-flame,4,flame+2))
        self.boundary(s.arena,camera)
        for pickup in s.pickups:
            x,y=xy(pickup.pos)
            if -20<x<WIDTH+20 and -20<y<HEIGHT+20:
                c=CYAN if pickup.kind=='xp' else (242,114,156)
                pg.draw.polygon(self.canvas,(24,78,97),[(x,y-8),(x+8,y),(x,y+8),(x-8,y)])
                pg.draw.polygon(self.canvas,c,[(x,y-5),(x+5,y),(x,y+5),(x-5,y)])
                if pickup.kind=='health': pg.draw.line(self.canvas,INK,(x-3,y),(x+3,y),2)
                elif pickup.kind=='chest':
                    pg.draw.rect(self.canvas,(86,53,39),(x-12,y-8,24,17));pg.draw.rect(self.canvas,GOLD,(x-12,y-8,24,17),2);pg.draw.rect(self.canvas,INK,(x-2,y-3,4,5))
        self.fx.begin()
        for a in s.areas:
            pos=xy(a.pos); radius=int(a.radius)
            if a.kind=='turret':
                pg.draw.rect(self.canvas,(39,46,54),(pos[0]-18,pos[1]-20,36,22));pg.draw.line(self.canvas,(210,187,98),pos,(pos[0]+42,pos[1]-16),6)
            if a.kind in ('glue','prison','chemical'):
                pg.draw.circle(self.canvas,(51,64,65),pos,radius)
                pg.draw.circle(self.canvas,(111,152,150),pos,radius,2)
                if a.kind=='chemical':
                    pg.draw.circle(self.canvas,(97,158,115),pos,radius,4)
                    for i in range(8):
                        at=V(pos)+V(radius*.7,0).rotate(s.time*50+i*45);pg.draw.rect(self.canvas,(174,244,151),(int(at.x)//4*4,int(at.y)//4*4,8,8))
                for n in range(5):
                    v=V(radius*.55,0).rotate(n*72); pg.draw.circle(self.canvas,(151,181,176),(int(pos[0]+v.x),int(pos[1]+v.y)),3)
            elif a.kind in ('wave','danger_wave'):
                c=PINK if a.kind=='danger_wave' else CHARACTERS[s.owner(a.owner).key]['color']
                self.fx.wave(pos,radius,a.life,c)
            elif a.kind=='swarm':
                self.fx.art.stamp(self.fx.layer,'swarm',self.fx.point(pos),min(112,radius/2),-s.time*40,100)
        self.fx.present(self.canvas)
        for t in s.telegraphs:
            if t.kind in ('dempsey','gazelle_combo','puppet_impact'):continue
            pos=xy(t.pos); hostile=t.kind in HOSTILE_KINDS
            caster=s.owner(t.owner);c=PINK if hostile else CHARACTERS[caster.key]['color']
            if hostile:
                # Danger remains prominent on every effects setting.
                radius=max(1,int(t.radius))
                if radius not in self.danger_fields:
                    field=pg.Surface((radius*2+2,radius*2+2),pg.SRCALPHA)
                    pg.draw.circle(field,(*PINK,28),(radius+1,radius+1),radius)
                    self.danger_fields[radius]=field
                    if len(self.danger_fields)>24:self.danger_fields.popitem(last=False)
                self.canvas.blit(self.danger_fields[radius],(pos[0]-radius-1,pos[1]-radius-1))
                for i in range(12):
                    a=V(pos)+V(radius+5,0).rotate(i*30+s.time*20)
                    b=V(pos)+V(radius+5,0).rotate(i*30+14+s.time*20)
                    pg.draw.line(self.canvas,PINK,a,b,3)
            if t.kind=='musashi_cut':
                end=xy(V(t.pos)+(t.direction or p.aim)*t.radius)
                pg.draw.line(self.canvas,(*c,),pos,end,3)
                pg.draw.line(self.canvas,INK,pos,end,1)
                continue
            if t.kind=='whip_visual':
                a=xy(caster.pos); b=pos
                pg.draw.lines(self.canvas,(73,153,107),False,[a,((a[0]+b[0])//2+18,(a[1]+b[1])//2-22),b],5)
                continue
            if t.kind in ('boss_fan','boss_sweep'):continue
            if not hostile and t.kind not in ('glue_ultimate','pacoca_ultimate'):continue
            if t.kind=='charge':
                end=V(t.pos)+t.direction*270; pg.draw.line(self.canvas,(116,53,83),pos,xy(end),int(t.radius*2))
                pg.draw.line(self.canvas,c,pos,xy(end),2)
            else:
                pg.draw.circle(self.canvas,c,pos,int(t.radius),2)
                pg.draw.circle(self.canvas,c,pos,max(2,int(t.radius*(1-min(1,t.delay)))),1)
            self.text('!' if hostile else '+',pos[0],pos[1],28,c,True)
            if t.kind in ('glue_ultimate','pacoca_ultimate'):
                sprite='attack_glue' if t.kind=='glue_ultimate' else 'attack_pacoca'
                self.sprite(sprite,(pos[0],pos[1]-int(t.delay*220)),3.5)
        for corpse in s.corpses:
            name=f'{corpse.theme}_anim_{6 if corpse.boss else corpse.kind}_7'
            if name in self.a.images:
                im=self.a.sprite(name).copy();im=pg.transform.scale(im,(round(im.get_width()*(1.9 if corpse.boss else 1.15)),round(im.get_height()*(1.9 if corpse.boss else 1.15))));im=pg.transform.flip(im,corpse.facing_left,False);im.set_alpha(round(210*corpse.life/.55));at=xy(corpse.pos);self.canvas.blit(im,im.get_rect(midbottom=(at[0],at[1]+10)))
        actors=[(getattr(e,'render_pos',e.pos).y,0,e) for e in s.enemies if not e.dead]
        actors.extend((getattr(ally,'render_pos',ally.pos).y,1,ally) for ally in s.allied_players)
        for _,kind,actor in sorted(actors,key=lambda item:(item[0],item[1])):
            if kind==0:self.draw_enemy(s,actor,xy,hitboxes)
            else:self.draw_player(s,actor,xy,hitboxes)
        pos=xy(getattr(p,'render_pos',p.pos));scale=self.player_scale(p)
        self.fx.begin()
        from expedition_ui import objectives_world
        objectives_world(self,s,xy)
        for ally in s.allied_players:
            if ally.attack_pose>0 and ally.hp>0:self.fx.attack_cast(xy(ally.pos),ally.aim,ally.key,ally.attack_pose,s.time)
        for q in s.projectiles:self.fx.projectile(q,xy(q.pos+q.vel*getattr(s,'interpolation_age',0)),s.time,s.arena.key=='usj')
        from combat_art import draw as draw_effect
        cap={'full':90,'balanced':48,'low':24}[self.fx.quality]
        for e in s.effects[-cap:]:draw_effect(self.fx,e,xy,s.time)
        self.fx.present(self.canvas)
        for a in s.areas:
            if a.kind=='swarm':
                for i in range(min(20,12+int(s.owner(a.owner).bat_power*2))):
                    v=V(a.radius*(.35+(i%4)*.17),0).rotate(s.time*190+i*137)
                    self.sprite(f'enemy_4_{int(s.time*12+i)%2}',xy(a.pos+v),.65)
        stride=2 if self.fx.quality=='balanced' else 4 if self.fx.quality=='low' else 1
        for x in s.particles[::stride]:
            pos2=xy(x.pos); pg.draw.rect(self.canvas,x.color,(*pos2,x.size,x.size))
        if options['numbers']:
            for x in s.texts[-40:]:
                at=xy(x.pos)
                if 0<at[0]<WIDTH and 100<at[1]<HEIGHT-80:self.text(x.text,*at,24 if x.critical else 18,x.color,True)
        if s.transform_pause>0:
            radius=int((.6-s.transform_pause)*420)
            pg.draw.circle(self.canvas,CHARACTERS[p.key]['color'],pos,max(5,radius),4)
            # Short visual transition: dissolve hair, compress human, fuse trio.
            progress=1-s.transform_pause/.55
            if p.key=='leo' and progress<.55:
                self.sprite('leo_transform',(pos[0],pos[1]+12),scale,flip_x=p.facing_left)
                for i in range(8): pg.draw.rect(self.canvas,(44,38,41),(pos[0]-14+i*4,pos[1]-78-progress*70+(i%3)*5,3,3))
            elif p.key=='rafael' and progress<.55:
                im=self.a.sprite('rafael_transform'); im=pg.transform.scale(im,(int(78+progress*20),int(104-progress*50)))
                if p.facing_left:im=pg.transform.flip(im,True,False)
                self.canvas.blit(im,im.get_rect(midbottom=(pos[0],pos[1]+12)))
            elif p.key=='leozauxta' and progress<.55:
                for i in range(3): self.sprite(f'member_{i}',(pos[0]+(i-1)*int(70*(1-progress)),pos[1]),1.4)
        self.canvas.blit(self.vignette,(0,0))
        # Draw crisp hostile contours after all VFX: visual density never hides danger.
        self.danger_foreground(s,xy)
        if p.hurt_flash>0 and self.flashes:
            self.damage_frame.set_alpha(round(255*p.hurt_flash/.28));self.canvas.blit(self.damage_frame,(0,0))
        alive=[e for e in s.enemies if not e.dead]
        guide=alive if s.waves.remaining==0 and len(alive)<=5 and not s.waves.rest else []
        if s.boss and not s.boss.dead and s.boss not in guide:guide=guide+[s.boss]
        for enemy in guide:self.edge_marker(xy(enemy.pos),enemy.boss,s.time)
        self.hud(s)
        from expedition_ui import tracker
        tracker(self,s)
        if s.rhythm.active:self.rhythm_hud(s)
    @staticmethod
    def player_scale(p):
        if p.key in ('ippo','eren','klein','musashi','joe','thorfinn','holden'):return 2.
        if p.key=='walter':return 1.25
        if p.key=='leozauxta':return 1.8 if p.transformed else 1.25
        return 1.65
    def draw_enemy(self,s,e,xy,hitboxes):
        x,y=xy(getattr(e,'render_pos',e.pos))
        if not(-150<x<WIDTH+150 and -220<y<HEIGHT+180):return
        pg.draw.ellipse(self.canvas,(6,12,22),(x-e.radius,y-e.radius*.4,e.radius*2,e.radius*.8))
        from monster_animation import sprite_name
        name=sprite_name(e,s.time,s.arena.key) if self.a.monster_animation_status.get(s.arena.key)=='animated' else enemy_sprite(e,s.time,s.arena.key)
        if name not in self.a.images:name=enemy_sprite(e,s.time,'crypt')
        scale=2.1 if getattr(e,'trial_key',None) else 1.9 if e.boss else 1.45 if e.elite else 1.15
        self.sprite(name,(x,y+10),scale,flip_x=e.facing_left,hit=e.hit>.05 and self.flashes)
        if e.boss and e.phase_guard>0:pg.draw.circle(self.canvas,(162,190,215),(x,y-35),80,3)
        if e.elite:pg.draw.circle(self.canvas,GOLD,(x,y),int(e.radius+5),1)
        if e.puppet_left>0:pg.draw.circle(self.canvas,(202,162,248),(x,y),int(e.radius+8),2)
        if e.hit>0:pg.draw.circle(self.canvas,INK,(x,y-16),int(e.radius+4),1)
        if e.hp<e.max_hp and not e.boss:self.bar(x-22,y-57,44,4,e.hp/e.max_hp,PINK)
        if hitboxes:pg.draw.circle(self.canvas,(255,0,80),(x,y),int(e.radius),1)
    def draw_player(self,s,p,xy,hitboxes):
        pos=xy(getattr(p,'render_pos',p.pos))
        if not(-160<pos[0]<WIDTH+160 and -240<pos[1]<HEIGHT+160):return
        scale=self.player_scale(p);color=CHARACTERS[p.key]['color'];name=p.sprite(s.time)
        pg.draw.ellipse(self.canvas,(4,10,20),(pos[0]-25,pos[1]-8,50,16))
        if p.hp>0:
            for sign in (-1,1):pg.draw.line(self.canvas,color,(pos[0]+sign*21,pos[1]-2),(pos[0]+sign*28,pos[1]+2),2)
        if p.transformed and p.key not in ('ippo','musashi','joe','thorfinn','holden'):
            for i in range(8):
                a=V(pos)+V(37,0).rotate(i*45+s.time*18);b=V(pos)+V(42,0).rotate(i*45+s.time*18)
                pg.draw.line(self.canvas,color,a,b,2)
        rhythm=s.rhythms.get(p.pid)
        if p.dash_left>0 and p.key=='leozauxta':
            for i in range(10):
                v=V(24,0).rotate(i*36+s.time*350);self.sprite('enemy_4_0',(pos[0]+v.x,pos[1]+v.y),.55)
        elif rhythm and rhythm.active and rhythm.hits:
            candidate=f'dance_{(p.dance_pose-1)%4}_{int(p.form_age*6)%6}'
            if candidate in self.a.images:name=candidate
        hop=abs(math.sin(p.form_age*10))*18 if rhythm and rhythm.active and p.dance_pose==4 else 0
        self.sprite(name,(pos[0],pos[1]+12-hop),scale if p.hp>0 else .85,flip_x=self.actor_flip(name,p.facing_left),hit=p.hurt_flash>.18 and self.flashes)
        if p.invulnerable>0:pg.draw.circle(self.canvas,(159,212,225),pos,p.radius+5,1)
        if hitboxes:pg.draw.circle(self.canvas,GREEN,pos,p.radius,1)
        if p is not s.player:
            h=self.a.logical.get(name,self.a.images[name].get_size())[1]*scale
            if p.hp<=0:
                self.text('APROXIME-SE PARA REANIMAR',pos[0],pos[1]-95,16,PINK,True)
                self.bar(pos[0]-40,pos[1]-75,80,5,p.revive_progress/3,GREEN)
            else:
                self.bar(pos[0]-28,pos[1]-h-5,56,5,p.hp/p.max_hp,color)
                self.text('P'+str(p.pid+1),pos[0],pos[1]-h-18,17,color,True)
    def danger_foreground(self,s,xy):
        for t in s.telegraphs:
            if t.kind not in HOSTILE_KINDS:continue
            pos=V(xy(t.pos));radius=max(6,round(t.radius))
            if t.kind=='boss_fan' and t.direction is not None:
                d=V(t.direction);length=min(600,t.reach)
                left=pos+d.rotate(-t.spread/2)*length;right=pos+d.rotate(t.spread/2)*length
                pg.draw.lines(self.canvas,(30,9,19),False,[left,pos,right],5)
                pg.draw.lines(self.canvas,(255,131,146),False,[left,pos,right],2)
                continue
            if t.kind in ('charge','boss_sweep') and t.direction is not None:
                d=V(t.direction);side=V(-d.y,d.x)*radius;end=pos+d*(t.reach if t.kind=='boss_sweep' else 270)
                pg.draw.lines(self.canvas,(30,9,19),False,[pos+side,end+side,end-side,pos-side],5)
                pg.draw.lines(self.canvas,(255,131,146),False,[pos+side,end+side,end-side,pos-side],2)
            else:
                if not(-radius<pos.x<WIDTH+radius and -radius<pos.y<HEIGHT+radius):continue
                pg.draw.circle(self.canvas,(30,9,19),pos,radius,5)
                pg.draw.circle(self.canvas,(255,131,146),pos,radius,2)
                # Segmented inner ring tracks the warning without covering the ground.
                for i in range(8):
                    a=pos+V(radius-4,0).rotate(i*45);b=pos+V(radius-4,0).rotate(i*45+20)
                    pg.draw.line(self.canvas,(255,194,174),a,b,2)
            pg.draw.rect(self.canvas,(30,9,19),(pos.x-10,pos.y-15,20,26),border_radius=3)
            self.text('!',pos.x,pos.y-1,25,(255,194,174),True)
            if t.total_delay>0:
                progress=max(0,min(1,1-t.delay/t.total_delay))
                self.bar(pos.x-17,pos.y+17,34,3,progress,(255,194,174))
    def hud(self,s):
        from ui_design import pips,icon
        p=s.player;c=CHARACTERS[p.key];color=c['color']
        self.bar(0,0,WIDTH,4,p.xp/p.threshold,CYAN,(15,17,25))
        self.panel((16,17,332,79),(19,20,29),(68,59,72))
        portrait='portrait_'+p.key+('_form' if p.transformed else '')
        if p.key in ('ippo','eren','klein','musashi','joe','thorfinn','holden'):
            from pixel_characters import stage_for
            from evolution_kit import stage_of
            portrait=f'{p.key}_form{stage_of(p)}_walk_1' if p.transformed else f'{p.key}_stage{stage_for(p)}_walk_1'
        if p.key=='walter' and p.evolved:portrait='portrait_'+('felina' if p.transformed else 'heisenberg')
        if portrait in self.a.images:
            pw,ph=self.a.logical[portrait];self.sprite(portrait,(53,86),min(51/pw,59/ph))
        size=22
        while size>14 and self.a.font(size).size(p.display_name)[0]>216:size-=1
        self.text(p.display_name,91,30,size,INK)
        self.bar(91,58,237,8,p.hp/p.max_hp,PINK,(48,29,39))
        self.text(f'{math.ceil(p.hp)} / {int(p.max_hp)}',91,74,17,MUTED)
        self.text(f'NV. {p.level}',282,74,17,CYAN)
        self.panel((518,17,244,68),(19,20,29),(68,59,72))
        self.text('ONDA '+str(s.waves.number)+(' / ∞' if s.waves.endless else ' / 10'),640,37,26,GOLD,True)
        self.text(f'{int(s.time)//60:02}:{int(s.time)%60:02}  •  {s.kills} ABATES',640,67,18,INK,True)
        self.panel((1005,17,259,69),(19,20,29),color)
        self.text('FORÇA HUMANA' if p.run_rule=='noform' else 'SIGMA',1024,31,19,color)
        meter=f'{p.form_left:.1f}s' if p.transformed else f'RECUPERA {p.form_recovery:.0f}s' if p.form_recovery>0 else 'PRONTO • E' if p.sigma>=100 else f'{int(p.sigma)}%'
        if p.run_rule=='noform':meter='+20% DANO';self.bar(1024,62,220,7,0,color)
        self.text(meter,1157,38,18,INK,True)
        self.bar(1024,62,220,7,0 if p.run_rule=='noform' else p.form_left/14 if p.transformed else p.sigma/100,color)
        if s.boss and not s.boss.dead:
            b=s.boss;status=f'ESCUDO {b.phase_guard:.1f}s' if b.phase_guard>0 else f'FASE {b.phase} / 3'
            self.panel((404,100,472,65),(27,17,28),PINK)
            self.text(getattr(b,'name','CHEFE')+' / '+status,640,115,17,PINK,True)
            self.bar(421,131,438,5,b.hp/b.max_hp,PINK)
            for fraction in (.34,.67):pg.draw.line(self.canvas,(255,214,177),(421+round(438*fraction),129),(421+round(438*fraction),138),1)
            self.text(b.attack_name or 'LEIA OS AVISOS • GUARDE SEU DASH',640,152,15,MUTED,True)
        elif not s.boss_spawned:
            alive=sum(not e.dead for e in s.enemies)
            self.text(f'PRÓXIMA ONDA EM {s.waves.rest:.1f}s' if s.waves.rest else f'{s.waves.remaining+alive} INIMIGOS RESTANTES',640,103,17,MUTED,True)
        if p.key=='walter' and not p.evolved:evolution=f'HEISENBERG EM {max(0,150-int(s.time))}s'
        elif p.key in ('ippo','eren','klein') and p.stage<(2 if p.key=='klein' else 1):evolution='EVOLUÇÃO NO NÍVEL '+str(9 if p.key=='klein' and p.stage==1 else 5 if p.key=='klein' else 6)
        elif p.key=='musashi':evolution='PRÓXIMO CAMINHO: NV. '+str((5,10,15)[p.stage]) if p.stage<3 else 'F • ALMA / '+('EGO' if p.soul_mode=='self' else 'VÍNCULO')
        elif p.key in ('joe','thorfinn','holden'):
            levels=(6,12) if p.key=='joe' else (5,10,15);evolution='EVOLUÇÃO NO NÍVEL '+str(levels[p.stage]) if p.stage<len(levels) else 'CAMINHO COMPLETO'
        else:evolution=''
        if evolution:self.text(evolution,23,109,16,CYAN)
        for i,ally in enumerate(a for a in s.allied_players if a.pid!=p.pid):
            y=145+i*39;ac=CHARACTERS[ally.key]['color']
            self.text(f'P{ally.pid+1} / '+CHARACTERS[ally.key]['name']+(' • CAÍDO' if ally.hp<=0 else ''),23,y,16,PINK if ally.hp<=0 else ac)
            self.bar(23,y+21,146,4,ally.hp/ally.max_hp,ac)
        if s.message_left>0:
            size=22
            while size>14 and self.a.font(size).size(s.message)[0]>780:size-=1
            width=self.a.font(size).size(s.message)[0]+36
            self.panel((640-width//2,164,width,35),(22,21,30),color)
            self.text(s.message,640,181,size,color,True)
        self.panel((16,645,270,49),(19,20,29),(68,59,72))
        label=self.weapon_label(s);size=18
        while size>13 and self.a.font(size).size(label)[0]>241:size-=1
        self.text(label,30,656,size,INK);self.text(f'TAB / BUILD  {1+len(p.aux)}/6  •  {s.chests} BAÚS',30,678,15,GOLD)
        hotx=318 if s.rhythm.active else 365
        self.ability(hotx,645,176,'ESPAÇO','DASH' if p.dash_cd<=0 else f'{p.dash_cd:.1f}s',max(0,1-p.dash_cd/2.4),CYAN)
        self.ability(hotx+188,645,178,'E','INDISPONÍVEL' if p.run_rule=='noform' else 'FORMA' if p.transformed else f'RECUPERA {p.form_recovery:.0f}s' if p.form_recovery>0 else 'TRANSFORMAR',0 if p.run_rule=='noform' else p.form_left/14 if p.transformed else p.sigma/100,color)
        self.ability(hotx+378,645,159,'Q','USADA' if p.ultimate_used else 'ULTIMATE',int(p.transformed and not p.ultimate_used),GOLD)
        if p.transformed:self.text(p.form_name,640,624,19,color,True)
        if not s.rhythm.active:
            mini=self.map_preview(s.arena.key,(112,112));at=(1144,539);self.canvas.blit(mini,at)
            pg.draw.rect(self.canvas,(109,94,86),(*at,112,112),1)
            for ally in s.allied_players:
                point=(at[0]+max(1,min(110,int(ally.pos.x/3600*112))),at[1]+max(1,min(110,int(ally.pos.y/3600*112))))
                pg.draw.circle(self.canvas,INK if ally.pid==p.pid else CHARACTERS[ally.key]['color'],point,3)
            if s.boss and not s.boss.dead:pg.draw.circle(self.canvas,PINK,(at[0]+max(1,min(110,int(s.boss.pos.x/3600*112))),at[1]+max(1,min(110,int(s.boss.pos.y/3600*112)))),3)
            zone=s.arena.zone_at(p.pos);size=15
            while size>11 and self.a.font(size).size(zone)[0]>153:size-=1
            self.text(zone,1181,523,size,GOLD,True);self.text('ESC / PAUSA',1200,678,15,MUTED,True)
        if p.hp<=0:self.text('ALIADO PRÓXIMO POR 3s / REANIMAR',640,583,25,PINK,True)
    def boundary(self,arena,camera):
        b=arena.bounds;t=48
        rects=(pg.Rect(b.left-t,b.top-t,b.width+2*t,t),pg.Rect(b.left-t,b.bottom,b.width+2*t,t),
               pg.Rect(b.left-t,b.top,t,b.height),pg.Rect(b.right,b.top,t,b.height))
        palettes={'usj':((32,48,60),(87,114,118)), 'ring':((39,30,38),(161,91,78)),
                  'walls':((74,69,60),(142,129,101)), 'fog':((26,35,44),(94,105,122))}
        dark,light=palettes.get(arena.key,((38,36,46),(96,85,105)))
        screen=pg.Rect(0,0,WIDTH,HEIGHT)
        for wall in rects:
            at=wall.move(-round(camera.x),-round(camera.y))
            if not at.colliderect(screen):continue
            pg.draw.rect(self.canvas,dark,at)
            for yy in range(max(at.top,-24),min(at.bottom,HEIGHT+24),24):
                for xx in range(max(at.left,-48),min(at.right,WIDTH+48),48):
                    pg.draw.rect(self.canvas,light,(xx+2,yy+2,44,20),2)
                    pg.draw.line(self.canvas,(15,20,27),(xx+4,yy+20),(xx+44,yy+20),3)
            pg.draw.rect(self.canvas,light,at,4)
    def ability(self,x,y,w,key,label,ready,color):
        self.panel((x,y,w,49),(19,20,29),color if ready>=1 else (68,59,72),2 if ready>=1 else 1)
        kw=55 if key=='ESPAÇO' else 24
        pg.draw.rect(self.canvas,(40,34,46),(x+9,y+9,kw,25))
        self.text(key,x+9+kw//2,y+21,15,color,True)
        size=17
        while size>12 and self.a.font(size).size(label)[0]>w-kw-25:size-=1
        self.text(label,x+kw+17,y+15,size,INK if ready>=1 else MUTED)
        self.bar(x+10,y+40,w-20,3,ready,color)
    def edge_marker(self,pos,boss,time):
        if 30<pos[0]<WIDTH-30 and 155<pos[1]<HEIGHT-115:return
        center=V(WIDTH/2,HEIGHT/2+35);d=V(pos)-center
        if not d.length_squared():return
        ratio=min((WIDTH/2-35)/max(1,abs(d.x)),(240 if d.y<0 else 205)/max(1,abs(d.y)))
        at=center+d*ratio;direction=d.normalize();side=V(-direction.y,direction.x)
        color=PINK if boss else GOLD
        pg.draw.circle(self.canvas,(13,19,27),at,16)
        pg.draw.polygon(self.canvas,color,[at+direction*11,at-direction*7+side*7,at-direction*7-side*7])
        if boss:self.text('CHEFE',at.x,at.y+24,15,color,True)
    @staticmethod
    def weapon_label(s): return s.weapon.name
    def dim(self):
        self.overlay.fill((8,8,10,231)); self.canvas.blit(self.overlay,(0,0))

    def rhythm_hud(self,s):
        rhythm=s.rhythm
        self.panel((865,205,385,488),(16,17,26),GREEN,2)
        self.text('TRIPLE SIGMA DANCE',1058,224,24,GREEN,True)
        self.text('IMORTAL' if rhythm.protected else 'ACERTE PARA PROTEGER',1058,253,18,GOLD if rhythm.protected else MUTED,True)
        xs=(910,1005,1100,1195);colors=((139,121,241),(96,219,228),(139,235,119),(236,121,177))
        for lane,x in enumerate(xs):
            pg.draw.line(self.canvas,(44,45,55),(x,280),(x,574),2)
            self.arrow(x,565,lane,colors[lane],False)
            self.text(('D','F','K','J')[lane],x,608,25,INK,True)
        for note in rhythm.notes:
            if note.judged:continue
            y=565-(note.time-rhythm.age)*160
            if 285<=y<=590:self.arrow(xs[note.lane],int(y),note.lane,colors[note.lane],True)
        self.text(f'COMBO {rhythm.combo}  /  MELHOR {rhythm.best}',1058,648,22,GREEN,True)
        if rhythm.feedback_until>rhythm.age:self.text(rhythm.feedback,1058,678,24,GOLD if rhythm.feedback!='ERRO' else PINK,True)
    def arrow(self,x,y,lane,color,filled):
        points=[(-17,0),(-3,-14),(-3,-6),(14,-6),(14,6),(-3,6),(-3,14)]
        angle=(0,-90,90,180)[lane]
        pts=[V(v).rotate(angle)+V(x,y) for v in points]
        pg.draw.polygon(self.canvas,(12,13,22),pts)
        pg.draw.polygon(self.canvas,color,pts,0 if filled else 3)
