# Cooperativo LAN / Radmin VPN — 2 a 4 jogadores

Todos precisam extrair o ZIP V9 (protocolo 6) e ter Python/Pygame instalados. Cada pessoa usa seu próprio `save.json`; não copie o save do anfitrião para os amigos.

## Criar e entrar

1. O anfitrião abre `JOGAR.bat`, entra em **COOPERATIVO** e escolhe **CRIAR SALA**.
2. Na mesma rede local, compartilhe um IPv4 mostrado na sala. Pelo Radmin VPN, todos entram na mesma rede virtual e usam o IPv4 do anfitrião mostrado no Radmin.
3. Os amigos abrem **COOPERATIVO → ENTRAR EM UMA SALA** e digitam o IP. Exemplo de formato: `26.12.34.56`. Esse exemplo não é um endereço real do seu anfitrião.
4. A porta padrão é **TCP 47640**. Também é aceito `IP:47640`. Permita o Python no firewall da rede privada do anfitrião.
5. Cada pessoa escolhe seu personagem e marca **PRONTO**. Trocar personagem cancela o próprio pronto. O anfitrião escolhe a arena e clica **INICIAR EXPEDIÇÃO**.

São necessários pelo menos dois jogadores. Há quatro vagas no total, contando o anfitrião. Sala cheia, versões incompatíveis e entradas depois do início são recusadas com mensagem.

## Durante a expedição

- Controles iguais ao solo: WASD/setas, Espaço, E, Q, F para Musashi e D/F/K/J na dança de Leozauxta.
- Ataques automáticos e inimigos pertencem à mesma simulação. O anfitrião calcula colisões, fases e dano; os clientes enviam controles.
- Cada personagem mantém vida, transformação, ultimate, build e upgrades individuais. XP é compartilhado; baús dão uma melhoria a cada build e uma única recompensa de moedas para o grupo.
- Ao subir de nível, todos que têm escolhas pendentes escolhem suas cartas. O mundo fica pausado até acabar a fila de escolhas. Um participante já pronto vê uma tela de espera.
- Cutscenes são vistas por todos e congelam o combate, inclusive o tempo da transformação. O anfitrião ou o dono da habilidade pode pular com Enter/Espaço. A ultimate só é executada ao terminar a cutscene.
- Aproximar-se de um aliado caído por 3 segundos o reanima com 40% de vida e 2 segundos de proteção. Sair de perto interrompe a contagem. O fim de uma onda também recupera aliados caídos. Todos caídos encerram a expedição.
- **Esc e Tab são telas locais**: não pausam os aliados. Quem está num menu deixa de andar e usar habilidades; ainda pode sofrer dano.
- Musashi no Caminho da Alma pode alternar Ego/Vínculo. Vínculo beneficia aliados de verdade dentro do alcance.
- Vida dos inimigos escala por `1 + 0,65 × (jogadores − 1)`. Ao perder um participante, os inimigos restantes têm a vida ajustada ao novo grupo, mantendo a proporção de vida restante.

## Vitória, infinito e saves

Derrotar o chefe da onda 10 registra uma vitória em cada save local. Moedas e missões são salvas por onda; o resultado registra as recompensas finais sem duplicar a vitória. Depois de todos os saves concluírem o registro, o anfitrião pode continuar no infinito ou usar **NOVA EXPEDIÇÃO** para voltar à sala com os mesmos participantes.

Os confrontos de personagens secretos são solo. Se o cooperativo completar os requisitos da segunda fusão, a seleção do desafio aparece ao voltar ao menu depois de sair da sala. O modo ??? permanece disponível para repetir um desafio perdido.

## Correções de conexão e diagnóstico da V8

O cliente mantém o socket sob controle enquanto a conexão não bloqueante está pendente. `select([], [sock], [sock], 0)` verifica conclusão sem bloquear o jogo; `SO_ERROR` confirma o resultado. Somente após o sucesso o jogo configura TCP_NODELAY, cria o Peer e envia o handshake. Não há chamada a select com todos os conjuntos vazios. A sequência prematura relatada na V6 foi retirada; não foi possível comprovar que ela era a única causa do WinError 10022 nas máquinas originais sem o traceback daquela execução.

