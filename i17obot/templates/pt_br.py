start = """🐍💱 @i17obot
Olá, *{name}*!
Este robô pode te ajudar a traduzir a documentação do Python para português!!

Clique em /tutorial para começar.

🕹 *Instruções*
/traduzir - envia um trecho com link para traduzir no Transifex
/lembrete - ativa ou desativa lembrete diário com link para traduzir
/tutorial - aprenda como começar a traduzir a documentação
/links - principais links
/ajuda - mostra esta mensagem

🇧🇷 *Documentação do Python em Português*
https://docs.python.org/pt-br/

📖 *Código Aberto*
https://github.com/rougeth/i17obot

Mas, por que *i17o*?
_"Internacionalização são processos de desenvolvimento e/ou adaptação de um produto para uma língua e cultura de um país."_

*internacionalização*
*i         17 letras         o*

Referência: [Wikipedia](https://u.rgth.co/i17o-ref)
"""


translate_at_transifex = """
📝 *Texto original*:
```
{source}
```
🔗 *Link para tradução*:
[{transifex_url}]({transifex_url})...

📚 *Referência e contexto*:
{docsurl}

/traduzir para receber outro trecho
"""

review_translation = """
📝 *Texto original*:
```
{source}
```

🔖 *Tradução*:
```
{translation}
```
🔗 [Link para tradução]({transifex_url})

📚 *Referência e contexto*:
{docsurl}
"""

translation_correct = """
*Tradução revisada com sucesso!* 🎉🥳
Se quiser continuar revisando as traduções, use o comando /revisar.
Obrigado pela contribuição, *{name}*.
"""

translation_incorrect = """
Sem problemas, *{name}*.
Se você quiser corrigir a tradução, acesse a [tradução no Transifex]({string_url}).
Obrigado pela contribuição!
"""

dont_know_review = """
Sem problemas, *{name}*.
Para tentar outra tradução, use o comando /revisar.
Obrigado pela contribuição!
"""

reminder_on = """*Lembrete configurado* 🎉🥳
Você deverá receber um trecho para ser traduzido por dia.
Se você quiser, use o comando /traduzir para receber outro trecho a qualquer momento.
Para desativar, use o comando /lembrete.
"""

reminder_off = """*Lembrete removido* 😢
Mas você pode continuar traduzindo usando o comando /traduzir.
"""

status = """📈 *Status*
- Total users: {users}
- Total reminders configured: {reminders}
"""


links = """*Referências*

📚 Como fazer a tradução da documentação oficial do Python?
https://sheilagomes.github.io/traducao-doc-python/

🐍 [@pybr_i18n](@pybr_i18n)
Grupo no Telegram da comunidade que traduz Python e Django para português.

🛠 [Transifex](https://www.transifex.com/python-doc/python-newest)
Ferramenta usada para traduzir a documentação do Python.

📜 [python/python-docs-pt-br](https://github.com/python/python-docs-pt-br)
Código fonte da tradução

🤖 [rougeth/i17obot](https://github.com/rougeth/i17obot)
Código fonte do [@i17obot](@i17obot)
"""

tutorial_part_1 = """*Tutorial*: 1/3
Para começar, Crie uma conta no Transifex, serviço que usamos para traduzir a documentação. Para isso, basta acessar o site:
https://transifex.com/signup
"""

tutorial_part_2 = """*Tutorial*: 2/3
Agora, é preciso entrar para o time de tradução do Python:

1. Acesse o site: https://transifex.com/python-doc/python-newest
2. Clique no botão "_Join team_"
3. Selecione a opção "_Portuguese (Brazil)_"
4. Clique no botão "_Join_"

Agora, basta aguardar até que os moderadores liberem o seu acesso, não deve demorar.
"""

tutorial_part_3 = """*Tutorial*: 3/3
🎉 Pronto! Agora você já pode começar a *contribuir* para a tradução da documentação do Python!

Não deixe de entrar para o grupo @pybr\_i18n, o melhor canal para tirar dúvidas, trocar ideias e sugestões.

/traduzir - Comece já a traduzir
/links - Principais links do projeto
/ajuda
"""

list_projects_start = """
Qual projeto você quer contribuir para traduções?
"""

list_projects = """
Qual projeto você quer contribuir para traduções?

Você está traduzindo o projeto {project}
"""

selected_project = "Você vai contribuir com o projeto {project}!"
