import random
import pygame as pg
from entities import V
from asset_generator import AssetManager
from save_manager import SaveManager
from session import GameSession
from renderer import Renderer
from settings import WIDTH,HEIGHT,FPS,INK,MUTED,CYAN,GOLD,GREEN,PINK,CHARACTERS
import upgrades
from maps import MAPS
from music import MusicPlayer,MUSIC_END
import progression
import expansion_ui
import interface
import ui_screens
import missions
from cinematics import Cinematic,CinematicRenderer
from release_info import RELEASE_ID,RELEASE_TITLE,audit

class Button:
    def __init__(self,rect,text,action,color=CYAN,enabled=True): self.rect=pg.Rect(rect); self.text=text; self.action=action; self.color=color;self.enabled=enabled
    def draw(self,r,mouse,blend=0.,focused=False):
        hover=self.enabled and (self.rect.collidepoint(mouse) or focused)
        primary=self.action in ('network_connect','network_host','endless','network_start') or self.action=='play' and self.text.startswith('INICIAR')
        base=(65,47,40) if primary else (29,28,39)
        fill=tuple(int(a+(b-a)*blend) for a,b in zip(base,(73,61,65)))
        r.panel(self.rect,fill,self.color if hover or primary and self.enabled else (72,64,77),2 if hover or primary else 1)
        if blend>.05:pg.draw.line(r.canvas,self.color,(self.rect.x+6,self.rect.y+7),(self.rect.x+6,self.rect.bottom-7),2)
        size=24
        while size>15 and r.a.font(size).size(self.text)[0]>self.rect.width-20:size-=1
        r.text(self.text,self.rect.centerx,self.rect.centery,size,self.color if hover else INK if self.enabled else (115,111,119),True)

