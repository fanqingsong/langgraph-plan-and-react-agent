import os
from langgraph.prebuilt import create_react_agent
from .tools import tools
from .state import PlanExecute, get_default_state
from .prompts import get_executor_system_prompt
from .llm_config import get_azure_llm

# Choose the LLM that will drive the agent
llm = get_azure_llm(
    model="gpt-4",
    temperature=0,
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_EXECUTOR", "gpt-4")
)


def _prepare_time_context(state: dict) -> str:
    """Prepare time context string from state."""
    return (
        f"Current UTC Date is {state['current_utc_date']}, "
        f"Current UTC Time is {state['current_utc_time']} (Year: {state['current_year']})."
    )


def _is_document_related_task(task_description: str) -> bool:
    """
    Check if a task is related to document creation/editing.
    
    Args:
        task_description: The task description to check.
        
    Returns:
        True if the task is document-related, False otherwise.
    """
    document_keywords = [
        "draft", "report", "summary", "document", "review", "refine", "generate", 
        "write", "add to", "organize", "create", "compile", "structure"
    ]
    return any(kw in task_description.lower() for kw in document_keywords)


def _prepare_task_input(task_description: str, current_draft_content: str = None) -> str:
    """
    Prepare task input for the agent, including draft content if relevant.
    
    Args:
        task_description: The task description.
        current_draft_content: Optional existing draft content.
        
    Returns:
        Formatted task input string for the agent.
    """
    task_is_document_related = _is_document_related_task(task_description)
    
    if task_is_document_related and current_draft_content:
        return f"""Current Task: {task_description}

You MUST operate on or use the following EXISTING DRAFT CONTENT:
--- EXISTING DRAFT CONTENT START ---
{current_draft_content}
--- EXISTING DRAFT CONTENT END ---
"""
    elif task_is_document_related:
        return f"""Current Task: {task_description}
(There is no existing draft content yet. You are likely creating an initial draft if the task implies generation.)
"""
    else:
        return task_description


def _update_draft_report(
    task_description: str, 
    agent_output: str, 
    current_draft_content: str = None
) -> str:
    """
    Determine if the agent output should update the draft report.
    
    Args:
        task_description: The task description.
        agent_output: The output from the agent.
        current_draft_content: Optional existing draft content.
        
    Returns:
        Updated draft report content.
    """
    if _is_document_related_task(task_description):
        return agent_output
    return current_draft_content


async def _execute_task_with_agent(
    task_input: str, 
    time_context: str
) -> str:
    """
    Execute a task using the ReAct agent.
    
    Args:
        task_input: The formatted task input for the agent.
        time_context: Time context string.
        
    Returns:
        The final output from the agent.
    """
    executor_system_prompt = get_executor_system_prompt(time_context)
    agent_executor = create_react_agent(llm, tools, prompt=executor_system_prompt)
    
    agent_response_obj = await agent_executor.ainvoke(
        {"messages": [("user", task_input)]}
    )
    
    return agent_response_obj["messages"][-1].content


async def execute_step(state: PlanExecute):
    """
    Execute a single step from the plan.
    
    Args:
        state: The current agent state.
        
    Returns:
        Updated state with execution results.
    """
    # Get default state values and update with current state
    current_state = get_default_state()
    current_state.update(state)
    
    # Handle empty plan case
    if not current_state["plan"]:
        return {
            "past_steps": [("No task to execute", "Plan was empty.")],
            "current_draft_report": current_state.get("current_draft_report")
        }

    # Get the current task (first task in the plan)
    current_task_description = current_state["plan"][0]
    current_draft_content = current_state.get("current_draft_report")
    
    # Prepare time context and task input
    time_context = _prepare_time_context(current_state)
    task_input = _prepare_task_input(current_task_description, current_draft_content)
    
    # Execute the task
    agent_final_output = await _execute_task_with_agent(task_input, time_context)
    
    # Update draft report if needed
    new_draft_report_content = _update_draft_report(
        current_task_description, 
        agent_final_output, 
        current_draft_content
    )
    
    # Remove the executed task from the plan
    # This ensures the next iteration will execute the next task in the plan
    remaining_plan = current_state["plan"][1:] if len(current_state["plan"]) > 1 else []
    
    return {
        "past_steps": [(current_task_description, agent_final_output)],
        "current_draft_report": new_draft_report_content,
        "plan": remaining_plan,  # Update plan to remove executed task
    }