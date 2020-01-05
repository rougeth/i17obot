def docsurl(resource):
    docspath = "/".join(resource.split("--"))
    docspath = docspath.replace("_", ".").replace("..", "__")
    return f"https://docs.python.org/{docspath}.html"
