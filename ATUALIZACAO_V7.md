> Registro histórico de uma versão anterior. Para o estado atual, consulte `README.md` e `AUDITORIA_V8.md`.

# SIGMA TRINITY V7 — pixel, interface e cooperativo

## Abrir esta versão

Feche todas as janelas antigas. Extraia o ZIP completo em uma pasta nova e abra `SIGMA_TRINITY_V7/JOGAR.bat`. Copie apenas seu `save.json` e músicas em `assets/music` para manter progresso e áudio. O menu e a janela mostram V7. `VERSÃO / ARTES` identifica os assets realmente carregados; sua galeria mostra as novas animações. Não misture código nem sprites de outras versões.

## O que mudou

- Ippo, Eren, Klein e Musashi: quatro estados por personagem, com quatro poses de caminhada e quatro de ataque por estado; 128 poses no total. Pixel art com alpha, escala por vizinho mais próximo e direção conforme o deslocamento. Walter conserva seu conjunto em pixel art. Fotos dos demais personagens permanecem como imagens.
- Menus, seleção, arenas, cartas de melhorias, build, missões, conquistas/loja, ajustes, ajuda, resultado e cooperativo receberam uma direção visual comum. Bordas em degraus, tons escuros, acentos quentes, títulos legíveis, ícones e progresso claro.
- Botões têm resposta gradual ao passar o mouse e foco por teclado. Cima/baixo e Enter navegam pelos botões; os atalhos de combate e de seleção continuam disponíveis. A fonte incluída suporta acentos, símbolos e nomes sem quadrados vazios.
- HUD menor, recargas no rodapé, vida dos aliados, minimapa compacto e progresso de XP no topo. Avisos hostis ficam acima das partículas/VFX. Atores são ordenados pela posição dos pés para manter profundidade visual.
- Pisos de expansão têm sombreamento para competir menos com os personagens. O impacto de boxe usa traços de velocidade e faísca curta, sem grande efeito de chama.
- Conexão multiplayer confirma TCP por `select` e `SO_ERROR` antes de criar Peer/configurar TCP_NODELAY. IPv4/porta validados, prazo TCP/handshake, erros por etapa, tentativa novamente e logs locais. Recusas podem completar o envio; falha de um aceite não derruba o host; desconexão limpa a vaga e mantém os demais jogadores.
- Snapshots ainda não enviados podem ser substituídos pelo mais recente; frames parcialmente enviados e mensagens de controle são preservados.

## Arte gerada

As quatro novas spritesheets foram produzidas com a geração de imagens integrada, com fundo transparente. Nenhuma chamada de IA é feita durante a partida. As imagens anteriores foram conservadas para referência/fallback; o carregamento da V7 usa os arquivos abaixo.

| Arquivo no projeto | Estados visuais | Quadros |
|---|---|---:|
| `assets/art/ippo_animation.png` | Desafiante, campeão, peek-a-boo, Dempsey Roll | 32 |
| `assets/art/eren_animation.png` | Soldado, veterano, Titã de Ataque, endurecimento | 32 |
| `assets/art/klein_animation.png` | Mágico, Gehrman Sparrow, preparação, Marionetista | 32 |
| `assets/art/musashi_animation.png` | Vagante, Caminho da Espada, Caminho da Morte, Caminho da Alma | 32 |

Briefs de produção: uma folha em grade de oito colunas por quatro linhas, um estado por linha; quatro poses de caminhada nas primeiras colunas e quatro poses de ataque nas últimas. Um personagem por célula, pés alinhados, espaço entre recortes, vista lateral voltada à direita, pixel art de paleta restrita, silhueta legível, alpha real, sem legendas, bordas, cenário ou personagens adicionais. O motor recorta as células e amplia os pixels sem suavização.

Detalhes por personagem: Ippo com cabelo preto, luvas vermelhas, shorts brancos/vermelhos e botas de boxe; poses de jab, direto, guarda e esquiva. Eren com uniforme/capa da Tropa de Exploração, equipamento e duas lâminas; estados titã com musculatura estilizada e punhos endurecidos. Klein com roupa vitoriana escura, cartola/cartas, disfarce Gehrman com arma, fogo e fios espirituais nos estados apropriados. Musashi com kimono gasto azul/cinza, cabelo preso, katana/duas espadas, postura de batalha e estado sereno. São interpretações de crossover, não imagens oficiais nem reprodução exata de todos os eventos das obras.

## Pesquisa da interface

| Referência consultada | Aplicação no SIGMA TRINITY |
|---|---|
| [Vampire Survivors / poncle](https://poncle.games/vampire-survivors) e [página oficial no Steam](https://store.steampowered.com/app/1794680/Vampire_Survivors/) | Prioridade ao campo de combate e às escolhas de progressão entre partidas. HUD reduzido e cartões de melhorias comparáveis. |
| [Brotato / Blobfish no Steam](https://store.steampowered.com/app/1942280/Brotato/) | Clareza de ondas e builds; separação visual de arsenal, atributos, opções e custos. Capturas da loja ajudaram a avaliar hierarquia. |
| [Halls of Torment / Chasing Carrots no Steam](https://store.steampowered.com/app/2218750/Halls_of_Torment/) | Paleta sombria, contraste de ícones e títulos, cartas com raridade e progressão permanente. Capturas de seleção e bênçãos ajudaram na composição. |

As escolhas acima são inferências de design a partir das referências. Nenhuma imagem, marca, fonte ou elemento de interface desses jogos foi copiado para o pacote.

Para a rede, foi consultada a documentação primária da Microsoft sobre [select/Winsock](https://learn.microsoft.com/en-us/windows/win32/api/winsock2/nf-winsock2-select): conclusão da conexão não bloqueante em writefds/exceptfds e consulta de SO_ERROR. O ZIP corrigido da outra conversa foi comparado, preservando os sistemas existentes e acrescentando testes de falha/limpeza.

## Conferência e limites

138 testes passaram, incluindo 22 testes de rede. Foram executados TCP real com quatro participantes e três processos clientes independentes, fluxo de partida, melhorias, cutscenes, vitória, infinito e desconexão. Falhas pendentes do Winsock foram exercitadas por injeção. O loop real do jogo com Ippo executou 180 quadros sem erro. Capturas reais estão em `preview/waves`; a galeria animada também fica disponível no menu.

**Não houve teste nas duas máquinas Windows via Radmin.** A conexão problemática foi corrigida e validada no ambiente disponível; a confirmação definitiva da VPN depende desse playtest. `VERIFICAR_MULTIPLAYER.bat` exercita TCP local no Windows e salva diagnóstico. Logs ficam em `logs/multiplayer.log`. Veja `MULTIPLAYER.md` para criar/entrar e conferir a sessão real.

Animações usam quatro poses por ação/estado e espelhamento horizontal. Fotos usam recortes; monstros mantêm seus conjuntos anteriores. Não há oito direções completas, reconexão durante a partida ou migração de anfitrião. Dificuldade humana e latência da dança ainda precisam de playtest.
