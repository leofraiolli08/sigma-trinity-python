"""Actual bitmap frames, stage selection, rendering isolation and UI input paths."""
import json
import tempfile
import unittest
from pathlib import Path
import pygame as pg
from asset_generator import AssetManager
from entities import Player,V
from pixel_characters import KEYS,stage_for,ATTACK_DURATION,export_frames
from netstate import snapshot,restore
from session import GameSession
from renderer import Renderer

class AnimationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pg.display.init();pg.font.init();pg.display.set_mode((1280,720));cls.assets=AssetManager()
    def test_browsable_pngs_match_runtime_and_replace_wrong_or_missing_cache(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);folder=root/'sprites'/'characters';folder.mkdir(parents=True)
            names=('eren_stage0_walk_0','eren_stage1_attack_2','ippo_stage0_0','portrait_musashi_form')
            frames={name:self.assets.images[name] for name in names}
            wrong=pg.Surface((48,64),pg.SRCALPHA);wrong.fill('blue')
            pg.image.save(wrong,str(folder/(names[0]+'.png')))
            export_frames(root,frames)
            for name in names:
                saved=pg.image.load(str(folder/(name+'.png')))
                self.assertEqual(pg.image.tostring(saved,'RGBA'),pg.image.tostring(frames[name],'RGBA'))
            path=folder/(names[0]+'.png');stamp=path.stat().st_mtime_ns
            export_frames(root,frames);self.assertEqual(path.stat().st_mtime_ns,stamp)
            path.unlink();export_frames(root,frames)
            self.assertEqual(pg.image.tostring(pg.image.load(str(path)),'RGBA'),pg.image.tostring(frames[names[0]],'RGBA'))
    def test_all_four_states_have_distinct_real_walk_and_attack_frames(self):
        a=self.assets;self.assertTrue(all(a.animation_status[k]=='animated' for k in KEYS))
        for key in KEYS:
            for stage in range(4):
                frames=[a.images[f'{key}_stage{stage}_{pose}_{i}'] for pose in ('walk','attack') for i in range(4)]
                self.assertEqual(len({f.get_size() for f in frames}),1)
                self.assertGreaterEqual(len({pg.image.tostring(f,'RGBA') for f in frames}),6)
                for f in frames:
                    self.assertGreater(pg.mask.from_surface(f,24).count(),100)
                    self.assertGreaterEqual(f.get_bounding_rect(min_alpha=24).bottom,f.get_height()-5)
                    self.assertEqual(f.get_at((0,0)).a,0)
    def test_pixel_frames_use_nearest_scaling_while_photos_stay_smooth(self):
        a=self.assets
        for key in KEYS:self.assertNotIn(key+'_stage0_walk_0',a.art_names)
        for key in ('leo','rafael','guxta','zatex','davi'):
            self.assertIn('portrait_'+key,a.art_names)
        name='ippo_stage0_walk_0';source=a.images[name];scaled=a.sprite(name,2)
        self.assertEqual(pg.image.tostring(scaled,'RGBA'),pg.image.tostring(pg.transform.scale(source,(source.get_width()*2,source.get_height()*2)),'RGBA'))
    def test_attack_sequence_and_persistent_movement_facing(self):
        p=Player('musashi');p.update(.05,V(-1,0));self.assertTrue(p.facing_left)
        self.assertIn('_walk_',p.sprite(.1));p.attack_animation_left=ATTACK_DURATION
        seen=[]
        for _ in range(4):seen.append(p.sprite(0));p.update(.071,V())
        self.assertEqual(len(set(seen)),4);self.assertTrue(all('_attack_' in name for name in seen))
        self.assertTrue(p.facing_left);self.assertIn('_walk_',p.sprite(1))
    def test_evolved_forms_and_marionettist_use_correct_rows(self):
        for key in ('ippo','eren'):
            p=Player(key);self.assertEqual(stage_for(p),0);p.evolved=True;self.assertEqual(stage_for(p),1)
            p.sigma=100;p.transform();self.assertEqual(stage_for(p),3)
        p=Player('klein');p.stage=2;self.assertEqual(stage_for(p),3)
        p=Player('musashi')
        for i in range(4):p.stage=i;self.assertEqual(stage_for(p),i)
    def test_multiplayer_snapshot_preserves_animation_and_damage_flash(self):
        s=GameSession('leo');p=s.add_player('ippo',1);p.attack_animation_left=.17;p.hurt_flash=.2;p.facing_left=True
        remote=restore(json.loads(json.dumps(snapshot(s))),1)
        self.assertEqual(remote.player.sprite(0),p.sprite(0));self.assertEqual(remote.player.hurt_flash,.2);self.assertTrue(remote.player.facing_left)
    def test_unicode_font_supports_actual_ui_glyphs(self):
        for glyph in '↑↓→∞✓ū':self.assertIsNotNone(self.assets.font(22).metrics(glyph)[0],glyph)
    def test_animation_gallery_back_and_menu_keyboard_navigation(self):
        from game import Game
        with tempfile.TemporaryDirectory() as d:
            g=Game(save_path=Path(d)/'save.json');g.action('release_info');g.action('animation_gallery');g.draw()
            g.handle(pg.event.Event(pg.KEYDOWN,key=pg.K_ESCAPE));self.assertEqual(g.state,'RELEASE_INFO')
            g.handle(pg.event.Event(pg.KEYDOWN,key=pg.K_ESCAPE));self.assertEqual(g.state,'MAIN_MENU');g.draw()
            g.handle(pg.event.Event(pg.KEYDOWN,key=pg.K_DOWN));self.assertEqual(g.ui_focus,'play')
            g.handle(pg.event.Event(pg.KEYDOWN,key=pg.K_RETURN));self.assertEqual(g.state,'CHARACTER_SELECT')
    def test_network_error_allows_edit_and_retry_without_stale_room(self):
        from game import Game
        with tempfile.TemporaryDirectory() as d:
            g=Game(save_path=Path(d)/'save.json');g.action('network_join');g.network_target='26.12.';g.action('network_connect');g.update(.02);g.draw()
            self.assertEqual(g.state,'NETWORK_ERROR');failed=g.net;g.action('network_join');self.assertIsNone(g.net)
            self.assertTrue(failed.closed);self.assertEqual(g.network_target,'26.12.')
    def test_hostile_warning_is_visible_over_effects_in_every_quality_mode(self):
        from entities import Telegraph
        s=GameSession('ippo');s.telegraphs.append(Telegraph(V(s.player.pos)+V(150,0),80,.8,'hostile_blast',100))
        r=Renderer(self.assets)
        for quality in ('full','balanced','low'):
            r.draw_world(s,{'shake':False,'numbers':False,'effects':quality})
            # Pygame's raster circle includes its rightmost pixel at center+r-1.
            self.assertEqual(r.canvas.get_at((869,395))[:3],(255,131,146))
