"""V9 integration regressions covering authored art, progression and real TCP."""
import copy,json,random,tempfile,unittest
from pathlib import Path
import pygame as pg
from entities import V,Player
from session import GameSession
from netstate import snapshot,restore
from save_manager import SaveManager
import expedition,specializations,upgrades
from cinematics import Cinematic

class ExpeditionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  from game import Game
  cls.tmp=tempfile.TemporaryDirectory();cls.g=Game(save_path=Path(cls.tmp.name)/'save.json')
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_three_heroes_four_stages_eight_distinct_poses(self):
  a=self.g.assets
  for key in ('joe','thorfinn','holden'):
   for stage in range(4):
    frames=[a.images[f'{key}_stage{stage}_{pose}_{i}'] for pose in ('walk','attack') for i in range(4)]
    self.assertEqual(len({f.get_size() for f in frames}),1);self.assertGreaterEqual(len({pg.image.tobytes(f,'RGBA') for f in frames}),6)
    for f in frames:self.assertEqual(f.get_at((0,0)).a,0);self.assertGreater(pg.mask.from_surface(f,24).count(),100)
 def test_six_maps_have_seven_families_and_eight_poses(self):
  from monster_animation import THEMES
  a=self.g.assets
  self.assertEqual(set(a.monster_animation_status.values()),{'animated'})
  for theme in THEMES:
   for row in range(7):
    frames=[a.images[f'{theme}_anim_{row}_{i}'] for i in range(8)]
    self.assertEqual(len({f.get_size() for f in frames}),1);self.assertGreaterEqual(len({pg.image.tobytes(f,'RGBA') for f in frames}),7)
    for f in frames:self.assertGreater(pg.mask.from_surface(f,24).count(),70);self.assertEqual(f.get_at((0,0)).a,0)
 def test_monster_animation_uses_simulation_state(self):
  from monster_animation import sprite_name
  s=GameSession('joe');e=s.spawn(kind=0);e.windup_left=.4
  self.assertTrue(sprite_name(e,0,'usj').endswith('_3'));e.windup_left=0;e.attack_left=.3
  self.assertTrue(sprite_name(e,0,'usj').endswith('_4'));e.hit=.2;self.assertTrue(sprite_name(e,0,'usj').endswith('_6'))
 def test_melee_is_telegraphed_and_can_be_dodged(self):
  s=GameSession('joe');p=s.player;e=s.spawn(kind=0,pos=p.pos+V(25,0));e.cooldown=0;hp=p.hp
  s.enemy_update(e,.01);t=next(t for t in s.telegraphs if t.kind=='enemy_melee');self.assertEqual(p.hp,hp);self.assertGreater(e.windup_left,0)
  old=V(p.pos);p.pos+=V(250,0);s.resolve_telegraph(t);self.assertEqual(p.hp,hp)
  p.pos=old;p.invulnerable=0;s.resolve_telegraph(t);self.assertLess(p.hp,hp)
 def test_defeat_echo_is_bounded_and_serializable(self):
  s=GameSession('joe')
  for i in range(60):e=s.spawn(kind=0,pos=s.player.pos+V(500,0));s.hit(e,1e9,False)
  self.assertEqual(len(s.corpses),45);r=restore(json.loads(json.dumps(snapshot(s))),0);self.assertEqual(len(r.corpses),45)
  s.hitstop=0;s.transform_pause=0;s.waves.rest=1
  for _ in range(15):s.update(.05)
  self.assertFalse(s.corpses)
 def test_level_jump_matches_sequential_evolution(self):
  import legends
  for key in ('joe','thorfinn','holden'):
   a=GameSession(key);b=GameSession(key);a.player.level=15;legends.tick(a)
   for i in range(1,16):b.player.level=i;legends.tick(b)
   self.assertEqual(a.player.stage,b.player.stage);self.assertAlmostEqual(a.player.base_damage,b.player.base_damage)
 def test_new_ultimates_deal_damage_once(self):
  for key in ('joe','thorfinn','holden'):
   s=GameSession(key);p=s.player;e=s.spawn(kind=0,pos=p.pos+V(110,0));e.hp=e.max_hp=1e7;e.speed=0;e.cooldown=999;p.invulnerable=999;p.sigma=100
   self.assertTrue(s.transform());s.transform_pause=0;self.assertTrue(s.ultimate());self.assertFalse(s.ultimate());s.waves.started=True;s.waves.remaining=0;s.spawn_cd=999;s.hazard_cd=999
   for _ in range(60):s.update(.05)
   self.assertGreater(p.damage_dealt,0,key);self.assertEqual(p.ultimates,1)
 def test_counter_and_thorfinn_support(self):
  s=GameSession('joe');p=s.player;e=s.spawn(kind=0,pos=p.pos+V(100,0));e.hp=10000;p.counter_left=.5;s.hurt_player(10)
  self.assertEqual(p.counters,1);self.assertLess(e.hp,10000)
  s=GameSession('thorfinn');a=s.add_player('joe',1);p=s.player;p.stage=3;s.weapon.skill(s,None);self.assertGreater(a.aura_armor,0)
 def test_specializations_are_exclusive_and_capped(self):
  p=Player('joe');p.level=4;offers=upgrades.choices(p,random.Random(1));self.assertEqual(len(offers),3);self.assertTrue(all(u.stat=='spec' for u,_ in offers))
  sid='spec_joe_0';speed=p.speed_bonus
  for i in range(3):self.assertTrue(specializations.apply(p,sid))
  self.assertEqual(p.specialization_rank,3);self.assertAlmostEqual(p.speed_bonus,speed-.08);self.assertFalse(specializations.apply(p,sid));self.assertFalse(specializations.apply(p,'spec_joe_1'))
 def test_protector_specialization_strengthens_ally_aura(self):
  s=GameSession('musashi');p=s.player;p.level=4;specializations.apply(p,'spec_musashi_2');a=s.add_player('joe',1)
  s.apply_ally_aura(p,300,2,speed=.12);self.assertGreater(a.aura_speed,.12)
 def test_rules_restrict_choices_and_survive_snapshot(self):
  for rule in expedition.RULES:
   s=GameSession('joe',run_rule=rule);s.add_player('holden',1);r=restore(json.loads(json.dumps(snapshot(s))),1);self.assertEqual(r.run_rule,rule);self.assertEqual(r.player.run_rule,rule)
  s=GameSession('joe',run_rule='noform');s.player.sigma=100;self.assertFalse(s.transform());self.assertAlmostEqual(s.player.power,1.2)
  s=GameSession('joe',run_rule='signature');s.player.allowed_items=None
  self.assertFalse(any(upgrades.eligible(s.player,u) for u in upgrades.UPGRADES if u.stat=='aux'))
 def test_objectives_are_optional_contested_and_reward_once(self):
  s=GameSession('joe');n=s.objectives[0];s.player.pos=V(n['x'],n['y']);s.waves.number=1;expedition.tick(s,10);self.assertEqual(n['progress'],0)
  s.waves.number=2;e=s.spawn(kind=0,pos=V(s.player.pos));expedition.tick(s,4);self.assertEqual(n['progress'],1);e.dead=True;expedition.tick(s,7);self.assertTrue(n['done']);self.assertEqual(s.coins,25)
  expedition.tick(s,20);self.assertEqual(s.coins,25);s.waves.number=6
  for n in s.objectives[1:]:s.player.pos=V(n['x'],n['y']);expedition.tick(s,8)
  self.assertEqual(expedition.completed(s),3);self.assertEqual(sum(p.kind=='chest' for p in s.pickups),1)
 def test_objectives_freeze_in_pause_and_cutscene(self):
  g=self.g;g.menu();g.start('joe');s=g.session;s.waves.number=2;n=s.objectives[0];s.player.pos=V(n['x'],n['y'])
  g.state='PAUSED';g.update(.05);self.assertEqual(n['progress'],0)
  s.player.sigma=100;g.state='PLAYING';g.combat_action('transform');g.update(.05);self.assertEqual(n['progress'],0);g.menu()
 def test_short_cinematics_and_save_discoveries(self):
  p=Player('joe');a=Cinematic.player(p,'transform');b=Cinematic.player(p,'transform');self.assertGreater(a.duration,b.duration);self.assertEqual(Cinematic.read(b.wire()).duration,.6)
  p.short_cinema=False;self.assertEqual(Cinematic.player(p,'transform').duration,a.duration)
  with tempfile.TemporaryDirectory() as d:
   save=SaveManager(Path(d)/'s.json');s=GameSession('joe');s.spawn(kind=0);s.player.clip_seen=p.clip_seen;save.record(s,False);other=SaveManager(save.path)
   self.assertIn('crypt:0',other.data['bestiary']);self.assertTrue(other.data['clip_seen']);self.assertNotIn('leozauxta',other.visible_characters())
 def test_malformed_extended_state_is_rejected_atomically(self):
  s=GameSession('joe');before=snapshot(s)
  for mutate in (lambda d:d['world']['objectives'][0].update(progress=9),lambda d:d['players'][0].update(specialization='spec_thorfinn_0',specialization_rank=1),lambda d:d['world'].update(run_rule='invalid'),lambda d:d['world'].update(discovered={'s':[{}]})):
   data=copy.deepcopy(before);mutate(data)
   with self.assertRaises(ValueError):restore(data,0,s)
   self.assertEqual(snapshot(s),before)
 def test_twelve_vfx_sequences_have_four_real_frames(self):
  from visual_assets import SEQUENCE_NAMES
  art=self.g.render.fx.art;self.assertEqual(set(art.sequences),set(SEQUENCE_NAMES))
  for frames in art.sequences.values():self.assertEqual(len({pg.image.tobytes(f,'RGBA') for f in frames}),4)
 def test_new_menu_paths_render_and_select_rule(self):
  g=self.g;g.menu()
  for state in ('CHALLENGES','BESTIARY','SETTINGS','ANIMATION_GALLERY'):
   g.state=state;g.draw();self.assertTrue(g.buttons)
  g.action('rule:signature');g.action('char:joe');g.action('map:usj');self.assertEqual(g.session.run_rule,'signature');g.draw()
  u=next(u for u in upgrades.UPGRADES if u.id=='damage');from expedition_ui import comparison
  self.assertEqual(comparison(Player('joe'),u,upgrades.RARITIES[0]),'1 → 1.15');g.menu()

