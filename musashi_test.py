"""Musashi progression and ally-aura contract regression tests."""
import tempfile,unittest
from pathlib import Path
import pygame as pg
from entities import Player,V
from session import GameSession
from ascension import tick

class MusashiTests(unittest.TestCase):
    def test_three_paths_unlock_by_level_and_wait_for_form(self):
        s=GameSession('musashi');p=s.player;base=p.base_damage
        p.level=5;tick(s,.01);self.assertEqual(p.stage,1);self.assertEqual(p.display_name,'MUSASHI • CAMINHO DA ESPADA')
        self.assertAlmostEqual(p.base_damage,base*1.1)
        p.level=10;p.form_left=1;tick(s,.01);self.assertEqual(p.stage,1)
        p.form_left=0;tick(s,.01);self.assertEqual(p.stage,2);self.assertEqual(p.display_name,'MUSASHI • CAMINHO DA MORTE')
        p.level=15;tick(s,.01);self.assertEqual(p.stage,3);self.assertEqual(p.display_name,'MUSASHI • CAMINHO DA ALMA')
        self.assertAlmostEqual(p.base_damage,base*1.1**3)
        tick(s,.01);self.assertAlmostEqual(p.base_damage,base*1.1**3)

    def test_sword_death_soul_and_ultimate_are_distinct(self):
        s=GameSession('musashi');p=s.player;e=s.spawn(kind=3,pos=p.pos+V(120,0));e.hp=e.max_hp=100000
        for stage in range(4):
            p.stage=stage;p.evolved=stage>0;s.weapon.skill_index=0;before=s.total_damage
            s.weapon.fire(s,e);s.weapon.skill(s,e)
            if stage<3:self.assertGreater(s.total_damage,before)
            else:self.assertGreater(p.aura_left,0)
        p.sigma=100;s.transform();s.transform_pause=0;self.assertTrue(s.ultimate())
        kinds=tuple(t.kind for t in s.telegraphs);self.assertTrue(kinds and set(kinds)=={'musashi_cut'})
        for t in list(s.telegraphs):s.resolve_telegraph(t)
        self.assertGreater(s.total_damage,0)

    def test_soul_mode_and_future_four_player_aura_contract(self):
        s=GameSession('musashi');p=s.player;p.stage=3;p.evolved=True
        self.assertEqual(p.soul_mode,'self');self.assertTrue(s.toggle_musashi_soul_mode());self.assertEqual(p.soul_mode,'bond')
        allies=[p,Player('leo'),Player('guxta'),Player('davi')]
        for i,ally in enumerate(allies):ally.pos=p.pos+V(i*50,0)
        s.allied_players=allies
        s.weapon.skill(s,None)
        self.assertTrue(all(a.aura_left>0 and a.aura_power>=.12 for a in allies))
        # The future peers use Player.update too, so expiration cannot leave permanent stats.
        for ally in allies:ally.update(4,V())
        self.assertTrue(all(a.aura_power==0 and a.aura_speed==0 for a in allies))

    def test_atlas_and_hud_are_real_and_control_is_reachable(self):
        from asset_generator import AssetManager
        from game import Game
        assets=AssetManager()
        for stage in range(4):
            self.assertIn(f'musashi_stage{stage}_0',assets.images)
            im=assets.images[f'musashi_stage{stage}_0'];self.assertGreater(pg.mask.from_surface(im,8).count(),100)
        with tempfile.TemporaryDirectory() as d:
            g=Game(save_path=Path(d)/'save.json');g.start('musashi');g.session.player.stage=3
            g.handle(pg.event.Event(pg.KEYDOWN,key=pg.K_f));self.assertEqual(g.session.player.soul_mode,'bond')
            g.draw();self.assertTrue(any('VÍNCULO' in str(x) for x in (g.session.message,)))
