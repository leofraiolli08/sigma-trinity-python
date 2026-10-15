"""Menus share the same hierarchy, spacing, icons and interaction language."""
import pygame as pg
from settings import INK,MUTED,GOLD,CYAN,GREEN,PINK,CHARACTERS
from maps import MAPS
from ui_design import header,wrap,icon,badge,pips,player_portrait

def level_up(g):
    r=g.render;p=g.session.player;r.dim()
    header(r,'Escolha sua próxima vantagem',f'Nível {p.level} • {1+len(p.aux)}/6 armas • {len(p.passives)}/6 passivas','AURA EM ASCENSÃO')
    for i,(u,rarity) in enumerate(g.choices):
        x=54+i*398;color=rarity[2];level=p.upgrades.get(u.id,0)
        if u.stat=='spec':
            from specializations import SPECS
            color=((230,108,90),(229,192,111),(143,189,166))[SPECS[u.id][2]]
        r.panel((x,185,374,398),(26,24,35),color,2)
        badge(r,rarity[0],x+20,205,rarity[2]);r.text(f'0{i+1}',x+310,204,35,color)
        r.panel((x+20,252,80,80),(13,14,22),color)
        icon(r,u.id if u.stat=='spec' else u.id[4:] if u.stat=='aux' else u.stat,x+60,292,color,66)
        badge(r,'ESPECIALIZAÇÃO' if u.stat=='spec' else 'NOVA ARMA' if u.stat=='aux' and not level else 'APRIMORAMENTO',x+105,276,MUTED)
        wrap(r,u.name,x+20,344,332,31,INK,31)
        wrap(r,u.description,x+20,413,332,22,MUTED,26)
        from ascension import RECIPES
        matches=[(key,name,passive,evolution) for key,(name,passive,evolution) in RECIPES.items() if u.id in ('aux_'+key,passive) and key not in p.evolutions]
        if matches:
            key,name,passive,evolution=matches[0]
            weapon_level=p.aux.get(key,0)+(int(u.stat=='aux' and u.id=='aux_'+key))
            support=p.upgrades.get(passive,0)>0 or u.id==passive
            r.text('RECEITA / '+evolution.upper(),x+20,479,15,GOLD)
            r.text(('✓' if weapon_level>=4 else '○')+' ARMA NV.4   '+('✓' if support else '○')+' PASSIVA   + BAÚ',x+20,500,15,GOLD if weapon_level>=4 and support else MUTED)
        pips(r,x+20,520,level+1,min(u.max_level,8),color,21)
        r.text(f'{"GRAU" if u.stat=="spec" else "NÍVEL"} {level} → {level+1}',x+20,546,18,color)
        if rarity[1]>1 and u.stat not in ('shots','triple','shards','aux','spec'):r.text(f'POTÊNCIA ×{rarity[1]:.1f}',x+230,546,18,color)
        g.button((x,602,374,46),f'[{i+1}] ESCOLHER','choice:'+str(i),color)
        from expedition_ui import comparison
        r.text(comparison(p,u,rarity),x+20,568,16,INK)
    g.button((470,668,340,35),f'[R] NOVAS OPÇÕES • {p.rerolls}','reroll',GOLD,p.rerolls>0 and not (p.level>=4 and not p.specialization))

def settings(g):
    r=g.render
    if g.session:r.dim()
    header(r,'Ajuste a sua experiência','Clique para alternar • ↑ ↓ e Enter também funcionam','CONFIGURAÇÕES')
    quality={'full':'COMPLETOS','balanced':'EQUILIBRADOS','low':'LEVE'}[g.opts['effects']]
    r.panel((45,176,562,424),(25,24,34));r.panel((632,176,603,424),(25,24,34))
    r.text('ÁUDIO',70,198,22,GOLD);r.text('IMAGEM E CONFORTO',658,198,22,CYAN)
    rows=[(f'SONS • {int(g.opts["volume"]*100)}%','volume'),(f'MÚSICA • {int(g.opts["music_volume"]*100)}%','music_volume'),('PRÓXIMA FAIXA • N','next_music')]
    for i,(label,action) in enumerate(rows):g.button((70,245+i*69,512,50),label,action,GOLD)
    wrap(r,g.music.label,70,475,502,20,MUTED)
    r.text('M / silenciar    N / próxima música',70,556,18,MUTED)
    rows=[('TELA CHEIA • '+('SIM' if g.fullscreen else 'NÃO'),'fullscreen'),('TREMER TELA • '+('SIM' if g.opts['shake'] else 'NÃO'),'shake'),('DANO VISÍVEL • '+('SIM' if g.opts['numbers'] else 'NÃO'),'numbers'),('EFEITOS • '+quality,'effects'),('CLARÕES • '+('SIM' if g.opts['flashes'] else 'NÃO'),'flashes'),('CENAS REPETIDAS CURTAS • '+('SIM' if g.opts['short_cinema'] else 'NÃO'),'short_cinema')]
    for i,(label,action) in enumerate(rows):g.button((658,237+i*52,550,43),label,action,CYAN)
    wrap(r,'Modo leve reduz efeitos. Desative clarões para evitar flashes de tela. Perigos continuam visíveis.',658,560,548,18,MUTED)
    g.button((440,651,400,43),'VOLTAR','back',GOLD)

