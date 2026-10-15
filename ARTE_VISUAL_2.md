> Registro histórico de uma versão anterior. Para o estado atual, consulte `README.md` e `AUDITORIA_V8.md`.

# Arte — revisão visual 2

Imagens produzidas pela ferramenta integrada de geração de imagens (ImageGen), depois recortadas em células, reduzidas e animadas pelo renderer. Nenhuma IA é executada durante a partida. Os arquivos originais de personagem e o mapa/atlas da U.A. foram preservados.

## Assets de produção

- `assets/art/city_monsters.png`, `ring_monsters.png`, `walls_monsters.png`, `fog_monsters.png`: quatro atlases 4×2, com seis inimigos e duas poses do chefe por mapa.
- `assets/art/combat_fx_atlas.png`: atlas 4×4 de dezesseis efeitos.
- `assets/art/impact_fx_atlas.png`: atlas 4×2 de oito impactos e assinaturas especiais.
- `assets/art/terrain_atlas.png`: quatro pisos em atlas 2×2, usados como cenografia transitável.

Os monstros normais usam uma pose e movimento leve de recorte. Os chefes têm duas poses. Os efeitos têm direção, rotação, expansão e dissipação calculadas pelo jogo; não são animações desenhadas frame a frame. Fios, cabos e avisos de perigo mantêm geometria dinâmica para indicar posições e alcance com precisão. Os recortes usam alpha nativo e escala por vizinho mais próximo.

## Prompts finais e referência

Os quatro atlases de monstros usaram `assets/art/pixel_monsters.png` como referência de estilo. O atlas de efeitos recebeu uma revisão para reduzir o bloom e deixar o recorte transparente. A imagem final é `combat_fx_atlas.png`.

### Cidade

```text
Use case: stylized-concept. Asset type: transparent game sprite atlas. Create ONE production 4 columns by 2 rows atlas for a dark pixel art survival game. Reference image 1 is the exact visual quality/style guide: detailed crisp painted pixel clusters, dark strong outline, like an expertly drawn 16-bit action RPG monster atlas, NOT realistic, not voxel, no smooth 3D. New city ruins themed enemy set. Exactly eight isolated full-body sprites, one centered inside each equal cell, generous transparent gutters, no labels, no text, no scenery. Row1 left to right: scrap-armored shambling robot with teal visor; skeletal artillery soldier with heavy amber cannon; crawling electric mutant with exposed wires; massive concrete-plated demolition brute. Row2: flying surveillance drone with two propellers and red optics; fast mechanical assassin with two blades; boss urban war-machine knight with enormous rust shield; SAME boss in second attacking pose with raised hammer. Ground enemies face slightly right in three-quarter game view, feet on consistent baseline. Strong readable silhouettes, metal/cloth texture in discrete pixel clusters; cool desaturated slate palette, modest cyan/amber accents. Each sprite entirely within its cell, no touching sprites. True transparent alpha everywhere outside figures. Square or landscape canvas. Six normal enemies and two boss poses.
```

### Ginásio

```text
Use case: stylized-concept. Asset type: transparent 4 columns by 2 rows game sprite atlas. Reference is style guide only, detailed dark crisp pixel art with strong outlines, hand-painted pixel clusters, 16-bit action RPG look. Exactly eight full-body figures, one per equal cell, 4x2 evenly aligned, transparent gaps, no words. Arena: haunted boxing gym. Row1: undead lightweight boxer in blue shorts and blue gloves; skeletal ranged cornerman with towel and small bell; crouched fast featherweight with red gloves; massive bald heavyweight wearing black/gold shorts. Row2: floating cursed bell with torn ribbon (small airborne enemy); lean masked kickboxer with dark maroon gloves; boss champion dark bruised skin golden waist belt white shorts huge burgundy gloves; same boss alternate hook punch pose. Normal grounded enemies face slightly right, 3/4 topdown compatible full body. Sports gear / no monster weapons, no exaggerated fantasy armor. Color charcoal, burgundy, muted bronze, bone, cold blue; readable faces and fingers, gritty sinister tone, discrete square pixel shading not realistic / not smooth 3D. SIX normal enemies and TWO poses same boss. All figures fit inside equal cells with generous transparent padding. No contact or overlap between subjects. True transparent background.
```

