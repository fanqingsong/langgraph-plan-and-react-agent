import os
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Union

from .planner import Plan
from .state import PlanExecute, get_default_state
from .prompts import REPLANNER_PROMPT_TEMPLATE
from .llm_config import get_azure_llm

# Response model as per the example
class Response(BaseModel):
    """Response to user."""
    response: str

# Act model as per the example
class Act(BaseModel):
    """Action to perform."""
    action: Union[Response, Plan] = Field(
        description="Action to perform. If you want to respond to user, use Response. "
        "If you need to further use tools to get the answer or continue working, use Plan."
    )

# Replanner prompt as per the example
replanner_prompt = ChatPromptTemplate.from_template(REPLANNER_PROMPT_TEMPLATE)

# LLM and replanner chain as per the example
replanner = replanner_prompt | get_azure_llm(
    model="gpt-4",
    temperature=0,
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_REPLANNER", "gpt-4")
).with_structured_output(Act)

async def replan_step(state: PlanExecute):
    """Replans the existing plan based on execution feedback."""
    # Get default state values and update with current state
    current_state = get_default_state()
    current_state.update(state)
    
    input_data_for_replanner = {
        "input": current_state["input"],
        "plan": current_state.get("plan", []),  # Previous plan
        "past_steps": current_state["past_steps"],
        "current_draft_report": current_state.get("current_draft_report", ""),  # Pass current draft
        "current_utc_date": current_state["current_utc_date"],
        "current_utc_time": current_state["current_utc_time"],
        "current_year": current_state["current_year"],
    }
    
    output_act = await replanner.ainvoke(input_data_for_replanner)

    if isinstance(output_act.action, Response):
        return {
            "response": output_act.action.response,  # This is the final answer/report
            "plan": []  # Clear plan as it's finished
        }
    elif isinstance(output_act.action, Plan):
        return {
            "plan": output_act.action.steps,  # New plan steps
            "response": ""  # Clear any old final response from state if continuing
            # current_draft_report remains in state, it's not cleared by replanner
        }
    else:
        print(f"Warning: replan_step received an unexpected action type: {type(output_act.action)}. Defaulting to empty plan.")
        # Potentially problematic, agent might get stuck.
        # Consider if it should re-try replanning or enter an error state.
        return {"plan": [], "response": "Replanning resulted in an unexpected action type."}