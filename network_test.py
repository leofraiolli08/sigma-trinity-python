"""Windows connection ordering and failure injection plus real TCP lifecycle checks."""
import json
import socket
import struct
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from multiplayer import Multiplayer
from netcode import Peer,address,encode,VERSION
from save_manager import SaveManager

class PendingSocket:
    def __init__(self,code=10035,error=0):
        self.code=code;self.error=error;self.pending=True;self.closed=False;self.calls=[];self.sent=bytearray()
    def setblocking(self,value):self.calls.append(('blocking',value))
    def connect_ex(self,dest):self.calls.append(('connect',dest));return self.code
    def getsockopt(self,*args):self.calls.append(('SO_ERROR',));self.pending=False;return self.error
    def setsockopt(self,*args):
        if self.pending:raise OSError(10022,'TCP configuration before connection')
        self.calls.append(('TCP_NODELAY',))
    def getpeername(self):raise AssertionError('Do not probe getpeername to complete connect')
    def recv(self,size):raise BlockingIOError()
    def send(self,buf):self.sent.extend(buf);return len(buf)
    def close(self):self.closed=True

class MemorySocket:
    def __init__(self,limit=7,chunks=None):self.limit=limit;self.chunks=list(chunks or []);self.sent=bytearray();self.closed=False
    def setblocking(self,value):pass
    def setsockopt(self,*args):pass
    def recv(self,size):
        if self.chunks:return self.chunks.pop(0)
        raise BlockingIOError()
    def send(self,buf):count=min(self.limit,len(buf));self.sent.extend(buf[:count]);return count
    def close(self):self.closed=True

def messages(raw):
    found=[]
    while raw:
        size=struct.unpack('!I',raw[:4])[0];found.append(json.loads(raw[4:4+size]));raw=raw[4+size:]
    return found

class NetworkTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.save=SaveManager(Path(self.tmp.name)/'save.json');self.rooms=[]
    def tearDown(self):
        for room in self.rooms:room.close()
        self.tmp.cleanup()
    def client(self,sock):
        with patch('multiplayer.socket.socket',return_value=sock):room=Multiplayer(self.save,target='26.12.34.56:47640')
        self.rooms.append(room);return room
    def test_ipv4_and_port_validation_has_no_raw_inet_pton_failure(self):
        self.assertEqual(address(' 26.12.34.56 : 47640 '),('26.12.34.56',47640))
        for bad in (None,'','x','https://26.12.34.56','26.12.34.999','26.12.34.56:',
                    '26.12.34.56:0','26.12.34.56:65536','26.12.34.56:-2','26.12.34.56:１２','::1','localhost'):
            with self.subTest(bad=bad),self.assertRaises(ValueError):address(bad)
        with self.assertRaises(ValueError):address('127.0.0.1',True)
    def test_windows_pending_socket_never_configured_or_used_early(self):
        sock=PendingSocket();c=self.client(sock)
        self.assertIsNone(c.server);self.assertIs(c.pending_socket,sock)
        with patch('multiplayer.select.select',return_value=([],[],[])) as select:
            c.pump(.02);select.assert_called_once_with([],[sock],[sock],0)
        self.assertFalse(sock.sent);self.assertNotIn(('TCP_NODELAY',),sock.calls)
        with patch('multiplayer.select.select',return_value=([],[sock],[])):c.pump(.02)
        self.assertFalse(c.error);self.assertIsNone(c.pending_socket);self.assertIsNotNone(c.server)
        self.assertLess(sock.calls.index(('SO_ERROR',)),sock.calls.index(('TCP_NODELAY',)))
        self.assertEqual(messages(bytes(sock.sent))[0]['type'],'hello')
        self.assertFalse(c.connected);c.client_receive({'type':'welcome','version':VERSION,'pid':1})
        self.assertTrue(c.connected)
    def test_connect_failure_in_exception_set_reads_SO_ERROR_and_closes(self):
        sock=PendingSocket(error=10061);c=self.client(sock)
        with patch('multiplayer.select.select',return_value=([],[],[sock])):c.pump(.02)
        self.assertIn('recusada',c.error);self.assertTrue(sock.closed);self.assertIsNone(c.server)
        self.assertEqual(c.phase,'error')
    def test_timeout_cancel_and_configuration_error_release_pending_socket(self):
        sock=PendingSocket();c=self.client(sock);c.connect_started=time.monotonic()-9
        with patch('multiplayer.select.select') as select:c.pump(.02);select.assert_not_called()
        self.assertTrue(sock.closed);self.assertIn('Tempo',c.error)
        sock=PendingSocket();c=self.client(sock);c.close();c.pump(.02);self.assertTrue(sock.closed)
        sock=PendingSocket();c=self.client(sock)
        with patch('multiplayer.select.select',return_value=([],[sock],[])),patch.object(sock,'setsockopt',side_effect=OSError(10022,'injected')):c.pump(.02)
        self.assertTrue(sock.closed);self.assertIn('10022',c.error)
    def test_failed_connect_ex_is_closed_and_error_distinguishes_unreachable(self):
        sock=PendingSocket(code=10065);c=self.client(sock)
        self.assertTrue(c.closed);self.assertTrue(sock.closed);self.assertIn('inacessível',c.error)
    def test_handshake_has_its_own_deadline_and_invalid_pid_is_rejected(self):
        sock=PendingSocket();c=self.client(sock)
        with patch('multiplayer.select.select',return_value=([],[sock],[])):c.pump(.02)
        c.handshake_started=time.monotonic()-9;c.pump(.02)
        self.assertIn('handshake',c.error);self.assertTrue(sock.closed)
        sock=PendingSocket();c=self.client(sock)
        for pid in (None,0,4,True,'1'):
            with self.assertRaises(ValueError):c.client_receive({'type':'welcome','version':VERSION,'pid':pid})
    def test_partial_frames_and_snapshot_coalescing_preserve_control_packets(self):
        sock=MemorySocket();p=Peer(sock)
        p.send({'type':'state','n':1});p.flush() # A partial frame cannot be replaced.
        p.send({'type':'state','n':2});p.send({'type':'welcome','pid':1});p.send({'type':'state','n':3})
        for _ in range(100):p.flush()
        rows=messages(bytes(sock.sent));self.assertEqual([(m['type'],m.get('n')) for m in rows],[('state',1),('welcome',None),('state',3)])
        reader=Peer(MemorySocket(chunks=[bytes(sock.sent[:3])]))
        self.assertEqual(reader.pump(),[]);reader.sock.chunks=[bytes(sock.sent[3:17])];self.assertEqual(reader.pump(),[])
        reader.sock.chunks=[bytes(sock.sent[17:])];self.assertEqual(reader.pump(),rows)
    def test_rejection_waits_for_partially_sent_message_before_closing(self):
        sock=MemorySocket(limit=3);p=Peer(sock);p.reject('Sala cheia')
        self.assertTrue(p.alive)
        for _ in range(100):p.pump()
        self.assertFalse(p.alive);self.assertTrue(sock.closed);self.assertEqual(messages(bytes(sock.sent))[0]['reason'],'Sala cheia')
    def test_real_refused_connection_retry_and_listener_port_reuse(self):
        h=Multiplayer(self.save,host=True,port=0);port=h.port;h.close()
        c=Multiplayer(self.save,target=f'127.0.0.1:{port}');self.rooms.append(c)
        for _ in range(20):c.pump(.02)
        self.assertIn('recusada',c.error)
        h=Multiplayer(self.save,host=True,port=port);self.rooms.append(h)
        c=Multiplayer(self.save,target=f'127.0.0.1:{port}');self.rooms.append(c)
        for _ in range(40):h.pump(.02);c.pump(.02)
        self.assertTrue(c.connected);self.assertEqual(len(h.members),2)
    def test_one_accept_configuration_error_does_not_kill_host(self):
        h=Multiplayer(self.save,host=True,port=0);self.rooms.append(h)
        sock=socket.create_connection(('127.0.0.1',h.port))
        try:
            with patch('multiplayer.Peer',side_effect=OSError(10022,'injected')):h.pump(.02)
            self.assertFalse(h.error);self.assertFalse(h.closed)
        finally:sock.close()
