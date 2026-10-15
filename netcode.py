"""Non-blocking LAN TCP transport. JSON only, bounded frames and stalled-peer timeouts."""
import errno
import ipaddress
import json
import math
import socket
import struct
import time

VERSION=7
PORT=47640
MAX_FRAME=1024*1024
MAX_BUFFER=3*MAX_FRAME

class ProtocolError(ValueError):pass

def encode(message):
    raw=json.dumps(message,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')
    if len(raw)>MAX_FRAME:raise ProtocolError('Mensagem grande demais')
    return struct.pack('!I',len(raw))+raw

def reject_constant(value):raise ProtocolError('Número inválido')
def finite_float(value):
    number=float(value)
    if not math.isfinite(number):raise ProtocolError('Número fora do intervalo')
    return number

class Peer:
    def __init__(self,sock):
        self.sock=sock;self.sock.setblocking(False);self.sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
        self.inbox=bytearray();self.outbox=bytearray();self.alive=True;self.pid=None;self.last_seen=time.monotonic();self.created=self.last_seen;self.error=''
        self.closing=False;self.close_deadline=0.;self.state_tail=None
    def send(self,message):
        if not self.alive:return
        data=encode(message)
        # Replace only a fully unsent snapshot. Partially sent frames stay intact;
        # control packets following it keep their order. Slow clients see fresh state.
        if message.get('type')=='state' and self.state_tail is not None:
            start,end=self.state_tail;del self.outbox[start:end];self.state_tail=None
        if len(self.outbox)+len(data)>MAX_BUFFER:self.close('Conexão lenta demais');return
        if message.get('type')=='state':self.state_tail=(len(self.outbox),len(self.outbox)+len(data))
        self.outbox.extend(data)
    def pump(self):
        if not self.alive:return []
        if self.closing:
            self.flush()
            if not self.outbox or time.monotonic()>=self.close_deadline:self.close(self.error)
            return []
        messages=[]
        try:
            for _ in range(16):
                try:data=self.sock.recv(65536)
                except BlockingIOError:break
                if not data:self.close('Conexão encerrada');break
                self.last_seen=time.monotonic();self.inbox.extend(data)
                if len(self.inbox)>MAX_BUFFER:raise ProtocolError('Buffer excedido')
            for _ in range(64):
                if len(self.inbox)<4:break
                size=struct.unpack('!I',self.inbox[:4])[0]
                if not 0<size<=MAX_FRAME:raise ProtocolError('Tamanho inválido')
                if len(self.inbox)<size+4:break
                payload=bytes(self.inbox[4:4+size]);del self.inbox[:4+size]
                value=json.loads(payload.decode('utf-8'),parse_constant=reject_constant,parse_float=finite_float)
                if not isinstance(value,dict):raise ProtocolError('Formato inválido')
                messages.append(value)
            self.flush()
            if time.monotonic()-self.last_seen>15:self.close('Tempo de conexão esgotado')
        except (OSError,ValueError,UnicodeError,RecursionError,struct.error) as exc:self.close(str(exc)[:100])
        return messages
    def flush(self):
        if not self.alive or not self.outbox:return
        try:
            count=self.sock.send(self.outbox)
            if count==0:self.close('Conexão encerrada durante o envio');return
            del self.outbox[:count]
            if self.state_tail is not None:
                start,end=self.state_tail
                self.state_tail=(start-count,end-count) if count<=start else None
        except BlockingIOError:pass
        except OSError as exc:self.close(str(exc)[:100])
    def close(self,reason=''):
        if not self.alive:return
        self.error=reason;self.alive=False
        try:self.sock.close()
        except OSError:pass

    def reject(self,reason):
        self.send({'type':'reject','reason':reason});self.closing=True
        self.error=reason;self.close_deadline=time.monotonic()+1.;self.flush()

def address(text,default=PORT):
    value=text.strip() if isinstance(text,str) else ''
    if not value:raise ValueError('Digite o IPv4 do anfitrião mostrado no Radmin VPN.')
    if value.count(':')>1:raise ValueError('Use IPv4 ou IPv4:porta, sem URL.')
    host,sep,port_text=value.partition(':')
    try:
        ip=ipaddress.IPv4Address(host.strip());host=str(ip)
    except ipaddress.AddressValueError as exc:raise ValueError('IP inválido. Use quatro números separados por pontos.') from exc
    if ip.is_unspecified or ip.is_multicast or host=='255.255.255.255':raise ValueError('Use o IPv4 do anfitrião, não um endereço de broadcast ou de rede.')
    if sep:
        port_text=port_text.strip()
        if not port_text.isascii() or not port_text.isdecimal():raise ValueError('Porta inválida. Use um número entre 1 e 65535.')
        port=int(port_text)
    else:port=default
    if type(port) is not int or not 1<=port<=65535:raise ValueError('Porta inválida. Use um número entre 1 e 65535.')
    return host,port

def socket_message(exc,port=PORT):
    code=exc if type(exc) is int else getattr(exc,'winerror',None) or getattr(exc,'errno',None)
    messages={
        errno.ECONNREFUSED:f'Conexão recusada. Abra a sala no anfitrião e confira a porta {port}.',
        10061:f'Conexão recusada. Abra a sala no anfitrião e confira a porta {port}.',
        errno.ETIMEDOUT:'Tempo de conexão esgotado. Confira IP, rede Radmin e firewall.',
        10060:'Tempo de conexão esgotado. Confira IP, rede Radmin e firewall.',
        errno.EHOSTUNREACH:'Anfitrião inacessível. Confira a rede Radmin e o IPv4.',
        errno.ENETUNREACH:'Rede inacessível. Confira se o Radmin está conectado.',
        10065:'Anfitrião inacessível. Confira a rede Radmin e o IPv4.',
        10051:'Rede inacessível. Confira se o Radmin está conectado.',
        errno.EADDRINUSE:f'Porta {port} em uso. Feche outra sala ou outra janela do jogo.',
        10048:f'Porta {port} em uso. Feche outra sala ou outra janela do jogo.',
        errno.EACCES:'O sistema recusou a operação de rede. Confira as permissões do Python.',
        10013:'O sistema recusou a operação de rede. Confira as permissões do Python.',
        10022:'Argumento de socket inválido (10022). A etapa da falha está no log multiplayer.',
    }
    return messages.get(code,f'Falha de socket ({code if code is not None else "sem código"}). Consulte o log multiplayer.')

def movement(value):
    if not isinstance(value,list) or len(value)!=2:return (0.,0.)
    # Arbitrary-size JSON integers must not pass through float conversion.
    if any(type(v) not in (int,float) or type(v) is float and not math.isfinite(v) for v in value):return (0.,0.)
    return tuple(max(-1.,min(1.,v)) for v in value)

def local_addresses():
    try:return sorted({info[4][0] for info in socket.getaddrinfo(socket.gethostname(),None,socket.AF_INET) if not info[4][0].startswith('127.')}) or ['127.0.0.1']
    except OSError:return ['127.0.0.1']
