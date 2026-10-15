# SIGMA TRINITY V10 — PIXEL, EVOLUÇÕES E ASSINATURAS

Jogo solo offline e cooperativo de **2–4 jogadores por LAN/Radmin VPN**, em Python + Pygame. **15 personagens (2 secretos), 6 arenas, 26 conquistas e 6 missões de arsenal**, builds e progressão entre partidas. A IA foi usada para criar imagens; não roda durante o jogo. Veja `ATUALIZACAO_V10.md`, `REFERENCIAS_V10.md` e `MULTIPLAYER.md` para esta versão.

A V10 adiciona **176 poses próprias de transformação**, ícones de IA e ultimates por evolução. Musashi termina com visual idoso e sábio; o chefe titã usa uma folha corrigida. Ambos os PCs do cooperativo precisam da V10.

## Abrir no Windows

1. Feche o jogo antigo e extraia TODO o ZIP em uma pasta nova. Entre na pasta **SIGMA_TRINITY_V10**. Não execute dentro do arquivo compactado nem use um atalho antigo.
2. Copie somente seu `save.json` antigo para **SIGMA_TRINITY_V10** para manter recordes, moedas e vitórias. Não copie os arquivos `.py`, `JOGAR.bat` nem a pasta `sprites` da versão antiga.
3. Copie suas músicas antigas para `assets/music`.
4. Abra `JOGAR.bat`. Se a versão anterior funcionava, as dependências são as mesmas.

O título da janela e o menu mostram **V10 / ASCENSÃO**. **VERSÃO / ARTES** mostra os monstros carregados de cada mapa e a pasta que você abriu. Os seis mapas agora usam folhas próprias de monstros animados, com movimento, preparação, ataque, impacto e derrota. A mesma arte aparece independentemente da qualidade dos efeitos.

`VERIFICAR_VERSAO.bat` identifica a pasta aberta e cria `DIAGNOSTICO.txt`. O jogo verifica a integridade de código/artes antes de iniciar e avisa quando arquivos faltam ou foram misturados com outra versão. Isso impede que uma instalação parcial pareça funcionar usando os desenhos antigos. Seus saves e MP3 não fazem parte dessa verificação.

Na primeira instalação, use Python 3.11 ou superior com “Add Python to PATH”. Na pasta do jogo, clique na barra de endereço do Explorador, digite `cmd` e pressione Enter:

```console
python -m pip install -r requirements.txt
python main.py
```

Se necessário, troque `python` por `py` no Windows ou `python3` no Linux. Este pacote contém código Python, não um EXE independente. Funciona offline após instalar Pygame.

## O que mudou na V9

- Joe Yabuki, Thorfinn e Judge Holden, com evoluções, kits e cutscenes próprios.
- Três especializações exclusivas por personagem a partir do nível 4; cada caminho tem três graus e uma desvantagem inicial.
- Objetivos opcionais nas ondas 2/4/6; bestiário persistente; quatro regras de expedição.
- 336 quadros de monstros e 48 fases de efeitos de combate criados por IA; sete personagens com animações reais em pixel art.
- Cutscenes repetidas curtas, comparação de atributos nas cartas, progresso de missões no menu, RTT no cooperativo.

### Correções e sistemas preservados da V8

- Seis chefes com padrões próprios, nomes dos golpes e avisos de alcance/tempo. Transições de fase cancelam ataques antigos.
- Sino do vazio e Brasas errantes: sete auxiliares disponíveis, cinco espaços para escolher; seis missões e 21 conquistas.
- Receitas indicadas nas cartas, build com todas as sete receitas e atributos paginados; resultado com dano real, DPS médio e dano recebido do seu personagem.
- Opção de desativar clarões; avisos de perigo ficam visíveis em todas as qualidades.
- Colisão otimizada por regiões, preservando trajetória, ricochetes e deslocamentos.
- Correções de XP/cura/baús, tiros nas muralhas, evolução do Klein e propriedade dos ataques no cooperativo.
- Backup automático e salvamento atômico; compras sem salvamento são revertidas; resultados são tentados novamente sem duplicar recompensas.

## Personagens e evolução durante a partida

