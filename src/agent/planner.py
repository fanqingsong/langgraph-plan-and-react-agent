import os
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
from typing import List
from langchain_core.messages import HumanMessage

from .state import PlanExecute, get_default_state
from .prompts import PLANNER_PROMPT_TEMPLATE
from .llm_config import get_azure_llm

class Plan(BaseModel):
    """Plan to follow in future"""
    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )


# 这句代码的作用是创建一个对话式提示模板（planner_prompt），
# 该模板包括系统消息（作为总体规划指令和背景设定，即PLANNER_PROMPT_TEMPLATE），
# 以及一个"placeholder"，用来动态插入用户的输入信息（messages）。
# 结果是：可以结构化地组织LLM提示，使其能融合固定规划准则和实时用户输入，有助于模型产出针对性强的任务分解方案。
# 是的，大模型的对话prompt通常采用"system"和"user"这样的role来区分系统设定和用户输入。这里"system"代表整体规划指令背景，"placeholder"用来动态填充用户输入数据（实际会被"HumanMessage"对象替换）。下面的写法即明确分为 system（设定场景/能力）和占位符（用户输入）：
planner_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", PLANNER_PROMPT_TEMPLATE),
        MessagesPlaceholder("messages"),
    ]
)

planner = planner_prompt | get_azure_llm(
    model="gpt-4",
    temperature=0,
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_PLANNER", "gpt-4")
).with_structured_output(Plan)

async def plan_step(state: PlanExecute):
    # Get default state values and update with current state
    current_state = get_default_state()
    current_state.update(state)
    
    plan = await planner.ainvoke({
        "messages": [HumanMessage(content=current_state["input"])],
        "current_utc_date": current_state["current_utc_date"],
        "current_utc_time": current_state["current_utc_time"],
        "current_year": current_state["current_year"],
    })
    return {"plan": plan.steps}