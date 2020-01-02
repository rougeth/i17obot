from urllib.parse import quote


def duckgo(term):
    search = quote(f'\\"{term}" site:docs.python.org')
    return f"https://duckduckgo.com/html/?q={search}" 


def docsurl(resource):
    path = "/".join(resource.split("--"))
    return f"https://docs.python.org/{path}.html"
