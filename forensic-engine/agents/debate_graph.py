from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, START, END

from agents.state import ForensicDebateState, DebateMessage
from agents.prosecutor_agent import run_prosecutor_turn
from agents.defence_agent import run_defence_turn
from agents.expert_agent import run_expert_verification
from agents.judge_agent import run_judge_assessment


def validate_initial_evidence(state: ForensicDebateState) -> Dict[str, Any]:
    """
    Initial validation gate before the debate begins.
    Checks if evidence is present, usable, and sufficient.
    """
    evidence = state.get("evidence", [])
    if not evidence or len(evidence) < 3:
        return {
            "evidence_sufficiency": {
                "can_proceed": False,
                "status": "insufficient_evidence",
                "reason": "Available forensic evidence is insufficient (fewer than 3 structured evidence items).",
                "missing_evidence": ["Structured evidence ledger is empty or critically incomplete."]
            },
            "stopping_reason": "Insufficient initial evidence to conduct debate.",
            "current_iteration": 0,
        }
    
    return {
        "evidence_sufficiency": {
            "can_proceed": True,
            "status": "sufficient",
            "reason": None,
            "missing_evidence": []
        },
        "current_iteration": 0,
    }


def route_after_validation(state: ForensicDebateState) -> str:
    """Routes to Prosecutor Turn 1 if sufficient, otherwise stops."""
    sufficiency = state.get("evidence_sufficiency", {})
    if sufficiency.get("can_proceed", False):
        return "prosecutor_turn_1"
    return END


def make_turn_runner(turn: int):
    """Factory functions for Prosecutor and Defence turn nodes."""
    def prosecutor_node(state: ForensicDebateState) -> Dict[str, Any]:
        p_turns = list(state.get("prosecutor_turns", []))
        all_msgs = list(state.get("debate_messages", []))
        
        msg = run_prosecutor_turn(state, turn)
        p_turns.append(msg)
        all_msgs.append(msg)
        
        return {
            "prosecutor_turns": p_turns,
            "debate_messages": all_msgs,
            "current_iteration": turn,
        }

    def defence_node(state: ForensicDebateState) -> Dict[str, Any]:
        d_turns = list(state.get("defence_turns", []))
        all_msgs = list(state.get("debate_messages", []))
        
        # Current turn state with updated debate_messages for defence to inspect
        msg = run_defence_turn(state, turn)
        d_turns.append(msg)
        all_msgs.append(msg)
        
        # Sufficiency check after this turn
        evidence = state.get("evidence", [])
        can_proceed = len(evidence) >= 3 and len(msg.get("supporting_evidence_ids", [])) > 0
        
        sufficiency = {
            "can_proceed": can_proceed,
            "status": "sufficient" if can_proceed else "insufficient_evidence",
            "reason": None if can_proceed else f"Evidence sufficiency check failed at iteration {turn}.",
            "missing_evidence": [] if can_proceed else [f"Failed to resolve supporting evidence at turn {turn}."]
        }
        
        stopping_reason = None if can_proceed else f"Insufficient evidence at turn {turn}."
        
        return {
            "defence_turns": d_turns,
            "debate_messages": all_msgs,
            "current_iteration": turn,
            "evidence_sufficiency": sufficiency,
            "stopping_reason": stopping_reason,
        }

    return prosecutor_node, defence_node


prosecutor_turn_1, defence_turn_1 = make_turn_runner(1)
prosecutor_turn_2, defence_turn_2 = make_turn_runner(2)
prosecutor_turn_3, defence_turn_3 = make_turn_runner(3)
prosecutor_turn_4, defence_turn_4 = make_turn_runner(4)


def route_after_turn(state: ForensicDebateState, next_node: str) -> str:
    """Checks sufficiency before proceeding to the next turn."""
    sufficiency = state.get("evidence_sufficiency", {})
    if sufficiency.get("can_proceed", False):
        return next_node
    return END


def expert_verifier_node(state: ForensicDebateState) -> Dict[str, Any]:
    """
    Expert Agent node. Runs only after all 8 messages are complete.
    Verifies claims, audits hallucinations, and decides recommendation.
    """
    report = run_expert_verification(state)
    return {"expert_report": report}


def route_after_expert(state: ForensicDebateState) -> str:
    """
    Routes to Judge Agent ONLY if Expert verification succeeds and recommendation is proceed_to_judge.
    """
    report = state.get("expert_report", {})
    if report.get("status") == "verified" and report.get("recommendation") == "proceed_to_judge":
        return "judge_agent"
    return END


def judge_agent_node(state: ForensicDebateState) -> Dict[str, Any]:
    """
    Judge Agent node. Formulates final assessment (REAL, FAKE, or UNCERTAIN).
    """
    result = run_judge_assessment(state)
    return {"judge_result": result}


