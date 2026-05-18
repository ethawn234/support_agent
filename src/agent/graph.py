from langgraph.graph import StateGraph, END, START

from agent.nodes import read_email, classification, human_review, create_ticket, read_email, send_slack_notification, request_email_clarification
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
    graph.add_node("read_email", read_email)
    graph.add_node("classification", classification)
    graph.add_node("request_email_clarification", request_email_clarification)
    graph.add_node("create_ticket", create_ticket)
    graph.add_node("send_slack_notification", send_slack_notification)
    graph.add_node("human_review", human_review)

    # add edges
    graph.add_edge(START, "read_email")
    graph.add_edge("read_email", "classification")
    graph.add_conditional_edges("classification", ['human_review', 'request_email_clarification', 'create_ticket'])
    graph.add_edge("create_ticket", "send_slack_notification")
    graph.add_edge("send_slack_notification", END)

    # compile graph and return    
    graph = graph.compile()
    await create_graph_diagram(graph, "graph.png")

    return graph
