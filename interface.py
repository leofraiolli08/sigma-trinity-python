"""Dark, legible menu composition using existing character art (no spoilers)."""
import math
import pygame as pg
from settings import CHARACTERS,INK,MUTED,GOLD,CYAN,GREEN
from settings import BASE_DIR
from release_info import RELEASE_ID,RELEASE_TITLE

def portrait(g,key,pos,box,form=False):
    name='portrait_'+key+('_form' if form else '')
    if name in g.assets.images:
        w,h=g.assets.logical[name];g.render.sprite(name,pos,min(box[0]/w,box[1]/h))

def main(g):
    from ui_design import icon,stat,badge,player_portrait
    r=g.render
    r.text('SOBREVIVA AO COLAPSO',48,154,19,GOLD)
    r.title('SIGMA',43,185,100,INK);r.title('TRINITY',47,266,85,GOLD)
    r.text('Dez ondas. Uma vitória. Infinitas possibilidades.',48,355,22,MUTED)
    g.button((48,400,435,58),'INICIAR EXPEDIÇÃO','play',GOLD)
    g.button((48,474,435,50),'COOPERATIVO • 2 A 4 JOGADORES','multiplayer',CYAN)
    g.button((48,540,211,57),'ARSENAL / MISSÕES','missions',CYAN)
    g.button((272,540,211,57),'CONQUISTAS / LOJA','archive',GOLD)
    g.button((48,603,211,29),'EXPEDIÇÕES','challenges',CYAN)
    g.button((272,603,211,29),'BESTIÁRIO','bestiary',GOLD)
    for i,(label,action) in enumerate([('AJUDA','help'),('AJUSTES','settings'),('SAIR','quit')]):g.button((48+i*148,640,138,36),label,action,MUTED)
    r.panel((529,151,703,400),(19,19,29),(84,67,72),2)
    if not hasattr(r,'hero_back'):
        r.hero_back=r.map_preview('crypt',(697,393)).copy()
        veil=pg.Surface(r.hero_back.get_size(),pg.SRCALPHA);veil.fill((14,14,29,160));r.hero_back.blit(veil,(0,0))
    r.canvas.blit(r.hero_back,(532,154))
    for radius in (100,155):pg.draw.circle(r.canvas,(71,60,67),(927,345),radius,1)
    badge(r,'ASCENSÃO / 01',552,175,GOLD)
    player_portrait(g,'leo',(809,506),(204,278),True)
    player_portrait(g,'davi',(1038,506),(226,283),True)
    from expedition import track_lines
    for i,line in enumerate(track_lines(g.save.data)):r.text(line,551,514+i*21,17,INK if i==0 else MUTED)
    for rect,label,value in [((529,571,224,80),'ESSÊNCIAS',g.save.data['coins']),((769,571,224,80),'MELHOR ONDA',g.save.data['best_wave']),((1009,571,223,80),'CONQUISTAS',len(g.save.data['achievements']))]:stat(r,rect,label,value)
    if g.save.challenge_available('leozauxta') or g.save.challenge_available('leozauxtaci'):g.button((1009,661,223,33),'???','trial',GOLD)
    else:r.text('ATAQUES AUTOMÁTICOS • EVOLUÇÕES • SEGREDOS',879,682,17,MUTED,True)
    g.button((986,22,247,32),'VERSÃO / ARTES','release_info',GOLD)

