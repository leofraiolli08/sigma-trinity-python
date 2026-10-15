"""Secret signatures must be defeated, not merely revealed by prerequisites."""
from session import GameSession
from entities import V
import ascension

def create(character,secret,seed=0,sound=None):
    if secret not in ('leozauxta','leozauxtaci'):raise ValueError('Desafio desconhecido')
    s=GameSession(character,seed,sound,'crypt');s.challenge=secret
    s.waves.number=10;s.waves.started=True;s.waves.remaining=0
    p=s.player;p.level=10;p.power=1.65;p.haste=1.25;p.reach=1.25;p.base_hp+=45;p.hp=p.max_hp;p.regen=.6
    p.aux={'knives':2,'lightning':2};p.sigma=100
    ascension.tick(s,0)
    boss=s.spawn(boss=True,pos=p.pos+V(370,-40));boss.trial_key=secret
    boss.name='LEOZAUXTA' if secret=='leozauxta' else 'LEOZAUXTACI COALA'
    boss.max_hp=boss.hp=6500 if secret=='leozauxta' else 8500;boss.speed=90;boss.damage=24 if secret=='leozauxta' else 28
    s.notice('DESAFIO SECRETO • DERROTE A ASSINATURA',4.)
    return s