class LegendCoopTests(unittest.TestCase):
 def test_four_hero_room_syncs_rule_path_objectives_cutscenes_and_latency(self):
  from multiplayer import Multiplayer
  with tempfile.TemporaryDirectory() as d:
   save=SaveManager(Path(d)/'s.json');h=Multiplayer(save,'joe',host=True,port=0);cs=[]
   try:
    cs=[Multiplayer(save,k,target=f'127.0.0.1:{h.port}') for k in ('thorfinn','holden','klein')]
    def pump(n=25):
     for _ in range(n):h.pump(.02,V());[c.pump(.02,V()) for c in cs]
    pump(65);self.assertEqual(len(h.members),4);h.command('rule',rule='signature');pump()
    h.command('ready');[c.command('ready') for c in cs];pump();h.command('start');pump()
    self.assertEqual(h.phase,'play');self.assertTrue(all(c.session.run_rule=='signature' for c in cs))
    for p in h.session.allied_players:p.level=4;p.pending=1
    pump();self.assertEqual(h.phase,'upgrade');self.assertTrue(all(u.stat=='spec' for u,_ in h.offers[0]))
    h.command('choice',index=0,token=h.tokens[0]);[c.command('choice',index=0,token=c.tokens[c.pid]) for c in cs];pump();self.assertEqual(h.phase,'play')
    h.session.objectives[0]['progress']=3.2;p=h.session.owner(cs[1].pid);p.sigma=100;pump(5);cs[1].command('transform');pump(5)
    self.assertEqual(h.phase,'cinema');self.assertEqual(cs[1].clip.key,'holden');self.assertEqual(cs[0].session.objectives[0]['progress'],3.2)
    cs[1].command('skip');pump(5);p.form_left=0;p.form_recovery=0;p.sigma=100;pump(5);cs[1].command('transform');pump(3)
    self.assertEqual(cs[1].clip.duration,.6);pump(80);self.assertTrue(all(c.rtt_ms is not None and not c.error for c in cs))
   finally:
    for c in cs:c.close()
    h.close()
