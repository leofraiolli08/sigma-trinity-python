"""Catch mixed/partial distributions and verify actual runtime art over caches."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import pygame as pg
from settings import BASE_DIR
from release_info import RELEASE_ID,audit,report

class InstallationTests(unittest.TestCase):
    def test_package_manifest_identifies_current_code_and_art(self):
        self.assertEqual(audit(),[])
        manifest=json.loads((BASE_DIR/'release_manifest.json').read_text())
        for name in ('game.py','multiplayer.py','assets/art/city_monsters.png','assets/art/combat_fx_atlas.png','assets/art/cinematic_atlas.png'):
            self.assertIn(name,manifest['files'])

    def test_missing_mixed_and_corrupt_files_cannot_pass_integrity(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);data=b'current art';(root/'art.png').write_bytes(data)
            (root/'release_manifest.json').write_text(json.dumps({'release':RELEASE_ID,'files':{'art.png':hashlib.sha256(data).hexdigest()}}))
            self.assertEqual(audit(root),[])
            (root/'art.png').write_bytes(b'old sprites')
            self.assertIn('art.png',audit(root)[0])
            (root/'art.png').unlink();self.assertIn('ausente',audit(root)[0])
            (root/'release_manifest.json').unlink();self.assertIn('manifest',audit(root)[0])
            for invalid in ([],None,{'release':RELEASE_ID,'files':{'art.png':None}}):
                (root/'release_manifest.json').write_text(json.dumps(invalid))
                self.assertTrue(audit(root))

    def test_new_monsters_replace_procedural_and_old_cached_sprites(self):
        from asset_generator import AssetManager
        from monster_art import load
        pg.display.init();pg.display.set_mode((1280,720))
        assets=AssetManager();fallback,_=load()
        self.assertTrue(all(v=='generated' for v in assets.art_status.values()))
        for theme in ('city','ring','walls','fog'):
            for kind in range(6):
                name=f'{theme}_enemy_{kind}_0'
                self.assertNotEqual(pg.image.tostring(assets.images[name],'RGBA'),pg.image.tostring(fallback[name],'RGBA'),name)

    def test_version_screen_has_real_art_and_returns_to_menu(self):
        from game import Game
        with tempfile.TemporaryDirectory() as d:
            g=Game(save_path=Path(d)/'save.json');self.assertIn(RELEASE_ID,pg.display.get_caption()[0])
            self.assertEqual(g.installation_errors,[]);self.assertTrue(any(b.action=='release_info' for b in g.buttons))
            g.action('release_info');g.draw();self.assertEqual(g.state,'RELEASE_INFO')
            self.assertTrue(any(b.action=='back' for b in g.buttons))
            g.handle(pg.event.Event(pg.KEYDOWN,key=pg.K_ESCAPE));self.assertEqual(g.state,'MAIN_MENU')

    def test_cli_diagnostic_uses_script_folder_even_from_another_cwd(self):
        with tempfile.TemporaryDirectory() as d:
            result=subprocess.run([sys.executable,str(BASE_DIR/'main.py'),'--diagnose'],cwd=d,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=15)
            self.assertEqual(result.returncode,0,result.stdout)
            self.assertIn(str(BASE_DIR),result.stdout);self.assertIn('Integridade: OK',result.stdout)
            self.assertFalse((Path(d)/'save.json').exists())
            self.assertIn(str(BASE_DIR),report())