| Ordem interna (não atalho) | Personagem | Identidade de combate / evolução |
|---|---|---|
| 1 | Leo | Cola, lentidão, prisão adesiva. Ultimate deixa um campo persistente. |
| 2 | Rafael | Paçocas com ricochete e fragmentos. Ultimate com tempestade de paçocas e explosão de farelos. |
| 3 | Leozauxta (secreto) | Robux, enxames e minigame de dança. Vitórias com Leo, Guxta e Zatex revelam o modo ???; derrote Leozauxta nele para liberar. |
| 4 | Davi Coala | Ar perfurante, Shoot Style, Blackwhip. Ultimate é um impacto direcional longo. |
| 5 | Walter White | Frascos e zonas químicas. Aos 2:30, vira Heisenberg: rajadas e ultimate de metralhadora perfurante. |
| 6 | Guxta | Orbes gravitacionais, atração e repulsão. Ultimate comprime o grupo, sem deslocar chefes. |
| 7 | Ippo Makunouchi | Jab/direto, Liver Blow e Gazelle Punch em curta distância. No nível 6, campeão; a ultimate passa de combo de Gazelle Punch para Dempsey Roll. |
| 8 | Eren Yeager | Lâminas e investida com cabos. E ativa o Titã de Ataque. No nível 6, veterano com punhos endurecidos na forma titã. |
| 9 | Klein Moretti | Começa como Mágico; nível 5: Sem Rosto/Gehrman; nível 9: Marionetista. Bala de ar, cartas, fogo, substituição de papel e fios espirituais. |
| 10 | Zatex | Ressonância e notas; transforma em Maestro do Véu. Ultimate com três ondas sonoras e notas perseguidoras. |
| 11 | Leozauxtaci Coala (secreto) | Fusão das formas finais de Leo, Guxta, Zatex e Davi. Vença com os quatro e com Leozauxta: seleção especial, cutscene de fusão e confronto para liberar. |
| 12 | Musashi Miyamoto | Combate de curta distância com Niten Ichi-ryū. Nível 5: Caminho da Espada; 10: Caminho da Morte; 15: Caminho da Alma. No último, **F** alterna Ego (autobuff) e Vínculo (aura para aliados). |

| 13 | Joe Yabuki | Boxe físico e Cross Counter; níveis 6/12. E representa espírito de luta; Q encadeia sete golpes. |
| 14 | Thorfinn | Começa com duas adagas; níveis 5/10/15 seguem renascimento, exploração e Vinland. Etapas posteriores usam deflexão desarmada e proteção de aliados. |
| 15 | Judge Holden | Rifle perfurante, pressão territorial e salvas direcionais; níveis 5/10/15. Os títulos das fases são adaptações deste jogo. |

A seleção mostra apenas personagens liberados. Use **1–6 na página atual** e setas esquerda/direita para trocar de página. Vitórias antigas registradas como Zato passam a contar como Zatex.

As evoluções esperam a transformação atual terminar e duram até o fim daquela partida. Ippo, Eren e Klein ganham 12% de dano base a cada etapa. Musashi ganha 10% por caminho, nos níveis 5, 10 e 15. Vida, XP e build são mantidos.

Ippo **não ganha poderes sobrenaturais**: E representa concentração defensiva, com redução de dano e breves esquivas. Seus socos precisam alcançar o alvo; projéteis de longa distância vêm apenas de armas auxiliares escolhidas na build.

Klein evita um golpe com substituição de papel a cada 12 segundos. Na etapa Marionetista, mantenha-se a menos de 400 unidades do inimigo marcado por 2,2 segundos para controlá-lo temporariamente por 5 segundos. A marionete ataca outros inimigos e recebe um contorno violeta. Chefes não podem ser controlados. Sair do alcance interrompe o progresso.

**Fidelidade:** habilidades e aparências se baseiam nas obras, mas níveis, duração, dano, controle temporário, alcance e ultimates são adaptações para este crossover. “Transformação” de Ippo/Klein significa estado de combate, não uma forma sobrenatural canônica. Walter não possui poderes químicos na série. As artes são interpretações estilizadas, não recursos oficiais nem reproduções exatas. Veja `AVALIACAO.md`.

## Expedições, especializações e bestiário

Abra **EXPEDIÇÕES** no menu para escolher: Expedição padrão; Assinatura pura (sem auxiliares); Força humana (sem transformação, +20% dano); Cerco de elites (mais elites e +25% moedas das ondas). O anfitrião também escolhe a regra no lobby. Alterar a regra cancela a confirmação dos participantes.

No nível 4, escolha um de três caminhos exclusivos. Os caminhos compartilham bases de ataque, velocidade e proteção, com nomes próprios e alguns bônus adicionais de contra-ataque, marionete e suporte. Cada um tem três graus. A desvantagem só é aplicada na escolha inicial. A escolha do caminho não pode ser rerrolada.

