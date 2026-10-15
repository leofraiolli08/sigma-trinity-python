> Histórico da V8. Resultados desta entrega: VALIDACAO.md e ATUALIZACAO_V9.md.

# Auditoria do SIGMA TRINITY V8 — 09/10/2026

## Resultado e escopo

Esta revisão analisou o pacote V7.1 que estava disponível, corrigiu falhas reproduzíveis e implementou melhorias de combate, progressão, apresentação e estabilidade. A comparação inicial confirmou que os 505 membros do ZIP V7.1 correspondiam aos bytes da árvore de trabalho; a revisão não partiu de uma cópia diferente do jogo.

Os **55 módulos Python, com 7.005 linhas incluindo os testes**, foram revistos como texto, analisados por AST e compilados. Scripts de execução, dependência, documentação e licença de fonte também foram conferidos. Imagens, GIF, sons e fontes receberam validação de formato e decodificação; imagens e animações são recursos binários, portanto não possuem “linhas de código” para auditar. Exemplos visuais foram inspecionados em capturas reais do Pygame.

`AUDITORIA_ARQUIVOS_V8.csv` identifica os arquivos do pacote individualmente, com tamanho, SHA-256, classificação e método de verificação. O próprio CSV fica fora da sua lista de hashes para evitar autorreferência. Arquivos pessoais de save, backups e logs foram excluídos da entrega. Esta cobertura de arquivos não equivale a provar todas as combinações possíveis de uma partida.

## Falhas encontradas e corrigidas

| Falha | Consequência | Correção e evidência |
|---|---|---|
| Projétil descartado ao sair do mapa antes de examinar a trajetória | Inimigo junto da muralha podia não receber um tiro que o atravessava | Colisão varrida é resolvida antes do descarte; teste de borda e ricochete |
| Último intervalo de vida ignorado | Tiro podia desaparecer antes de um acerto válido | Deslocamento limitado à vida restante; sem viajar além dela |
| XP excedente agregado a qualquer pickup | Cura/baú podia receber um valor de XP | Apenas pilhas vivas de XP são fundidas; loot raro preservado no limite |
| Pickup expirado ainda coletado | XP ou cura concedidos depois da expiração | Expiração verificada antes da coleta e da limpeza de onda |
| Salto de níveis do Klein aplicava um só aumento | Chegar direto ao nível 9 dava menos dano que passar pelo 5 | Cada estágio pendente recebe o aumento exatamente uma vez |
| Rafael/Leozauxta alteravam o último projétil global | Ao atingir o limite, um tiro de outro aliado podia ganhar modificadores | Apenas projéteis efetivamente criados pelo ataque atual são alterados |
| Marionete usava a distância do alvo aliado mais próximo | Um jogador distante podia concluir a conversão por causa de outro aliado | Progresso depende do controlador vivo e presente |
| Ondas/efeitos visuais consultavam o personagem local para cor/origem | Cooperativo podia desenhar cola/enxame/Blackwhip com autoria errada | Consulta pelo `owner` do ataque |
| Investida se deslocava durante seu aviso | A origem do perigo não correspondia ao ataque executado | O monstro segura a posição durante a preparação; transição cancela avisos antigos |
| Dano exibido incluía excesso sobre HP restante | Números e contribuição eram inflados | Estatísticas e números usam dano efetivamente aplicado |
| Corpo a corpo gastava ataque com inimigo fora do alcance | Animação/recarga sem soco ou corte útil | O básico exige um alvo no alcance; habilidades mantêm seus alcances próprios |
| Compra continuava após falha de escrita | Saldo/upgrade podiam ficar inconsistentes | Compra revertida em memória; save antigo permanece íntegro |
| Resultado era considerado salvo mesmo após erro | Sem nova tentativa; cliente podia liberar a sala antes de gravar | Resultado só é confirmado após sucesso; tentativas idempotentes |
| Apenas um save e arquivo temporário fixo | Corrupção ou interrupção podia perder progresso | Temporário único, flush/fsync, substituição atômica e backup válido anterior |
| Dados de rede incompletos e não finitos | Entidades quebradas, escalas excessivas ou erro de renderização | Validação de esquema, números, tamanhos, referências e estágios antes da restauração |
| Referência de chefe/ritmo removido durante a revisão do protocolo | Validação podia recusar vitória/desconexão legítima | Snapshot envia apenas referências ainda presentes; fluxo TCP reexecutado |
| Inteiro extremo passado a `math.isfinite` no movimento | Conversão podia gerar OverflowError e interromper o anfitrião | Inteiros são limitados sem conversão para float; caso de 1.000 dígitos testado |
| Evento de fim da música antiga permanecia na fila | Trocar faixa podia pular a seguinte | Evento ignorado se a nova música ainda toca ou está pausada |
| Argumentos padrão usavam Vector2 mutável | Estado poderia ser compartilhado entre chamadas | Padrões usam None e criam o vetor por chamada |
| Diagnóstico CLI retornava sucesso com pacote inválido | Automação podia aceitar instalação misturada | Diagnóstico retorna código 2 quando a integridade falha |

