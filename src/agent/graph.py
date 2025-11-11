from langgraph.graph import StateGraph, END

from .state import PlanExecute
from .planner import plan_step  # Updated import
from .executor import execute_step
from .replanner import replan_step

"""
Graph拓扑图 (Graph Topology):

工作流程说明：
1. Planner: 创建初始计划 (plan = ["task1", "task2", "task3"])
2. Executor: 执行 plan[0] (task1)，执行后从 plan 中移除该任务
   - 执行后: plan = ["task2", "task3"]
   - 将执行结果添加到 past_steps
3. Replanner: 分析执行结果和剩余计划
   - 如果任务完成 → 返回 Response，结束流程
   - 如果未完成 → 返回新的 Plan（包含剩余任务或调整后的任务）
4. 循环: 如果 replanner 返回 Plan，流程回到 Executor 继续执行

    [START]
       |
       v
   ┌─────────┐
   │ planner │  (入口节点，创建初始计划)
   └────┬────┘
        |
        v
   ┌──────────┐
   │ executor │  (执行 plan[0]，执行后从 plan 中移除)
   └────┬─────┘
        |
        v
   ┌───────────┐
   │ replanner │  (分析结果，决定继续或结束)
   └────┬──────┘
        |
        | (条件边)
        ├─── 如果 state["response"] 存在 → [END]
        |
        └─── 否则 → executor (循环执行剩余任务)
"""

# Define the graph
workflow = StateGraph(PlanExecute)

# Add the nodes
workflow.add_node("planner", plan_step)  # Updated function mapping
workflow.add_node("executor", execute_step)
workflow.add_node("replanner", replan_step)

# Set the entrypoint
workflow.set_entry_point("planner")

# Define the edges
workflow.add_edge("planner", "executor")
workflow.add_edge("executor", "replanner")

# Define conditional logic for continuing or finishing after replanning
def should_end(state: PlanExecute):  # Renamed and logic adjusted
    """Determines whether to end the process or continue to the agent (executor)."""
    if "response" in state and state["response"]:
        return END
    else:
        # Corresponds to 'agent' in the example, which is our 'executor' node
        return "executor"  

workflow.add_conditional_edges(
    "replanner",
    should_end,  # Updated function
    {
        END: END,
        "executor": "executor", 
    }
)


# Compile the graph
# memory = SqliteSaver.from_conn_string(":memory:") # Example for in-memory checkpointer
# graph = workflow.compile(checkpointer=memory)

# For local testing without a persistent checkpointer initially:
graph = workflow.compile(name="Plan and Execute Agent")

# To make the agent runnable, you'd typically expose `graph`
# and provide a way to invoke it, e.g., via a FastAPI endpoint or a CLI.

# The configuration part from the original template might need to be adapted
# if you want to make parts of this plan-and-execute agent configurable
# (e.g., the models used in planner, executor, replanner).
# For now, the models are hardcoded in their respective files.
