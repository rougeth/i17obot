start = """🐍💱 @i17obot
Olá, *{name}*!
Este robô pode te ajudar a traduzir a documentação do Python para português!!

🕹 *Instruções*
/traduzir - envia um trecho com link para traduzir no Transifex
/lembrete - ativa ou desativa lembrete diário com link para traduzir
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