Os quatro primeiros cenários básicos foram registrados antes das correções em reproduções locais: tiro na borda, XP na cura, XP expirado e salto de evolução. Os demais foram cobertos por inspeção, execução e testes específicos. Nenhuma falha de uma máquina Windows física foi reproduzida neste ambiente.

## Melhorias de jogo implementadas

- **Chefes distintos:** Cripta usa círculos e selos; U.A. pressão/investida; Cidade bombardeio/varredura; Ginásio golpes próximos; Muralhas pisões/fissuras; Backlund cartas e selos espelhados. Cada um tem quatro padrões com variantes por fase. Dano é anunciado; as três fases e travas contra burst permanecem.
- **Leitura de combate:** avisos direcionais, barra de preparação, nome do golpe e perigos acima de efeitos. Opção de retirar clarões brancos sem esconder avisos.
- **Builds:** sete auxiliares para escolher, mantendo cinco vagas auxiliares; Sino do vazio/controle e Brasas errantes/chamas têm receitas próprias. Cartas indicam os requisitos; a build mostra sete receitas e pagina atributos.
- **Metas persistentes:** seis missões e 21 conquistas. Novas conquistas contemplam as seis arenas, o Caminho da Alma e uma vitória com quatro participantes.
- **Resultados úteis:** dano real do próprio personagem, dano recebido e DPS médio de toda a expedição. O DPS inclui descanso entre ondas; não é uma medida isolada do dano ativo da arma.
- **Fluidez:** grade espacial temporária reduz candidatos de colisão; a colisão varrida exata continua decisiva. A grade acompanha knockback e é limpa quando a onda termina.
- **Instalação confiável:** manifesto agora cobre também caches de sprites, sons e licença/fontes, além do código e artes. Saves e músicas pessoais continuam independentes.

## Revisão por módulo

A coluna de linhas é uma medida do texto revisado, não uma declaração de execução de cada linha. Os módulos de teste também foram revistos: testes errados poderiam mascarar regressões.

| Arquivo | Linhas | Foco da revisão |
|---|---:|---|
| `animation_test.py` | 92 | Quadros reais, alpha, orientação, escala e navegação |
| `arena_art.py` | 68 | Pisos de fallback e geração procedural de cenografia |
| `art_assets.py` | 92 | Carregamento, isolamento e alinhamento de recortes |
| `art_test.py` | 54 | Assets carregados e transparência |
| `ascension.py` | 336 | Kits, progressão por estágio, efeitos, auxiliares e receitas |
| `ascension_test.py` | 137 | Ataques específicos, auxiliares, receitas e slots |
| `asset_generator.py` | 256 | Cache de sprites, prioridade de animações, fontes e sons |
| `audit_test.py` | 240 | Reproduções de combate, saves, chefes, protocolo e colisão |
| `audit_ui_test.py` | 42 | Telas, acessibilidade e nova tentativa de salvamento |
| `boss_patterns.py` | 80 | Padrões das seis arenas e resolução de leques/faixas |
| `cinematic_test.py` | 127 | Pausa, capacidades distintas e fusão |
| `cinematics.py` | 138 | Coreografias, duração, validação e clarões opcionais |
| `combat_art.py` | 106 | Fallback de efeitos e impactos em pixels |
| `coop_test.py` | 176 | Sala, quatro jogadores, progressão, vitória e desconexão |
| `entities.py` | 201 | Atributos, transformação, dano real e entidades de combate |
| `expansion_test.py` | 144 | Elenco, equilíbrio e evolução dos personagens |
| `expansion_ui.py` | 48 | Arenas e build; seleção delegada para evitar duplicação |
| `game.py` | 370 | Eventos, transições, salvamento, apresentação e fluxo cooperativo |
| `guxta_test.py` | 32 | Gravidade e progressão dos segredos |
| `installation_test.py` | 59 | Versão, integridade, extração e artes reais |
| `interface.py` | 150 | Menu, seleção sem spoilers, galeria e resultado |
| `main.py` | 39 | Entrada CLI, modos de teste e integridade antes de executar |
| `maps.py` | 114 | Limites, colisão externa, perigos e pisos |
| `missions.py` | 28 | Seis missões persistentes e sua apresentação |
| `monster_art.py` | 92 | Atlases por arena e isolamento de um corpo por célula |
| `multiplayer.py` | 312 | Ciclo TCP, handshake, sala, autoridade e encerramento |
| `multiplayer_diagnostic.py` | 32 | Diagnóstico TCP e relatório local |
| `musashi_test.py` | 54 | Caminhos, combos e aura individual/grupo |
| `music.py` | 45 | Faixas locais, falhas de áudio e eventos de término |
| `netcode.py` | 135 | Framing JSON, tamanho, números, IPv4, porta e Winsock |
| `netstate.py` | 183 | Codec de estado e validação antes de alterar a simulação |
| `network_log.py` | 24 | Logs por etapa e rotação limitada |
| `network_test.py` | 124 | TCP real, envio parcial, prazos e falhas de socket |
| `pixel_characters.py` | 82 | 128 poses reais e exportação dos PNGs utilizados |
| `pixel_style.py` | 185 | Recorte do atlas U.A., piso e camada de efeitos |
| `progression.py` | 96 | Checkpoint, conquistas, economia e compras |
| `release_checks.py` | 103 | Execução visual das telas, arenas, kits e cooperativo |
| `release_info.py` | 52 | Identificação e verificação de integridade do pacote |
| `renderer.py` | 484 | Camadas, orientação, perigos, caches, HUD e autoria dos efeitos |
| `rhythm.py` | 33 | Notas, janela, combo e proteção da dança |
| `rhythm_test.py` | 63 | Janelas de acerto, falha, proteção e pausa |
| `save_manager.py` | 138 | Migração, backup, gravação atômica e recompensas únicas |
| `self_test.py` | 234 | Integração de toda a suíte e fluxos reais da interface |
| `session.py` | 455 | Simulação, colisões, loot, atores e estados dos aliados |
| `settings.py` | 42 | Constantes, definições de personagens e limites |
| `spatial.py` | 20 | Grade temporária e atualização após deslocamento |
| `trials.py` | 17 | Criação dos dois confrontos secretos |
| `ui_design.py` | 76 | Hierarquia, ícones, textos, barras e retratos |
| `ui_screens.py` | 137 | Cartas, receitas, ajustes, pausa, ajuda e rede |
| `upgrades.py` | 79 | Escolhas, raridade, aplicação e famílias de passivas |
| `visual_assets.py` | 96 | Atlas de VFX e cache limitado de transformações |
| `visual_upgrade_test.py` | 83 | Artes, camadas, HUD e qualidade de efeitos |
| `waves.py` | 65 | Spawn, limpeza, coleta, escalada e infinito |
| `waves_test.py` | 129 | Vitória única, dificuldade, famílias e persistência |
| `weapons.py` | 206 | Armas base, alcance, projéteis e autoria dos modificadores |

