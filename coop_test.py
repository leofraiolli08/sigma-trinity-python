"""Actual TCP integration plus multiplayer combat/progression regression tests."""
import json
import socket
import struct
import subprocess
import sys
import time
import os
import tempfile
import unittest
from pathlib import Path
from entities import V,Projectile,Pickup
from session import GameSession
from save_manager import SaveManager
from multiplayer import Multiplayer
from netcode import encode,movement,MAX_FRAME,VERSION
from netstate import snapshot,restore
from ascension import effect

class CoopTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.save=SaveManager(Path(self.tmp.name)/'save.json')
        self.connections=[]
    def tearDown(self):
        for c in self.connections:c.close()
        self.tmp.cleanup()
    def room(self,count=4):
        h=Multiplayer(self.save,'musashi',host=True,port=0);self.connections.append(h)
        cs=[Multiplayer(self.save,key,target='127.0.0.1:'+str(h.port)) for key in ('ippo','davi','klein')[:count-1]]
        self.connections.extend(cs)
        self.pump(h,cs,60)
        self.assertFalse(h.error);self.assertEqual(len(h.members),count)
        self.assertTrue(all(c.connected and not c.error for c in cs))
        return h,cs
    def pump(self,h,cs,n=20,move=None):
        if move is None:move=V()
        for _ in range(n):
            h.pump(.02,move)
            for c in cs:c.pump(.02,-move)
    def start(self,h,cs):
        h.command('ready')
        for c in cs:c.command('ready')
        self.pump(h,cs);h.command('start');self.pump(h,cs)
        self.assertEqual(h.phase,'play');self.assertTrue(all(c.phase=='play' for c in cs))
    def test_four_clients_share_world_and_independent_movement(self):
        h,cs=self.room();self.start(h,cs);before={p.pid:V(p.pos) for p in h.session.allied_players}
        self.pump(h,cs,50,V(1,0));s=h.session
        self.assertGreater(s.player.pos.x,before[0].x)
        for p in s.allied_players[1:]:self.assertLess(p.pos.x,before[p.pid].x)
        for c in cs:
            self.assertFalse(c.error);self.assertEqual(len(c.session.allied_players),4)
            self.assertEqual(c.session.player.pid,c.pid)
            self.assertAlmostEqual(c.session.time,s.time,delta=.07)
            self.assertEqual(c.session.kills,s.kills)
    def test_all_upgrade_choices_are_authoritative_and_duplicate_safe(self):
        h,cs=self.room();self.start(h,cs)
        for p in h.session.allied_players:p.xp_gain(17)
        self.pump(h,cs);self.assertEqual(h.phase,'upgrade');t=h.session.time
        token=h.tokens[0];h.command('choice',index=0,token=token)
        applied=dict(h.session.player.upgrades);h.command('choice',index=0,token=token)
        self.assertEqual(h.session.player.upgrades,applied)
        for c in cs:c.command('choice',index=0,token=c.tokens[c.pid])
        self.pump(h,cs);self.assertEqual(h.phase,'play')
        self.assertTrue(all(p.pending==0 and p.upgrades for p in h.session.allied_players))
        self.assertGreaterEqual(h.session.time,t)
    def test_boss_phase_victory_endless_and_new_match_sync(self):
        h,cs=self.room();self.start(h,cs);s=h.session;s.waves.number=10;s.waves.started=True
        b=s.spawn(boss=True,pos=s.player.pos+V(300,0))
        for _ in range(3):
            b.phase_age=8;b.phase_guard=0;s.hit(b,1e9,False);s.enemy_update(b,.01)
        self.pump(h,cs,8);self.assertEqual(h.phase,'result');self.assertEqual(s.waves.completed,10)
        self.assertTrue(all(c.session.result=='VICTORY' for c in cs))
        h.command('result_ack')
        for c in cs:c.command('result_ack')
        self.pump(h,cs);h.command('endless');self.pump(h,cs,8)
        self.assertTrue(all(c.session.waves.endless and c.phase=='play' for c in cs))
        s.result='GAME_OVER';self.pump(h,cs,8);h.command('result_ack')
        for c in cs:c.command('result_ack')
        self.pump(h,cs);h.command('restart');self.pump(h,cs,8)
        self.assertEqual(h.phase,'lobby');self.assertTrue(all(c.session is None and c.phase=='lobby' for c in cs))
        self.start(h,cs);self.assertEqual(h.session.waves.number,1)
        self.assertTrue(all(c.session.waves.number==1 for c in cs))
    def test_client_transform_ultimate_cinematics_do_not_spend_form_time(self):
        h,cs=self.room(2);self.start(h,cs);client=cs[0];p=h.session.owner(client.pid);p.sigma=100
        self.pump(h,cs,4);client.command('transform');self.pump(h,cs,5)
        self.assertEqual(h.phase,'cinema');left=p.form_left;t=h.session.time
        self.pump(h,cs,12);self.assertEqual(p.form_left,left);self.assertEqual(h.session.time,t)
        self.assertEqual(client.clip.key,'ippo');client.command('skip');self.pump(h,cs,5)
        self.assertEqual(h.phase,'play');client.command('ultimate');self.pump(h,cs,5)
        self.assertEqual(h.phase,'cinema');self.assertEqual(p.ultimates,0)
        client.command('skip');self.pump(h,cs,5);self.assertEqual(p.ultimates,1)
        client.command('ultimate');self.pump(h,cs,5);self.assertEqual(p.ultimates,1)
    def test_disconnection_keeps_host_playing_and_frees_lobby_slot(self):
        h,cs=self.room();cs[-1].close();self.pump(h,cs[:-1]);self.assertEqual(len(h.members),3)
        self.start(h,cs[:-1]);hp=h.session.spawn(boss=True).hp
        cs[-2].close();self.pump(h,cs[:-2])
        self.assertEqual(len(h.session.allied_players),2);self.assertEqual(h.phase,'play');self.assertLess(h.session.boss.hp,hp)
        h.close();cs[0].pump(.02);self.assertEqual(cs[0].phase,'error')
    def test_full_room_and_incompatible_versions_are_rejected(self):
        h,cs=self.room()
        extra=Multiplayer(self.save,'leo',target='127.0.0.1:'+str(h.port));self.connections.append(extra)
        self.pump(h,cs+[extra]);self.assertEqual(extra.phase,'error');self.assertIn('cheia',extra.error)
        sock=socket.create_connection(('127.0.0.1',h.port));sock.sendall(encode({'type':'hello','version':VERSION-1}));self.pump(h,cs)
        self.assertFalse(h.error);sock.close()
    def test_bad_frame_or_profile_does_not_shutdown_room(self):
        h,cs=self.room(2)
        for content in (struct.pack('!I',MAX_FRAME+1),encode({'type':'hello','version':VERSION,'profile':{'key':'fake'}})):
            sock=socket.create_connection(('127.0.0.1',h.port));sock.sendall(content);self.pump(h,cs)
            self.assertFalse(h.error);self.assertEqual(len(h.members),2);sock.close()
        self.assertEqual(movement([float('nan'),0]),(0.,0.));self.assertEqual(movement([99,-99]),(1.,-1.))
    def test_three_independent_processes_join_and_receive_match(self):
        h=Multiplayer(self.save,'leo',host=True,port=0);self.connections.append(h);h.command('ready')
        script="""
import sys,time,json
from pathlib import Path
from save_manager import SaveManager
from multiplayer import Multiplayer
from entities import V
c=Multiplayer(SaveManager(Path(sys.argv[2])),sys.argv[3],target='127.0.0.1:'+sys.argv[1])
ready=False;deadline=time.monotonic()+8
while time.monotonic()<deadline and not c.error:
 c.pump(.02,V(1,0))
 if c.connected and c.phase=='lobby' and not ready:c.command('ready');ready=True
 if c.session and c.session.time>1:
  print(json.dumps({'pid':c.pid,'count':len(c.session.allied_players),'phase':c.phase,'time':c.session.time}));c.close();raise SystemExit(0)
 time.sleep(.005)
print(c.error or 'timeout');c.close();raise SystemExit(1)
"""
        env=dict(os.environ,PYGAME_HIDE_SUPPORT_PROMPT='1')
        children=[subprocess.Popen([sys.executable,'-c',script,str(h.port),str(Path(self.tmp.name)/f'child{i}.json'),key],cwd=Path(__file__).resolve().parent,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for i,key in enumerate(('ippo','davi','klein'))]
        try:
            deadline=time.monotonic()+10
            while time.monotonic()<deadline and any(p.poll() is None for p in children):
                h.pump(.02,V(-1,0))
                if h.phase=='lobby' and len(h.members)==4 and all(m['ready'] for m in h.members):h.command('start')
                time.sleep(.005)
            for child in children:
                out,err=child.communicate(timeout=1);self.assertEqual(child.returncode,0,(out,err))
                report=json.loads(out.strip());self.assertEqual(report['count'],4);self.assertEqual(report['phase'],'play');self.assertGreater(report['time'],1)
        finally:
            for child in children:
                if child.poll() is None:child.kill();child.wait()
    def test_snapshot_preserves_sources_owners_builds_and_rhythm(self):
        s=GameSession('leo');p=s.add_player('leozauxta',1);p.sigma=100;s.action_for(1,'transform');s.transform_pause=0
        with s.acting(p):
            s.weapon.ultimate(s);s.add_projectile(Projectile(V(p.pos),V(300,0),15,'token'));effect(s,'swarm',p.pos)
        s.spawn(boss=True);raw=json.loads(json.dumps(snapshot(s)));remote=restore(raw,1)
        self.assertEqual(remote.player.key,'leozauxta');self.assertEqual(remote.projectiles[0].owner,1)
        self.assertIs(remote.telegraphs[0].source,remote.player);self.assertEqual(remote.telegraphs[0].owner,1)
        self.assertTrue(remote.rhythm.active);self.assertEqual(remote.boss.uid,s.boss.uid)
        self.assertEqual(remote.player.form_left,s.owner(1).form_left)
    def test_hostile_damage_targets_each_player_and_revive(self):
        s=GameSession('leo');p=s.add_player('davi',1);s.player.pos=V(900,900);p.pos=V(1800,1800)
        q=Projectile(V(p.pos)-V(20,0),V(400,0),20,'hostile',hostile=True)
        hp=s.player.hp;s.projectile_update(q,.05);self.assertLess(p.hp,p.max_hp);self.assertEqual(s.player.hp,hp)
        p.invulnerable=0
        with s.acting(p):s.hurt_player(9999)
        self.assertIsNone(s.result);s.player.pos=V(p.pos)+V(40,0);s.player.invulnerable=999
        s.waves.started=True;s.waves.remaining=99;s.spawn_cd=999;s.hazard_cd=999
        for _ in range(65):s.update(.05,{0:V(),1:V()})
        self.assertGreater(p.hp,0)
    def test_shared_pickups_do_not_multiply_coins_or_chests(self):
        s=GameSession('leo')
        for pid,key in enumerate(('davi','guxta','zatex'),1):s.add_player(key,pid)
        s.pickups=[Pickup(V(s.player.pos),17),Pickup(V(s.player.pos),1,'chest')]
        s.spawn_cd=999;s.waves.started=True;s.waves.remaining=10;s.update(.01)
        self.assertEqual(s.chests,1);self.assertEqual(s.coins,15)
        self.assertTrue(all(p.level==2 for p in s.allied_players))
    def test_musashi_buff_reaches_real_allies_and_owner_damage_is_independent(self):
        s=GameSession('musashi');p=s.add_player('davi',1);s.player.stage=3;s.player.soul_mode='bond'
        s.weapon.skill(s,None);self.assertGreater(p.aura_power,0)
        p.crit=0;s.player.crit=.8;s.player.base_damage=9999;p.base_damage=10
        e=s.spawn(kind=0,pos=p.pos+V(10,0));e.hp=e.max_hp=1000
        with s.acting(p):q=Projectile(V(p.pos),V(400,0),10,'air');s.add_projectile(q)
        with s.acting(s.owner(q.owner)):s.projectile_update(q,.05)
        self.assertEqual(e.hp,990)