Cada arena possui três pontos opcionais, abertos nas ondas 2, 4 e 6. Fique dentro do círculo por oito segundos; inimigos próximos atrasam a captura. Aliados colaboram. Cada ponto dá 25 essências, XP e cura; os três completos também geram um baú. Você pode vencer a onda 10 sem fazê-los. O bestiário registra os tipos encontrados e só revela seus desenhos depois da descoberta.

Em **AJUSTES**, cenas repetidas curtas preservam a primeira apresentação e reduzem repetições para 0,6 s. No cooperativo, configure a preferência antes de criar/entrar na sala.

## Builds: 6 armas e 6 famílias de passivas

A arma assinatura ocupa um espaço. Você pode escolher até **5 armas auxiliares**, além de até **6 famílias de passivas**. Melhorias do mesmo atributo compartilham a família. Ao subir de nível, escolha uma das três cartas. Cada partida começa com 3 rerrolagens; pressione **R** na escolha. A loja pode acrescentar até 2.

Armas auxiliares têm quatro níveis. Para evoluir uma, combine **arma no nível 4 + ao menos um nível da passiva indicada + um baú**. A evolução tem efeito próprio, não apenas um aumento de dano.

| Arma | Passiva necessária | Evolução |
|---|---|---|
| Lâminas orbitais | Ritmo acelerado | Coroa cortante: quatro lâminas e órbita maior |
| Condutor elétrico | Horizonte | Tempestade em cadeia: até cinco alvos |
| Selos arcanos | Poder bruto | Catedral de selos: campo maior |
| Sentinela | Fluxo contínuo | Dupla sentinela: dois disparadores e perfuração |
| Bumerangue | Ímã de aura | Órbita voraz: perseguição, mais ricochetes e perfuração |
| Sino do vazio | Fluxo contínuo | Réquiem do vazio: maior alcance, dano e controle dos inimigos comuns |
| Brasas errantes | Poder bruto | Fênix errante: três chamas perseguidoras e perfurantes |

**TAB** mostra a build e as receitas; pausa apenas o solo. No cooperativo a partida continua para os aliados. O último inimigo das ondas normais múltiplas de 3 é elite e deixa um baú. Baús evoluem uma receita pronta ou dão uma melhoria válida aleatória, além de 15 moedas. O fim da onda recolhe automaticamente os itens restantes e recupera 6% de vida.

Lâminas orbitais começam disponíveis. No **ARSENAL / MISSÕES**, libere Condutor completando a onda 3, Selos abrindo 2 baús, Sentinela com 250 abates e Bumerangue usando 3 transformações. Sino do vazio exige derrotar o primeiro chefe; Brasas errantes exige completar a onda 8. Os totais persistem entre partidas; armas liberadas entram nas escolhas da próxima partida.

## Conquistas e melhorias permanentes

No menu, abra **CONQUISTAS / MELHORIAS**. São 26 conquistas: as anteriores mais vitórias com os três novos personagens, completar objetivos e vencer uma expedição com regra especial.

Moedas, missões e recordes são salvos ao concluir cada onda e no resultado final. Sair pelo menu ou fechar o jogo mantém os checkpoints concluídos, mas descarta o progresso da onda em andamento. Não há retomada da partida. Vitória só conta ao matar o chefe da onda 10, uma vez por partida, mesmo continuando no infinito. Morrer depois não apaga essa vitória. Conquistas são premiadas uma única vez por save.

A loja tem cinco melhorias com limites pequenos: até +15% dano, +25 HP, +60 coleta, +0,40 HP/s e +2 rerrolagens. Não há compras com dinheiro real. Saves antigos são migrados sem apagar seus recordes e vitórias. A partir da V8, `save.json.bak` guarda o checkpoint válido anterior; se o principal estiver ilegível, ele é recuperado automaticamente. Um arquivo corrompido é preservado para recuperação. Se houver erro de escrita, o jogo avisa e tenta novamente; mantenha a pasta com permissão de escrita.

## Seis arenas

A revisão visual usa **24 monstros e oito poses de chefes gerados por IA** nos quatro mapas de expansão. Cripta e U.A. mantêm seus conjuntos existentes. Os quatro pisos também foram gerados como pixel art; as pedras da Cripta ficaram menores e mais legíveis. Veja `ARTE_VISUAL_2.md` para fontes e prompts.

- **Cripta do Colapso:** piso de pedra, velas e explosões rituais a cada 12s.
- **U.A. / Academia:** mantém o mapa e o atlas de monstros que você enviou; perigos a cada 10s.
- **Cidade em Ruínas:** ruas com +8% de velocidade e bombardeio triplo a cada 10s.
- **Ginásio / Noite de Luta:** tablados de boxe, cordas, assentos e avisos a cada 14s.
- **Distrito das Muralhas:** arquitetura estilizada inspirada em Attack on Titan; estilhaços em linha a cada 12s.
- **Backlund / Neblina:** inspiração vitoriana/ocultista, lampiões e selos alternados a cada 13s.

