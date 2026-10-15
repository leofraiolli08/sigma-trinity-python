"""Integration tests use real pygame surfaces, simulation and UI transitions."""
import os
import json
import tempfile
import unittest
from pathlib import Path
import pygame as pg
from entities import V,Player,Projectile,Area,Pickup,segment_distance
from session import GameSession
from save_manager import SaveManager
from asset_generator import AssetManager,generated
from settings import CHARACTERS,MAX_PROJECTILES,MAX_PARTICLES,MAX_ENEMIES,RUN_DURATION
import upgrades

def finish_boss(s):
    s.waves.number=10;s.waves.started=True
    # Explicitly traverse phase guards; phase behavior itself has separate tests.
    for _ in range(3):
        s.boss.phase_age=8; s.boss.phase_guard=0; s.hit(s.boss,1e9,False); s.enemy_update(s.boss,.01)

class SimulationTests(unittest.TestCase):
    def test_all_transforms_preserve_progress_and_expire(self):
        for key in CHARACTERS:
            s=GameSession(key,1); p=s.player; p.sigma=100; p.level=8; p.power=2; pos=V(p.pos)
            self.assertTrue(s.transform()); self.assertFalse(s.transform())
            self.assertEqual(p.transforms,1); self.assertEqual(p.level,8); self.assertEqual(p.power,2)
            self.assertEqual(p.pos,pos); self.assertTrue(p.transformed)
            self.assertIn(p.sprite(0),generated())
            p.update(15.1,V()); self.assertFalse(p.transformed); self.assertGreater(p.hp,0); self.assertLessEqual(p.hp,p.max_hp)
            self.assertEqual(p.level,8); self.assertEqual(p.power,2)
    def test_each_ultimate_single_use_and_damage(self):
        for key in CHARACTERS:
            s=GameSession(key,2); s.spawn_cd=999; e=s.spawn(kind=3,pos=s.player.pos+V(120,0)); e.hp=e.max_hp=100000
            s.player.sigma=100; s.transform(); s.transform_pause=0
            self.assertTrue(s.ultimate()); self.assertFalse(s.ultimate())
            for _ in range(90): s.update(.05)
            self.assertGreater(s.total_damage,0); self.assertEqual(s.player.ultimates,1)
            if key=='leozauxta': self.assertEqual(s.events['dance_pulses'],6)
    def test_skills_and_dance_gameplay(self):
        for key in CHARACTERS:
            s=GameSession(key); e=s.spawn(kind=3,pos=s.player.pos+V(80,0)); e.hp=100000
            for i in range(3): s.weapon.skill_index=i; s.weapon.skill(s,e)
            self.assertTrue(s.projectiles or s.telegraphs or s.areas or s.effects)
            s.player.sigma=100; s.transform(); s.transform_pause=0
            before=s.total_damage; s.weapon.passive(s)
            if key in ('leo','leozauxta'): self.assertGreater(s.total_damage,before)
    def test_auto_attack_requires_live_target(self):
        s=GameSession('leo'); s.weapon.update(s,.1); self.assertEqual(len(s.projectiles),0)
        e=s.spawn(kind=0,pos=s.player.pos+V(70,0)); s.weapon.update(s,1); self.assertGreater(len(s.projectiles),0)
        e.dead=True; self.assertIsNone(s.nearest(e.pos))
    def test_damage_reward_once_and_xp_collection(self):
        s=GameSession('leo'); e=s.spawn(kind=0,pos=s.player.pos)
        s.hit(e,9999); s.hit(e,9999); self.assertEqual(s.kills,1)
        xp=sum(q.value for q in s.pickups if q.kind=='xp'); self.assertEqual(xp,3)
        s.spawn_cd=999; s.update(.01); self.assertEqual(s.player.xp,3); s.update(.01); self.assertEqual(s.player.xp,3)
    def test_levels_queue_without_lost_xp(self):
        p=Player('rafael'); p.xp_gain(100); self.assertEqual(p.level,4); self.assertEqual(p.pending,3); self.assertEqual(p.xp,28)
    def test_swept_collision_and_piercing_once(self):
        s=GameSession('leo'); p=s.player; e=s.spawn(kind=0,pos=p.pos+V(10,0)); e.hp=10000
        q=Projectile(V(p.pos),V(1000,0),10,'crumb',pierce=3)
        s.projectile_update(q,.05); before=e.hp; self.assertLess(before,10000)
        q.pos=V(p.pos); s.projectile_update(q,.05); self.assertEqual(before,e.hp)
        self.assertEqual(segment_distance(V(2,0),V(),V()),2)
    def test_ricochet_homing_dead_targets(self):
        s=GameSession('rafael'); p=s.player; e=s.spawn(kind=0,pos=p.pos+V(20,0)); b=s.spawn(kind=1,pos=p.pos+V(80,0))
        q=Projectile(V(p.pos),V(400,0),2,'pacoca',bounce=2,homing=True)
        s.projectile_update(q,.05); self.assertIn(e.uid,q.hit); self.assertFalse(q.dead)
        b.dead=True; s.projectile_update(q,.05)
    def test_boss_immune_to_root_phase_and_once(self):
        s=GameSession('leo'); b=s.spawn(boss=True,pos=s.player.pos+V(200,0))
        self.assertIs(s.spawn(boss=True),b); self.assertEqual(sum(e.boss for e in s.enemies),1)
        b.glue(100,.99,True); self.assertEqual(b.root,0); self.assertGreaterEqual(b.slow_factor,.75)
        b.hp=b.max_hp*.49; b.phase_age=8; s.enemy_update(b,.01); b.phase_guard=0; self.assertEqual(b.phase,2); self.assertLess(b.hp,b.max_hp*.5)
        for i in range(4): b.cooldown=0; s.enemy_update(b,.01)
        self.assertTrue({'boss_ring','charge','hostile_blast','summon'}.issubset({t.kind for t in s.telegraphs}))
        for t in list(s.telegraphs): s.resolve_telegraph(t)
        self.assertTrue(any(q.hostile for q in s.projectiles)); self.assertGreater(b.charge_left,0)
        finish_boss(s); self.assertEqual(s.result,'VICTORY')
    def test_no_permanent_common_root(self):
        e=GameSession('leo').spawn(kind=0,pos=V())
        e.glue(1,.8,True); e.tick_status(.8); e.glue(1,.8,True); self.assertEqual(e.root,0)
    def test_dash_iframes_and_cooldown(self):
        s=GameSession('leozauxta'); self.assertTrue(s.dash()); self.assertFalse(s.dash())
        old=s.player.hp; s.hurt_player(9999); self.assertEqual(s.player.hp,old)
        s.player.update(.3,V()); s.hurt_player(9999); self.assertEqual(s.result,'GAME_OVER')
    def test_zero_vector_and_dt(self):
        s=GameSession('leo'); s.spawn_cd=999
        s.spawn(kind=0,pos=s.player.pos); s.update(100,V()); self.assertLessEqual(s.time,.05)
    def test_entity_caps(self):
        s=GameSession('rafael')
        for _ in range(400): s.fragments(s.player.pos,20,10)
        self.assertEqual(len(s.projectiles),MAX_PROJECTILES)
        s.particles_at(s.player.pos,(255,255,255),9999); self.assertEqual(len(s.particles),MAX_PARTICLES)
        for _ in range(80): s.add_area(Area(V(),50,3,'glue'))
        self.assertLessEqual(len(s.areas),48)
        for _ in range(200): s.spawn()
        self.assertEqual(len(s.enemies),MAX_ENEMIES)
    def test_spawn_outside_screen(self):
        s=GameSession('leo'); p=s.player
        for _ in range(100):
            e=s.spawn(); delta=e.pos-p.pos
            self.assertGreater(delta.length(),800); self.assertTrue(abs(delta.x)>640 or abs(delta.y)>395)
    def test_all_upgrades_valid(self):
        for key in CHARACTERS:
            for u in upgrades.UPGRADES:
                if u.character in ('all',key) and upgrades.eligible(Player(key),u):
                    p=Player(key);old=getattr(p,u.stat)
                    if u.stat=='aux':
                        upgrades.apply(p,(u,upgrades.RARITIES[0]));self.assertEqual(p.aux[u.id[4:]],1)
                    else:
                        upgrades.apply(p,(u,upgrades.RARITIES[0]));self.assertGreater(getattr(p,u.stat),old)
            for u,_ in upgrades.choices(p,__import__('random').Random(1)): self.assertIn(u.character,('all',key))
    def test_seed_reproducible(self):
        a=GameSession('leo',123); b=GameSession('leo',123)
        for _ in range(80): a.update(.02,V(1,0)); b.update(.02,V(1,0))
        self.assertEqual(a.time,b.time); self.assertEqual([e.pos for e in a.enemies],[e.pos for e in b.enemies])
    def test_sustained_simulation_all_characters(self):
        for key in CHARACTERS:
            s=GameSession(key,97)
            # Test-only invulnerability, orbit and healing; not a balance claim.
            for i in range(6700):
                p=s.player; p.invulnerable=1; p.hp=p.max_hp
                if p.pending: upgrades.apply(p,upgrades.choices(p,s.rng)[0]); p.pending-=1
                if p.sigma>=100: s.transform()
                if p.transformed: s.ultimate()
                target=s.nearest(p.pos,5000)
                movement=(target.pos-p.pos).normalize() if target and target.pos.distance_to(p.pos)>40 else V(1,0).rotate(i*.7)
                s.update(.05,movement)
            self.assertGreater(s.kills,20); self.assertGreater(p.level,1)
            self.assertLessEqual(len(s.projectiles),MAX_PROJECTILES); self.assertLessEqual(len(s.particles),MAX_PARTICLES)
            if not s.result:
                s.spawn(boss=True);finish_boss(s)
            self.assertEqual(s.result,'VICTORY')

