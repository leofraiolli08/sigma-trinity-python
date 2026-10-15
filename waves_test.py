"""Progression regression: real wave controller, persistence and menu routing."""
import tempfile,unittest,random
from pathlib import Path
import pygame as pg
from entities import V,Pickup,Projectile,segment_distance
from session import GameSession
from save_manager import SaveManager
from missions import unlocked,MISSIONS
from waves import FAMILIES

class WavesTests(unittest.TestCase):
    def test_ten_waves_then_optional_endless(self):
        s=GameSession('zatex');s.waves.begin(s)
        for number in range(1,10):
            self.assertEqual(s.waves.number,number)
            count=0
            while s.waves.remaining:
                s.spawn_cd=0;s.waves.update(s,.01);count+=1
                for e in list(s.enemies):s.hit(e,1e9,False)
            s.waves.update(s,.01)
            self.assertEqual(count,8+number*4);self.assertEqual(s.waves.completed,number)
            s.waves.update(s,3)
        self.assertTrue(s.boss.boss);self.assertEqual(s.waves.number,10)
        for _ in range(3):
            b=s.boss;b.phase_age=8;b.phase_guard=0;s.hit(b,1e9,False);s.enemy_update(b,.01)
        self.assertEqual(s.result,'VICTORY');self.assertEqual(s.waves.completed,10)
        coins=s.coins;s.waves.clear(s);self.assertEqual(s.coins,coins)
        self.assertTrue(s.waves.continue_endless(s));self.assertFalse(s.waves.continue_endless(s))
        s.waves.update(s,3);self.assertEqual(s.waves.number,11);self.assertIsNone(s.result)
        s.enemies.clear();s.waves.number=20;s.waves.begin(s)
        self.assertGreater(s.boss.max_hp,15000)
        for _ in range(3):
            b=s.boss;b.phase_age=8;b.phase_guard=0;s.hit(b,1e9,False);s.enemy_update(b,.01)
        self.assertIsNone(s.result);self.assertEqual(s.waves.completed,20)

    def test_checkpoint_reload_and_endless_death_no_duplicate(self):
        with tempfile.TemporaryDirectory() as d:
            save=SaveManager(Path(d)/'save.json');s=GameSession('zatex')
            s.kills=25;s.coins=12;s.waves.completed=1
            save.record(s,False,False);first=save.data['coins'];save.record(s,False,False)
            self.assertEqual(save.data['coins'],first);self.assertEqual(save.data['lifetime_kills'],25)
            self.assertEqual(SaveManager(save.path).data['coins'],first)
            s.waves.completed=10;s.coins+=100;save.record(s,True,False)
            won=save.data['coins'];save.record(s,True)
            self.assertEqual(save.data['coins'],won);self.assertEqual(save.data['wins']['zatex'],1)
            s.kills+=4;s.coins+=20;s.waves.completed=11;save.record(s,False)
            self.assertEqual(save.data['wins']['zatex'],1);self.assertEqual(save.data['coins'],won+21)
            self.assertEqual(save.data['mission_stats']['kills'],29)

    def test_secrets_require_each_distinct_victory(self):
        with tempfile.TemporaryDirectory() as d:
            save=SaveManager(Path(d)/'s.json')
            for key in ('leo','guxta'):
                save.record(GameSession(key),True)
                self.assertNotIn('leozauxta',save.visible_characters())
            save.record(GameSession('zatex'),True)
            self.assertTrue(save.challenge_available('leozauxta'));self.assertNotIn('leozauxta',save.visible_characters())
            from trials import create
            trial=create('leo','leozauxta')
            for _ in range(3):
                b=trial.boss;b.phase_age=8;b.phase_guard=0;trial.hit(b,1e9,False);trial.enemy_update(b,.01)
            save.record(trial,True)
            self.assertIn('leozauxta',save.visible_characters());self.assertNotIn('leozauxtaci',save.visible_characters())
            save.record(GameSession('leozauxta'),True);self.assertFalse(save.is_unlocked('leozauxtaci'))
            save.record(GameSession('davi'),True);self.assertFalse(save.is_unlocked('leozauxtaci'));self.assertTrue(save.challenge_available('leozauxtaci'))
            trial=create('leo','leozauxtaci')
            for _ in range(3):
                b=trial.boss;b.phase_age=8;b.phase_guard=0;trial.hit(b,1e9,False);trial.enemy_update(b,.01)
            save.record(trial,True);self.assertTrue(save.is_unlocked('leozauxtaci'))
            self.assertTrue(SaveManager(save.path).is_unlocked('leozauxtaci'))

    def test_mission_boundaries_and_locked_upgrade_pool(self):
        from upgrades import choices
        data={'mission_stats':{}}
        self.assertEqual(unlocked(data),{'knives'})
        p=GameSession('leo').player;p.allowed_items=unlocked(data)
        for seed in range(100):
            for u,_ in choices(p,random.Random(seed)):
                if u.stat=='aux':self.assertEqual(u.id,'aux_knives')
        for key,(_,_,stat,n) in MISSIONS.items():
            data['mission_stats'][stat]=n-1;self.assertNotIn(key,unlocked(data))
            data['mission_stats'][stat]=n;self.assertIn(key,unlocked(data))

    def test_loot_collected_once_between_waves(self):
        s=GameSession('leo');s.pickups=[Pickup(V(),100),Pickup(V(),1,'chest')]
        s.waves.clear(s);xp=(s.player.xp,s.player.level,s.player.pending)
        self.assertEqual(s.chests,1);self.assertFalse(s.pickups)
        s.waves.clear(s);self.assertEqual(s.chests,1);self.assertEqual(xp,(s.player.xp,s.player.level,s.player.pending))

    def test_boss_not_spawned_by_elapsed_time(self):
        s=GameSession('leo');s.time=999;s.update(.01)
        self.assertIsNone(s.boss);self.assertEqual(s.waves.number,1)

    def test_families_and_endless_population_budget(self):
        names=set()
        for key in FAMILIES:
            s=GameSession('leo',map_key=key);s.waves.number=100;s.waves.begin(s)
            names.add(s.boss.name)
            for _ in range(300):s.spawn()
            self.assertLessEqual(len(s.enemies),160)
        self.assertEqual(len(names),6)

    def test_swept_projectiles_match_exact_collision(self):
        rng=random.Random(831)
        for _ in range(250):
            s=GameSession('leo');start=s.player.pos+V(rng.uniform(-200,200),rng.uniform(-200,200))
            velocity=V(rng.uniform(-2000,2000),rng.uniform(-2000,2000))
            e=s.spawn(kind=0,pos=start+V(rng.uniform(-100,100),rng.uniform(-100,100)));e.hp=10000
            q=Projectile(start,velocity,10,'token',radius=6,pierce=0)
            expected=segment_distance(e.pos,start,start+velocity*.05)<e.radius+6
            s.projectile_update(q,.05);self.assertEqual(e.hp<10000,expected)

    def test_ui_pagination_secrecy_and_time_substeps(self):
        from game import Game
        with tempfile.TemporaryDirectory() as d:
            g=Game(save_path=Path(d)/'s.json');g.state='CHARACTER_SELECT'
            for page in range(2):
                g.roster_page=page;g.draw()
                self.assertFalse(any(b.action in ('char:leozauxta','char:leozauxtaci') for b in g.buttons))
                for b in g.buttons:self.assertTrue(pg.Rect(0,0,1280,720).contains(b.rect))
            g.start('zatex');g.update(.1,V());self.assertAlmostEqual(g.session.time,.1)
            g.state='PAUSED';g.update(.1,V());self.assertAlmostEqual(g.session.time,.1)

    def test_new_character_cutouts_and_map_sprites(self):
        from asset_generator import AssetManager
        a=AssetManager()
        for key in ('zatex','zatex_form','leozauxtaci','leozauxtaci_form'):
            im=a.sources[key];coverage=pg.mask.from_surface(im,8).count()/(im.get_width()*im.get_height())
            self.assertGreater(coverage,.1);self.assertLess(coverage,.95)
