# SIGMA TRINITY V9 — Lendas e expedições

Base preservada: V8 salva, versão 9 do arquivo original. A reconstrução recuperou as dez folhas geradas e refez as alterações sobre essa base, com validação nova. Não reutilizou o resultado de testes de uma pasta desaparecida.

## Personagens

| Personagem | Progressão | Assinatura | Ultimate |
|---|---|---|---|
| Joe Yabuki | Níveis 6 e 12; estado de luta temporário com E | Jab, Cross Counter, janela de resposta após dash/habilidade | Último Round: sete golpes físicos próximos |
| Thorfinn | Níveis 5, 10 e 15; E usa o estado final | Adagas no início, deflexão sem armas depois, aura defensiva | Não Tenho Inimigos: proteção de aliados, controle e pulsos de repulsão |
| Judge Holden | Níveis 5, 10 e 15; E usa A Dança do Juiz | Rifle perfurante e pressão territorial | Meridiano de Sangue: oito salvas direcionais |

Cada novo personagem possui quatro estados visuais, quatro poses de caminhada e quatro de ataque por estado. Os sete personagens em pixel art têm 224 poses principais; aliases e retratos também são exportados para PNGs consultáveis. As fotos dos personagens reais continuam sendo fotos.

A aparência e a identidade se inspiram nas obras; títulos de fases, progressão por nível, efeitos, buffs e ultimates são adaptações de crossover. Thorfinn não ganha poderes sobrenaturais na obra; a aura representa proteção no sistema do jogo. Holden não recebe uma alegação de imortalidade literal. As artes são geradas e estilizadas, não oficiais. Joe continua sendo um boxeador de curto alcance.

## Combate e apresentação

- Seis folhas animadas de monstros, sete tipos por mapa, oito poses por tipo: 336 quadros. O render usa essas folhas diretamente; não os caches antigos.
- Estados de caminhada, preparação, ataque, impacto e derrota. O corpo a corpo comum tem aviso de 0,45 s e área evitável; não é dano instantâneo invisível.
- Derrotas com fade de 0,55 s, limitadas a 45 imagens simultâneas.
- Doze sequências de efeitos com quatro fases distintas cada: soco, corte, cartas, disparo, aura, raio, cola, paçoca, enxame, química, vórtice e ressonância. Efeitos legados continuam disponíveis como fallback.
- Perigos hostis mantêm contornos por cima dos efeitos; mirroring depende do movimento e conserva a direção ao andar na vertical.
- Novos sons locais de soco, lâmina, rifle, contra-ataque e objetivo. As cinco músicas MP3 continuam dependentes dos arquivos enviados pelo usuário.

## Progressão e interface

Três caminhos exclusivos por personagem, três graus, escolha inicial a partir do nível 4 e perda aplicada só uma vez. As 45 opções usam três bases compartilhadas; contra-ataque, marionete e suporte possuem bônus específicos. Não são 45 sistemas de combate totalmente independentes.

Três objetivos opcionais por arena nas ondas 2/4/6: captura, contestação por inimigos e colaboração dos aliados. Cada captura dá 25 moedas, XP e cura; completar as três dá um baú. As arenas usam nomes próprios e a mesma regra de captura.

Quatro regras de expedição, bestiário persistente, 26 conquistas, comparações numéricas nas cartas, caminho/telemetria no resultado e build, acompanhamento das primeiras missões incompletas no menu, galeria paginada, preferência por cenas repetidas curtas e RTT no cooperativo.

## Rede

Protocolo 6. Conexão não bloqueante aguarda select e SO_ERROR antes de criar Peer/TCP_NODELAY. Caminhos, objetivos, regra, métricas, poses e derrotas são validados antes de restaurar o mundo. Entrada inválida de descoberta não pode gerar erro de hash. Desconectar o dono de uma cutscene cancela a cena e mantém os demais na partida. O diagnóstico contém uma sala com Joe, Thorfinn, Holden e Klein.

## Referências de identidade dos personagens

- Joe: https://kodansha.us/series/ashita-no-joe-fighting-for-tomorrow/ e https://tmsanime.com/news/tomorrows-joe-premiere-announced
- Thorfinn: https://kodansha.us/series/vinland-saga/ e https://kodansha.us/series/vinland-saga/volume-9/
- Holden: https://www.penguinrandomhouse.com/books/110472/blood-meridian-by-cormac-mccarthy/ e https://catdir.loc.gov/catdir/samples/random044/00064576.html

Evidências e limites atuais estão em VALIDACAO.md e AVALIACAO.md. Para abrir, extraia em pasta nova e execute JOGAR.bat. Não misture sprites/código antigos; copie somente save.json e as músicas.