class PersistenceTests(unittest.TestCase):
    def test_save_roundtrip_bad_json_and_types(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'save.json'; sm=SaveManager(path); sm.data['high_score']=543; self.assertTrue(sm.save())
            self.assertEqual(SaveManager(path).data['high_score'],543)
            for content in ('{bad','[]','{"settings":null,"plays":4,"high_score":"x"}', '{"high_score":NaN,"settings":{"volume":Infinity}}'):
                path.write_text(content); sm=SaveManager(path); self.assertEqual(sm.data['high_score'],0); self.assertEqual(sm.data['settings']['volume'],.45)
    def test_asset_regeneration_and_corrupt_png(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); a=AssetManager(root); self.assertGreater(len(a.images),50)
            p=root/'sprites'/'characters'/'leo_walk_0.png'; p.unlink(); b=AssetManager(root); self.assertTrue(p.exists())
            p.write_bytes(b'not png'); c=AssetManager(root); self.assertEqual(c.images['leo_walk_0'].get_size(),(48,64))
            self.assertTrue((root/'sounds'/'victory.wav').exists())

class UITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from game import Game
        cls.tmp=tempfile.TemporaryDirectory(); cls.g=Game(seed=42,save_path=Path(cls.tmp.name)/'save.json')
    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()
    def test_complete_ui_flow_and_actual_renders(self):
        g=self.g; g.menu(); g.draw(); self.assertEqual(g.state,'MAIN_MENU')
        # A real mouse event on the real, rendered play button.
        b=g.buttons[0]; g.handle(pg.event.Event(pg.MOUSEBUTTONDOWN,button=1,pos=b.rect.center)); self.assertEqual(g.state,'CHARACTER_SELECT'); g.draw()
        g.save.data['wins'].update(leo=1,guxta=1,zato=1,zatex=1,davi=1,leozauxta=1)
        g.save.data['secret_clears']=['leozauxta','leozauxtaci'];g.save.data['fusion_offered']=True
        for key in CHARACTERS:
            g.action('char:'+key); g.draw(); self.assertEqual(g.state,'MAP_SELECT'); g.action('map:usj'); g.draw(); s=g.session
            s.player.xp_gain(17); g.update(.01,V()); self.assertEqual(g.state,'LEVEL_UP'); g.draw()
            g.handle(pg.event.Event(pg.KEYDOWN,key=pg.K_1)); self.assertEqual(g.state,'PLAYING')
            s.player.sigma=100; g.handle(pg.event.Event(pg.KEYDOWN,key=pg.K_e)); g.draw(); s.transform_pause=0
            self.assertEqual(g.state,'CUTSCENE');g.handle(pg.event.Event(pg.KEYDOWN,key=pg.K_RETURN))
            g.handle(pg.event.Event(pg.KEYDOWN,key=pg.K_q));self.assertEqual(g.state,'CUTSCENE')
            g.handle(pg.event.Event(pg.KEYDOWN,key=pg.K_RETURN));self.assertEqual(s.player.ultimates,1)
            for _ in range(20): g.update(.05,V()); g.draw()
            g.handle(pg.event.Event(pg.KEYDOWN,key=pg.K_ESCAPE)); self.assertEqual(g.state,'PAUSED'); g.draw()
            time=s.time; form=s.player.form_left; cd=s.weapon.skill_cd
            for _ in range(10): g.update(.05,V(1,0))
            self.assertEqual((time,form,cd),(s.time,s.player.form_left,s.weapon.skill_cd))
            g.open_settings(); g.draw(); g.action('shake'); g.action('numbers'); g.action('volume'); g.back(); self.assertEqual(g.state,'PAUSED')
            g.action('resume'); s.player.invulnerable=0; s.player.guard_cd=12; s.hurt_player(100000); g.update(.01,V()); self.assertEqual(g.state,'GAME_OVER'); g.draw()
            old=s; g.action('restart'); self.assertIsNot(old,g.session); self.assertEqual(len(g.session.projectiles),0); self.assertFalse(g.session.boss_spawned)
            b=g.session.spawn(boss=True); finish_boss(g.session); g.update(.01,V()); self.assertEqual(g.state,'VICTORY'); g.draw()
            wins=g.save.data['wins'][key]; g.update(.01,V()); self.assertEqual(g.save.data['wins'][key],wins)
            g.menu(); g.draw(); self.assertIsNone(g.session)
        g.action('help'); g.draw(); g.back(); self.assertEqual(g.state,'MAIN_MENU')
    def test_resize_fullscreen_preserves_session(self):
        g=self.g; g.start('leo'); s=g.session
        g.handle(pg.event.Event(pg.VIDEORESIZE,w=900,h=600)); g.draw(); self.assertIs(g.session,s)
        g.toggle_fullscreen(); g.draw(); self.assertIs(g.session,s)
        g.toggle_fullscreen(); g.draw(); self.assertIs(g.session,s)
        self.assertEqual(g.map_mouse(g.viewport.center),(640,360))
    def test_audio_device_failure(self):
        from unittest.mock import patch
        from game import Game
        pg.mixer.quit()
        with patch("pygame.mixer.init",side_effect=pg.error("No audio device")):
            silent=Game(save_path=Path(self.tmp.name)/"silent.json")
            silent.sound("ultimate"); silent.draw()
            self.assertFalse(pg.mixer.get_init())

    def test_headless_real_loop(self):
        g=self.g; g.menu(); g.running=True; g.run(frames=4); self.assertTrue(g.running)
        g.handle(pg.event.Event(pg.QUIT)); self.assertFalse(g.running)

def run():
    os.environ['SDL_VIDEODRIVER']='dummy'; os.environ['SDL_AUDIODRIVER']='dummy'
    pg.display.init(); pg.font.init(); pg.display.set_mode((1280,720))
    suite=unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__))
    import guxta_test
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(guxta_test))
    import rhythm_test
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(rhythm_test))
    import expansion_test
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(expansion_test))
    import art_test
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(art_test))
    import ascension_test
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(ascension_test))
    import waves_test
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(waves_test))
    import musashi_test
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(musashi_test))
    import visual_upgrade_test
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(visual_upgrade_test))
    import coop_test,cinematic_test,installation_test
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(coop_test))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(cinematic_test))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(installation_test))
    import network_test,animation_test
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(network_test))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(animation_test))
    import audit_test
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(audit_test))
    import audit_ui_test
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(audit_ui_test))
    import expedition_test
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(expedition_test))
    import evolution_art_test
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(evolution_art_test))
    result=unittest.TextTestRunner(verbosity=2).run(suite); pg.quit()
    if not result.wasSuccessful(): raise SystemExit(1)
    print('SELF TEST: OK')
