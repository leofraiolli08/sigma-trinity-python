import json,tempfile,unittest
from pathlib import Path
import pygame as pg
from save_manager import SaveManager
from session import GameSession
from entities import V
class UnlockTests(unittest.TestCase):
 def test_migration_and_required_victories(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'save.json';path.write_text(json.dumps({'wins':{'leo':2,'leozauxta':4},'high_score':900}))
   save=SaveManager(path);self.assertFalse(save.is_unlocked('leozauxta'));self.assertEqual(save.data['high_score'],900)
   s=GameSession('guxta');save.record(s,False);self.assertFalse(save.unlock_progress()['guxta'])
   save.record(GameSession('guxta'),True);self.assertFalse(save.is_unlocked('leozauxta'))
   save.data['wins']['zato']=1;save.save();restored=SaveManager(path)
   self.assertTrue(restored.is_unlocked('leozauxta'));self.assertEqual(restored.data['wins']['leozauxta'],4)
 def test_ui_and_direct_start_guard(self):
  from game import Game
  with tempfile.TemporaryDirectory() as d:
   g=Game(save_path=Path(d)/'save.json',character='leozauxta')
   self.assertIsNone(g.session);self.assertEqual(g.state,'CHARACTER_SELECT')
   g.action('char:leozauxta');self.assertEqual(g.state,'CHARACTER_SELECT')
   g.draw();self.assertNotIn('leozauxta',g.save.visible_characters())
   g.action('char:guxta');self.assertEqual(g.selected,'guxta');self.assertEqual(g.state,'MAP_SELECT')
   g.start();self.assertEqual(g.session.player.key,'guxta');g.draw()
   self.assertIn('guxta_walk_0',g.assets.art_names);self.assertIn('red_moon_0',g.assets.art_names)
   g.save.data['wins'].update(leo=1,guxta=1,zato=1);g.save.data['secret_clears']=['leozauxta'];g.start('leozauxta');self.assertEqual(g.session.player.key,'leozauxta')
 def test_gravity_and_boss_immunity_to_pull(self):
  s=GameSession('guxta');p=s.player
  target=s.spawn(pos=p.pos+V(100,0));near=s.spawn(pos=p.pos+V(140,0));boss=s.spawn(boss=True,pos=p.pos+V(150,0))
  before=V(boss.pos);old=near.pos.distance_to(target.pos);s.weapon.skill(s,target)
  self.assertLess(near.pos.distance_to(target.pos),old);self.assertEqual(boss.pos,before)
  p.sigma=100;s.transform();s.transform_pause=0;self.assertTrue(s.ultimate());self.assertFalse(s.ultimate());self.assertTrue(p.sprite(0).startswith('red_moon'))
