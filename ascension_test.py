import json,random,tempfile,unittest
from pathlib import Path
import pygame as pg
from entities import Player,V,Projectile
from session import GameSession
from ascension import RECIPES,chest,tick,effect
from upgrades import UPGRADES,RARITIES,apply,choices
from save_manager import SaveManager
import progression

class AscensionTests(unittest.TestCase):
    def test_character_evolution_is_level_gated_and_once(self):
        for key in ('ippo','eren','klein'):
            s=GameSession(key);p=s.player;base=p.base_damage
            tick(s,.01);self.assertFalse(p.evolved)
            p.level=6;tick(s,.01);self.assertTrue(p.evolved);self.assertAlmostEqual(p.base_damage,base*1.12)
            tick(s,.01);self.assertAlmostEqual(p.base_damage,base*1.12)
            if key=='klein':p.level=9;tick(s,.01);self.assertEqual(p.stage,2)
    def test_evolution_waits_until_form_ends(self):
        s=GameSession('eren');p=s.player;p.level=6;p.form_left=1
        tick(s,.1);self.assertFalse(p.evolved);p.form_left=0;tick(s,.1);self.assertTrue(p.evolved)
    def test_ippo_never_fires_long_range_projectiles(self):
        s=GameSession('ippo');e=s.spawn(kind=3,pos=s.player.pos+V(500,0));hp=e.hp
        s.weapon.fire(s,e);self.assertEqual(e.hp,hp);self.assertFalse(s.projectiles)
        e.pos=s.player.pos+V(70,0);s.weapon.fire(s,e);self.assertLess(e.hp,hp)
    def test_klein_paper_substitute_has_cooldown(self):
        s=GameSession('klein');p=s.player;hp=p.hp;s.hurt_player(30);self.assertEqual(p.hp,hp)
        p.invulnerable=0;s.hurt_player(30);self.assertLess(p.hp,hp)
        p.invulnerable=0;p.guard_cd=0;hp=p.hp;s.hurt_player(30);self.assertEqual(p.hp,hp)
    def test_marionette_requires_control_time_and_attacks_enemies(self):
        s=GameSession('klein');p=s.player;p.stage=2;p.evolved=True
        puppet=s.spawn(kind=3,pos=p.pos+V(70,0));puppet.hp=10000;puppet.speed=0
        s.weapon.skill(s,puppet);self.assertEqual(puppet.puppet_left,0)
        for _ in range(46):s.enemy_update(puppet,.05)
        self.assertGreater(puppet.puppet_left,0)
        target=s.spawn(kind=3,pos=puppet.pos+V(60,0));target.hp=10000;hp=target.hp
        for _ in range(20):s.enemy_update(puppet,.05)
        self.assertLess(target.hp,hp)
        boss=s.spawn(boss=True,pos=p.pos+V(100,0));s.weapon.skill(s,boss);self.assertEqual(boss.puppet_mark,0)
    def test_visual_budget_does_not_change_combat_rng(self):
        s=GameSession('leo');state=s.rng.getstate()
        for _ in range(200):effect(s,'spark',V())
        self.assertLessEqual(len(s.effects),90);self.assertEqual(state,s.rng.getstate())
    def test_build_pauses_and_keys_reach_new_content(self):
        from game import Game
        with tempfile.TemporaryDirectory() as d:
            g=Game(save_path=Path(d)/'s.json');g.state='CHARACTER_SELECT'
            g.action('roster_next');g.handle(pg.event.Event(pg.KEYDOWN,key=pg.K_2));self.assertEqual(g.selected,'klein')
            g.handle(pg.event.Event(pg.KEYDOWN,key=pg.K_6));self.assertEqual(g.session.arena.key,'fog')
            g.handle(pg.event.Event(pg.KEYDOWN,key=pg.K_TAB));age=g.session.time
            g.update(.05,V(1,0));self.assertEqual(g.session.time,age)
            g.handle(pg.event.Event(pg.KEYDOWN,key=pg.K_ESCAPE));self.assertEqual(g.state,'PLAYING')
    def test_new_ultimates_hit_and_are_distinct(self):
        signatures=[]
        for key in ('ippo','eren','klein'):
            s=GameSession(key);p=s.player;p.level=10;tick(s,.01)
            e=s.spawn(kind=3,pos=p.pos+V(100,0));e.hp=100000
            p.sigma=100;s.transform();s.transform_pause=0;s.ultimate()
            signatures.append(tuple(t.kind for t in s.telegraphs))
            for t in list(s.telegraphs):s.resolve_telegraph(t)
            self.assertGreater(s.total_damage,0)
        self.assertEqual(len(set(signatures)),3)
    def test_recipes_require_both_conditions(self):
        for key,(_,passive,_) in RECIPES.items():
            s=GameSession('leo');p=s.player;p.aux[key]=4;chest(s);self.assertNotIn(key,p.evolutions)
            p.upgrades[passive]=1;chest(s);self.assertIn(key,p.evolutions)
            n=len(p.evolutions);chest(s);self.assertEqual(len(p.evolutions),n)
    def test_all_auxiliary_weapons_deal_damage(self):
        for key in RECIPES:
            s=GameSession('leo');p=s.player;p.aux[key]=4;p.evolutions.add(key)
            e=s.spawn(kind=3,pos=p.pos+V(80,0));e.hp=100000;e.speed=0
            for _ in range(120):
                tick(s,.05)
                for q in list(s.projectiles):s.projectile_update(q,.05)
                # Areas use the main simulation's damage ticks.
                if key=='seals':
                    s.spawn_cd=999;s.player.invulnerable=1;s.update(.05)
            self.assertGreater(s.total_damage,0,key)
    def test_build_limits_and_max_rank(self):
        p=Player('leo')
        for u in UPGRADES:
            for _ in range(8):apply(p,(u,RARITIES[0]))
        self.assertLessEqual(len(p.passives),6);self.assertLessEqual(len(p.aux),5)
        for u in UPGRADES:self.assertLessEqual(p.upgrades.get(u.id,0),u.max_level)
        for u,_ in choices(p,random.Random(1)):
            self.assertTrue(u.stat=='heal' or u.stat=='aux' or u.stat in p.passives)
    def test_guaranteed_elite_and_chest(self):
        s=GameSession('leo');s.waves.number=3;s.waves.begin(s);s.waves.remaining=1;s.spawn_cd=0;s.waves.update(s,.1)
        elites=[e for e in s.enemies if e.elite];self.assertEqual(len(elites),1)
        s.hit(elites[0],1e8);self.assertTrue(any(q.kind=='chest' for q in s.pickups))
    def test_meta_save_migration_validation(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'save.json';path.write_text(json.dumps({'high_score':998,'coins':-3,'meta':{'power':900,'regen':'x'},'achievements':['victory','bogus','victory',{}]}))
            save=SaveManager(path);self.assertEqual(save.data['high_score'],998);self.assertEqual(save.data['coins'],0)
            self.assertEqual(save.data['meta']['power'],5);self.assertEqual(save.data['achievements'],['victory'])
    def test_rewards_recorded_exactly_once(self):
        with tempfile.TemporaryDirectory() as d:
            save=SaveManager(Path(d)/'s.json');s=GameSession('ippo');s.kills=120;s.time=200
            save.record(s,True);coins=save.data['coins'];save.record(s,True)
            self.assertEqual(coins,save.data['coins']);self.assertEqual(save.data['wins']['ippo'],1)
            self.assertIn('ippo',save.data['achievements']);self.assertGreater(s.reward,0)
    def test_shop_affordability_caps_and_effect(self):
        with tempfile.TemporaryDirectory() as d:
            save=SaveManager(Path(d)/'s.json');self.assertFalse(progression.purchase(save,'power'))
            save.data['coins']=10000
            for _ in range(9):progression.purchase(save,'power')
            self.assertEqual(save.data['meta']['power'],5)
            p=Player('leo');progression.meta_apply(save.data,p);self.assertAlmostEqual(p.power,1.15)
    def test_all_new_art_states_have_alpha(self):
        from asset_generator import AssetManager
        a=AssetManager()
        for key in ('ippo','eren','klein'):
            for stage in range(4):
                im=a.images[f'{key}_stage{stage}_0'];count=pg.mask.from_surface(im,8).count()
                self.assertGreater(count,100);self.assertLess(count,im.get_width()*im.get_height()*.9)
    def test_pixel_vfx_visible_and_distinct(self):
        from pixel_style import PixelEffects
        from combat_art import draw,projectile
        fx=PixelEffects();s=GameSession('klein');results=[]
        for kind in ('slash','punch','lightning','threads','paper','vortex','nuclear','spill','chemical'):
            effect(s,kind,V(640,360),V(750,400),radius=100)
            fx.begin();draw(fx,s.effects[-1],lambda p:p,1);results.append(pg.image.tobytes(fx.layer,'RGBA'))
            self.assertGreater(pg.mask.from_surface(fx.layer,1).count(),0)
        self.assertEqual(len(set(results)),len(results))
        for kind in ('card','air_bullet','flame','gravity','laser','boomerang'):
            fx.begin();self.assertTrue(projectile(fx,Projectile(V(),V(1,0),1,kind),V(640,360),1))
    def test_all_ui_pages_and_reroll(self):
        from game import Game
        with tempfile.TemporaryDirectory() as d:
            g=Game(save_path=Path(d)/'s.json')
            for state in ('CHARACTER_SELECT','MAP_SELECT','ARCHIVE'):
                g.state=state;g.draw()
                for b in g.buttons:self.assertTrue(pg.Rect(0,0,1280,720).contains(b.rect))
            g.archive_page=1;g.draw();g.start('klein');g.state='BUILD';g.draw()
            p=g.session.player;p.pending=1;g.state='LEVEL_UP';g.choices=choices(p,g.session.rng);g.draw()
            for _ in range(5):g.action('reroll')
            self.assertEqual(p.rerolls,0);g.choose(0);self.assertEqual(g.state,'PLAYING')