def build_forensic_debate_graph() -> StateGraph:
    """
    Assembles the 4-agent LangGraph workflow.
    Workflow sequence:
    START -> validate_evidence
          -> (if sufficient) prosecutor_turn_1 -> defence_turn_1
          -> (if sufficient) prosecutor_turn_2 -> defence_turn_2
          -> (if sufficient) prosecutor_turn_3 -> defence_turn_3
          -> (if sufficient) prosecutor_turn_4 -> defence_turn_4
          -> (if sufficient) expert_agent
          -> (if verified & approved) judge_agent -> END
    """
    builder = StateGraph(ForensicDebateState)

    # 1. Validation node
    builder.add_node("validate_evidence", validate_initial_evidence)

    # 2. Debate agent nodes (Turn 1 to 4)
    builder.add_node("prosecutor_turn_1", prosecutor_turn_1)
    builder.add_node("defence_turn_1", defence_turn_1)

    builder.add_node("prosecutor_turn_2", prosecutor_turn_2)
    builder.add_node("defence_turn_2", defence_turn_2)

    builder.add_node("prosecutor_turn_3", prosecutor_turn_3)
    builder.add_node("defence_turn_3", defence_turn_3)

    builder.add_node("prosecutor_turn_4", prosecutor_turn_4)
    builder.add_node("defence_turn_4", defence_turn_4)

    # 3. Expert and Judge nodes
    builder.add_node("expert_agent", expert_verifier_node)
    builder.add_node("judge_agent", judge_agent_node)

    # Edges
    builder.add_edge(START, "validate_evidence")

    builder.add_conditional_edges(
        "validate_evidence",
        route_after_validation,
        {"prosecutor_turn_1": "prosecutor_turn_1", END: END}
    )

    builder.add_edge("prosecutor_turn_1", "defence_turn_1")
    builder.add_conditional_edges(
        "defence_turn_1",
        lambda s: route_after_turn(s, "prosecutor_turn_2"),
        {"prosecutor_turn_2": "prosecutor_turn_2", END: END}
    )

    builder.add_edge("prosecutor_turn_2", "defence_turn_2")
    builder.add_conditional_edges(
        "defence_turn_2",
        lambda s: route_after_turn(s, "prosecutor_turn_3"),
        {"prosecutor_turn_3": "prosecutor_turn_3", END: END}
    )

    builder.add_edge("prosecutor_turn_3", "defence_turn_3")
    builder.add_conditional_edges(
        "defence_turn_3",
        lambda s: route_after_turn(s, "prosecutor_turn_4"),
        {"prosecutor_turn_4": "prosecutor_turn_4", END: END}
    )

    builder.add_edge("prosecutor_turn_4", "defence_turn_4")
    builder.add_conditional_edges(
        "defence_turn_4",
        lambda s: route_after_turn(s, "expert_agent"),
        {"expert_agent": "expert_agent", END: END}
    )

    builder.add_conditional_edges(
        "expert_agent",
        route_after_expert,
        {"judge_agent": "judge_agent", END: END}
    )

    builder.add_edge("judge_agent", END)

    return builder.compile()


# Singleton compiled graph
debate_graph = build_forensic_debate_graph()


def run_forensic_debate(
    analysis_result: Dict[str, Any],
    evidence: List[Dict[str, Any]],
    image_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes the forensic debate on an analysis result and evidence ledger.
    Returns the structured result according to user specifications.
    """
    initial_state: ForensicDebateState = {
        "image_id": image_id or analysis_result.get("image_id", "unknown_image"),
        "analysis_result": analysis_result,
        "evidence": evidence,
        "prosecutor_turns": [],
        "defence_turns": [],
        "debate_messages": [],
        "current_iteration": 0,
        "evidence_sufficiency": {},
        "stopping_reason": None,
        "expert_report": None,
        "judge_result": None,
        "processing_errors": [],
    }

    final_state = debate_graph.invoke(initial_state)

    sufficiency = final_state.get("evidence_sufficiency", {})
    can_proceed = sufficiency.get("can_proceed", False)
    debate_messages = final_state.get("debate_messages", [])
    expert_report = final_state.get("expert_report")
    judge_result = final_state.get("judge_result")

    # If stopped early due to insufficient evidence
    if not can_proceed or len(debate_messages) < 8:
        return {
            "status": "insufficient_evidence",
            "can_proceed": False,
            "debate_completed": False,
            "message": "I cannot proceed with the investigation because the available forensic evidence is insufficient.",
            "completed_iterations": final_state.get("current_iteration", 0),
            "stopping_reason": final_state.get("stopping_reason"),
            "debate_messages": debate_messages,
            "expert_report": None,
            "judge_result": None,
        }

    # Successful completion through Expert and Judge
    return {
        "status": "completed",
        "can_proceed": True,
        "debate_completed": True,
        "completed_iterations": 4,
        "total_messages": len(debate_messages),
        "debate_messages": debate_messages,
        "prosecutor_turns": final_state.get("prosecutor_turns", []),
        "defence_turns": final_state.get("defence_turns", []),
        "evidence_sufficiency": sufficiency,
        "expert_report": expert_report,
        "judge_result": judge_result,
    }
