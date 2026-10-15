import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pygame as pg
from entities import V,Player
from session import GameSession
from maps import Arena,MAPS
from music import MusicPlayer,MUSIC_END
from save_manager import SaveManager

class ExpansionTests(unittest.TestCase):
    def test_energy_cap_under_hundreds_of_hits(self):
        s=GameSession('rafael');p=s.player;e=s.spawn(kind=0,pos=p.pos+V(500,0));e.hp=e.max_hp=1e12
        for _ in range(600):
            p.update(.05,V())
            for _ in range(10):s.hit(e,10000,False)
        self.assertLessEqual(p.sigma,75.00001);self.assertFalse(p.transform())
        for _ in range(201):p.update(.05,V());p.gain_sigma(10000)
        self.assertEqual(p.sigma,100);self.assertTrue(p.transform())
        p.update(14,V());self.assertEqual(p.form_recovery,10)
        p.gain_sigma(10000);self.assertEqual(p.sigma,0)
        p.sigma=100;self.assertFalse(p.transform());p.update(10,V());self.assertTrue(p.transform())
    def test_boss_cannot_skip_phases_with_overpowered_burst(self):
        s=GameSession('leozauxta');b=s.spawn(boss=True,pos=s.player.pos+V(500,0))
        s.waves.number=10;s.waves.started=True
        for phase,fraction in ((1,.67),(2,.34)):
            self.assertEqual(b.phase,phase)
            s.hit(b,1e12,False);self.assertAlmostEqual(b.hp,b.max_hp*fraction)
            s.enemy_update(b,.05);self.assertEqual(b.phase,phase)
            b.phase_age=8;s.enemy_update(b,.05);self.assertEqual(b.phase,phase+1)
            hp=b.hp;s.hit(b,1e12,False);self.assertEqual(b.hp,hp)
            b.tick_status(2.1)
        s.hit(b,1e12,False);self.assertEqual(b.hp,1);self.assertIsNone(s.result)
        b.phase_age=8;s.hit(b,10,False);self.assertEqual(s.result,'VICTORY')
    def test_davi_attacks_and_control_respect_boss_immunity(self):
        s=GameSession('davi');p=s.player;e=s.spawn(kind=3,pos=p.pos+V(250,0));e.hp=10000
        s.weapon.fire(s,e);self.assertEqual(s.projectiles[0].kind,'air')
        s.weapon.skill(s,e);self.assertEqual(s.projectiles[-1].kind,'shoot_style')
        before=e.pos.distance_to(p.pos);s.weapon.skill_index=1;s.weapon.skill(s,e)
        self.assertLess(e.pos.distance_to(p.pos),before);self.assertGreater(e.root,0)
        b=s.spawn(boss=True,pos=p.pos+V(280,0));pos=V(b.pos);s.weapon.skill(s,b)
        self.assertEqual(b.pos,pos);self.assertEqual(b.root,0)
        p.sigma=100;s.transform();self.assertTrue(p.sprite(0).startswith('full_cowl'))
    def test_maps_have_distinct_rules_and_safe_spawn(self):
        for key in MAPS:
            s=GameSession('davi',map_key=key);self.assertEqual(s.arena.key,key)
            s.spawn_cd=999;s.hazard_cd=0;s.update(.01)
            self.assertTrue(s.telegraphs);self.assertTrue(all(t.delay>1 for t in s.telegraphs))
            self.assertEqual(s.player.hp,s.player.max_hp)
        usj=Arena('usj');self.assertEqual(usj.zone_at(V(1800,1800)),'PRAÇA DA U.A.')
        self.assertLess(usj.speed_at(V(3180,2080)),1)
        self.assertGreater(Arena('city').speed_at(V(1800,1500)),1)
        with self.assertRaises(ValueError):Arena('missing')
    def test_empty_playlist_and_corrupt_tracks_never_crash(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);m=MusicPlayer(root);m.next();self.assertIn('SEM MP3',m.label)
            for i in range(7):(root/f'{i+1:02}.mp3').write_bytes(b'invalid audio')
            with patch('pygame.mixer.get_init',return_value=(22050,-16,1)),patch('pygame.mixer.music.set_endevent'),patch('pygame.mixer.music.load',side_effect=pg.error('bad')):
                m=MusicPlayer(root);self.assertEqual(len(m.tracks),5);self.assertEqual(len(m.failed),5);m.next();self.assertIn('INVÁLIDAS',m.label)
    def test_playlist_next_wrap_pause_and_volume(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for i in range(5):(root/f'{i+1}.mp3').touch()
            with patch('pygame.mixer.get_init',return_value=(22050,-16,1)),patch('pygame.mixer.music') as backend:
                m=MusicPlayer(root);self.assertEqual(m.index,0)
                for _ in range(5):m.next()
                self.assertEqual(m.index,0);m.pause(True);backend.pause.assert_called()
                m.pause(False);backend.unpause.assert_called();m.set_volume(.6);backend.set_volume.assert_called_with(.6)
                m.toggle();backend.set_volume.assert_called_with(0)
    def test_real_wav_stream_and_end_event(self):
        import wave
        if not pg.mixer.get_init():pg.mixer.init()
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'01.wav'
            with wave.open(str(path),'wb') as wav:
                wav.setparams((1,2,22050,0,'NONE','not compressed'));wav.writeframes(b'\x00\x00'*2205)
            pg.event.clear(MUSIC_END);m=MusicPlayer(Path(d));self.assertEqual(m.current,path)
            self.assertTrue(pg.mixer.music.get_busy())
            for _ in range(30):
                pg.time.wait(10)
                if pg.event.peek(MUSIC_END):break
            self.assertTrue(pg.event.get(MUSIC_END))
            pg.mixer.music.stop()
    def test_old_save_migrates_new_character_and_music(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'save.json';p.write_text('{"plays":{"leo":8},"high_score":123}')
            s=SaveManager(p);self.assertEqual(s.data['plays']['leo'],8);self.assertEqual(s.data['plays']['davi'],0)
            s.data['settings']['music_volume']=.7;s.save();self.assertEqual(SaveManager(p).data['settings']['music_volume'],.7)
    def test_davi_atlas_has_alpha_and_separate_forms(self):
        from asset_generator import AssetManager
        a=AssetManager()
        for key in ('davi','davi_form'):
            self.assertIn(key,a.sources);im=a.sources[key]
            self.assertLess(pg.mask.from_surface(im,8).count(),im.get_width()*im.get_height()*.95)
        self.assertNotEqual(pg.image.tobytes(a.sources['davi'],'RGBA'),pg.image.tobytes(a.sources['davi_form'],'RGBA'))

class BalanceRegressionTests(unittest.TestCase):
    def test_discrete_shots_keep_energy_between_frames(self):
        times=[]
        for dt in (.02,.05):
            p=Player('davi');elapsed=0.;next_shot=.6
            while elapsed<65 and p.sigma<100:
                p.update(dt,V());elapsed+=dt
                if elapsed+1e-8>=next_shot:
                    p.combat_left=2;p.gain_sigma(.8);next_shot+=.6
            self.assertLess(elapsed,55);self.assertGreater(elapsed,40);times.append(elapsed)
        self.assertLess(abs(times[0]-times[1]),.2)
        idle=Player('leo')
        for _ in range(2000):idle.update(.05,V())
        self.assertEqual(idle.sigma,0)
    def test_actual_four_weapons_charge_in_moderate_time(self):
        from settings import CHARACTERS
        for key in CHARACTERS:
            s=GameSession(key,42);s.spawn_cd=999;s.hazard_cd=999;s.player.invulnerable=999
            e=s.spawn(kind=3,pos=s.player.pos+V(180,0));e.hp=e.max_hp=1e9;e.speed=0;e.cooldown=999
            for _ in range(1300):
                # Melee training dummy stays within physical punching range.
                if key in ('ippo','eren','joe','thorfinn','musashi'):e.pos=s.player.pos+V(80,0)
                s.update(.05)
                if s.player.sigma>=100:break
            self.assertEqual(s.player.sigma,100,key)
            self.assertGreaterEqual(s.time,39);self.assertLessEqual(s.time,60,key)
    def test_island_boundary_and_supplied_map_pixels(self):
        from settings import BASE_DIR
        from maps import make_map
        arena=Arena('usj')
        for pos in (V(0,0),V(3599,0),V(3599,3599),V(0,3599),V(1800,1800)):
            self.assertTrue(arena.contains(arena.constrain(pos)))
        source=pg.image.load(str(BASE_DIR/'assets/art/hero_map.png')).convert()
        tile=pg.Surface((64,64));actual=make_map('usj',tile)
        expected=pg.Surface((3600,3600));expected.fill((18,27,31))
        width=round(source.get_width()*3600/source.get_height())
        expected.blit(pg.transform.scale(source,(width,3600)),((3600-width)//2,0))
        self.assertEqual(pg.image.tobytes(actual,'RGB'),pg.image.tobytes(expected,'RGB'))
        s=GameSession('davi',map_key='usj');s.spawn_cd=999;s.hazard_cd=999
        s.player.pos=arena.constrain(V(0,0));s.player.invulnerable=999
        for _ in range(90):s.update(.05,V(-1,-1))
        self.assertTrue(arena.contains(s.player.pos))
    def test_boss_reinforcements_no_longer_overwhelm(self):
        s=GameSession('leo');s.time=301;s.waves.number=10;s.waves.begin(s);s.hazard_cd=999;s.update(.01)
        self.assertEqual(s.boss.max_hp,15000)
        self.assertEqual(s.waves.remaining,0)
        self.assertLessEqual(len(s.enemies),3)
