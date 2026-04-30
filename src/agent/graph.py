from langgraph.graph import StateGraph, END, START

from agent.nodes import validate_issue, approval, classification, classification, create_ticket, input_guardrail, output_guardrail, send_slack_notification, output_guardrail
from agent.state import AgentState

async def create_graph_diagram(graph, filename):
    try:
        graph_bytes = graph.get_graph().draw_mermaid_png()
        with open(filename, "wb") as f:
            f.write(graph_bytes)
    except Exception as e:
        print(f"Failed to save workflow graph: {e}")

async def workflow():
    graph = StateGraph(AgentState)
    # add nodes
    graph.add_node("input_guardrail", input_guardrail)
    graph.add_node("classification", classification)
    graph.add_node("validate_issue", validate_issue)
    graph.add_node("output_guardrail", output_guardrail)
    graph.add_node("approval", approval)
    graph.add_node("create_ticket", create_ticket)
    graph.add_node("send_slack_notification", send_slack_notification)

    # add edges
    graph.add_edge(START, "input_guardrail")
    graph.add_edge("input_guardrail", "classification")
    graph.add_edge("classification", "validate_issue")
    graph.add_edge("validate_issue", "output_guardrail")
    graph.add_edge("output_guardrail", "approval")
    graph.add_edge("approval", "create_ticket")
    graph.add_edge("create_ticket", "send_slack_notification")
    graph.add_edge("send_slack_notification", END)

    # compile graph and return    
    graph = graph.compile()
    await create_graph_diagram(graph, "graph.png")

    return graph
