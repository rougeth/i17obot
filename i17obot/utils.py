def docsurl(resource):
    corner_cases = {
        "library--multiprocessing_shared_memory": "library/multiprocessing.shared_memory",
    }

    docspath = corner_cases.get(resource)
    if not docspath:
        docspath = "/".join(resource.split("--"))
        docspath = docspath.replace("_", ".").replace("..", "__")

    return f"https://docs.python.org/pt-br/3/{docspath}.html"
