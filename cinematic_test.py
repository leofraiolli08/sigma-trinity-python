"""Real cutscene rendering, secret flows, atlas masks and six-map bounds."""
import tempfile
import unittest
from pathlib import Path
import pygame as pg
from entities import V,Player
from session import GameSession
from maps import MAPS
from settings import CHARACTERS
from cinematics import Cinematic,CinematicRenderer,PROFILES
from save_manager import SaveManager
from trials import create

def defeat(s):
    for _ in range(3):
        b=s.boss;b.phase_age=8;b.phase_guard=0;s.hit(b,1e9,False);s.enemy_update(b,.01)

class CinematicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from game import Game
        pg.display.init();pg.font.init()
        cls.tmp=tempfile.TemporaryDirectory();cls.g=Game(save_path=Path(cls.tmp.name)/'save.json')
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def test_twenty_four_cinematic_signatures_are_visible_and_different(self):
        g=self.g;signatures=[]
        self.assertEqual(set(PROFILES),set(CHARACTERS));self.assertEqual(len(g.cinematic_renderer.backgrounds),3)
        for key in CHARACTERS:
            p=Player(key);p.sigma=100;p.transform()
            for kind in ('transform','ultimate'):
                c=Cinematic.player(p,kind);c.age=c.duration*.67;g.cinematic_renderer.draw(g.render,c)
                signatures.append(pg.image.tobytes(g.render.canvas,'RGB'))
        self.assertEqual(len(set(signatures)),len(CHARACTERS)*2)
    def test_world_and_form_freeze_and_ultimate_occurs_after_cutscene_once(self):
        g=self.g;g.menu();g.start('davi');s=g.session;s.player.sigma=100
        g.combat_action('transform');t=s.time;left=s.player.form_left
        g.update(.1,V(1,0));self.assertEqual(s.time,t);self.assertEqual(s.player.form_left,left)
        g.finish_cinematic();g.combat_action('ultimate');self.assertEqual(s.player.ultimates,0)
        g.finish_cinematic();self.assertEqual(s.player.ultimates,1)
        g.combat_action('ultimate');self.assertEqual(g.state,'PLAYING');self.assertEqual(s.player.ultimates,1)
    def test_question_mode_boss_victory_unlocks_first_secret(self):
        g=self.g;g.save.data=__import__('save_manager').defaults();g.opts=g.save.data['settings'];g.menu();g.draw()
        self.assertFalse(any(b.action=='trial' for b in g.buttons))
        g.save.data['wins'].update(leo=1,guxta=1,zatex=1);g.menu();g.draw()
        button=next(b for b in g.buttons if b.action=='trial');self.assertEqual(button.text,'???')
        self.assertFalse(g.save.is_unlocked('leozauxta'));g.action('trial');g.action('char:leo')
        self.assertEqual(g.state,'CUTSCENE');self.assertEqual(g.session.challenge,'leozauxta')
        g.finish_cinematic();defeat(g.session);g.update(.01,V())
        self.assertEqual(g.state,'VICTORY');self.assertTrue(g.save.is_unlocked('leozauxta'))
        self.assertEqual(g.save.data['wins']['leo'],1);before=g.save.data['coins'];g.update(.1)
        self.assertEqual(g.save.data['coins'],before);self.assertTrue(SaveManager(g.save.path).is_unlocked('leozauxta'))
    def test_fusion_auto_selection_then_scene_and_fight(self):
        g=self.g;g.save.data=__import__('save_manager').defaults();g.opts=g.save.data['settings']
        g.save.data['wins'].update(leo=1,guxta=1,zatex=1,leozauxta=1);g.save.data['secret_clears']=['leozauxta']
        g.menu();g.start('davi');s=g.session;s.waves.completed=10;s.result='VICTORY';g.update(.01,V())
        self.assertEqual(g.state,'CHARACTER_SELECT');self.assertEqual(g.pending_trial,'leozauxtaci')
        self.assertFalse(g.save.is_unlocked('leozauxtaci'));g.action('char:musashi')
        self.assertEqual(g.state,'CUTSCENE');self.assertEqual(g.cinematic.kind,'fusion')
        for age in (1.,3.,5.5):g.cinematic.age=age;g.draw()
        g.finish_cinematic();self.assertEqual(g.session.boss.trial_key,'leozauxtaci')
        defeat(g.session);g.update(.01,V());self.assertTrue(g.save.is_unlocked('leozauxtaci'))
    def test_failed_trial_does_not_unlock(self):
        with tempfile.TemporaryDirectory() as tmp:
            save=SaveManager(Path(tmp)/'s.json');save.data['wins'].update(leo=1,guxta=1,zatex=1)
            s=create('leo','leozauxta');s.hurt_player(9999);save.record(s,False)
            self.assertFalse(save.is_unlocked('leozauxta'));self.assertTrue(save.challenge_available('leozauxta'))
    def test_all_map_edges_block_players_and_spawn_charging_monsters_inside(self):
        for key in MAPS:
            s=GameSession('davi',91,map_key=key);s.waves.started=True;s.waves.remaining=99;s.spawn_cd=999;s.hazard_cd=999
            b=s.arena.bounds;s.player.pos=s.arena.constrain(V(b.left,b.top),s.player.radius);s.player.invulnerable=999
            for _ in range(80):
                s.update(.05,V(-1,-1));self.assertTrue(s.arena.contains(s.player.pos,s.player.radius))
            for kind in range(6):
                e=s.spawn(kind=kind,elite=True)
                self.assertTrue(s.arena.contains(e.pos,e.radius));self.assertGreater(e.pos.distance_to(s.player.pos),400)
                e.charge_left=1;e.charge_dir=V(-1,-1).normalize()
                for _ in range(20):s.enemy_update(e,.05);self.assertTrue(s.arena.contains(e.pos,e.radius))
    def test_enemy_facing_uses_movement_including_retreat_and_charge(self):
        s=GameSession('leo');s.waves.started=True;s.waves.remaining=99;s.spawn_cd=999;s.hazard_cd=999
        e=s.spawn(kind=1,pos=s.player.pos+V(100,0));e.cooldown=999
        s.update(.05);self.assertFalse(e.facing_left) # retreats right despite player to its left
        e.charge_left=1;e.charge_dir=V(-1,0);s.update(.05);self.assertTrue(e.facing_left)
        e.charge_dir=V(0,1);s.update(.05);self.assertTrue(e.facing_left)
    def test_ua_cells_have_one_isolated_silhouette_without_backdrop(self):
        a=self.g.assets
        from pixel_style import GROUPS
        for group,boxes in GROUPS.items():
            for i in range(len(boxes)):
                im=a.images[f'ua_{group}_{i}'];mask=pg.mask.from_surface(im,8)
                self.assertEqual(len(mask.connected_components(20)),1,(group,i))
                self.assertLess(mask.count()/(im.get_width()*im.get_height()),.88,(group,i))
    def test_native_left_art_is_normalized_and_vertical_direction_persists(self):
        r=self.g.render;p=Player('leo');p.update(.05,V(1,0))
        self.assertTrue(r.actor_flip(p.sprite(0),p.facing_left))
        p.update(.05,V(-1,0));self.assertFalse(r.actor_flip(p.sprite(0),p.facing_left))
        p.update(.05,V(0,1));self.assertTrue(p.facing_left)
        ippo=Player('ippo');self.assertFalse(r.actor_flip(ippo.sprite(0),False))
    def test_multiplayer_menu_keyboard_build_cutscene_and_saved_rewards(self):
        from game import Game
        g=self.g;g.save.data=__import__('save_manager').defaults();g.opts=g.save.data['settings'];g.menu();g.selected='leo'
        g.action('multiplayer');g.draw();self.assertTrue(any(b.action=='network_host' for b in g.buttons))
        client=Game(save_path=Path(self.tmp.name)/'client.json')
        try:
            g.action('network_host');self.assertFalse(g.net.error)
            client.network_target='127.0.0.1:'+str(g.net.port);client.action('network_connect')
            def pump(n=20):
                for _ in range(n):g.update(.02,V());client.update(.02,V())
            pump(50);self.assertEqual(client.state,'NETWORK_LOBBY');g.draw();client.draw()
            g.action('network_ready');client.action('network_ready');pump();g.action('network_start');pump()
            self.assertEqual(g.state,'PLAYING');self.assertEqual(client.state,'PLAYING')
            client.handle(pg.event.Event(pg.KEYDOWN,key=pg.K_TAB));pump(5);self.assertEqual(client.state,'BUILD');client.draw()
            client.action('resume');g.session.owner(client.net.pid).sigma=100;pump(5)
            client.handle(pg.event.Event(pg.KEYDOWN,key=pg.K_e));pump(5);self.assertEqual(client.state,'CUTSCENE');client.draw()
            client.handle(pg.event.Event(pg.KEYDOWN,key=pg.K_RETURN));pump(5);self.assertEqual(client.state,'PLAYING')
            s=g.session;s.waves.number=10;s.waves.completed=10;s.result='VICTORY';pump(5)
            self.assertEqual(g.state,'VICTORY');self.assertEqual(client.state,'VICTORY');client.draw()
            coins=client.save.data['coins'];pump(5);self.assertEqual(client.save.data['coins'],coins)
            self.assertEqual(client.save.data['wins']['leo'],1)
            g.action('endless');pump(5);self.assertEqual(client.state,'PLAYING');self.assertTrue(client.session.waves.endless)
            s.kills+=4;s.coins+=12;s.result='GAME_OVER';pump(5)
            self.assertEqual(client.state,'GAME_OVER');self.assertGreater(client.save.data['coins'],coins)
            self.assertEqual(client.save.data['wins']['leo'],1)
            g.action('network_restart');pump(5);self.assertEqual(client.state,'NETWORK_LOBBY');self.assertIsNone(client.session)
        finally:
            if client.net:client.net.close();client.net=None
            g.menu()