class Game:
    def __init__(self,seed=0,debug=False,character=None,save_path=None):
        pg.display.init(); pg.font.init()
        try: pg.mixer.init(frequency=22050,size=-16,channels=1,buffer=512)
        except pg.error: pass
        self.save=SaveManager(save_path); self.opts=self.save.data['settings']; self.windowed=(WIDTH,HEIGHT)
        self.screen=pg.display.set_mode(self.windowed,pg.RESIZABLE)
        pg.display.set_caption(f'SIGMA TRINITY {RELEASE_ID} — {RELEASE_TITLE}')
        self.assets=AssetManager(); self.render=Renderer(self.assets); self.clock=pg.time.Clock()
        self.installation_errors=audit()
        self.installation_errors.extend('Arte não carregada: '+theme for theme,status in self.assets.art_status.items() if status!='generated')
        self.installation_errors.extend('Animação não carregada: '+key for key,status in self.assets.animation_status.items() if status!='animated')
        self.installation_errors.extend('Monstro sem animação: '+key for key,status in self.assets.monster_animation_status.items() if status!='animated')
        self.running=True; self.state='MAIN_MENU'; self.return_state='MAIN_MENU'; self.session=None
        self.selected='leo'; self.seed=seed; self.debug=debug; self.hitboxes=False; self.buttons=[]; self.choices=[]
        self.ui_time=0.; self.run_index=0; self.mouse=(0,0); self.viewport=pg.Rect(0,0,WIDTH,HEIGHT)
        self.fullscreen=False; self.recorded=False; self.map_key='crypt'
        self.archive_page=0
        self.roster_page=0;self.focus_character='leo';self.hover_levels={};self.ui_dt=1/60;self.new_secrets=[]
        self.music=MusicPlayer(volume=self.opts['music_volume'])
        self.cinematic_renderer=CinematicRenderer();self.cinematic=None;self.cinematic_action=None
        self.pending_trial=None;self.net=None;self.net_match_seen='';self.net_result_seen=None;self.network_target='';self.network_message=''
        self.selection_context=None
        self.ui_focus=None;self.release_return='MAIN_MENU';self.drawn_state=None
        self.save_retry_left=0.;self.build_page=0;self.run_rule="standard";self.bestiary_page=0;self.gallery_page=0
        if self.opts['fullscreen']: self.toggle_fullscreen()
        if character: self.start(character)
        self.draw()
    def sound(self,name): self.assets.play(name,self.opts['volume'])
    def toggle_fullscreen(self):
        try:
            new=not self.fullscreen
            self.screen=pg.display.set_mode((0,0) if new else self.windowed,pg.FULLSCREEN if new else pg.RESIZABLE)
            self.fullscreen=new; self.opts['fullscreen']=new; self.save.save()
        except pg.error:
            self.screen=pg.display.set_mode(self.windowed,pg.RESIZABLE); self.fullscreen=False; self.opts['fullscreen']=False
    def start(self,key=None):
        candidate=key or self.selected
        if not self.save.is_unlocked(candidate):
            self.state='CHARACTER_SELECT'; return False
        self.selected=candidate; self.run_index+=1
        self.session=GameSession(self.selected,self.seed+self.run_index,self.sound,self.map_key,run_rule=self.run_rule)
        progression.meta_apply(self.save.data,self.session.player)
        self.session.player.allowed_items=missions.unlocked(self.save.data)
        self.session.player.clip_seen=set(self.save.data['clip_seen']);self.session.player.short_cinema=self.opts['short_cinema']
        self.new_secrets=[]
        self.state='PLAYING'; self.recorded=False; self.choices=[]
        self.save.data['plays'][self.selected]+=1; self.save.save()
    def open_settings(self): self.return_state=self.state; self.state='SETTINGS'
    def back(self):
        if self.state=='ANIMATION_GALLERY':self.state='RELEASE_INFO';self.return_state=self.release_return
        elif self.state=='RELEASE_INFO':self.state=self.release_return
        else:self.state=self.return_state
    def menu(self):
        if self.net:self.net.close();self.net=None
        self.state='MAIN_MENU';self.session=None;self.choices=[];self.pending_trial=None;self.selection_context=None
        self.cinematic=None
        self.offer_fusion()
    def offer_fusion(self):
        if not self.net and self.save.challenge_available('leozauxtaci') and not self.save.data['fusion_offered']:
            self.save.data['fusion_offered']=True;self.save.save();self.begin_trial('leozauxtaci')
    def begin_trial(self,key):
        if not self.save.challenge_available(key):return False
        self.pending_trial=key;self.selection_context='trial';self.roster_page=0;self.state='CHARACTER_SELECT';return True
    def start_trial(self,character):
        if not self.pending_trial or not self.save.is_unlocked(character):return False
        from trials import create
        self.selected=character;self.run_index+=1
        self.session=create(character,self.pending_trial,self.seed+self.run_index,self.sound)
        self.new_secrets=[];self.recorded=False;self.choices=[]
        self.cinematic=Cinematic(self.pending_trial,'fusion' if self.pending_trial=='leozauxtaci' else 'trial')
        self.cinematic_action=None;self.state='CUTSCENE';self.selection_context=None;return True
    def combat_action(self,action):
        if self.net:self.net.command(action);return
        s=self.session;p=s.player
        if s.result or p.hp<=0:return
        if action=='transform':
            if s.transform():self.cinematic=Cinematic.player(p,'transform');self.cinematic_action=None;self.state='CUTSCENE'
        elif action=='ultimate':
            if p.transformed and not p.ultimate_used and s.transform_pause<=0:
                self.cinematic=Cinematic.player(p,'ultimate');self.cinematic_action='ultimate';self.state='CUTSCENE'
        elif action.startswith('note:'):s.rhythm_tap(int(action[5:]))
        else:getattr(s,{'soul':'toggle_musashi_soul_mode'}.get(action,action))()
    def finish_cinematic(self):
        if self.net:self.net.command('skip');return
        self.session.transform_pause=0
        if self.cinematic_action:self.session.ultimate()
        self.cinematic=None;self.cinematic_action=None;self.state='PLAYING'
    def network_open(self,host):
        from multiplayer import Multiplayer
        if self.net:self.net.close()
        self.net=Multiplayer(self.save,self.selected,host=host,target=self.network_target or None,sound=self.sound)
        self.session=None;self.net_match_seen='';self.net_result_seen=None;self.selection_context=None;self.state='NETWORK_LOBBY'
    def choose(self,index):
        if self.state!='LEVEL_UP' or not 0<=index<len(self.choices): return
        if self.net:
            self.net.command('choice',index=index,token=self.net.tokens.get(self.net.pid));return
        upgrades.apply(self.session.player,self.choices[index]); self.session.player.pending-=1
        if self.session.player.pending>0: self.choices=upgrades.choices(self.session.player,self.session.rng)
        else: self.state='PLAYING'; self.choices=[]
        self.sound('level')
    def action(self,name):
        if name=='quit': self.running=False
        elif name=='release_info':
            if self.state!='ANIMATION_GALLERY':self.release_return=self.state
            self.return_state=self.release_return;self.state='RELEASE_INFO'
        elif name=='animation_gallery':self.return_state='RELEASE_INFO';self.state='ANIMATION_GALLERY'
        elif name=='play': self.run_rule='standard';self.state='CHARACTER_SELECT'
        elif name=='challenges':self.state='CHALLENGES'
        elif name=='bestiary':self.state='BESTIARY'
        elif name=='bestiary_next':self.bestiary_page=(self.bestiary_page+1)%6
        elif name=='gallery_next':self.gallery_page=(self.gallery_page+1)%2
        elif name.startswith('rule:'):self.run_rule=name.split(':')[1];self.state='CHARACTER_SELECT'
        elif name=='network_rule' and self.net and self.net.is_host:
            from expedition import RULES
            self.net.command('rule',rule=list(RULES)[(list(RULES).index(self.net.run_rule)+1)%len(RULES)])
        elif name=='trial':self.begin_trial('leozauxta' if self.save.challenge_available('leozauxta') else 'leozauxtaci')
        elif name=='multiplayer':self.state='MULTIPLAYER_MENU'
        elif name=='network_host':self.network_open(True)
        elif name=='network_join':
            if self.net:self.net.close();self.net=None
            self.session=None;self.state='NETWORK_JOIN';self.network_message=''
        elif name=='network_retry':self.network_open(self.net.is_host if self.net else False)
        elif name=='network_connect':self.network_open(False)
        elif name=='network_ready' and self.net:self.net.command('ready')
        elif name=='network_start' and self.net:self.net.command('start')
        elif name=='network_restart' and self.net:self.net.command('restart')
        elif name=='network_character' and self.net:self.selection_context='network';self.state='CHARACTER_SELECT'
        elif name=='network_map' and self.net and self.net.is_host:
            self.net.command('map',map=list(MAPS)[(list(MAPS).index(self.net.map_key)+1)%len(MAPS)])
        elif name=='menu': self.menu()
        elif name=='resume': self.state='PLAYING'
        elif name=='restart':
            if not self.net:
                if self.session and self.session.challenge:self.pending_trial=self.session.challenge;self.start_trial(self.selected)
                else:self.start()
        elif name=='help': self.return_state=self.state; self.state='HELP'
        elif name=='settings': self.open_settings()
        elif name=='archive':self.state='ARCHIVE'
        elif name=='missions':self.state='MISSIONS'
        elif name=='roster_prev':self.roster_page=(self.roster_page-1)%max(1,(len(self.save.visible_characters())+5)//6)
        elif name=='roster_next':self.roster_page=(self.roster_page+1)%max(1,(len(self.save.visible_characters())+5)//6)
        elif name=='endless' and self.net:
            self.net.command('endless');self.recorded=False
        elif name=='endless' and self.session and not self.session.challenge and self.session.waves.continue_endless(self.session):
            self.recorded=False
            if self.session.player.pending:self.state='LEVEL_UP';self.choices=upgrades.choices(self.session.player,self.session.rng)
            else:self.state='PLAYING'
        elif name=='archive_next':self.archive_page=(self.archive_page+1)%((len(progression.ACHIEVEMENTS)+6)//7)
        elif name=='build':self.state='BUILD'
        elif name=='build_next':self.build_page+=1
        elif name.startswith('buy:'):progression.purchase(self.save,name.split(':')[1])
        elif name=='reroll' and self.state=='LEVEL_UP' and self.session.player.rerolls>0 and not (self.session.player.level>=4 and not self.session.player.specialization):
            if self.net:self.net.command('reroll',token=self.net.tokens.get(self.net.pid))
            else:self.session.player.rerolls-=1;self.choices=upgrades.choices(self.session.player,self.session.rng)
        elif name=='back': self.back()
        elif name=='fullscreen': self.toggle_fullscreen()
        elif name=='volume': self.opts['volume']=round((self.opts['volume']+.2)%1.01,2); self.save.save()
        elif name in ('shake','numbers','flashes','short_cinema'):
            self.opts[name]=not self.opts[name];self.save.save()
            if name=='short_cinema' and self.session:self.session.player.short_cinema=self.opts[name]
        elif name=='effects':
            modes=('full','balanced','low');self.opts['effects']=modes[(modes.index(self.opts['effects'])+1)%3];self.save.save()
        elif name=='music_volume':
            self.opts['music_volume']=round((self.opts['music_volume']+.2)%1.01,2); self.music.set_volume(self.opts['music_volume']); self.save.save()
        elif name=='next_music': self.music.next()
        elif name.startswith('char:'):
            key=name.split(':')[1]
            if self.save.is_unlocked(key):
                self.selected=key
                if self.selection_context=='network' and self.net:self.net.set_character(self.save,key);self.selection_context=None;self.state='NETWORK_LOBBY'
                elif self.pending_trial:self.start_trial(key)
                else:self.state='MAP_SELECT'
        elif name.startswith('map:'): self.map_key=name.split(':')[1]; self.start()
        elif name.startswith('choice:'): self.choose(int(name.split(':')[1]))
    def map_mouse(self,pos):
        return ((pos[0]-self.viewport.x)*WIDTH/max(1,self.viewport.width),(pos[1]-self.viewport.y)*HEIGHT/max(1,self.viewport.height))
    def handle(self,event):
        if event.type==MUSIC_END: self.music.handle_end(); return
        if event.type==pg.QUIT: self.running=False
        elif event.type==pg.MOUSEMOTION:self.ui_focus=None
        elif event.type==pg.VIDEORESIZE and not self.fullscreen:
            self.windowed=(max(640,event.w),max(360,event.h)); self.screen=pg.display.set_mode(self.windowed,pg.RESIZABLE)
        elif event.type==pg.WINDOWFOCUSLOST and self.state=='PLAYING': self.state='PAUSED'
        elif event.type==pg.KEYDOWN:
            k=event.key
            if self.state=='NETWORK_JOIN':
                if k==pg.K_RETURN:self.action('network_connect')
                elif k==pg.K_ESCAPE:self.state='MULTIPLAYER_MENU'
                elif k==pg.K_BACKSPACE:self.network_target=self.network_target[:-1]
                elif k==pg.K_v and getattr(event,'mod',0)&pg.KMOD_CTRL:
                    try:
                        pg.scrap.init();raw=pg.scrap.get(pg.SCRAP_TEXT)
                        if raw:
                            value=raw.decode('utf-8',errors='ignore').strip('\x00 \r\n')
                            if len(value)<=30 and all(c in '0123456789.:' for c in value):self.network_target=value
                    except pg.error:pass
                elif len(self.network_target)<30 and getattr(event,'unicode','') and event.unicode in '0123456789.:':self.network_target+=event.unicode
                return
            if self.state=='CUTSCENE' and k in (pg.K_RETURN,pg.K_SPACE):
                if not getattr(event,'repeat',False):self.finish_cinematic()
                return
            if k==pg.K_n: self.music.next(); return
            if k==pg.K_m: self.music.toggle(); return
            if k==pg.K_F11: self.toggle_fullscreen(); return
            if k==pg.K_F3: self.debug=not self.debug
            if k==pg.K_F4: self.hitboxes=not self.hitboxes
            if self.state not in ('PLAYING','CUTSCENE') and k in (pg.K_UP,pg.K_DOWN):
                options=[b for b in self.buttons if b.enabled]
                if options:
                    old=next((i for i,b in enumerate(options) if b.action==self.ui_focus),-1)
                    self.ui_focus=options[(old+(1 if k==pg.K_DOWN else -1))%len(options)].action
                return
            if self.state not in ('PLAYING','CUTSCENE') and k==pg.K_RETURN and self.ui_focus:
                b=next((b for b in self.buttons if b.action==self.ui_focus and b.enabled),None)
                if b:self.action(b.action);self.ui_focus=None;return
            if k==pg.K_ESCAPE:
                if self.state=='PLAYING': self.state='PAUSED'
                elif self.state=='PAUSED': self.state='PLAYING'
                elif self.state=='BUILD':self.state='PLAYING'
                elif self.state=='MAP_SELECT': self.state='CHARACTER_SELECT'
                elif self.state in ('SETTINGS','HELP','RELEASE_INFO','ANIMATION_GALLERY'): self.back()
                elif self.state not in ('LEVEL_UP','CUTSCENE'): self.menu()
            elif self.state=='PLAYING':
                if self.session.rhythm.active and k in (pg.K_d,pg.K_f,pg.K_k,pg.K_j):
                    if not getattr(event,'repeat',False):self.combat_action('note:'+str((pg.K_d,pg.K_f,pg.K_k,pg.K_j).index(k)))
                elif k==pg.K_SPACE: self.combat_action('dash')
                elif k==pg.K_e: self.combat_action('transform')
                elif k==pg.K_q: self.combat_action('ultimate')
                elif k==pg.K_f: self.combat_action('soul')
                elif k==pg.K_TAB:self.state='BUILD'
            elif self.state=='LEVEL_UP' and k in (pg.K_1,pg.K_2,pg.K_3): self.choose(k-pg.K_1)
            elif self.state=='LEVEL_UP' and k==pg.K_r:self.action('reroll')
            elif self.state=='CHARACTER_SELECT' and k in (pg.K_LEFT,pg.K_RIGHT):self.action('roster_prev' if k==pg.K_LEFT else 'roster_next')
            elif self.state=='CHARACTER_SELECT' and pg.K_1<=k<=pg.K_6:
                keys=self.save.visible_characters()[self.roster_page*6:self.roster_page*6+6];index=k-pg.K_1
                if index<len(keys):self.action('char:'+keys[index])
            elif self.state=='MAP_SELECT' and pg.K_1<=k<=pg.K_6: self.action('map:'+list(MAPS)[k-pg.K_1])
            elif self.state=='MAIN_MENU' and k==pg.K_RETURN: self.state='CHARACTER_SELECT'
        elif event.type==pg.MOUSEBUTTONDOWN and event.button==1:
            if self.state!=self.drawn_state:return
            mouse=self.map_mouse(event.pos)
            for b in self.buttons:
                if b.enabled and b.rect.collidepoint(mouse): self.action(b.action);self.ui_focus=None;break
    def update(self,dt,movement=None):
        dt=max(0,min(.15,dt));self.ui_dt=min(.05,dt)
        self.ui_time+=dt
        self.save_retry_left=max(0,self.save_retry_left-dt)
        if not self.net and self.session and self.session.result and not self.recorded and self.save_retry_left<=0:self.record_progress()
        self.music.pause(self.state in ('PAUSED','LEVEL_UP','SETTINGS','HELP','BUILD'))
        if self.net:
            self.network_update(dt,movement);return
        if self.state=='CUTSCENE':
            if self.cinematic and self.cinematic.update(dt):self.finish_cinematic()
            return
        while dt>1e-8 and self.state=='PLAYING':
            step=min(1/60,dt);self._update_step(step,movement);dt-=step
    def _update_step(self,dt,movement=None):
        if self.state!='PLAYING': return
        if movement is None:
            keys=pg.key.get_pressed(); movement=V(int(keys[pg.K_d] or keys[pg.K_RIGHT])-int(keys[pg.K_a] or keys[pg.K_LEFT]),int(keys[pg.K_s] or keys[pg.K_DOWN])-int(keys[pg.K_w] or keys[pg.K_UP]))
        self.session.update(dt,movement)
        self.record_progress()
        if self.session.result:
            self.state=self.session.result;self.offer_fusion()
        elif self.session.player.pending:
            self.state='LEVEL_UP'; self.choices=upgrades.choices(self.session.player,self.session.rng); self.sound('level')
    def record_progress(self):
        if self.save_retry_left>0:return
        if self.session.waves.completed>self.session.last_saved_wave:
            visible=set(self.save.visible_characters())
            saved=self.save.record(self.session,self.session.waves.completed>=10,finished=False)
            self.new_secrets=[k for k in self.save.visible_characters() if k not in visible]
            if saved:self.session.last_saved_wave=self.session.waves.completed
            else:self.save_retry_left=2.;return
        if self.session.result:
            if not self.recorded:
                visible=set(self.save.visible_characters());self.recorded=self.save.record(self.session,self.session.result=='VICTORY')
                self.new_secrets.extend(k for k in self.save.visible_characters() if k not in visible and k not in self.new_secrets)
                if not self.recorded:self.save_retry_left=2.
    def network_update(self,dt,movement=None):
        if movement is None:
            keys=pg.key.get_pressed();movement=V(int(keys[pg.K_d] or keys[pg.K_RIGHT])-int(keys[pg.K_a] or keys[pg.K_LEFT]),int(keys[pg.K_s] or keys[pg.K_DOWN])-int(keys[pg.K_w] or keys[pg.K_UP]))
        if self.state not in ('PLAYING','CUTSCENE'):movement=V()
        net=self.net;net.pump(dt,movement)
        if net.error:self.network_message=net.error;self.state='NETWORK_ERROR';return
        if net.session:
            self.session=net.session
            if net.match_id!=self.net_match_seen:
                self.net_match_seen=net.match_id;self.recorded=False;self.new_secrets=[]
                self.save.data['plays'][self.session.player.key]+=1;self.save.save()
            elif self.net_result_seen and not self.session.result:self.recorded=False
            self.net_result_seen=self.session.result
            self.record_progress()
            if self.session.result and self.recorded:net.command('result_ack')
        elif net.phase=='lobby':self.session=None
        if self.state in ('SETTINGS','HELP','BUILD','PAUSED','CHARACTER_SELECT') and net.phase in ('lobby','play'):return
        if net.phase=='lobby':self.state='NETWORK_LOBBY'
        elif net.phase=='cinema':self.state='CUTSCENE';self.cinematic=net.clip
        elif net.phase=='upgrade':
            self.choices=net.offers.get(net.pid,[]);self.state='LEVEL_UP' if self.choices else 'NETWORK_WAIT'
        elif net.phase=='result':self.state=self.session.result or 'NETWORK_WAIT'
        else:self.state='PLAYING';self.cinematic=None
    def button(self,rect,text,action,color=CYAN,enabled=True):
        b=Button(rect,text,action,color,enabled);self.buttons.append(b)
        old=self.hover_levels.get(action,0.);target=float(enabled and (b.rect.collidepoint(self.mouse) or action==self.ui_focus))
        blend=old+(target-old)*min(1,self.ui_dt*14);self.hover_levels[action]=blend
        b.draw(self.render,self.mouse,blend,action==self.ui_focus)
    def draw(self):
        if self.state!=self.drawn_state:
            self.ui_focus=None;self.hover_levels.clear();self.drawn_state=self.state
        r=self.render; self.buttons=[]; self.mouse=self.map_mouse(pg.mouse.get_pos())
        if self.session and self.state not in ('MAIN_MENU','CHARACTER_SELECT','MAP_SELECT','MULTIPLAYER_MENU','NETWORK_JOIN','NETWORK_LOBBY','NETWORK_ERROR','RELEASE_INFO','ANIMATION_GALLERY','CHALLENGES','BESTIARY'): r.draw_world(self.session,self.opts,self.hitboxes)
        else: r.background(self.ui_time)
        if self.state=='MAIN_MENU':interface.main(self)
        elif self.state=='RELEASE_INFO':interface.release_info(self)
        elif self.state=='ANIMATION_GALLERY':interface.animation_gallery(self)
        elif self.state=='MISSIONS':missions.draw(self)
        elif self.state in ('CHALLENGES','BESTIARY'):
            import expedition_ui
            getattr(expedition_ui,'challenges' if self.state=='CHALLENGES' else 'bestiary')(self)
        elif self.state=='CHARACTER_SELECT':interface.roster(self)
        elif self.state in ('GAME_OVER','VICTORY'):interface.end(self)
        elif self.state=='ARCHIVE':progression.draw_menu(self)
        elif self.state=='BUILD':expansion_ui.build(self)
        elif self.state=='MAP_SELECT':expansion_ui.arenas(self)
        elif self.state=='CUTSCENE' and self.cinematic:self.cinematic_renderer.draw(r,self.cinematic,self.opts)
        elif self.state in ('MULTIPLAYER_MENU','NETWORK_JOIN','NETWORK_LOBBY','NETWORK_ERROR','NETWORK_WAIT'):self.draw_network()
        elif self.state=='PAUSED':ui_screens.pause(self)
        elif self.state=='LEVEL_UP':ui_screens.level_up(self)
        elif self.state=='SETTINGS':ui_screens.settings(self)
        elif self.state=='HELP':ui_screens.help_screen(self)
        if self.state in ('SETTINGS','PLAYING','PAUSED'):
            r.text(self.music.label[:68]+'  [M / N]',22,704,16,MUTED)
        if self.net and self.net.rtt_ms is not None and self.state=='PLAYING':r.text(f'REDE {self.net.rtt_ms:.0f} ms',970,704,16,CYAN)
        if self.save.warning: r.text(self.save.warning,24,625,18,GOLD)
        if self.debug:
            s=self.session; info=f'{self.clock.get_fps():.0f} FPS | {self.state}'
            if s: info+=f' | E:{len(s.enemies)} P:{len(s.projectiles)} FX:{len(s.particles)} | {s.player.key} T:{s.player.transformed} | {int(s.player.pos.x)},{int(s.player.pos.y)}'
            r.text(info,24,124,19,GOLD)
        sw,sh=self.screen.get_size(); factor=min(sw/WIDTH,sh/HEIGHT); size=(max(1,int(WIDTH*factor)),max(1,int(HEIGHT*factor)))
        self.viewport=pg.Rect((sw-size[0])//2,(sh-size[1])//2,*size); self.screen.fill((0,0,0))
        if size==(WIDTH,HEIGHT):self.screen.blit(r.canvas,self.viewport)
        else:self.screen.blit(pg.transform.scale(r.canvas,size),self.viewport)
        pg.display.flip()
    def run(self,frames=None):
        count=0
        while self.running and (frames is None or count<frames):
            dt=min(self.clock.tick(FPS)/1000.,.15)
            for event in pg.event.get(): self.handle(event)
            self.update(dt); self.draw(); count+=1
        self.save.save()
        if self.net:self.net.close()
    def draw_network(self):ui_screens.network(self)
