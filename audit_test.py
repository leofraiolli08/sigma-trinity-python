"""Regressions from the V8 audit: physics, ownership, saves and wire-state validation."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pygame as pg
from entities import V,Enemy,Projectile,Pickup,Telegraph
from session import GameSession
from save_manager import SaveManager
from netstate import snapshot,restore
import ascension
import boss_patterns

class AuditCombatTests(unittest.TestCase):
    def test_spatial_index_matches_full_collision_scan_with_knockback_and_ricochets(self):
        import random
        from spatial import EnemyGrid
        rng=random.Random(271);plain=GameSession('leo',seed=8);indexed=GameSession('leo',seed=8)
        for i in range(160):
            pos=V(rng.uniform(1300,2300),rng.uniform(1300,2300))
            for s in (plain,indexed):e=s.spawn(kind=i%6,pos=pos);e.hp=e.max_hp=1000
        indexed.enemy_index=EnemyGrid(indexed.enemies)
        for i in range(250):
            pos=V(rng.uniform(1300,2300),rng.uniform(1300,2300));vel=V(2500,0).rotate(rng.uniform(0,360))
            q=Projectile(pos,vel,10,('jet','bonder','stuffed','token')[i%4],pierce=2,bounce=int(i%3==0))
            a=copy.deepcopy(q);b=copy.deepcopy(q);plain.projectile_update(a,.05);indexed.projectile_update(b,.05)
            self.assertEqual(a.__dict__,b.__dict__)
            self.assertEqual([(e.hp,e.pos) for e in plain.enemies],[(e.hp,e.pos) for e in indexed.enemies])
        self.assertEqual(plain.total_damage,indexed.total_damage)
    def test_spatial_index_accounts_for_large_radius_and_cell_crossing(self):
        from spatial import EnemyGrid
        e=Enemy(1,V(160,160),0);e.radius=70;grid=EnemyGrid([e])
        self.assertIn(e,list(grid.query(90,90,92,92)))
        e.pos=V(800,800);grid.move(e)
        self.assertNotIn(e,list(grid.query(90,90,92,92)));self.assertIn(e,list(grid.query(800,800,810,810)))
    def test_projectile_hits_before_crossing_wall(self):
        s=GameSession('leo');right=s.arena.bounds.right
        e=s.spawn(kind=0,pos=V(right-28,1800));q=Projectile(V(right-80,1800),V(2000,0),5,'token')
        s.projectile_update(q,.05)
        self.assertIn(e.uid,q.hit);self.assertLess(e.hp,e.max_hp);self.assertTrue(q.dead)
    def test_final_partial_lifetime_hits_but_cannot_travel_extra_distance(self):
        s=GameSession('leo');a=s.spawn(kind=0,pos=V(1830,1800));b=s.spawn(kind=0,pos=V(1910,1800))
        q=Projectile(V(1800,1800),V(2000,0),5,'token',life=.02,pierce=2)
        s.projectile_update(q,.05)
        self.assertIn(a.uid,q.hit);self.assertNotIn(b.uid,q.hit);self.assertEqual(q.pos.x,1840);self.assertTrue(q.dead)
    def test_ricochet_survives_wall_crossing_when_redirected_inside(self):
        s=GameSession('leo');right=s.arena.bounds.right
        e=s.spawn(kind=0,pos=V(right-28,1800));s.spawn(kind=0,pos=V(right-170,1800))
        q=Projectile(V(right-80,1800),V(2000,0),5,'token',bounce=1)
        s.projectile_update(q,.05)
        self.assertIn(e.uid,q.hit);self.assertFalse(q.dead);self.assertLess(q.vel.x,0)
    def test_xp_overflow_never_merges_with_health(self):
        s=GameSession('leo');s.pickups=[Pickup(V(2000,2000),13,'health') for _ in range(300)]
        s.add_pickup(Pickup(V(2000,2000),3))
        self.assertTrue(all(q.value==13 for q in s.pickups));self.assertEqual(s.player.xp,3)
    def test_xp_overflow_merges_with_only_live_xp_and_keeps_value(self):
        s=GameSession('leo');s.pickups=[Pickup(V(2100,2100),13,'health') for _ in range(298)]
        live=Pickup(V(2100,2100),3,life=5);expired=Pickup(V(2000,2000),100,life=0);s.pickups.extend((live,expired))
        s.add_pickup(Pickup(V(2000,2000),7,life=75))
        self.assertEqual(live.value,10);self.assertEqual(live.life,75);self.assertEqual(expired.value,100)
    def test_full_pickup_cap_preserves_chest_once_for_allies(self):
        s=GameSession('leo');s.add_player('rafael',1);s.pickups=[Pickup(V(2100,2100),3) for _ in range(300)]
        with patch('ascension.chest',wraps=ascension.chest) as chest:s.add_pickup(Pickup(V(2100,2100),1,'chest'))
        self.assertEqual(chest.call_count,2);self.assertEqual(s.chests,1);self.assertEqual(s.coins,15)
    def test_expired_pickup_cannot_grant_xp_or_heal_at_wave_clear(self):
        s=GameSession('leo');s.pickups=[Pickup(V(s.player.pos),40,life=0),Pickup(V(s.player.pos),500,'health',life=0)]
        s.player.hp=30;s.player.regen=0;s.update(.01,V())
        self.assertEqual(s.player.xp,0);self.assertEqual(s.player.hp,30)
        s.pickups=[Pickup(V(s.player.pos),100,life=0)];s.waves.clear(s);self.assertEqual(s.player.xp,0)
    def test_pickup_collected_by_ally_heals_that_ally_only(self):
        s=GameSession('leo');p=s.add_player('guxta',1);s.player.hp=20;p.hp=20
        item=Pickup(V(p.pos),13,'health');s.collect_pickup(item,p);s.collect_pickup(item,p)
        self.assertEqual(s.player.hp,20);self.assertEqual(p.hp,33)
    def test_capped_projectiles_do_not_modify_another_players_shot(self):
        for key in ('rafael','leozauxta'):
            s=GameSession('leo');p=s.add_player(key,1);e=s.spawn(kind=0,pos=V(1900,1800))
            s.projectiles=[Projectile(V(1800,1800),V(1,0),1,'glue',owner=0) for _ in range(280)]
            before=copy.deepcopy(s.projectiles[-1].__dict__)
            with s.acting(p):s.weapon.fire(s,e)
            self.assertEqual(s.projectiles[-1].__dict__,before)
    def test_klein_multi_level_jump_matches_sequential_evolution(self):
        jump=GameSession('klein');sequence=GameSession('klein');jump.player.level=9;ascension.tick(jump,.01)
        for level in (5,9):sequence.player.level=level;ascension.tick(sequence,.01)
        self.assertEqual(jump.player.stage,2);self.assertAlmostEqual(jump.player.damage,sequence.player.damage)
    def test_marionette_uses_controller_distance_not_nearest_ally(self):
        s=GameSession('klein');ally=s.add_player('leo',1);e=s.spawn(kind=0,pos=V(1800,1800));e.puppet_mark=5;e.puppet_owner=0
        s.player.pos=V(2500,1800);ally.pos=V(e.pos)
        with s.acting(ally):s.enemy_update(e,.05)
        self.assertEqual(e.puppet_progress,0)
        s.player.pos=V(e.pos);ally.pos=V(2500,1800)
        with s.acting(ally):s.enemy_update(e,.05)
        self.assertAlmostEqual(e.puppet_progress,.05)
    def test_damage_stats_are_actual_and_owned_not_overkill(self):
        s=GameSession('leo');p=s.add_player('guxta',1);e=s.spawn(kind=0,pos=V(1900,1800));e.hp=10
        with s.acting(p):s.hit(e,1000,False)
        self.assertEqual(p.damage_dealt,10);self.assertEqual(p.kills,1);self.assertEqual(s.player.damage_dealt,0)
        self.assertEqual(s.texts[-1].text,'10');p.hp=5;p.invulnerable=0;p.hurt(1000);self.assertEqual(p.damage_taken,5)
    def test_melee_does_not_consume_attack_on_distant_target(self):
        for key in ('ippo','eren','musashi'):
            s=GameSession(key);s.spawn(kind=0,pos=s.player.pos+V(600,0));s.weapon.skill_cd=99;s.weapon.passive_cd=99
            s.weapon.update(s,.01);self.assertLessEqual(s.weapon.attack_cd,0);self.assertEqual(s.player.attack_animation_left,0)
            s.enemies[0].pos=s.player.pos+V(80,0);s.weapon.update(s,.01);self.assertGreater(s.weapon.attack_cd,0)
    def test_bell_and_embers_deal_damage_and_only_evolve_via_recipe(self):
        for key,passive in (('bell','cooldown'),('embers','damage')):
            s=GameSession('leo');e=s.spawn(kind=3,pos=s.player.pos+V(80,0));s.player.aux={key:4};ascension.tick(s,.01)
            for q in list(s.projectiles):s.projectile_update(q,.3)
            self.assertLess(e.hp,e.max_hp);self.assertNotIn(key,s.player.evolutions)
            s.player.upgrades[passive]=1;ascension.chest(s);self.assertIn(key,s.player.evolutions)

class AuditBossTests(unittest.TestCase):
    def test_all_arena_patterns_all_phases_are_warned_and_stay_inside(self):
        from maps import MAPS
        signatures={}
        for key in MAPS:
            s=GameSession('leo',map_key=key);e=s.spawn(boss=True,pos=s.player.pos+V(-200,0));rows=[]
            for phase in (1,2,3):
                e.phase=phase
                for pattern in range(4):
                    s.telegraphs.clear();hp=s.player.hp;boss_patterns.queue(s,e,s.player,pattern)
                    self.assertTrue(s.telegraphs);self.assertEqual(s.player.hp,hp)
                    self.assertTrue(all(t.delay>=.95 and t.total_delay==t.delay and s.arena.contains(t.pos) for t in s.telegraphs))
                    rows.append((e.attack_name,tuple((t.kind,t.radius,t.reach,t.count) for t in s.telegraphs)))
            signatures[key]=tuple(rows)
        self.assertEqual(len(set(signatures.values())),6)
    def test_charge_holds_origin_while_winding_up(self):
        s=GameSession('leo');e=s.spawn(boss=True,pos=V(1600,1800));e.cooldown=99
        boss_patterns.queue(s,e,s.player,1);origin=V(e.pos);s.enemy_update(e,.05)
        self.assertEqual(e.pos,origin);self.assertGreater(e.windup_left,0)
    def test_phase_change_cancels_old_attack_and_charge(self):
        s=GameSession('leo');e=s.spawn(boss=True);e.hp=e.max_hp*.67;e.phase_age=6
        boss_patterns.queue(s,e,s.player,1);e.charge_left=.4;s.enemy_update(e,.05)
        self.assertEqual(e.phase,2);self.assertFalse(s.telegraphs);self.assertEqual(e.charge_left,0)
    def test_sweep_hits_players_in_strip_not_players_outside(self):
        s=GameSession('leo');p=s.add_player('guxta',1);p.pos=s.player.pos+V(0,150)
        t=Telegraph(s.player.pos-V(100,0),30,1,'boss_sweep',20,direction=V(1,0),reach=400)
        boss_patterns.resolve(s,t);self.assertLess(s.player.hp,s.player.max_hp);self.assertEqual(p.hp,p.max_hp)
    def test_fan_is_bounded_and_hostile(self):
        s=GameSession('leo');t=Telegraph(V(1600,1800),35,1,'boss_fan',20,direction=V(1,0),count=11,spread=100,reach=800)
        self.assertTrue(boss_patterns.resolve(s,t));self.assertEqual(len(s.projectiles),11)
        self.assertTrue(all(q.hostile for q in s.projectiles))
        for q in s.projectiles:self.assertAlmostEqual(q.vel.length(),250)

class AuditSaveTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'save.json'
    def tearDown(self):self.tmp.cleanup()
    def test_atomic_backup_recovers_previous_checkpoint(self):
        save=SaveManager(self.path);save.data['coins']=50;self.assertTrue(save.save());save.data['coins']=100;self.assertTrue(save.save())
        self.path.write_text('broken');recovered=SaveManager(self.path)
        self.assertEqual(recovered.data['coins'],50);self.assertIn('backup',recovered.warning)
        self.assertTrue(recovered.save());self.assertTrue(list(self.path.parent.glob('save.json.corrompido.*.json')))
        self.assertEqual(SaveManager(self.path).data['coins'],50)
    def test_failed_atomic_replace_retains_original_and_cleans_temporary_files(self):
        save=SaveManager(self.path);save.data['coins']=50;save.save();before=self.path.read_bytes();save.data['coins']=100
        original=Path.replace
        def fail_primary(path,target):
            if target==self.path:raise OSError('simulated disk failure')
            return original(path,target)
        with patch.object(Path,'replace',fail_primary):self.assertFalse(save.save())
        self.assertEqual(self.path.read_bytes(),before);self.assertFalse(list(self.path.parent.glob('*.tmp')))
    def test_purchase_rolls_back_when_storage_fails(self):
        from progression import purchase,cost,META
        save=SaveManager(self.path);save.data['coins']=1000;key=next(iter(META));before=copy.deepcopy(save.data)
        with patch.object(save,'save',return_value=False):self.assertFalse(purchase(save,key))
        self.assertEqual(save.data,before);price=cost(save.data,key);self.assertTrue(purchase(save,key));self.assertEqual(save.data['coins'],1000-price)
    def test_nan_cannot_overwrite_good_save(self):
        save=SaveManager(self.path);save.save();before=self.path.read_bytes();save.data['best_time']=float('nan')
        self.assertFalse(save.save());self.assertEqual(self.path.read_bytes(),before)
    def test_retry_records_victory_and_new_mission_only_once(self):
        save=SaveManager(self.path);s=GameSession('leo');s.waves.completed=10
        with patch.object(save,'save',return_value=False):self.assertFalse(save.record(s,True))
        coins=save.data['coins'];self.assertTrue(save.record(s,True));self.assertEqual(save.data['coins'],coins)
        self.assertEqual(save.data['wins']['leo'],1);self.assertEqual(save.data['mission_stats']['victories'],1)
        from missions import unlocked
        self.assertIn('bell',unlocked(save.data));self.assertIn('embers',unlocked(save.data))

class AuditWireTests(unittest.TestCase):
    def test_large_integer_input_cannot_overflow_and_stop_host(self):
        from netcode import movement
        self.assertEqual(movement([10**1000,-10**1000]),(1.,-1.))
        for move in ([True,0],[float('inf'),0],[float('nan'),0],['1',0]):self.assertEqual(movement(move),(0.,0.))
        from multiplayer import Multiplayer
        with tempfile.TemporaryDirectory() as d:
            host=Multiplayer(SaveManager(Path(d)/'save.json'),host=True,port=0)
            try:
                host.receive(0,{'type':'input','move':[10**1000,-10**1000]})
                host.pump(.01,V());self.assertFalse(host.error)
            finally:host.close()
    def test_finished_boss_wave_does_not_reference_removed_boss(self):
        s=GameSession('leo');s.waves.number=10;s.boss=s.spawn(boss=True);s.waves.clear(s)
        remote=restore(snapshot(s),0);self.assertIsNone(remote.boss);self.assertEqual(remote.result,'VICTORY')
    def test_departed_players_rhythm_is_not_sent_to_remaining_players(self):
        s=GameSession('leo');p=s.add_player('leozauxta',1);s.rhythms[1].start();s.allied_players.remove(p)
        data=snapshot(s);self.assertEqual(set(data['rhythms']),{'0'});restore(data,0)
    def test_all_characters_forms_and_boss_attacks_round_trip(self):
        from settings import CHARACTERS
        for key in CHARACTERS:
            s=GameSession(key);s.player.level=12;ascension.tick(s,.01);s.player.sigma=100;s.transform()
            e=s.spawn(boss=True);boss_patterns.queue(s,e,s.player,1)
            remote=restore(json.loads(json.dumps(snapshot(s))),0)
            self.assertEqual(remote.player.sprite(0),s.player.sprite(0));self.assertEqual(remote.boss.uid,e.uid)
            self.assertEqual(remote.telegraphs[0].total_delay,s.telegraphs[0].total_delay)
    def test_invalid_wire_is_rejected_before_mutating_existing_session(self):
        s=GameSession('leo');s.spawn(boss=True);base=snapshot(s)
        mutations=[lambda d:d['world'].update(message=123),lambda d:d['world'].update(time=float('inf')),
            lambda d:d['world']['events'].update(hits='wrong'),lambda d:d['players'][0].update(stage=9),
            lambda d:d['players'][0].pop('pos'),lambda d:d['players'][0].update(pos={'v':[1,2,3]}),
            lambda d:d['players'][0].update(aux={'unknown':1}),lambda d:d['enemies'][0].update(kind=9),
            lambda d:d['enemies'][0].update(radius=1e9),lambda d:d.update(boss=99999),
            lambda d:d['rhythms']['0'].update(notes=[{'n':[1,7,False]}]),lambda d:d['rhythms']['0'].update(notes=[None])]
        for mutate in mutations:
            data=copy.deepcopy(base);mutate(data)
            with self.assertRaises(ValueError):restore(data,0,s)
            self.assertEqual(snapshot(s),base)
    def test_oversized_enemy_warning_and_invalid_direction_are_rejected(self):
        s=GameSession('leo');s.telegraphs.append(Telegraph(V(1800,1800),35,1,'boss_fan',20,direction=V(1,0),count=7))
        for field,value in (('radius',1e6),('count',1000),('direction',None)):
            data=snapshot(s);data['telegraphs'][0][field]=value
            with self.assertRaises(ValueError):restore(data,0)
    def test_transport_rejects_overflow_numeric_literal(self):
        import struct
        from netcode import Peer
        from network_test import MemorySocket
        raw=b'{"time":1e999}'
        peer=Peer(MemorySocket(chunks=[struct.pack('!I',len(raw))+raw]))
        self.assertEqual(peer.pump(),[]);self.assertFalse(peer.alive)
        self.assertIn('Número',peer.error)

class AuditMusicTests(unittest.TestCase):
    def test_stale_end_event_does_not_skip_current_or_paused_track(self):
        from music import MusicPlayer
        music=MusicPlayer(Path('/nonexistent/music'))
        with patch.object(music,'next') as advance,patch('pygame.mixer.get_init',return_value=True),patch('pygame.mixer.music.get_busy',return_value=True):
            music.handle_end();advance.assert_not_called()
        music.paused=True
        with patch.object(music,'next') as advance:music.handle_end();advance.assert_not_called()
        music.paused=False
        with patch.object(music,'next') as advance,patch('pygame.mixer.get_init',return_value=True),patch('pygame.mixer.music.get_busy',return_value=False):
            music.handle_end();advance.assert_called_once()