### Muralhas

```text
Use case: stylized-concept. Asset type: 4x2 transparent sprite atlas for dark pixel survival game. Reference image is the STYLE guide: intricate pixel clusters, crisp deep outline, handcrafted 16-bit RPG monster detail, non-realistic, NO 3D. Exactly 8 full body isolated sprites in equal 4 column 2 row grid with 16px transparent margins inside each cell. Row1: wiry hairless grinning humanoid giant wandering forward; giant throwing broken stone (ranged); creepy crouching runner giant with long arms; bulky giant protected by ivory hardened muscle plates. Row2: winged skeletal flying scout beast; lean black-haired berserker giant with clenched fists; colossal armored humanoid boss with layered bone-like plates and steam vents; same colossal boss alternate raised fist attack pose. Original designs, inspired by monstrous giant anatomy in a ruined walled district. Exposed muscle textures, skin red-brown muted tan, not gore or wounds. Six normal enemies plus two same boss poses. All game-view 3/4 slightly facing right, soles at consistent cell baseline. All bodies completely visible including feet, no clipping. Isolated figures only, no names, labels, text, floor, background or watermark. True transparent alpha and ample empty gutters. Consistent lighting and dark moody colors.
```

### Backlund

```text
Use case: stylized-concept. Asset type: transparent 4-column 2-row monster atlas for dark pixel art survival game. Reference is detailed old-school pixel art style guide, strong outlines and tiny crisp square clusters, no realism or smooth 3D. Exactly eight isolated full-body sprites evenly laid out one in each equal cell, transparent margins. Theme: sinister foggy Victorian occult city. Row1: masked ragged cultist holding iron lantern; hooded plague alchemist throwing a small violet vial; crouching masked shadow assassin with cane blade; huge stitched black-coat grave sentinel with brass shoulder armor. Row2: flying many-eyed shadow moth; skeletal duelist with top hat and rapier; boss eldritch Victorian ritual master in ornate black violet coat with golden pocket chains and faceless mask, tentacular shadow hem; SAME boss casting pose arms outstretched. Six normal enemies, two same boss poses. Three-quarter game angle slightly facing right, consistent grounded baseline for feet. Lantern amber, violet/cold blue accents, desaturated dark cloth, readable distinct silhouettes. Every sprite fully visible including legs and wings, separated with ample transparent empty gutter. No captions, labels, names, letters, watermark, background, floor, scene. True transparent alpha. Match the reference's visual density and contrast.
```

### Efeitos

```text
Use case: stylized-concept. Asset type: transparent combat VFX sprite atlas for pixel survival game. Create exactly 16 isolated effects in perfect FOUR columns FOUR rows equal grid. Each effect occupies middle 70% of its cell with transparent padding, no labels/text. Crisp high-quality 16-bit hand pixel art, luminous readable cores, saturated accent colors and black/dark outline, no realistic smoke/no photography/no 3D. ROW1: left-to-right orange-red boxing glove and explosive punch-impact star pointing RIGHT; white gold sweeping crescent katana slash pointing RIGHT; jagged emerald lightning fork running horizontally RIGHT; amber-red flame burst horizontally RIGHT. ROW2: bubbling toxic lime green potion flask and smoke splash; cyan icy-blue crystal shard cluster pointing RIGHT; violet gravitational black-hole vortex with curved crescent rim; fan of cream ornate playing cards with purple magical edge. ROW3: violet musical notes and bright soundwave; bright jade squared fantasy currency token (no writing); golden crumbly peanut candy projectile with falling crumbs; turquoise clear glue droplet with splash tail horizontally RIGHT. ROW4: gold-white bullet streak pointing RIGHT; amber nuclear mushroom explosion burst (stylized non-realistic); pale cyan compressed air spiralling projectile pointing RIGHT; turquoise gold concentric occult aura ring, oblique top-down ellipse with small motes and no symbols/text. Each isolated visual should be readable at 32-96 pixels. Actual transparent alpha background throughout. No solid backplates, cell borders, numbers, captions, floor, environment, characters or watermark. All 16 effects fully separated and fully visible. This is one game asset spritesheet, not a diagram.
```