## Recursos e documentação

Todos os PNGs entregues passam por decodificação; chunks e CRC são conferidos no empacotamento. Todos os frames do GIF de galeria foram carregados. Sons WAV foram lidos integralmente como PCM; duas fontes foram analisadas e usadas para renderizar símbolos/acentos. A licença DejaVu foi preservada. Os 200 PNGs exportados dos quatro personagens de ficção são comparados ao conteúdo RGBA efetivamente usado pelo motor.

Arquivos antigos de prompts/notas de versão foram preservados e marcados como histórico. README, avaliação, multiplayer e validação descrevem a V8. Executáveis `.bat` continuam usando a pasta onde estão instalados; não copiam código nem sprites de outras versões. As músicas comerciais não estão incluídas.

## Testes e desempenho

Os resultados finais, percentuais de cobertura, amostras de carga e validação da extração limpa estão em `VALIDACAO.md`; `test-results.txt` contém a saída integral da suíte. `preview/waves` contém capturas reais, incluindo avisos dos seis chefes. O teste de grade compara 250 trajetórias com a varredura completa, envolvendo cola, deslocamentos, fragmentos, perfuração e ricochetes.

Fontes técnicas primárias consultadas: [Microsoft — select/Winsock](https://learn.microsoft.com/en-us/windows/win32/api/winsock2/nf-winsock2-select), para conclusão de conexão não bloqueante e SO_ERROR; [Pygame — mixer.music](https://www.pygame.org/docs/ref/music.html), para get_busy, pausa e eventos de término. A sequência TCP confirmada antes de Peer/TCP_NODELAY foi preservada.

## Limites e próximos passos

Não é possível provar ausência de bugs com uma auditoria ou transformar uma avaliação técnica em “melhor jogo do mundo”. A evidência aqui cobre o ambiente Linux/Pygame, testes controlados e TCP em loopback. **Windows/Radmin entre computadores físicos ainda precisa de playtest.** Há logs e diagnóstico incluídos para verificar a etapa caso falhe. Não há reconexão durante a run, migração de anfitrião ou retomada de expedição.

Mapas têm muralhas externas com colisão; interiores permanecem transitáveis. Monstros não têm animações completas em oito direções. Os novos padrões de chefes têm regras verificadas, mas sua dificuldade/duração/diversão precisam de jogadores humanos. As interpretações dos personagens continuam sendo adaptações do crossover, não representações oficiais.

A autocrítica está em `AVALIACAO.md`: o próximo trabalho de maior valor é testar builds e latência com pessoas, animar os monstros existentes e desenhar objetivos de cenário com rotas consistentes. Não inflei o elenco ou a loja como substituto desses problemas.

## Como usar

Extraia o ZIP V8 em uma pasta nova, copie apenas seu `save.json` e suas músicas, e execute `JOGAR.bat`. Todos no cooperativo devem usar a V8, protocolo 5. Para conferir a instalação, abra `VERIFICAR_VERSAO.bat`; para testar TCP naquela máquina, `VERIFICAR_MULTIPLAYER.bat`.
