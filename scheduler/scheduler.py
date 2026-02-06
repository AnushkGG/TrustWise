def schedule(tasks: list):
    web_tasks = [t for t in tasks if t["source_type"] == "web"]
    paper_tasks = [t for t in tasks if t["source_type"] == "research_papers"]

    return web_tasks, paper_tasks
