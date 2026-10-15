> Registro histórico de uma versão anterior. Para o estado atual, consulte `README.md` e `AUDITORIA_V8.md`.

# SIGMA TRINITY V7.1 — correção dos PNGs

A pasta assets/sprites/characters da V7 continha imagens provisórias genéricas com nomes de Ippo, Eren, Klein e Musashi. O jogo substituía essas imagens em memória pelos recortes reais das folhas assets/art/*_animation.png, mas as miniaturas no gerenciador de arquivos continuavam erradas.

A V7.1 exporta todos os quadros reais de caminhada, ataque, aliases e retratos desses quatro personagens. Os arquivos exportados também estão vinculados ao manifesto de integridade. Arquivos provisórios ou ausentes são reparados a partir das folhas reais quando o gerenciador de imagens é carregado, sem sobrescrever arquivos que já são idênticos.

Extraia em uma pasta nova e execute JOGAR.bat dentro de SIGMA_TRINITY_V7.1. Para preservar seu progresso, copie somente save.json; músicas pessoais ficam em assets/music. Não copie a pasta de sprites antiga.

Esta revisão corrige a distribuição das imagens; não adiciona novas artes nem muda o multiplayer. A validação por Radmin entre dois PCs Windows continua dependendo de um playtest nessa rede.
