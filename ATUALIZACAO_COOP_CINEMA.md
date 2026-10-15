> Registro histórico de uma versão anterior. Para o estado atual, consulte `README.md` e `AUDITORIA_V8.md`.

# Cooperativo, cinematics e desafios secretos

- Orientação baseada no movimento real de jogadores e monstros, incluindo recuos e cargas. Artes que originalmente olham à esquerda têm compensação de orientação.
- Recortes da U.A. removem o fundo com variações de cor e isolam um corpo. Não houve substituição do mapa ou do atlas enviados.
- Muralhas visíveis nas seis arenas; jogadores, dashes, investidas, invocações e spawns respeitam os limites. Projéteis deixam de existir ao cruzar o limite. A câmera evita mostrar grandes faixas vazias nas bordas.
- 24 cutscenes de transformação/ultimate, com coreografias por personagem, textos conforme evolução, pausa real de combate e opção de pular. O tempo da forma fica intacto. Leozauxta continua visível durante dash.
- Novas placas de cenário em pixel art geradas por IA, usadas pelas animações de cutscene. Fusão: Leozauxta e Davi convergem, fissuras se abrem, fragmentos sobem, ocorre a ruptura e a forma final aparece.
- Requisitos de Leo/Guxta/Zatex revelam **???**; vencer Leozauxta libera sua seleção. Requisitos de Leo/Guxta/Zatex/Davi/Leozauxta abrem seleção especial, cutscene e confronto da fusão final. Perder não remove o desafio.
- Desafios solo com build inicial de nível 10, três fases e chefes próprios. Só a vitória no confronto libera o personagem; ela não substitui uma vitória normal necessária para o próximo requisito.
- Cooperativo real para 2–4 jogadores por LAN/Radmin, com sala, escolha de personagem/arena, prontos, início compartilhado, upgrades por participante, cutscenes sincronizadas, aura de Musashi, reanimação, vitória, infinito e nova expedição sem recriar a sala.
- XP compartilhado; baús/moedas não multiplicam o contador de itens; vida dos inimigos escala pelo grupo. Recompensas são salvas em cada computador. A morte depois do infinito registra as recompensas dos clientes sem pagar outra vitória.
- Rede TCP não bloqueante, mensagens JSON com tamanho máximo, versão de protocolo, validação de controles, timeout e identificação da vaga pelo servidor. Não usa pickle ou execução de código recebida da rede.

## Autocrítica

A versão anterior tinha arte mais rica, mas direção incorreta, recortes frágeis e bordas sem colisão fora da U.A. A revisão corrigiu o sistema de movimento e os recortes, além de dar significado aos segredos: agora são confrontos, não cartões liberados automaticamente.

As cutscenes são animações compostas no Pygame, não vídeos prontos. Personagens ainda usam poses de recorte; VFX e cenários mantêm pixel art. Os seis chefes de arena ainda compartilham sua base de ataques. Não há colisão em todos os edifícios do cenário, migração de anfitrião, reconexão no meio da run ou retomada de uma run encerrada.

A suíte cobre simulação, interface, rede e persistência. Isso não significa ausência garantida de bugs nem substitui teste de dificuldade/latência com quatro jogadores reais.

## Arte nova

Recurso: `assets/art/cinematic_atlas.png`. Gerado com a ferramenta de imagem integrada, não com API/CLI. Recortado em três placas de cenário; personagens e VFX são sobrepostos e animados pelo jogo. Original: `exec-7a477cc0-b05a-431a-a575-9837cfbe0ba2.png`.

Prompt final:

> Use case: stylized-concept. Asset type: in-game dark pixel art cinematic background atlas. Create ONE landscape sprite sheet with EXACTLY 3 equally sized panels arranged horizontally, each a 16:9 wide environment plate, consistent highly polished dark fantasy 16-bit pixel art for a Vampire Survivors inspired game. First panel: ruined dark stone arena at night under a massive red moon, crumbling suspended chunks of masonry around the edges and EMPTY center to overlay game characters. Second panel: same arena split open by a spectacular emerald lightning and violet arcane golden energy fusion rift, two energy currents colliding into a brilliant core, floating fractured stone and dramatic radial cracks, empty silhouetted foreground for character overlays. Third panel: ancient sword sanctuary in ink-black mist, moonlit pale blue columns and glowing golden motes, calm empty central stage. Very crisp actual pixel art, visibly stepped edges, small intentional dithering, rich cinematic composition and dark legible palette, no photo textures, no realistic humans. All panels fill their own entire cell, no margins, no captions, no labels, no characters, no UI, no watermark. This sheet will be cropped into 3 backgrounds for individually animated character cutscenes.
