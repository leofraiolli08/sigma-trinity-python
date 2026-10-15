"""V10 regressions: real bitmap selection, distinct moves and frozen network identity."""
import json
import unittest
import pygame as pg
from asset_generator import AssetManager
from cinematics import Cinematic,CinematicRenderer
from entities import Player,V
from evolution_kit import STAGES,stage_of,signature
from netstate import snapshot,restore
from pixel_characters import KEYS
from pixel_ui import SPEC_ORDER
from session import GameSession
from renderer import Renderer

class EvolutionArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pg.display.init();pg.font.init();pg.display.set_mode((1280,720));cls.assets=AssetManager()
    def test_every_playable_evolution_has_separate_normal_and_form_bitmaps(self):
        for key in KEYS:
            normal=[];forms=[]
            for stage in range(len(STAGES[key])):
                p=Player(key);p.stage=stage;p.evolved=bool(stage)
                base=p.sprite(0);p.form_left=1;form=p.sprite(0)
                self.assertNotEqual(base,form);self.assertIn(form,self.assets.images)
                normal.append(pg.image.tobytes(self.assets.images[base],'RGBA'))
                forms.append(pg.image.tobytes(self.assets.images[form],'RGBA'))
                self.assertNotEqual(normal[-1],forms[-1],(key,stage))
            self.assertEqual(len(set(forms)),len(forms),key)
            self.assertEqual(len(set(normal)),len(normal),key)
    def test_form_walk_and_attack_frames_have_transparent_padding_and_actual_animation(self):
        for key in KEYS:
            for stage in range(len(STAGES[key])):
                frames=[self.assets.images[f'{key}_form{stage}_{pose}_{i}'] for pose in ('walk','attack') for i in range(4)]
                self.assertEqual(len({f.get_size() for f in frames}),1,(key,stage))
                self.assertGreaterEqual(len({pg.image.tobytes(f,'RGBA') for f in frames}),6,(key,stage))
                for f in frames:
                    box=f.get_bounding_rect(min_alpha=24)
                    self.assertGreater(box.left,0);self.assertLess(box.right,f.get_width())
                    self.assertGreater(box.top,0);self.assertEqual(box.bottom,f.get_height()-3)
    def test_each_evolution_has_different_transform_and_ultimate_titles(self):
        for key in KEYS:
            for kind in ('transform','ultimate'):
                titles=[]
                for stage in range(len(STAGES[key])):
                    p=Player(key);p.stage=stage;p.evolved=bool(stage);p.form_left=1
                    c=Cinematic.player(p,kind);titles.append(c.title())
                    self.assertEqual(Cinematic.read(json.loads(json.dumps(c.wire()))).title(),c.title())
                    self.assertIn(c.sprite,self.assets.images)
                self.assertEqual(len(set(titles)),len(titles),(key,kind))
    def test_stage_ultimates_have_different_gameplay_patterns(self):
        for key in KEYS:
            patterns=[]
            for stage in range(len(STAGES[key])):
                s=GameSession(key);p=s.player;p.stage=stage;p.evolved=bool(stage)
                for i in range(10):
                    e=s.spawn(kind=i%6,pos=p.pos+V(100+i*10,0).rotate(i*31));e.hp=e.max_hp=100000
                p.sigma=100;self.assertTrue(s.transform());s.transform_pause=0
                self.assertTrue(s.ultimate());self.assertFalse(s.ultimate())
                patterns.append((tuple((t.kind,round(t.delay,3),round(t.damage,2),round(t.radius),tuple(t.direction) if t.direction else ()) for t in s.telegraphs),tuple((q.kind,round(q.damage,2),round(q.vel.x),round(q.vel.y)) for q in s.projectiles),round(s.total_damage,2),p.aura_power,p.aura_armor,p.invulnerable,p.counter_left))
            self.assertEqual(len(set(patterns)),len(patterns),key)
    def test_final_thorfinn_ultimate_protects_without_dealing_damage(self):
        s=GameSession('thorfinn');p=s.player;p.stage=3;p.evolved=True
        ally=s.add_player('leo',1);ally.pos=p.pos+V(100,0);ally.hp-=35
        enemy=s.spawn(kind=0,pos=p.pos+V(140,0));before=enemy.hp
        p.sigma=100;s.transform();s.transform_pause=0;s.ultimate()
        self.assertEqual(enemy.hp,before);self.assertFalse(s.projectiles);self.assertFalse(s.telegraphs)
        self.assertGreater(ally.aura_armor,0);self.assertGreater(ally.hp,ally.max_hp-35)
        self.assertGreater(enemy.slow,0)
    def test_coop_state_preserves_chosen_stage_and_effect_art_on_each_player(self):
        s=GameSession('musashi');p=s.player;p.stage=3;p.evolved=True
        joe=s.add_player('joe',1);joe.stage=1;joe.evolved=True
        for actor in (p,joe):
            with s.acting(actor):actor.sigma=100;s.transform()
        remote=restore(json.loads(json.dumps(snapshot(s))),1)
        for actor in s.allied_players:self.assertEqual(remote.owner(actor.pid).sprite(0),actor.sprite(0))
        self.assertEqual([e.art for e in remote.effects],[e.art for e in s.effects])
        with s.acting(joe):s.weapon.fire(s,s.spawn(kind=0,pos=joe.pos+V(80,0)))
        self.assertEqual(s.effects[-1].art,signature('joe',1))
    def test_ai_icons_and_ultimate_art_are_unique_and_present(self):
        images=[self.assets.images[f'ui_spec_{key}_{lane}'] for key in SPEC_ORDER for lane in range(3)]
        self.assertEqual(len({pg.image.tobytes(im,'RGBA') for im in images}),45)
        self.assertTrue(all(pg.mask.from_surface(im,24).count()>100 for im in images))
        r=Renderer(self.assets)
        for key in KEYS:
            for stage in range(len(STAGES[key])):self.assertIn(signature(key,stage),r.fx.art.images)
    def test_titan_boss_is_a_single_complete_silhouette_in_each_frame(self):
        for i in range(8):
            f=self.assets.images[f'walls_anim_6_{i}'];mask=pg.mask.from_surface(f,96);components=mask.connected_components(20)
            self.assertEqual(len(components),1,i)
            box=f.get_bounding_rect(min_alpha=24)
            self.assertGreater(box.left,0);self.assertLess(box.right,f.get_width());self.assertGreater(box.top,0)
            self.assertEqual(box.bottom,f.get_height()-3)
        # The authored defeat is crouched, rather than another cropped walking pose.
        self.assertLess(self.assets.images['walls_anim_6_7'].get_bounding_rect().height,self.assets.images['walls_anim_6_0'].get_bounding_rect().height)
    def test_new_stage_cutscenes_and_hud_render_for_all_qualities(self):
        r=Renderer(self.assets);cinema=CinematicRenderer()
        for key in KEYS:
            for stage in range(len(STAGES[key])):
                s=GameSession(key);p=s.player;p.stage=stage;p.evolved=bool(stage);p.sigma=100;s.transform();s.transform_pause=0;s.ultimate()
                for quality in ('full','low'):
                    r.fx.quality=quality
                    for kind in ('transform','ultimate'):
                        c=Cinematic.player(p,kind);c.age=c.duration*.55;cinema.draw(r,c,{'flashes':False})
                    r.draw_world(s,{'effects':quality,'shake':False,'numbers':True,'flashes':False})
        self.assertLessEqual(len(r.fx.art.cache),r.fx.art.max_cache)

if __name__=='__main__':unittest.main()