IPv4/porta são validados antes do socket. A tentativa TCP e a espera do handshake possuem prazos próprios de oito segundos. Conexão recusada, rede inacessível, porta ocupada, timeout e incompatibilidade de versão têm mensagens distintas. **TENTAR NOVAMENTE** recria o transporte; **CORRIGIR ENDEREÇO** preserva o texto para edição. Ctrl+V cola um IPv4 no campo no Windows.

`logs/multiplayer.log` registra release, sistema, versão do Python, papel na sala, etapa, códigos de erro e traceback das falhas internas. É um arquivo local com rotação limitada. Ele contém o endereço usado para diagnosticar a rede; não grava saves, perfis completos nem os controles da partida. Logs e saves pessoais não são incluídos no ZIP.

Abra **VERIFICAR_MULTIPLAYER.bat** se ocorrer um erro: o diagnóstico executa 22 testes de rede, incluindo quatro participantes reais por TCP e três processos clientes independentes, e grava `DIAGNOSTICO_MULTIPLAYER.txt`. Rodá-lo em Windows exercita o Winsock daquela máquina, mas continua sendo um teste em loopback. Ele não libera firewall nem altera configurações da rede.

Para validar Radmin entre os dois PCs: use este mesmo ZIP em ambos, crie a sala, entre pelo IPv4 do anfitrião, confirme os dois cartões, marque pronto e inicie. Exercite movimento, E/Q, melhorias e saída de um cliente; confira se o anfitrião continua. Se falhar, os logs dos dois PCs e o diagnóstico identificam a etapa. A confirmação desse playtest é necessária antes de declarar o multiplayer validado no seu ambiente.

Snapshots totalmente não enviados são substituídos pelo estado mais recente quando a rede fica lenta. Um frame parcialmente enviado é preservado, assim como as mensagens de controle, para evitar quebrar o protocolo. Recusas de sala têm tempo para completar o envio. Uma falha ao configurar um cliente aceito não encerra a sala inteira. As vagas e estruturas daquele participante são limpas após desconexão.

## Conexão e limites atuais

Se não conectar, confira: mesmo ZIP, mesma rede local/virtual, IPv4 correto, sala aberta, porta 47640 e permissão do Python no firewall. O campo de IP aceita IPv4 numérico, sem URL ou nome de domínio.

Um cliente desconectado libera sua vaga na sala de preparação. Durante a run, os demais continuam. Se o anfitrião sair, todos recebem a mensagem de desconexão; não há migração de anfitrião nem reconexão durante a run. O progresso já salvo por onda permanece.

A sincronização de estado usa 20 atualizações/s, com interpolação visual de personagens/inimigos e previsão curta de projéteis. O loop de desenho mira 60 FPS; isso não garante 60 FPS em qualquer hardware. Música e efeitos sonoros são locais. A dança usa o relógio compartilhado de simulação, não o ritmo de um MP3.

Validado aqui com sockets TCP reais em loopback e quatro participantes. Testes entre computadores Windows/Radmin físicos e playtests humanos ainda são necessários.

## Auditoria adicional da V8

- Rafael e Leozauxta só modificam seus próprios tiros quando o limite de 280 projéteis é atingido.
- A marionete usa a distância de seu controlador; efeitos e campos usam o dono correto para cor/dano.
- Snapshots validam tipos, números finitos, campos obrigatórios, estados de evolução, dimensões e referências antes de alterar o mundo. Referências de chefe e ritmo são limpas na vitória/desconexão.
- O cliente confirma o resultado apenas após gravar seu save; falhas de escrita geram novas tentativas sem duplicar vitória ou moedas.
- O protocolo mudou: clientes V7/V7.1/V8 são recusados com mensagem para usar o mesmo pacote.

A suíte completa e os limites de ambiente estão em `AUDITORIA_V8.md` e `VALIDACAO.md`.

## V9

O anfitrião escolhe a regra no lobby. Os três novos personagens, caminhos, objetivos, poses, derrotas e histórico de cutscenes fazem parte do estado sincronizado. O HUD do cliente mostra RTT quando uma resposta de ping é recebida. Objetivos concedem uma recompensa ao mundo; não uma duplicação por aliado. Se o dono de uma cutscene se desconectar, ela é cancelada e a sala continua. `VERIFICAR_MULTIPLAYER.bat` executa 23 testes TCP locais, incluindo uma sala de quatro com os novos personagens. Isso não comprova funcionamento entre dois PCs físicos com Radmin; essa etapa continua necessária.
