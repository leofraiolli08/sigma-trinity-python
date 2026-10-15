"""Repeatable offscreen presentation checks. Writes only QA captures, not a player save."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import tempfile,statistics,time
from pathlib import Path
import pygame as pg
from game import Game
from entities import V
from ascension import tick,RECIPES
from upgrades import choices
from settings import BASE_DIR

def run():
    output=BASE_DIR/'preview/waves';output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        g=Game(save_path=Path(tmp)/'save.json')
        def capture(name):
            g.draw();target=output/(name+'.png');staging=output/(name+'.stage.png')
            with staging.open('wb') as handle:
                pg.image.save(g.render.canvas,handle,'png');handle.flush();os.fsync(handle.fileno())
            pg.image.load(str(staging));staging.replace(target)
        for state,name in [('MAIN_MENU','menu'),('CHARACTER_SELECT','personagens'),('MAP_SELECT','arenas'),('ARCHIVE','conquistas'),('MISSIONS','missoes')]:
            g.state=state;capture(name)
        g.roster_page=1;g.state='CHARACTER_SELECT';g.focus_character='zatex';capture('zatex_roster')
        g.save.data['wins'].update(leo=1,guxta=1,zatex=1,davi=1,leozauxta=1)
        g.save.data['secret_clears']=['leozauxta','leozauxtaci'];g.save.data['fusion_offered']=True
        g.roster_page=1;g.state='CHARACTER_SELECT';g.focus_character='musashi';capture('musashi_roster')
        g.state='SETTINGS';capture('settings_visual')
        from cinematics import Cinematic
        for key in ('leo','rafael','leozauxta','davi','walter','guxta','ippo','eren','klein','zatex','leozauxtaci','musashi'):
            g.start(key);p=g.session.player;p.sigma=100;p.transform()
            for kind in ('transform','ultimate'):
                g.cinematic=Cinematic.player(p,kind);g.cinematic.age=g.cinematic.duration*.67;g.state='CUTSCENE';capture('cinema_'+key+'_'+kind)
        for age in (1,3,5):
            g.cinematic=Cinematic('leozauxtaci','fusion');g.cinematic.age=age;g.state='CUTSCENE';capture('fusao_'+str(age))
        g.cinematic=None
        for arena in ('crypt','usj','city','ring','walls','fog'):
            g.map_key=arena;g.start('leo');s=g.session;p=s.player
            for i in range(6):s.spawn(kind=i,pos=p.pos+V(160+i*31,0).rotate(i*60))
            s.spawn(boss=True,pos=p.pos+V(290,-90))
            capture('arena_'+arena)
            p.pos=s.arena.constrain(V(0,0),p.radius);capture('barreira_'+arena)
        for key,arena in [('leo','crypt'),('rafael','city'),('davi','usj'),('walter','city'),('guxta','fog'),('zatex','fog'),('leozauxtaci','crypt'),('ippo','ring'),('eren','walls'),('klein','city'),('musashi','ring')]:
            g.map_key=arena;g.start(key);s=g.session;p=s.player;p.level=15 if key=='musashi' else 10;tick(s,.01)
            p.sigma=100;s.transform();s.transform_pause=0;s.spawn_cd=999;s.hazard_cd=999
            for i in range(22):
                e=s.spawn(kind=i%6,pos=p.pos+V(90+i*15,0).rotate(i*137));e.hp=e.max_hp=5000
            s.ultimate()
            for _ in range(12):p.invulnerable=1;s.update(.025)
            capture(key)
        s.waves.number=10;s.waves.completed=10;s.result='VICTORY';g.save.record(s,True)
        g.state='VICTORY';capture('vitoria');g.action('endless');g.state='PLAYING';s.waves.number=11;capture('infinito')
        p.aux={key:4 for key in ('knives','lightning','seals','bell','embers')};p.evolutions={'lightning','knives'}
        p.upgrades.update({'aux_'+key:4 for key in p.aux})
        g.state='BUILD';capture('build')
        g.state='LEVEL_UP';g.choices=choices(p,s.rng);capture('melhorias')
        from boss_patterns import queue
        for arena,pattern in (('crypt',2),('usj',2),('city',1),('ring',1),('walls',1),('fog',0)):
            g.map_key=arena;g.start('musashi');s=g.session;p=s.player
            boss=s.spawn(boss=True,pos=p.pos+V(-270,0));boss.phase=3
            queue(s,boss,p,pattern);capture('chefe_'+arena)
        g.map_key='ring';g.start('musashi');s=g.session;p=s.player
        for i in range(22):
            e=s.spawn(kind=i%6,pos=p.pos+V(90+i*15,0).rotate(i*137));e.hp=e.max_hp=5000
        p.aux={key:4 for key in ('knives','lightning','seals','bell','embers')};s.waves.started=True;s.waves.remaining=0;s.hazard_cd=999
        g.state='PLAYING'
        for _ in range(5):s.update(.016);g.draw()
        durations=[]
        for _ in range(120):
            start=time.perf_counter();p.invulnerable=1;s.update(1/60);g.draw();durations.append((time.perf_counter()-start)*1000)
        print('QA frame (headless, 22 alvos, 5 auxiliares): mediana %.2f ms; p95 %.2f ms' %(statistics.median(durations),sorted(durations)[113]))
        g.menu();g.action('multiplayer');capture('multiplayer_menu');g.action('network_join');g.network_target='127.0.0.1:47640';capture('multiplayer_entrar')
        g.action('network_host')
        from multiplayer import Multiplayer
        clients=[Multiplayer(g.save,key,target='127.0.0.1:'+str(g.net.port)) for key in ('ippo','davi','klein')]
        for _ in range(60):
            g.update(.02,V())
            for c in clients:c.pump(.02)
        assert len(g.net.members)==4 and not g.net.error
        capture('multiplayer_sala');g.action('network_ready')
        for c in clients:c.command('ready')
        for _ in range(15):
            g.update(.02,V())
            for c in clients:c.pump(.02)
        g.action('network_start')
        for _ in range(20):
            g.update(.02,V())
            for c in clients:c.pump(.02)
        capture('multiplayer_partida')
        for c in clients:c.close()
        g.menu()
        from pixel_style import GROUPS
        atlas=pg.Surface((1000,len(GROUPS)*100));atlas.fill((24,30,40))
        for row,(group,boxes) in enumerate(GROUPS.items()):
            atlas.blit(g.assets.font(20).render(group,True,(235,230,215)),(5,row*100+5))
            for i in range(len(boxes)):
                im=g.assets.sprite(f'ua_{group}_{i}',1.);atlas.blit(im,im.get_rect(midbottom=(150+i*140,row*100+96)))
        with (output/'ua_recortes.png').open('wb') as file:pg.image.save(atlas,file,'png')
        print('Capturas:',output)
    pg.quit()

if __name__=='__main__':run()
