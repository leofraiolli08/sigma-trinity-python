# Validação da cópia de entrega — 14/10/2026

## Resultado

**203 testes passaram em 315.166 segundos**, com Pygame 2.6.1 e Python
3.12.14. Registro integral em test-results-entrega.txt. O diagnóstico de integridade
passou e o jogo executou 180 quadros em modo headless com Leo.

A cópia mantém as funcionalidades da V10 e substitui os onze arquivos de arte
dos personagens originais por quatorze avatares fictícios gerados por IA, sem
referência a fotografias. Os quadros exportados foram reconstruídos. O recorte
usa alfa maior que 32 para não incluir pixels quase transparentes distantes.
Menu, seleção e partida foram renderizados e inspecionados; capturas em docs/.
O ZIP anterior do jogo permanece separado desta cópia de entrega.

## Verificação dos arquivos e Git

Todos os módulos Python enviados foram analisados por AST e compilados. PNGs
foram decodificados integralmente, JSONs analisados e textos lidos como UTF-8.
Os hashes do manifesto foram conferidos. A lista individual de arquivos, tamanhos
e SHA-256 está em AUDITORIA_ENTREGA.csv. O ZIP passa em testzip para integridade
CRC, sem saves, logs, ambientes virtuais, pasta .git ou backups pessoais.

O .gitignore foi exercitado com save.json, backup, .env, .venv, logs e MP3 pessoal.
O .gitattributes preserva os bytes dos arquivos no checkout; isso evita que
autocrlf invalide hashes no Windows. Nenhum arquivo individual excede 100 MiB.
Uma busca por formatos comuns de tokens, chaves privadas e CPF não encontrou
ocorrências nos textos da entrega; isso não é uma prova formal de ausência de
qualquer informação sensível. Participantes constam conforme informados.

## Limites

Os testes usam Linux/SDL dummy. Não houve execução desta cópia em computadores
Windows físicos com Radmin VPN nem garantia formal de ausência de todos os bugs.
Os testes TCP reais locais de conexão, lobby, sincronização e desconexão fazem
parte da suíte. O avaliador pode executar o modo solo sem configurar uma rede.

O README, requirements.txt, .gitignore, código .py e assets estão preparados.
A publicação no GitHub e o envio do formulário ainda precisam ser feitos pelo
responsável; o link do formulário não estava presente no texto do e-mail.