def help_screen(g):
    r=g.render
    if g.session:r.dim()
    header(r,'Domine a expedição','Movimente-se, reúna aura e construa sua próxima evolução.','GUIA DE SOBREVIVÊNCIA')
    lines=[('WASD / SETAS','Movimento. Seus ataques miram automaticamente.'),('ESPAÇO','Dash com breve proteção. Recarga: 2,4 segundos.'),('E','Barra Sigma cheia: transforme por 14 segundos.'),('Q','Uma ultimate por transformação, com cutscene própria.'),('F','Musashi no Caminho da Alma: alterna Ego / Vínculo.'),('D F K J','Dança de Leozauxta: acertos protegem e atacam.'),('1 / 2 / 3','Escolha cartas. R troca as opções disponíveis.'),('ESC / TAB','Pausa / build. No cooperativo são menus locais.')]
    for i,(key,desc) in enumerate(lines):
        y=174+i*51;r.panel((40,y,1200,44),(24,24,33))
        r.text(key,58,y+12,20,CYAN);r.text(desc,271,y+12,22,INK)
    r.text('ONDA 10 / derrote o chefe para vencer. Depois, continue no infinito.',640,615,23,GOLD,True)
    g.button((440,660,400,38),'VOLTAR','back',GOLD)

def pause(g):
    r=g.render;r.dim();header(r,'Um instante antes do próximo golpe','No cooperativo, seus aliados continuam jogando.' if g.net else 'O combate e os tempos de recarga estão pausados.','EXPEDIÇÃO EM ANDAMENTO')
    actions=[('CONTINUAR','resume'),('BUILD / RECEITAS','build')]
    if not g.net:actions.append(('REINICIAR','restart'))
    actions.extend([('CONFIGURAÇÕES','settings'),('VOLTAR AO MENU','menu'),('SAIR','quit')])
    for i,(label,action) in enumerate(actions):g.button((430,186+i*74,420,53),label,action,GOLD if i==0 else CYAN)

