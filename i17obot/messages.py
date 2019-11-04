start = """🐍💱 @i17obot
Olá, *{name}*!
Este robô pode te ajudar a traduzir a Documentação do Python para português!!

🕹 *Instruções*
/traduzir - envia um trecho com link para traduzir no Transifex
/lembrete - ativa ou desativa lembrete diário com link para traduzir
/ajuda - mostra esta mensagem

Mas, por que *i17o*?
_"Internacionalização são processos de desenvolvimento e/ou adaptação de um produto para uma língua e cultura de um país."_

*internacionalização*
*i         17 letras         o*

Referência: [Wikipedia](https://u.rgth.co/i17o-ref)

🇧🇷 *Documentação do Python em Português*
https://docs.python.org/pt-br/

📖 *Código Aberto*
https://github.com/rougeth/i17obot
"""


translate_at_transifex = """
*Texto original*:
```
{source}
```
*Link para tradução:*
[{transifex_url:.90}...]({transifex_url})

Para escolher outro trecho, use o comando /traduzir.
"""
