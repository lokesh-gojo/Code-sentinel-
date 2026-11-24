import pytest
from langgraph.types import Command
from app.services.agent_graph import code_review_agent


def test_agent_graph_interrupt_and_resume():
    """
    Verifies that:
    1. Agent executes static analysis and patch generation
    2. Pauses at human_approval node with __interrupt__
    3. Resumes when human approval is provided
    """
    thread_id = "test-user:unit-test-thread"
    config = {"configurable": {"thread_id": thread_id}}

    buggy_code = """def divide(a, b):
    return a / b
"""
    initial_state = {
        "filename": "main.py",
        "original_code": buggy_code,
        "language": "python",
        "findings": [],
        "proposed_patch": "",
        "regression_test": "",
        "explanation": "",
        "test_passed": False,
        "test_output": "",
        "retry_count": 0,
        "max_retries": 2,
        "approved": None,
        "feedback": None,
        "published": False,
    }

    # Step 1: Run until interrupt
    result = code_review_agent.invoke(initial_state, config=config)
    assert "__interrupt__" in result, "LangGraph agent should pause at human_approval interrupt"

    proposal = result["__interrupt__"][0].value
    assert "proposed_patch" in proposal
    assert "explanation" in proposal

    # Step 2: Resume with human approval
    decision = {"approved": True, "feedback": "Patch looks solid, proceed."}
    resumed = code_review_agent.invoke(Command(resume=decision), config=config)

    assert resumed.get("approved") is True
    assert resumed.get("published") is True
