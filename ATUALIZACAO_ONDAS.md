> Registro histórico de uma versão anterior. Para o estado atual, consulte `README.md` e `AUDITORIA_V8.md`.

# Waves & Secrets — 08/10/2026

## Implementado

- Musashi Miyamoto: Niten Ichi-ryū de curta distância e três progressões por nível — Caminho da Espada (5), Caminho da Morte (10) e Caminho da Alma (15). O último usa **F** para alternar entre Ego, que maximiza o próprio Musashi, e Vínculo, uma aura menor para aliados próximos.
- Auras são aplicadas pela interface `allied_players` e expiram pelo mesmo ciclo do jogador. A revisão cooperativa inclui os até quatro jogadores nessa lista e aplica o efeito aos aliados próximos.
- Zatex normal e Maestro do Véu: imagens de corpo inteiro baseadas nas duas fotos fornecidas, notas musicais, controle e ultimate de ressonância.
- Vitórias com Leo, Guxta e Zatex abrem o modo ???; derrotar Leozauxta nesse desafio desbloqueia o personagem. A antiga vitória de Zato é migrada.
- Vitórias com os quatro integrantes (Leo, Guxta, Zatex, Davi) e Leozauxta abrem a seleção para o desafio de Leozauxtaci Coala, com cutscene de fusão e desbloqueio após derrotá-lo. Arte com quatro rostos, quatro braços e elementos das formas finais. Alterna os quatro kits; ultimate combina as quatro assinaturas.
- Ondas finitas: 12 inimigos na primeira, mais 4 por onda normal até o limite de 100. Chefes a cada 10 ondas. A onda 10 registra vitória e oferece continuar; as seguintes não contam como vitórias adicionais.
- Infinito aumenta vida e dano, limita velocidade e entidades simultâneas e paga mais moedas por onda. Bônus de onda: 8 + 2 × onda, mais 45 se chefe. Abates, baús, vitória e conquistas somam outras recompensas.
- Salvamento de moedas/missões por onda; cura de 6%, coleta automática e pausa de 2,5 segundos entre ondas. Elites nas ondas normais múltiplas de 3.
- Quatro missões persistentes liberam armas auxiliares para as próximas partidas. Receitas, loja e conquistas preservadas.
- Famílias por mapa: mortos-vivos, vilões da U.A., máquinas, pugilistas, titãs e entidades encapuzadas. Novos sprites pixelados para cidade, ringue, muralhas e neblina; arte da cripta e atlas fornecido da U.A. preservados.
- Menu escuro, seleção paginada com perfil, missão com barras de progresso, resultado com escolha do infinito e HUD com onda/restantes.
- Cache limitado de textos e prévias, buffer de efeitos reutilizado, eliminação de escala redundante e filtro espacial nas colisões. Quadros lentos são divididos em passos menores de simulação até 150 ms por quadro.

## Autocrítica e decisões

O jogo acumulava personagens sem um ciclo claro de objetivos e recompensas. As ondas e missões dão metas curtas; o checkpoint torna uma derrota posterior menos frustrante. As duas fusões viram descobertas reais na seleção, sem cartões bloqueados entregando os nomes.

Efeitos grandes podem esconder perigos. Mantive ataques e cenários pixelados, personagens suaves, limites de efeitos e avisos de perigo. A interface usa contraste e hierarquia de texto em vez de novos painéis decorativos pesados.

Não aumentei indefinidamente a quantidade de inimigos: no infinito a pressão cresce também por atributos e composição. O teste automatizado de carga não representa todos os computadores. A dificuldade precisa de partidas humanas, especialmente com builds de corpo a corpo.

Ainda há limites: personagens usam animação de recorte, não sprites desenhados pose a pose; os seis chefes de arena têm aparência/nome próprios, mas compartilham padrões; edifícios internos são cenografia e não há retomada de uma run encerrada. A revisão cooperativa adiciona barreiras externas e multiplayer de duas a quatro pessoas; detalhes em `MULTIPLAYER.md` e `ATUALIZACAO_COOP_CINEMA.md`.

## Origem das novas artes

Zatex: atlas transparente gerado por IA a partir das duas fotos enviadas, reconstruindo pernas e removendo a obstrução da segunda foto; uniforme normal e traje preto com microfone transformado. A fusão usa como referências as formas finais existentes e o atlas de Zatex. São interpretações visuais, não fotografias reais da fusão. Na revisão visual 2, os quatro conjuntos adicionais de monstros foram substituídos por atlases gerados por IA; os desenhos em código permanecem como fallback. Nada é gerado durante o jogo.

Musashi: atlas transparente original de quatro estágios, com ronin, espada dupla, caminho de combate e postura serena. Cabelo preso, roupas gastas, luta de curta distância e o Niten Ichi-ryū remetem ao personagem; os nomes dos três caminhos, indicadores e buffs são adaptações de jogo. Não são páginas, poses nem arte extraída de *Vagabond*.
# Revisão visual 2

Atualização sobre o sistema de ondas existente: quatro atlases de monstros em pixel art gerada por IA (24 inimigos e oito poses de chefe), 24 efeitos de ataque, quatro pisos, HUD com recargas, perfis com atributos, indicadores para encontrar os últimos inimigos e opção de qualidade dos efeitos. Personagens, mapa/atlas da U.A., progressão e saves existentes são preservados. Nenhuma IA é chamada durante as partidas. Fontes, prompts e limites de animação estão em `ARTE_VISUAL_2.md`; evidências em `VALIDACAO.md`.