def release_info(g):
    r=g.render
    r.title(f'SIGMA TRINITY • {RELEASE_ID}',640,70,42,INK,True)
    r.text(RELEASE_TITLE,640,101,20,GOLD,True)
    r.text('Sprites realmente carregados por esta instalação',640,149,24,INK,True)
    themes=(('crypt','CRIPTA'),('usj','U.A.'),('city','CIDADE'),('ring','GINÁSIO'),('walls','MURALHAS'),('fog','BACKLUND'))
    for i,(theme,label) in enumerate(themes):
        x=40+i*202;r.panel((x,181,190,176),(20,27,39),GOLD)
        name=f'{theme}_anim_0_1'
        if name in g.assets.images:
            w,h=g.assets.logical.get(name,g.assets.images[name].get_size())
            r.sprite(name,(x+95,311),min(120/w,113/h))
        r.text(label,x+95,328,20,CYAN,True)
        r.text('ARTE CARREGADA' if g.assets.monster_animation_status.get(theme)=='animated' else 'ARTE AUSENTE',x+95,348,14,GREEN if g.assets.monster_animation_status.get(theme)=='animated' else GOLD,True)
    r.text('ARTES E CÓDIGO VERIFICADOS' if not g.installation_errors else 'INSTALAÇÃO INCOMPLETA / ARQUIVOS MISTURADOS',640,388,24,GREEN if not g.installation_errors else GOLD,True)
    r.text('Seis bestiários animados: movimento, preparação, ataque e derrota.',640,431,22,INK,True)
    r.text('Joe, Thorfinn e Holden: novos estilos de combate e evoluções.',640,459,21,MUTED,True)
    r.text('E / Q: cutscenes diferentes • Menu: cooperativo para até quatro jogadores',640,498,22,CYAN,True)
    # The actual install path helps distinguish an old shortcut from this folder.
    r.text('PASTA ABERTA',40,546,17,GOLD)
    path=str(BASE_DIR);parts=[];line=''
    for char in path:
        if r.a.font(18).size(line+char)[0]>1190:parts.append(line);line=''
        line+=char
    parts.append(line)
    for i,line in enumerate(parts[:2]):r.text(line,40,570+i*22,18,MUTED)
    g.button((845,608,395,35),'ANIMAÇÕES DOS PERSONAGENS','animation_gallery',CYAN)
    g.button((440,650,400,42),'VOLTAR','back',GOLD)

def animation_gallery(g):
    from evolution_kit import STAGES
    from pixel_characters import KEYS
    from entities import Player
    r=g.render
    r.title('EVOLUÇÕES • BASE E TRANSFORMAÇÃO',640,72,35,INK,True)
    r.text('Cada estágio tem arte, postura, transformação e ultimate próprias.',640,101,19,MUTED,True)
    for i,key in enumerate(KEYS[g.gallery_page*4:g.gallery_page*4+4]):
        x=32+i*312;color=CHARACTERS[key]['color'];stage=int(g.ui_time/4)%len(STAGES[key])
        p=Player(key);p.stage=stage;p.evolved=bool(stage)
        r.panel((x,162,280,385),(20,27,39),color,2)
        r.text(key.upper(),x+140,192,27,color,True)
        r.text(f'EVOLUÇÃO {stage} / {len(STAGES[key])-1}',x+140,228,18,MUTED,True)
        for j,form in enumerate((False,True)):
            p.form_left=int(form);p.walking=True
            p.attack_animation_left=.28-(g.ui_time%1)*.28 if int(g.ui_time)%2 else 0
            name=p.sprite(g.ui_time)
            if name in g.assets.images:
                w,h=g.assets.logical[name];r.sprite(name,(x+75+j*133,414),min(120/w,160/h))
            r.text('BASE' if not form else 'FORMA / E',x+75+j*133,449,17,color,True)
        from ui_design import wrap
        wrap(r,STAGES[key][stage][1],x+16,479,246,18,MUTED,21)
    r.text('Leo, Rafael, Guxta, Zatex, Davi e as fusões usam avatares fictícios de IA.',640,590,20,MUTED,True)
    g.button((440,608,400,32),f'PRÓXIMOS • {g.gallery_page+1}/2','gallery_next',CYAN)
    g.button((440,650,400,42),'VOLTAR','release_info',GOLD)

