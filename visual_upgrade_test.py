"""Real rendering regressions: art fallback, transparency and simulation isolation."""
import unittest
import tempfile
import json
from pathlib import Path
import pygame as pg
from entities import V,Projectile
from settings import BASE_DIR
from visual_assets import ArtVFX,FX_NAMES,PROJECTILES,terrain
from pixel_style import PixelEffects
from monster_art import load
from save_manager import SaveManager
from session import GameSession
from asset_generator import AssetManager
from renderer import Renderer
from ascension import effect

class VisualUpgradeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pg.display.init();pg.font.init()
        if not pg.display.get_surface():pg.display.set_mode((1280,720))
        cls.assets=AssetManager();cls.render=Renderer(cls.assets)
    def test_all_maps_have_distinct_generated_enemies_and_bosses(self):
        a=self.assets;normal=[];boss=[]
        for theme in ('city','ring','walls','fog'):
            self.assertTrue((BASE_DIR/f'assets/art/{theme}_monsters.png').is_file())
            for kind in range(6):
                im=a.images[f'{theme}_enemy_{kind}_0'];normal.append(pg.image.tostring(im,'RGBA'))
                self.assertGreater(pg.mask.from_surface(im,24).count(),100)
                self.assertEqual(im.get_at((0,0)).a,0)
            boss.append(pg.image.tostring(a.images[f'{theme}_boss_0'],'RGBA'))
        self.assertEqual(len(set(normal)),24);self.assertEqual(len(set(boss)),4)
    def test_missing_generated_monsters_and_effects_fall_back(self):
        with tempfile.TemporaryDirectory() as d:
            images,sizes=load(Path(d));self.assertEqual(len(images),56)
            fx=ArtVFX(Path(d)/'missing.png');self.assertFalse(fx.stamp(pg.Surface((64,64)), 'slash',(20,20),20))
    def test_every_generated_vfx_and_projectile_is_visible(self):
        fx=PixelEffects();self.assertEqual(set(fx.art.images),set(FX_NAMES))
        signatures=[]
        for kind in PROJECTILES:
            fx.begin();q=Projectile(V(),V(350,110),10,kind);fx.projectile(q,(640,360),.25)
            self.assertGreater(pg.mask.from_surface(fx.layer,30).count(),0,kind)
            signatures.append(pg.image.tostring(fx.layer,'RGBA'))
        self.assertGreater(len(set(signatures)),12)
    def test_render_modes_preserve_randomness_and_simulation(self):
        s=GameSession('musashi',913,map_key='crypt')
        e=s.spawn(kind=1,pos=s.player.pos+V(130,0));effect(s,'musashi_slash',s.player.pos,e.pos)
        s.add_projectile(Projectile(V(s.player.pos),V(300,0),10,'air'))
        before=(s.rng.getstate(),s.player.hp,V(s.player.pos),e.hp,s.projectiles[0].life,len(s.effects))
        signatures=[]
        for quality in ('full','balanced','low'):
            self.render.draw_world(s,{'shake':False,'numbers':True,'effects':quality})
            self.assertEqual(before,(s.rng.getstate(),s.player.hp,V(s.player.pos),e.hp,s.projectiles[0].life,len(s.effects)))
            signatures.append(pg.image.tostring(self.render.canvas,'RGBA'))
        self.assertNotEqual(signatures[0],signatures[2])
    def test_vfx_transform_cache_is_bounded(self):
        fx=ArtVFX();layer=pg.Surface((320,180),pg.SRCALPHA)
        for i in range(900):fx.stamp(layer,FX_NAMES[i%16],(160,90),10+i%100,i*15)
        self.assertLessEqual(len(fx.cache),fx.max_cache)
    def test_quality_setting_migrates_persists_and_rejects_invalid(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'save.json';save=SaveManager(path);self.assertEqual(save.data['settings']['effects'],'full')
            save.data['settings']['effects']='low';save.save();self.assertEqual(SaveManager(path).data['settings']['effects'],'low')
            raw=json.loads(path.read_text());raw['settings']['effects']='invalid';path.write_text(json.dumps(raw))
            self.assertEqual(SaveManager(path).data['settings']['effects'],'full')
    def test_generated_terrain_is_distinct_and_optional(self):
        signatures=[]
        for key in ('city','ring','walls','fog'):
            im=terrain(key);self.assertEqual(im.get_size(),(900,900));signatures.append(pg.image.tostring(im,'RGB'))
        self.assertEqual(len(set(signatures)),4);self.assertIsNone(terrain('usj'))
    def test_cropped_effect_pass_matches_full_pass_without_stale_pixels(self):
        fx=PixelEffects();fx.begin();fx.art.stamp(fx.layer,'slash',(90,80),40)
        actual=pg.Surface((1280,720));actual.fill((21,31,41));expected=actual.copy()
        expected.blit(pg.transform.scale(fx.layer,(1280,720)),(0,0));fx.present(actual)
        self.assertEqual(pg.image.tostring(actual,'RGB'),pg.image.tostring(expected,'RGB'))
        fx.begin();actual.fill((21,31,41));fx.present(actual)
        expected.fill((21,31,41));self.assertEqual(pg.image.tostring(actual,'RGB'),pg.image.tostring(expected,'RGB'))
    def test_road_bonus_matches_generated_avenue_grid(self):
        from maps import Arena
        arena=Arena('city')
        self.assertEqual(arena.speed_at(V(1800,1800)),1.08)
        self.assertEqual(arena.speed_at(V(2250,2250)),1.)