Os cenários inspirados nas obras são layouts originais em pixel art. Prédios e cenografia interior são transitáveis; as **muralhas externas bloqueiam personagens e inimigos**, e nenhum monstro nasce fora delas. A câmera limita o vazio nas bordas. Os perigos têm aviso de 1,4s. Cada mapa tem sua família de monstros e chefe nomeado. Os chefes têm três fases e padrões específicos: círculo/selos na Cripta, investidas/pressão na U.A., bombardeio/varredura na Cidade, combinações curtas no Ginásio, pisões/fissuras nas Muralhas e cartas/selos espelhados em Backlund. Avisos duram pelo menos 0,95s; ataques pendentes são cancelados nas transições de fase. Os desafios secretos conservam seus confrontos próprios.

## Revisão visual e fluidez

Desde a V7, **Ippo, Eren, Klein e Musashi usam pixel art com 32 quadros por personagem**: quatro estados, quatro poses de caminhada e quatro de ataque por estado. Os ataques ativam a sequência de poses; o lado acompanha o deslocamento. Walter mantém seu conjunto existente; os personagens originais desta cópia usam avatares fictícios de IA. Veja a prévia animada em **VERSÃO / ARTES → ANIMAÇÕES DOS PERSONAGENS**.

Todos os menus receberam o mesmo sistema visual: fundo escuro, bordas em degraus, tipografia com acentos/símbolos, cartas com ícones e raridade, progresso das missões e compras indisponíveis desabilitadas. Setas cima/baixo e Enter navegam pelos botões. O HUD ocupa menos espaço; aliados mostram vida; perigos são redesenhados sobre os efeitos.

A conexão multiplayer usa um socket pendente: aguarda `select` e confirma `SO_ERROR` antes de configurar o `Peer` e enviar `hello`. Há validação de IPv4, prazos separados para TCP/handshake, diagnóstico por etapa e tentativa novamente sem fechar o jogo. **VERIFICAR_MULTIPLAYER.bat** exercita a rede TCP no seu próprio Windows e cria `DIAGNOSTICO_MULTIPLAYER.txt`. Este teste local não substitui a partida entre dois PCs por Radmin.


- 24 sprites de efeitos gerados por IA: socos, cortes, eletricidade, chamas, química, cartas, gravidade, cola, paçoca, notas, enxames, impactos e auras. O jogo orienta, expande e dissipa os recortes sem chamar IA durante a partida.
- Personagens e monstros viram conforme seu movimento real; movimento vertical mantém o último lado. Fotografias com orientação original à esquerda são compensadas. Recuos e investidas dos monstros usam a direção do deslocamento.
- O atlas da U.A. remove o fundo com variações de cor e isola um corpo por recorte. As imagens originais permanecem intactas.
- 24 cutscenes, uma de transformação e uma de ultimate por personagem, com coreografias distintas e arte de cenário em pixel art gerada por IA. Walter, Ippo, Klein e Musashi levam a evolução em conta. Elas congelam o combate e o tempo da forma; Enter permite pular. No cooperativo são sincronizadas.
- HUD mais compacto, recargas visíveis para Dash / transformação / ultimate, atributos no perfil do personagem e prévias das arenas sem faixas vazias.
- Setas na borda ajudam a encontrar o chefe e os últimos cinco inimigos quando a onda terminou de gerar inimigos.
- Em Ajustes, desative **CLARÕES** para retirar os flashes brancos de acerto e cutscene, preservando os perigos. Alterne **EFEITOS VISUAIS** entre Completos, Equilibrados e Leve. Leve reduz rastros, partículas decorativas e o número de efeitos simultâneos; projéteis, dano e avisos de perigo permanecem ativos.
- Imagens, rotações, brilho de acerto e pisos ficam em caches limitados. A camada de efeitos escala apenas a região ocupada, evitando trabalho de tela inteira quando está vazia.

## Equilíbrio e controles

A barra Sigma recebe no máximo 2,5 pontos/s e não carrega sozinha fora do combate. Alvo: 40–60s de combate constante; inimigos fora do alcance prolongam isso. Transformação: 14s, cura até 18 HP, recuperação de 10s depois de terminar. Uma ultimate por transformação.

