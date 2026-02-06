from orchestrator.orchestrator import generate_plan
from chunker.chunker import chunk_tasks
from scheduler.scheduler import schedule
from agents import web_agent, research_agent

def main():
    query = input("Enter query: ")

    try:
        plan = generate_plan(query)
        print("\n--- Generated Plan ---")
        print(plan)
        print("----------------------\n")
        
        tasks = chunk_tasks(plan)
        web_tasks, paper_tasks = schedule(tasks)

        print(f"Scheduled {len(web_tasks)} web tasks and {len(paper_tasks)} research tasks.\n")

        # Dispatch to Agents
        for task in web_tasks:
            web_agent.run(task)

        for task in paper_tasks:
            research_agent.run(task)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
