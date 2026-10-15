> Nota desta cópia de entrega: os textos abaixo registram a versão original. As fotos dos personagens foram substituídas por avatares fictícios de IA nesta cópia; consulte README.md.

# Avaliação crítica da V9

A V9 melhora variedade de combate e leitura de decisões: novos kits, objetivos opcionais, caminhos com custos, avisos de corpo a corpo e estados reais de animação. O conteúdo anterior, as seis arenas, as fusões secretas e a vitória da onda 10 foram preservados.

## O que ficou melhor

- Joe acrescenta risco/resposta; Thorfinn muda a identidade de combate com a evolução e protege aliados; Holden ocupa o espaço de rifle/território.
- Especializações dão uma decisão persistente além de acumular porcentagens. Capturas acrescentam posicionamento e objetivos sem obrigar o jogador a fazê-las.
- Monstros animados e fases de efeitos reduzem a aparência de figuras estáticas; o bestiário permite conferir a arte realmente carregada.
- Comparação nas cartas, missões no menu e cenas repetidas mais curtas removem atrito entre combate e menus.
- Rede autoritativa, validação de snapshots, diagnóstico e continuidade após desconexão permanecem testados.

## Limites e próximos trabalhos

1. Balanceamento ainda precisa de partidas humanas com/sem upgrades, controles e PCs diferentes. Testes com invulnerabilidade verificam funcionamento, não dificuldade ou diversão.
2. Os três caminhos compartilham bases de atributos; futuros talentos podem mudar padrões de ataque de mais personagens. Não afirmar que cada caminho já possui uma árvore própria.
3. Objetivos usam uma regra comum de captura. Missões com escolta, resgate ou destruição exigem sistemas e teste próprios.
4. As animações têm poses reais, mas não oito direções nem interpolação de esqueleto. Recortes gerados podem exigir ajustes de pixel a pixel, principalmente mãos e armas.
5. O mapa é uma arena aberta com muralhas externas; prédios desenhados não constituem colisões internas completas. Acrescentar navegação e obstáculos requer rever o spawn e o comportamento da horda.
6. O cooperativo tem 2–4 participantes via TCP, sem migração de anfitrião ou entrada no meio da partida. Loopback não prova rede Radmin/firewall em duas máquinas Windows. VERIFICAR_MULTIPLAYER.bat testa Winsock local quando executado lá.
7. Existem doze motivos animados de VFX compartilhados entre habilidades, além dos efeitos legados. Nem todo golpe possui uma folha exclusiva.
8. Os cinco MP3 ainda precisam ser fornecidos. A dança usa o relógio da simulação, não análise de batida do arquivo musical.
9. Progressão, ultimates e auras são adaptações de crossover; preservar identidade narrativa não significa reproduzir literalmente a obra.

Não há base para prometer ausência de todos os bugs ou “o melhor jogo do mundo”. A entrega oferece correções reproduzíveis, testes e limites claros. O próximo ganho depende de playtest humano e ajuste de conteúdo, com uma instalação V9 limpa para evitar comparar versões diferentes.
