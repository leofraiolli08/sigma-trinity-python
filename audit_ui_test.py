"""Integration checks for presentation, storage retry and accessibility."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pygame as pg
from entities import V,Telegraph

class AuditUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from game import Game
        cls.tmp=tempfile.TemporaryDirectory();cls.g=Game(save_path=Path(cls.tmp.name)/'save.json')
    @classmethod
    def tearDownClass(cls):
        cls.g.menu();cls.tmp.cleanup()
    def test_arsenal_build_and_all_achievement_pages_fit_screen(self):
        g=self.g;g.menu()
        for state in ('MISSIONS','ARCHIVE','SETTINGS'):
            g.state=state
            for page in range(3):
                g.archive_page=page;g.draw()
                self.assertTrue(g.buttons)
                self.assertTrue(all(pg.Rect(0,0,1280,720).contains(b.rect) for b in g.buttons))
        g.start('leo');g.state='BUILD'
        for page in (0,1):g.build_page=page;g.draw();self.assertTrue(all(b.rect.bottom<=720 for b in g.buttons))
        g.menu()
    def test_result_retries_storage_and_does_not_duplicate_rewards(self):
        g=self.g;g.menu();g.save_retry_left=0;g.start('leo');s=g.session;s.result='VICTORY';s.waves.completed=10
        wins=g.save.data['wins']['leo']
        with patch.object(g.save,'save',return_value=False):g.update(.01,V());self.assertFalse(g.recorded)
        reward=g.save.data['coins'];g.save_retry_left=0;g.update(.01,V())
        self.assertTrue(g.recorded);self.assertEqual(g.save.data['coins'],reward);self.assertEqual(g.save.data['wins']['leo'],wins+1)
        g.menu()
    def test_flashes_off_retains_hostile_warning_in_every_quality(self):
        g=self.g;g.start('ippo');s=g.session
        s.telegraphs.append(Telegraph(s.player.pos+V(150,0),80,.8,'hostile_blast',100));s.player.hurt_flash=.2
        for quality in ('full','balanced','low'):
            g.render.draw_world(s,dict(shake=False,numbers=False,flashes=False,effects=quality))
            self.assertEqual(g.render.canvas.get_at((869,395))[:3],(255,131,146))
            self.assertFalse(g.render.flashes)
        g.menu()
