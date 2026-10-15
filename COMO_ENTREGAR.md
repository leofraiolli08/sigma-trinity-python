# Entrega do projeto Python

Prazo informado no e-mail: **15/10**. O formulário só deve ser preenchido depois
de concluir a publicação e testar o link.

## 1. Preparar

Extraia o ZIP inteiro. Abra a pasta `SIGMA_TRINITY_ENTREGA`. O README já lista os três participantes: Leonardo Cardoso Fraiolli, Wendell e
Davi Ribeiro. Confira a grafia; se o formulário pedir o nome completo de Wendell,
preencha nele. Instale e execute conforme o README.

## 2. Criar o repositório

Entre em https://github.com/new e escolha o nome `sigma-trinity-python`.
Use público, conforme a preferência do e-mail. Deixe desmarcadas as opções de
criar README, .gitignore e licença: os arquivos já estão preparados nesta pasta.
Clique em Create repository e copie a URL HTTPS do repositório.

Instale Git para Windows se necessário: https://git-scm.com/downloads/win.
Abra Git Bash dentro da pasta extraída e execute um comando por vez:

```console
git init -b main
git add .
git status
git commit -m "Entrega do projeto Python: Sigma Trinity"
git remote add origin https://github.com/SEU_USUARIO/sigma-trinity-python.git
git push -u origin main
```

Troque `SEU_USUARIO` pelo seu usuário. Se criou com outro nome, use a URL exata
copiada do GitHub. Se o Git pedir nome/e-mail de autor, configure apenas neste
repositório, usando seu nome de apresentação e o e-mail noreply fornecido na
conta GitHub; depois repita o commit. A autenticação é feita no seu computador.
Não cole token ou senha no README, no código ou em conversas.

**Envie os arquivos extraídos, não o ZIP como único arquivo do repositório.**
Não use o upload pelo navegador para arrastar a pasta inteira: a quantidade de
assets torna Git/GitHub Desktop mais adequado. Os arquivos individuais desta
cópia estão abaixo de 100 MiB, então não é necessário Git LFS.

Se preferir GitHub Desktop, adicione a pasta como repositório local, crie o
primeiro commit e use Publish repository. Confira se o README está na raiz.

Documentação oficial:
https://docs.github.com/pt/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github
https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository

## 3. Conferir e preencher o formulário

Abra o link do repositório numa janela anônima, confira `README.md`, `main.py`,
`requirements.txt`, `.gitignore` e `assets/`. Faça um download novo do GitHub e
confirme que o jogo inicia após instalar as dependências.

No formulário original do e-mail, informe os participantes e o link do
repositório. O texto copiado para este chat não contém a URL de "Acesse ao
formulário clicando aqui"; abra esse botão no e-mail original.

Sugestão de descrição:

> SIGMA TRINITY é um jogo 2D de sobrevivência por ondas, desenvolvido em Python
> com Pygame. Possui personagens com habilidades e evoluções distintas, seis
> arenas, chefes, melhorias durante as partidas, conquistas e progressão salva
> localmente. Pode ser jogado sozinho e inclui cooperativo opcional por rede
> local. O repositório contém todo o código, assets, testes, dependências e
> instruções de execução. Houve auxílio de IA na implementação e criação de artes.

Esta preparação não publica o repositório nem envia o formulário automaticamente.