def roster(g):
    from ui_design import header,wrap,player_portrait,pips,badge
    r=g.render;keys=g.save.visible_characters();pages=max(1,(len(keys)+5)//6);g.roster_page%=pages
    page=keys[g.roster_page*6:g.roster_page*6+6]
    header(r,'Escolha sua assinatura' if not g.pending_trial else '??? / Enfrente o desconhecido','1–6 para escolher • setas para mudar de página')
    if g.focus_character not in page:g.focus_character=page[0]
    for i,key in enumerate(page):
        x=395+i%3*285;y=166+i//3*238;c=CHARACTERS[key]
        if pg.Rect(x,y,270,222).collidepoint(g.mouse):g.focus_character=key
        active=key==g.focus_character
        r.panel((x,y,270,222),(36,32,42) if active else (24,25,34),c['color'] if active else (66,61,72),2 if active else 1)
        name=c['name'];size=23
        while r.a.font(size).size(name)[0]>238:size-=1
        r.text(name,x+16,y+15,size,c['color'])
        pg.draw.line(r.canvas,(58,51,63),(x+16,y+48),(x+254,y+48))
        for j,form in enumerate((False,True)):player_portrait(g,key,(x+82+j*117,y+158),(96,106),form,True)
        r.text(c['role'],x+135,y+171,16,MUTED,True)
        g.button((x+12,y+190,246,25),f'[{i+1}] ESCOLHER','char:'+key,c['color'])
    key=g.focus_character;c=CHARACTERS[key]
    r.panel((32,166,338,462),(24,23,33),c['color'],2)
    badge(r,'PERFIL DE COMBATE',51,185,c['color'])
    size=27
    while r.a.font(size).size(c['name'])[0]>300:size-=1
    r.text(c['name'],51,226,size,c['color'])
    player_portrait(g,key,(200,458),(269,193),True,True)
    r.text(c['form'],200,477,21,INK,True)
    r.text(f'VIDA {c["hp"]}  /  DANO {c["damage"]}',200,506,18,MUTED,True)
    wrap(r,c['desc'],51,537,300,18,MUTED,20)
    for i,(label,rating) in enumerate(zip(('DANO','DEFESA','MOVIMENTO','CONTROLE'),c['ratings'])):
        xx=51+i%2*159;yy=583+i//2*23;r.text(label,xx,yy,13,MUTED);pips(r,xx+80,yy+4,rating,5,c['color'],9)
    g.button((32,662,180,36),'VOLTAR','menu')
    g.button((773,662,220,36),'PÁGINA ANTERIOR','roster_prev')
    g.button((1006,662,242,36),f'PRÓXIMA • {g.roster_page+1}/{pages}','roster_next')

def end(g):
    from ui_design import header,stat,player_portrait,wrap,badge
    r=g.render;s=g.session;victory=g.state=='VICTORY';r.dim();color=GREEN if victory else GOLD
    header(r,'Você atravessou o colapso.' if victory else 'Toda jornada deixa uma marca.',
           'Vitória registrada. O infinito ainda espera por você.' if victory else 'Recompensas das ondas concluídas foram preservadas.',
           'EXPEDIÇÃO CONCLUÍDA' if victory else 'FIM DA EXPEDIÇÃO')
    r.panel((62,192,344,398),(25,24,34),color,2)
    player_portrait(g,s.player.key,(235,518),(220,261),s.player.transformed,True)
    size=25
    while r.a.font(size).size(s.player.display_name)[0]>308:size-=1
    r.text(s.player.display_name,235,220,size,INK,True)
    r.text('SUA ASSINATURA',235,558,18,color,True)
    for i,(label,value) in enumerate([('ONDA ALCANÇADA',s.waves.number),('INIMIGOS DERROTADOS',s.kills),('NÍVEL FINAL',s.player.level),('ESSÊNCIAS GANHAS',s.reward)]):
        stat(r,(438+i%2*387,192+i//2*112,358,92),label,value,color)
    if g.new_secrets:
        r.text('NOVA ASSINATURA DESCOBERTA',438,438,21,GOLD)
        wrap(r,' / '.join(CHARACTERS[k]['name'] for k in g.new_secrets),438,470,750,27,INK,28)
    else:
        r.text(f'{len(s.awarded)} CONQUISTAS NESTA EXPEDIÇÃO',438,438,21,GOLD)
        r.text(f'DANO {s.player.damage_dealt:,.0f}  •  DPS {s.player.damage_dealt/max(1,s.time):.1f}  •  DANO RECEBIDO {s.player.damage_taken:,.0f}',438,473,19,MUTED)
    from specializations import label
    r.text(label(s.player)+f' • GRAU {s.player.specialization_rank}',438,500,18,CYAN)
    if s.telemetry['boss_seconds']:r.text(f'CHEFE / {s.telemetry["boss_seconds"]:.1f}s',438,518,15,MUTED)
    if victory and not s.challenge and (not g.net or g.net.is_host):
        g.button((438,534,745,56),'CONTINUAR / ONDAS INFINITAS' if not g.net or g.net.results_ready else 'AGUARDANDO OS SAVES DOS ALIADOS…','endless',GOLD,not g.net or g.net.results_ready)
    if not g.net:g.button((438,614,359,45),'NOVA TENTATIVA','restart',CYAN)
    elif g.net.is_host:g.button((438,614,359,45),'NOVA EXPEDIÇÃO','network_restart',CYAN,g.net.results_ready)
    g.button((824 if not g.net or g.net.is_host else 438,614,359 if not g.net or g.net.is_host else 745,45),'VOLTAR AO MENU','menu',MUTED)
    r.text('Desafio vencido: a assinatura está na seleção.' if victory and s.challenge else 'Cada dez ondas: um novo chefe, mais dificuldade e mais recompensas.',640,693,18,MUTED,True)
