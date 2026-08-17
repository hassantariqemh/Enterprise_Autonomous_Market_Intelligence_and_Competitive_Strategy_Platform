from typing import TypedDict
from langgraph.graph import StateGraph, END
from app.agents import competitor_agent, strategy_agent


class AgentState(TypedDict):
    question: str
    evidence: dict
    answer: dict


def research_node(state: AgentState) -> AgentState:
    evidence = competitor_agent.run(state["question"])
    return {**state, "evidence": evidence}


def strategy_node(state: AgentState) -> AgentState:
    result = strategy_agent.run(state["question"], state["evidence"])
    return {**state, "answer": result}


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("research", research_node)
    graph.add_node("strategy", strategy_node)

    graph.set_entry_point("research")
    graph.add_edge("research", "strategy")
    graph.add_edge("strategy", END)

    return graph.compile()


orchestrator = build_graph()


def ask(question: str) -> dict:
    result = orchestrator.invoke({"question": question, "evidence": {}, "answer": {}})
    return result["answer"]