Limpe nove ondas para enfrentar o chefe na **onda 10**, com 15.000 HP, resistência de 20%, três fases e travas contra explosão excessiva. Transições têm 1,25s de escudo; cada fase dura no mínimo 6s. Matá-lo registra vitória e oferece continuar no infinito. Há outro chefe a cada 10 ondas, sem encerrar automaticamente a partida. Vida, dano e recompensas crescem; velocidade e população têm limites. Os testes usam invulnerabilidade controlada e não substituem partidas humanas para avaliar dificuldade.

| Tecla | Ação |
|---|---|
| WASD / setas | Movimento; ataques automáticos |
| Espaço | Dash |
| E / Q | Estado transformado / ultimate |
| F | Musashi no Caminho da Alma: alternar Ego / Vínculo |
| TAB | Build e receitas; pausa no solo |
| Enter durante cutscene | Pular; no cooperativo, anfitrião ou dono da habilidade |
| 1–6 / esquerda-direita | Personagens da página / trocar página |
| 1–6 | Arenas |
| 1–3 / R | Escolher melhoria / rerrolar |
| D F K J | Notas durante a dança de Leozauxta |
| M / N | Silenciar música / próxima faixa |
| Esc / F11 | Pausa ou voltar / tela cheia |
| F3 / F4 | Diagnóstico / colisões |

Leozauxta mantém sua dança: acertar notas ataca a arena e renova a proteção; errar quebra a proteção. O minigame não sincroniza automaticamente com MP3.

**Zatex substitui o nome reservado Zato**. Os dois personagens secretos não têm cartão, silhueta ou missão revelando o nome antes do desbloqueio. Os requisitos estão neste documento para consulta do criador. Os confrontos secretos são solo e fornecem uma build inicial de nível 10. Perder mantém o desafio disponível. A segunda fusão abre automaticamente a seleção quando os requisitos são concluídos no solo; requisitos concluídos em coop abrem ao sair da sala. Depois da primeira oferta, o modo ??? permite tentar novamente. Saves antigos preservam segredos que já tinham sido efetivamente jogados, desde que os requisitos estejam completos.

## Cooperativo

No menu, abra **COOPERATIVO**. O anfitrião escolhe **CRIAR SALA**; os amigos escolhem **ENTRAR**, digitam o IPv4 do anfitrião e conectam. Todos precisam estar na V9 (protocolo 6). Todos escolhem personagem e marcam **PRONTO**. O anfitrião escolhe a arena e inicia. Porta padrão: **TCP 47640**; permita o Python na rede privada do firewall. No Radmin, use o IP virtual do anfitrião e a mesma rede virtual para todos. Instruções completas em `MULTIPLAYER.md`.

Cada jogador tem sua vida, build, Sigma, transformação e ultimate. XP é compartilhado. Aproximar-se de um aliado caído por 3 segundos reanima-o; todos caídos encerram a run. O mundo pausa para as escolhas de melhoria e as cutscenes. A vida dos inimigos escala com o grupo. Moedas, missões e vitórias são registradas no save local de cada participante. O anfitrião decide continuar no infinito ou começar outra expedição na mesma sala.

## Música

Abra `ABRIR_MUSICAS.bat` e coloque até cinco arquivos na pasta aberta (`assets/music`). Use nomes como `01 - abertura.mp3` até `05 - colapso.mp3`. Reinicie o jogo. MP3, OGG e WAV são aceitos; as primeiras cinco faixas em ordem alfabética são repetidas automaticamente. Volume separado nas configurações. Nenhuma música comercial está incluída.

## Testes e limites

Execute `python main.py --self-test`. Consulte `VALIDACAO.md`, `test-results.txt` e as capturas reais em `preview/waves/` (incluem spoilers).

O cooperativo foi exercitado com conexões TCP reais em loopback, incluindo quatro participantes e o fluxo da interface. Ainda precisa de playtest entre computadores Windows/Radmin reais, sobretudo com latência e loja maximizada. Não há migração de anfitrião nem reconexão no meio da run; um cliente que sai não encerra a run dos demais. Se o anfitrião sai, a sala fecha. Não há retomada de partidas encerradas.

### Correção de PNGs preservada da V7.1

Os PNGs de Ippo, Eren, Klein e Musashi em `assets/sprites/characters` agora são os quadros reais das animações carregadas pelo jogo. A V7 distribuía arquivos provisórios genéricos nessa pasta, apesar de carregar as animações corretas a partir de `assets/art`. A exportação dos recortes reais ocorre antes de empacotar, verifica sua integridade e substitui arquivos provisórios quando as folhas de animação estão disponíveis. Fotos e demais mecânicas preservadas.
