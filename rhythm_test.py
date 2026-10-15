import unittest
import pygame as pg
from entities import V
from session import GameSession
from rhythm import Rhythm
from settings import BASE_DIR

class RhythmTests(unittest.TestCase):
    def test_hit_miss_repeat_and_expiry(self):
        r=Rhythm();r.start();r.update(1.,True)
        self.assertTrue(r.tap(0));self.assertTrue(r.protected);self.assertEqual(r.combo,1)
        self.assertFalse(r.tap(0));self.assertFalse(r.protected)
        r.update(1.48,True);self.assertTrue(r.tap(1));self.assertTrue(r.protected)
        r.update(2.2,True);self.assertFalse(r.protected);self.assertGreater(r.misses,1)
        r.update(2.44,True);self.assertTrue(r.tap(3));r.update(14,False);self.assertFalse(r.protected)
    def test_global_damage_swarm_and_immunity(self):
        s=GameSession('leozauxta');p=s.player;p.sigma=100;s.transform();s.transform_pause=0
        near=s.spawn(kind=3,pos=p.pos+V(200,0));far=s.spawn(kind=3,pos=V(3400,3400));near.hp=far.hp=10000
        p.form_age=1;s.rhythm.update(1,True);self.assertTrue(s.rhythm_tap(0))
        self.assertLess(near.hp,10000);self.assertLess(far.hp,10000);self.assertTrue(any(a.kind=='swarm' for a in s.areas))
        p.invulnerable=0;hp=p.hp;s.hurt_player(1000);self.assertEqual(hp,p.hp)
        s.rhythm_tap(2);s.hurt_player(10);self.assertLess(p.hp,hp)
        p.form_left=0;self.assertFalse(s.rhythm_tap(1))
    def test_chart_is_reachable_without_missing(self):
        r=Rhythm();r.start()
        for note in r.notes:
            r.update(note.time,True);self.assertTrue(r.tap(note.lane))
        self.assertEqual(r.hits,27);self.assertEqual(r.misses,0);self.assertEqual(r.best,27)
    def test_pause_and_real_keyboard_routing(self):
        from game import Game
        from pathlib import Path
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            g=Game(save_path=Path(d)/'save.json');g.save.data['wins'].update(leo=1,guxta=1,zato=1);g.save.data['secret_clears']=['leozauxta'];g.start('leozauxta');s=g.session;s.player.sigma=100;s.transform();s.transform_pause=0
            s.player.form_age=1;s.rhythm.update(1,True)
            g.handle(pg.event.Event(pg.KEYDOWN,key=pg.K_d));self.assertEqual(s.rhythm.hits,1)
            g.handle(pg.event.Event(pg.KEYDOWN,key=pg.K_d,repeat=True));self.assertEqual(s.rhythm.misses,0)
            g.state='PAUSED';age=s.rhythm.age
            for _ in range(10):g.update(.05)
            self.assertEqual(s.rhythm.age,age)
            g.start('leo');self.assertFalse(g.session.rhythm.active)
    def test_walter_evolution_and_two_distinct_forms(self):
        s=GameSession('walter');p=s.player;s.spawn_cd=999;s.hazard_cd=999;p.sigma=100;s.transform()
        self.assertEqual(p.form_name,'TRAJE HAZMAT');self.assertTrue(p.sprite(0).startswith('hazmat'))
        s.time=151;s.transform_pause=0;s.update(.05);self.assertFalse(p.evolved)
        p.form_left=.01;s.update(.05);self.assertTrue(p.evolved);self.assertEqual(p.display_name,'HEISENBERG')
        self.assertTrue(p.sprite(0).startswith('heisenberg'));damage=p.base_damage;s.update(.05);self.assertEqual(p.base_damage,damage)
        p.form_recovery=0;p.sigma=100;s.transform();self.assertEqual(p.form_name,'FELINA');self.assertTrue(p.sprite(0).startswith('felina'))
        e=s.spawn(kind=3,pos=p.pos+V(200,0));s.weapon.fire(s,e);self.assertEqual(s.projectiles[-1].kind,'bullet')
    def test_all_atlas_variants_load_and_player_art_stays_smooth(self):
        from asset_generator import AssetManager
        from pixel_style import GROUPS,enemy_sprite
        a=AssetManager()
        for group,boxes in GROUPS.items():
            for i in range(len(boxes)):
                name=f'ua_{group}_{i}';self.assertIn(name,a.images)
                im=a.images[name];self.assertLess(pg.mask.from_surface(im).count(),im.get_width()*im.get_height())
        for key in ('leo_walk_0','rafael_walk_0','leozauxta_0','davi_walk_0'):self.assertIn(key,a.art_names)
        for key in ('walter_0','hazmat_0','heisenberg_0','felina_0','enemy_0_0','boss_0'):
            self.assertIn(key,a.images);self.assertNotIn(key,a.art_names)
        s=GameSession('leo');e=s.spawn(kind=0,pos=V(200,200))
        self.assertTrue(enemy_sprite(e,0,'usj').startswith('ua_'))
        self.assertFalse(enemy_sprite(e,0,'crypt').startswith('ua_'))
