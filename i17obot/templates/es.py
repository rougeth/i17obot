start = """🐍💱 @i17obot
Hola, *{name}*!
Este bot puede ayudarte a traducir la documentación do Python al español!!

Haz click en /tutorial para comenzar.

🕹 *Instrucciones*
/traducir - envía un fragmento con un link para traducir en Transifex
/recordatorio - activa o desactiva el recordatorio diario con el link para traducir
/tutorial - aprenda como comenzar a traducir la documentación
/links - links principales
/ayuda - muestra este mensaje

🇺🇸 *Documentación de Python en Español*
https://python-docs-es.readthedocs.io/es/3.7/index.html

📖 *Código Abierto*
https://github.com/rougeth/i17obot

Pero, por qué *i17o*? _Este bot fue desarrollado originalmente en portugués_
_"La internacionalización es un proceso de desarrollo y/o adaptación de un producto al idioma y cultura de un país"

*internacionalização*
*i         17 letras         o*

Referencia: [Wikipedia](https://es.wikipedia.org/wiki/Internacionalizaci%C3%B3n_y_localizaci%C3%B3n)
"""


translate_at_transifex = """
📝 *Texto original*:
```
{source}
```
🔗 *Link para traducción*:
[{transifex_url}]({transifex_url})...

📚 *Referencia y contexto*:
{docsurl}

/traducir para recibir otro fragmento
"""

reminder_on = """*Recordatorio configurado* 🎉🥳
Deberías recibir un fragmento para traducir por día.
Si quieres, usa el comando /traducir para recibir otro fragmento en cualquier momento.
Para desactivar, usa el comando /recordatorio.
"""

reminder_off = """*Recordatorio eliminado* 😢
Puedes continuar traduciendo usando el comando /traducir.
"""

status = """📈 *Status*
- Usuarios totales: {users}
- Recordatorios configurados: {reminders}
"""


links = """*Referencias*

📚 Cómo traducimos la documentación oficial de Python?
https://python-docs-es.readthedocs.io/es/3.7/CONTRIBUTING.html

🐍 [@python_docs_es](@python_docs_es)
Grupo de Telegram para trabajar en la traducción de Python al español.

🛠 [Transifex](https://www.transifex.com/python-doc/python-newest)
Herramienta utilizada para traducir la documentación de Python.

📜 [PyCampES/python-docs-es](https://github.com/PyCampES/python-docs-es)
Código fuente de la traducción.

🤖 [rougeth/i17obot](https://github.com/rougeth/i17obot)
Código fuente de [@i17obot](@i17obot)
"""

tutorial_part_1 = """*Tutorial*: 1/3
Para comenzar, cree una cuenta en Transifex, servicio que usamos para traducir la documentación. Para eso, acceda al sitio:
https://transifex.com/signup
"""

tutorial_part_2 = """*Tutorial*: 2/3
Ahora es necesario unirse al equipo de traducción de Python:

1. Acceder al sitio: https://transifex.com/python-doc/python-newest
2. Click en el botón "_Join team_"
3. Seleccione la opción "_Spanish_"
4. Click en el botón "_Join_"

Basta esperar a que los moderadores aprueben la solicitud.
"""

tutorial_part_3 = """*Tutorial*: 3/3
🎉 Listo! Ahora puedes comenzar a *contribuir* en la traducción de la documentación de Python!

No olvides consultar tus dudas o sugerir ideas en el canal @python\_docs\_es.

/traducir - Comience a traducir
/links - Links principales del proyecto
/ayuda
"""
