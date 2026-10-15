from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
WIDTH, HEIGHT = 1280, 720
FPS = 60
RUN_DURATION = 300.0
WORLD_SIZE = 3600
SCREEN_SHAKE_ENABLED = True
MAX_ENEMIES, MAX_PROJECTILES, MAX_PARTICLES = 160, 280, 400
BG = (12, 12, 13)
INK = (227, 220, 204)
MUTED = (157, 152, 141)
CYAN = (148, 187, 187)
GOLD = (194, 158, 98)
GREEN = (145, 176, 140)
PINK = (191, 80, 84)
CHARACTERS = {
 'davi': dict(name='DAVI COALA',color=(103,217,156),hp=105,damage=26,speed=240,crit=.12,
 form='FULL COWL',weapon='Delaware Smash',role='IMPACTO / MOBILIDADE',
 desc='Um coala. Cem por cento de coragem.',ratings=(4,3,5,3)),
 'leo': dict(name='LEO', color=CYAN, hp=125, damage=23, speed=225, crit=.08,
             form='CALVO ABSOLUTO', weapon='Tacada de cola', role='CONTROLE / RESISTÊNCIA',
             desc='O cabelo acaba. O poder não.', ratings=(3,5,3,5)),
 'rafael': dict(name='RAFAEL', color=GOLD, hp=95, damage=30, speed=240, crit=.24,
                form='PAÇOCA ASCENDIDA', weapon='Paçoca balística', role='DISTÂNCIA / CRÍTICO',
                desc='Contém amendoim e poder absoluto.', ratings=(5,2,4,3)),
 'leozauxta': dict(name='LEOZAUXTA', color=GREEN, hp=115, damage=34, speed=215, crit=.12,
                   form='TITÃ SIGMA TRÍPLICE', weapon='Robux Barrage', role='TRIO / PODER MÁXIMO',
                   desc='Três cabeças. Uma péssima influência.', ratings=(5,4,2,4)),
}
ENEMY_NAMES = ['SIGMA HATER','NPC','BRAINROT SLIME','TAX COLLECTOR','ANTI-SIGMA BAT','CRINGE KNIGHT']

CHARACTERS['davi'] = CHARACTERS.pop('davi')

CHARACTERS['walter']=dict(name='WALTER WHITE',color=(131,199,226),hp=100,damage=28,speed=220,crit=.12,form='TRAJE HAZMAT',weapon='Reação em cadeia',role='QUÍMICA / EVOLUÇÃO',desc='Professor. Depois, Heisenberg.',ratings=(4,3,3,4))

CHARACTERS['guxta']=dict(name='GUXTA',color=(211,85,99),hp=110,damage=25,speed=230,crit=.10,form='LUA VERMELHA',weapon='Pulso gravitacional',role='GRAVIDADE / CONTROLE',desc='A caneta caiu. A gravidade também.',ratings=(4,3,3,5))
CHARACTERS['ippo']=dict(name='IPPO MAKUNOUCHI',color=(238,130,94),hp=145,damage=34,speed=245,crit=.13,form='PEEK-A-BOO',weapon='Jab / direto',role='BOXE / COMBOS',desc='Desafiante > campeão no nível 6.',ratings=(5,4,4,2))
CHARACTERS['eren']=dict(name='EREN YEAGER',color=(129,184,142),hp=125,damage=27,speed=248,crit=.1,form='TITÃ DE ATAQUE',weapon='Lâminas duplas',role='MOBILIDADE / TITÃ',desc='Soldado > veterano no nível 6.',ratings=(5,4,4,3))
CHARACTERS['klein']=dict(name='KLEIN MORETTI',color=(187,160,229),hp=95,damage=24,speed=235,crit=.16,form='PREPARAÇÃO',weapon='Bala de ar / cartas',role='TRUQUES / CONTROLE',desc='Mágico > Sem Rosto > Marionetista.',ratings=(4,2,4,5))
CHARACTERS['zatex']=dict(name='ZATEX',color=(170,153,236),hp=110,damage=26,speed=235,crit=.14,form='MAESTRO DO VÉU',weapon='Ressonância',role='ECO / CONTROLE',desc='A voz transforma a arena.',ratings=(4,3,4,5))
CHARACTERS['leozauxtaci']=dict(name='LEOZAUXTACI COALA',color=(233,202,136),hp=155,damage=33,speed=230,crit=.15,form='CONVERGÊNCIA FINAL',weapon='Quatro assinaturas',role='FUSÃO / CONVERGÊNCIA',desc='Quatro formas finais. Uma vontade.',ratings=(5,5,4,5))
CHARACTERS['musashi']=dict(name='MUSASHI MIYAMOTO',color=(221,193,135),hp=118,damage=29,speed=242,crit=.15,form='MUSHIN',weapon='Niten Ichi-ryū',role='ESPADA / POSTURAS',desc='A lâmina encontra o vazio, não a glória.',ratings=(5,4,5,3))

CHARACTERS['joe']=dict(name='JOE YABUKI',color=(232,122,94),hp=128,damage=29,speed=250,crit=.14,form='ESPÍRITO DE LUTA',weapon='Cross Counter',role='CONTRA-ATAQUE / RISCO',desc='Vagante > peso-galo > sem guarda. Evolui nos níveis 6 e 12.',ratings=(5,3,4,2))
CHARACTERS['thorfinn']=dict(name='THORFINN',color=(179,203,160),hp=120,damage=26,speed=260,crit=.12,form='NÃO TENHO INIMIGOS',weapon='Adagas / deflexão',role='MOBILIDADE / PROTEÇÃO',desc='Vingança > renascer > explorador > Vinland. Níveis 5, 10 e 15.',ratings=(4,4,5,3))
CHARACTERS['holden']=dict(name='JUDGE HOLDEN',color=(215,193,159),hp=150,damage=32,speed=212,crit=.10,form='A DANÇA DO JUIZ',weapon='Rifle perfurante',role='PRECISÃO / TERRITÓRIO',desc='Naturalista > atirador > estrategista > dança. Níveis 5, 10 e 15.',ratings=(5,4,2,4))
