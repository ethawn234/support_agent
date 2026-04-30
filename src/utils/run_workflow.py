import asyncio
from agent.graph import workflow
from agent.state import AgentState

async def run_workflow(new_email):
    try:
        graph = await workflow()
        print(f"\n\ngraph instantiated: {graph}")
        print(f"\n\nnew_email is: {new_email[0].keys()}")
        
        msg = new_email[0]['body']
        print(f"msg is: {msg}")
        initial_state = AgentState(
            messages=[msg],
            classification=None
        )
        result = await graph.ainvoke(initial_state)
        return result
    except Exception as e:
        print(f"Error creating workflow in start_workflow: {e}")