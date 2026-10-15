"""Presentation regression checks. Executed by --self-test discovery import."""
import unittest
from pathlib import Path
import pygame as pg
from settings import BASE_DIR
from asset_generator import AssetManager
from art_assets import load_art
from entities import Player,V
from renderer import Renderer
from pixel_style import PixelEffects

class ArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pg.display.init(); pg.font.init()
        if not pg.display.get_surface():pg.display.set_mode((1280,720))
        cls.assets=AssetManager()
    def test_all_six_cutouts_have_real_alpha(self):
        for key in ('leo','rafael','leozauxta','leo_form','rafael_form','leozauxta_form'):
            self.assertIn(key,self.assets.sources)
            s=self.assets.sources[key]
            pixels=s.get_width()*s.get_height()
            self.assertGreater(1-pg.mask.from_surface(s,8).count()/pixels,.08)
            self.assertGreater(pg.mask.from_surface(s,220).count()/pixels,.15)
            self.assertTrue((BASE_DIR/'assets'/'art'/(key+'.png')).exists())
    def test_dancing_frames_differ_and_cache_reused(self):
        a=self.assets
        frames=[pg.image.tostring(a.images[f'titan_{i}'],'RGBA') for i in range(6)]
        self.assertGreaterEqual(len(set(frames)),4)
        self.assertIs(a.sprite('titan_0',1.8),a.sprite('titan_0',1.8))
    def test_enemy_atlas_and_portraits_are_loaded(self):
        for key in ('leo','rafael','leozauxta','davi'):
            for suffix in ('','_form'):self.assertIn('portrait_'+key+suffix,self.assets.art_names)
        for i in range(6):self.assertIn(f'enemy_{i}_0',self.assets.images)
        self.assertIn('boss_0',self.assets.images)
    def test_missing_art_graceful_fallback(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            images,logical,sources=load_art(Path(d));self.assertEqual(images,{})
    def test_horizontal_direction_persists_and_sprite_is_mirrored(self):
        p=Player('guxta');p.update(.05,V(-1,0));self.assertTrue(p.facing_left)
        p.update(.05,V(0,-1));self.assertTrue(p.facing_left)
        p.update(.05,V(1,0));self.assertFalse(p.facing_left)
        r=Renderer(self.assets);r.canvas.fill((0,0,0));r.sprite('guxta_walk_0',(150,170),1)
        right=pg.image.tostring(r.canvas,'RGBA')
        r.canvas.fill((0,0,0));r.sprite('guxta_walk_0',(150,170),1,flip_x=True)
        self.assertNotEqual(right,pg.image.tostring(r.canvas,'RGBA'))
        self.assertIn(('guxta_walk_0',1),r.flipped)
    def test_attack_effects_have_distinct_visible_signatures(self):
        from entities import Projectile
        fx=PixelEffects();images=[]
        for kind in ('glue','pacoca','token','shoot_style','flask','bullet'):
            fx.begin();fx.projectile(Projectile(V(),V(300,0),10,kind),V(320,180),.2);images.append(pg.image.tostring(fx.layer,'RGBA'))
        self.assertEqual(len(set(images)),len(images))