def network(g):
    r=g.render;net=g.net
    if g.state=='NETWORK_WAIT':
        r.dim();header(r,'Os aliados estão escolhendo','A expedição continua quando todos concluírem suas melhorias.','COOPERATIVO')
        if net:
            for i,m in enumerate(net.members):
                x=50+i*305;r.panel((x,231,280,250),(26,24,35))
                player_portrait(g,m['key'],(x+140,404),(150,146),animated=True)
                r.text('ESCOLHENDO' if m['pid'] in net.offers else 'PRONTO',x+140,445,22,GOLD if m['pid'] in net.offers else GREEN,True)
        return
    header(r,'Ninguém atravessa o colapso sozinho','Cooperativo de 2 a 4 jogadores • LAN / Radmin VPN • TCP 47640','EXPEDIÇÃO COOPERATIVA')
    if g.state=='MULTIPLAYER_MENU':
        for i,(title,desc,kind,button,action,color) in enumerate([
            ('ABRA AS PORTAS','Escolha a arena, reúna seu grupo e inicie a expedição.','team','CRIAR SALA','network_host',GOLD),
            ('ENTRE NA EXPEDIÇÃO','Use o IPv4 do anfitrião mostrado no Radmin VPN.','control','ENTRAR EM UMA SALA','network_join',CYAN)]):
            x=60+i*600;r.panel((x,203,560,352),(25,24,34),color,2);icon(r,kind,x+54,260,color,40)
            r.text(title,x+28,317,29,INK);wrap(r,desc,x+28,373,496,24,MUTED)
            g.button((x+28,476,504,52),button,action,color)
        r.text('Todos usam o mesmo ZIP e entram na mesma rede virtual do Radmin.',640,607,22,MUTED,True)
    elif g.state=='NETWORK_JOIN':
        r.panel((246,212,788,350),(25,24,34),CYAN,2)
        r.text('ENDEREÇO DO ANFITRIÃO',276,241,20,CYAN)
        r.text('IPv4 ou IPv4:porta • Ctrl+V para colar',276,278,21,MUTED)
        r.panel((276,324,728,76),(13,17,24),CYAN)
        text=g.network_target+('|' if int(g.ui_time*2)%2==0 else '')
        r.text(text or '26.12.34.56',304,349,35,CYAN if g.network_target else MUTED)
        g.button((276,447,728,54),'CONECTAR • ENTER','network_connect',GOLD)
        r.text('O endereço acima é apenas um exemplo de formato.',640,536,17,MUTED,True)
    elif g.state=='NETWORK_ERROR':
        r.panel((177,203,926,384),(28,23,34),PINK,2)
        icon(r,'control',227,250,PINK,34);r.text('A CONEXÃO PRECISA DE ATENÇÃO',266,236,31,INK)
        wrap(r,g.network_message,208,297,854,27,INK,31)
        r.text('Confira a sala aberta, o IPv4 e a mesma rede Radmin.',208,408,22,MUTED)
        r.text('Logs: logs/multiplayer.log',208,444,19,GOLD)
        if net:r.text('Etapa: '+net.connection_stage+' • diagnóstico '+net.trace_id,208,473,18,MUTED)
        g.button((208,523,419,42),'TENTAR NOVAMENTE','network_retry',GOLD)
        g.button((647,523,419,42),'CORRIGIR ENDEREÇO','network_join',CYAN)
    elif net and (net.connecting or not net.connected):
        stage=net.connection_stage
        r.text('Preparando sua entrada…',640,266,36,INK,True)
        for i,(label,done) in enumerate([('ENDEREÇO',stage!='validar'),('CONEXÃO TCP',stage in ('configurar','handshake','sala')),('ENTRADA NA SALA',net.connected)]):
            x=206+i*294;r.panel((x,340,276,104),(25,24,34),GREEN if done else CYAN)
            r.text('OK' if done else '…',x+138,368,30,GREEN if done else GOLD,True);r.text(label,x+138,413,18,MUTED,True)
        r.text('Você pode cancelar e corrigir o endereço.',640,514,22,MUTED,True)
    elif net:
        if net.is_host:
            ips=' / '.join(net.addresses)
            r.text('IPs locais: '+ips+'  •  porta '+str(net.port),640,169,20,GOLD,True)
            r.text('Pelo Radmin, compartilhe o IPv4 exibido no aplicativo Radmin VPN.',640,195,18,MUTED,True)
        for i in range(4):
            x=50+i*305;m=next((m for m in net.members if m['pid']==i),None)
            color=GREEN if m and m['ready'] else CHARACTERS[m['key']]['color'] if m else (68,63,75)
            r.panel((x,232,280,276),(27,26,35),color,2 if m else 1)
            badge(r,'P'+str(i+1)+(' / ANFITRIÃO' if i==0 else ' / ALIADO'),x+16,249,GOLD if i==0 else CYAN)
            if m:
                player_portrait(g,m['key'],(x+140,423),(148,138),animated=True)
                size=23
                while r.a.font(size).size(CHARACTERS[m['key']]['name'])[0]>254:size-=1
                r.text(CHARACTERS[m['key']]['name'],x+140,445,size,INK,True)
                r.text('PRONTO' if m['ready'] else 'PREPARANDO',x+140,484,18,GREEN if m['ready'] else MUTED,True)
            else:
                icon(r,'team',x+140,355,MUTED,35);r.text('AGUARDANDO ALIADO',x+140,411,19,MUTED,True)
        r.text('ARENA / '+MAPS[net.map_key][0],640,533,24,GOLD,True)
        from expedition import RULES
        if net.is_host:g.button((442,556,396,24),'REGRA / '+RULES[net.run_rule][0],'network_rule',CYAN)
        else:r.text('REGRA / '+RULES[net.run_rule][0],640,563,18,CYAN,True)
        g.button((50,589,275,47),'PERSONAGEM','network_character',CYAN)
        g.button((355,589,275,47),'CANCELAR PRONTO' if next((m['ready'] for m in net.members if m['pid']==net.pid),False) else 'ESTOU PRONTO','network_ready',GREEN)
        if net.is_host:
            g.button((660,589,275,47),'TROCAR ARENA','network_map',CYAN)
            can_start=len(net.members)>=2 and all(m['ready'] for m in net.members)
            g.button((965,589,275,47),'INICIAR EXPEDIÇÃO','network_start',GOLD,can_start)
        r.text('Todos devem estar prontos. Trocar personagem cancela sua confirmação.',640,659,18,MUTED,True)
    g.button((32,678,240,30),'VOLTAR AO MENU','menu',MUTED)