### Ajuste dos efeitos

```text
Edit target: this 16-cell 4x4 game combat VFX atlas. Change ONLY background and glow handling. Remove EVERY broad soft colored glow, bloom, haze, tinted backplate and color gradient from all cells and gutters. Set everything outside the crisp pixel shapes and their discrete pixel sparks to exactly zero transparent alpha. No large area of colored semi-transparency. Retain all 16 distinct effect subjects, exact positions, colors, shape and 4x4 equal grid. Make effects slightly smaller to leave clear transparent padding around all four edges of every cell. Edges should be crisp detailed pixel art. Keep small sharp luminous cores. No text, no scenery, no background whatsoever. True fully transparent background, not a drawn checkerboard. Production sprite sheet on transparent alpha.
```

### Impactos e assinaturas

```text
Use case: stylized-concept. Asset type: transparent pixel art combat effects atlas, ONE 4 columns by 2 rows grid, exactly eight distinct isolated effects, no labels. Crisp luminous 16-bit pixel game art with discrete square clusters and sharp edges; clear zero-alpha gaps, no large soft blooms or gradient backdrop. Row1 left-to-right: brown-gray cracked stone ground shockwave with dust and debris around crater (no fire, no mushroom, no fist, no glove); small brilliant cream-gold four-point hit spark with short shards; black-violet bat swarm bursting out of a vortex, wing silhouettes visibly readable; dark ruby-red gravity vortex with black center and curved crimson tendrils. Row2: cyan glue pool with rising sticky threads and falling droplets; golden peanut candy storm exploding into chunky crumbs, no fire; violet-blue musical shockwave with two luminous notes and sweeping arcs; cream white arcane puppet strings suspended from glowing thin branching threads above a small violet seal, no figures. Full visuals each centered in middle 70% of its respective equal cell, entirely within cell, no overlapping. Transparent background with alpha exactly zero outside sharp sprite forms and crisp sparks. No floor outside crater/pool, no backplates, no text, no labels, no watermark, no borders.
```

### Pisos

```text
Use case: stylized-concept. Asset type: top-down pixel art floor material atlas. ONE SQUARE canvas with exactly FOUR equal SQUARE quadrants (2 columns 2 rows), NO labels, borders or separating gutters. Each quadrant is an independent top-down RPG arena ground tile covering its whole square. Orthographic OVERHEAD view, no isometric perspective, no vertical walls, no characters/creatures. Dark but readable handcrafted 16-bit pixel art, strong visible square pixel clusters, muted colors, no photoreal texture. Top-left: ruined city asphalt avenue intersection, muted blue slate broken brick pavements, scattered rust scrap, painted worn ochre dashes, tiny rubble and cracked foundations at edges; top-right: haunted boxing gym arena wood floor, several thin red/cream ring boundary lines, worn floorboards and sports equipment silhouettes at edges; bottom-left: ruined walled district cobblestone town square, small patches moss and dusty terracotta debris, a circular stone pavement motif, broken wagon wheel at edge; bottom-right: Victorian occult city's cobblestone plaza, gray teal pavement, a subtle ceremonial circle engraved in stones, warm brass lamp pools at corners, drainage grates and subtle purple cracks. ALL four floors traversable, visually mostly open and calm, many subtle crisp details visible at game zoom, no large obstructions. No gradient illumination, no thick walls, no objects taller than knee height, no lettering, no UI, no watermarks. Need to tile as backgrounds in 2D action survivor game. Each quadrant should have matching opposite-edge colors so repeated tiles do not produce bright seams.
```

