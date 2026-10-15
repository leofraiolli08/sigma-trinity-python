> Nota desta cópia de entrega: os textos abaixo registram a versão original. As fotos dos personagens foram substituídas por avatares fictícios de IA nesta cópia; consulte README.md.

# SIGMA TRINITY V10 — Pixel, evoluções e assinaturas

Extraia todo o ZIP numa pasta nova e execute SIGMA_TRINITY_V10/JOGAR.bat. Transfira somente save.json e MP3. Todos os participantes do cooperativo precisam desta versão: protocolo 7.

## Artes

Artes criadas com a ferramenta integrada de geração de imagens: sete folhas de transformação, Musashi normal refeito, folha exclusiva do chefe titã, 45 ícones de especialização, 25 ícones gerais, quatro ícones revisados de Joe/Musashi e 28 motivos de efeitos. Prompts em assets/art/generation_prompts_v10.json e generation_prompts_v10_additions.json; os primeiros prompts também documentam as tentativas refeitas. Os PNGs finais estão em assets/art e os quadros usados em assets/sprites. São interpretações de fãs, não artes oficiais.

As 22 etapas jogáveis dos sete personagens em pixel art têm oito poses de transformação próprias: quatro de caminhada e quatro de ataque. São 176 poses adicionais. HUD, seleção, galeria e cutscenes escolhem o estágio correto. Fotos dos personagens reais continuam fotos. Musashi no Caminho da Alma tem corpo idoso, barba branca, cabelo grisalho, kimono claro e bokken.

Após encontrar poses encostando, as folhas de Musashi e Ippo foram refeitas com células mais largas. O carregamento isola a silhueta inteira antes de reduzir. O chefe titã usa uma folha independente de oito poses, com escala/canvas comuns e margens para mãos, cabeça e pés, corrigindo o recorte que misturava os limites da folha de monstros.

UI: tipografia rasterizada sem suavização, bordas em degraus, barras retangulares, fundo discreto de pedra e ícones de IA com escala por vizinho mais próximo. Especializações usam vermelho para ataque, dourado para ritmo/mobilidade e verde para defesa; raridade permanece em selo próprio. A galeria mostra base e forma lado a lado.

## Identidade de combate

A evolução dura naquela partida; E continua temporário e Q continua limitado a uma ultimate por transformação. Bônus de abertura expiram, preservando build/save. Cada etapa possui títulos e padrão de ultimate próprios.

| Personagem | Ultimates por evolução |
|---|---|
| Ippo | Desafiante: três Gazelle Punches; campeão: dez golpes de Dempsey Roll. Finalizador básico mais frequente após a evolução. |
| Eren | Cinco impactos em linha; sete impactos cristalinos ao redor e armadura no estágio de endurecimento. |
| Klein | Rajada circular de fogo; cinco balas de ar dirigidas/evasão; controle progressivo de oito alvos com fios, respeitando chefes. |
| Musashi | Corte único; dois cortes cruzados e finalizador; linha decisiva de preparação longa; bokken e buffs de Ego/Vínculo. |
| Joe | Três golpes; três contra-ataques espaçados; sete golpes do Último Round com resistência/recuperação. |
| Thorfinn | Flanco com adagas; resistência; desarme/proteção; Vinland cura aliados e afasta inimigos sem dano direto de ultimate. |
| Holden | Disparo preciso; leque de salvas; três tiros/controle; dança com doze tiros em círculo. |
| Walter | Preserva Hazmat/Reação em Cadeia e Felina/Último Plano; histórico de cutscenes agora diferencia as duas fases. |

A arte de cada efeito é congelada na criação e transmitida no snapshot. Cutscenes usam o sprite, título e motivo daquele estágio. Enter pula; cenas repetidas podem ser encurtadas. A galeria alterna estágios reais de cada personagem.

## Coerência e limites

Fontes primárias e decisões em REFERENCIAS_V10.md. Nomes de caminhos, progressão por nível e buffs são adaptações deste crossover. O Musashi idoso se inspira na extensão de Vagabond da The LAST Manga Exhibition, não é apresentado como último capítulo serializado. Ippo/Joe permanecem boxeadores físicos; Thorfinn tardio prioriza defesa; Holden não ganhou imortalidade literal.

VALIDACAO_V10.md documenta os testes e capturas. TCP real em loopback inclui quatro jogadores, handshake, sincronização e desconexão. Não houve acesso a dois PCs Windows físicos com Radmin: esse playtest continua necessário. Não há promessa de ausência absoluta de bugs ou reprodução perfeita de cada página das obras.
