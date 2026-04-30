import asyncio
from agent.graph import workflow
from agent.state import AgentState

async def run_workflow(email):
    try:
        graph = await workflow()
        initial_state = AgentState(
            raw_email=email,
            email_content=email[0]['body'],
            classification=None,
            is_valid_req=None,
            draft_ticket=None,
            id=email[0]['threadId'],
            messages=None
        )
        result = await graph.ainvoke(initial_state)
        return result
    except Exception as e:
        print(f"Error creating workflow in start_workflow: {e}")