> Nota desta cópia de entrega: os textos abaixo registram a versão original. As fotos dos personagens foram substituídas por avatares fictícios de IA nesta cópia; consulte README.md.

> Registro histórico de uma versão anterior. Para o estado atual, consulte `README.md` e `AUDITORIA_V8.md`.

# Direção visual e prompts — Dark Edition

Foi usado o gerador de imagens integrado. As imagens originais produzidas, com alpha preservado, são consumidas pelo jogo em `assets/art/`. A apresentação usa desenho por Pygame e animação de recortes; não há chamadas de IA durante o jogo.

## Prompts por asset

- `leo.png`: extrair fotograficamente apenas Leo da primeira foto; preservar rosto, cabelo curto escuro, colar, camiseta azul-marinho, shorts, gesto e pose. Remover ambiente, partes de outras pessoas e marca da câmera. Transparência real, figura inteira e pequenos ajustes para completar os tênis.
- `rafael.png`: extrair Rafael da segunda foto, preservando sorriso, óculos, cabelo, camiseta clara, jeans, tênis e pose sentada. Remover sala, cadeira, mochila, outras pessoas e telefone; mãos naturais. Transparência real, sem cenário.
- `leozauxta.png`: extrair os três amigos juntos da terceira foto como um só sprite. Preservar rostos distintos, penteados, roupas, poses e braços entrelaçados. Remover restaurante, banco, letreiro e pequena figura na mão; alpha real.
- `leo_form.png`: transformar o Leo da referência em Calvo Absoluto, completamente careca, com bigode grande escuro, rosto reconhecível, colar, camiseta azul-marinho, shorts e tênis. Galão de cola claro, casaco escuro desgastado e expressão séria. Corpo inteiro, sem texto ou aura. Segunda edição para remover o fundo e halo, mantendo o personagem e o galão.
- `rafael_form.png`: transformar Rafael literalmente num bloco vivo de paçoca de amendoim, textura granulosa, braços pequenos, botas, óculos retangulares e rosto/sorriso reconhecível na superfície. Material realista, ocre e sombras castanhas, transparência real.
- `leozauxta_form.png`: fundir os três integrantes num único titã de exatamente três cabeças reconhecíveis. Uma cabeça para cada integrante, óculos no da esquerda, corpo enorme, roupas pretas e marrons desgastadas, calças e tênis. Pose de dança com joelhos flexionados e braços abertos; iluminação dramática contida, corpo inteiro e alpha real.
- `floor.png`: textura ortográfica de piso de cripta em lajes irregulares escuras, pedra desgastada, fissuras e musgo discreto. Charcoal, ardósia e terra; luz difusa uniforme. Sem perspectiva, personagens, mobiliário, texto ou neon. Repetição de piso.
- `enemies.png`: atlas transparente de oito silhuetas separadas, quatro colunas e duas linhas, estilo dark fantasy realista. Perseguidor de manto vermelho, atirador de manto cinza com besta, slime musgoso, cobrador robusto com baú, morcego de couro, cavaleiro de ferro escuro, chefe fantasma coroado e obelisco de pedra. Corpos inteiros, tons dessaturados, sem chão, sombras projetadas, texto ou bordas.

Os prompts preservam o absurdo dos personagens dentro de um cenário mais sério. A identidade visual não utiliza neon dominante, painéis arredondados luminosos ou mudanças nas mecânicas de combate.

## Coala Update

`davi_atlas.png`: atlas transparente gerado a partir das duas referências do usuário. Duas figuras de corpo inteiro, base e Full Cowl, com rosto e cabelo inspirados no Davi, traje verde, proteção creme, pescoceira prateada e botas/cinto vermelhos. A transformação tem pose baixa de combate e raios verdes. O runtime separa as duas células e anima os recortes; não há esqueleto 3D nem animação quadro a quadro redesenhada. A aparência é uma recriação por IA a partir das fotos, não uma preservação literal de todos os pixels do rosto.

As novas arenas são desenhadas em Pygame e recebem a textura de pedra existente. Referências do USJ estão no README; não se trata de um mapa idêntico ao anime ou ao jogo comercial. O combate também foi reequilibrado nesta atualização; a observação anterior de mecânicas preservadas descreve somente a Dark Edition anterior.

## Revisão de equilíbrio e mapa enviado

O antigo desenho procedural do USJ foi substituído pelo PNG exato enviado pelo usuário (`image(20261008-010409).png`). Cópia íntegra em `assets/art/hero_map.png`, redimensionada pelo renderer. Sem geração por IA ou pintura sobre essa imagem. O limite de navegação foi traçado sobre o contorno da ilha; edifícios são elementos visuais transitáveis nesta arena 2D. As descrições anteriores do USJ de seis setores referem-se à versão anterior.

## Pixel & Rhythm Update — versão atual

A imagem da ilha foi substituída pelo novo `mapa_ua_limpo(1).png`, copiado sem alteração para `hero_map.png`. `sprites_monstros_atlas(1).png` foi copiado para `ua_monsters.png`. O runtime recorta as células sem títulos, retira o fundo escuro conectado à borda e usa o corpo principal para excluir fragmentos vizinhos. As animações reutilizam poses fornecidas; elas não são animações novas quadro a quadro.

O gerador integrado de imagens produziu dois novos atlas, integrados em `assets/art/`:
- `pixel_monsters.png`: prompt para quatro colunas e duas linhas com cultista esquelético vermelho, caçador de besta cinza, slime de musgo, cobrador robusto de armadura, morcego roxo, cavaleiro negro e duas poses de espectro coroado. Referência de estilo: atlas U.A. fornecido. Pixel art detalhada de 16 bits, silhuetas completas, transparência, sem texto, sem aparência realista. Componentes alpha isolam as oito figuras sem cortar asas ou espadas.
- `walter_atlas.png`: prompt para oito sprites de um personagem fictício estilizado, sem reproduzir o rosto do ator real: professor de jaqueta bege, versão com traje amarelo de proteção, alter ego de chapéu preto e aparência final de barba/jaqueta verde. Duas poses por visual, quatro colunas e duas linhas, pixel art de paleta limitada e transparência. A primeira tentativa com semelhança explícita ao ator foi bloqueada; o asset utilizado é a representação fictícia estilizada.

A dança usa o recorte original do Titã, com inclinação, compressão, espelhamento e salto, conforme a pista acertada. Não é captura de movimento nem uma animação de esqueleto articulado. Cenário e efeitos são desenhados com pixels; os rostos e imagens de Leo, Rafael, Leozauxta e Davi continuam no pipeline original.


## Guxta
Recortes gerados pelo editor de imagens integrado a partir das referências enviadas, em assets/art/guxta.png e guxta_form.png. Solicitações: isolar somente o rapaz com camiseta e caneta, preservar rosto/roupa/pose, remover outras pessoas; isolar o homem de manto de nuvens vermelhas, preservar rosto/pose/roupa, remover lua/cenário/fumaça. Fundo alpha transparente, sem pixelização. Recortes por IA podem apresentar pequenas diferenças da foto original. Animação leve do recorte em execução, sem regenerar quadros.
