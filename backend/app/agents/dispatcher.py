from app.agents.base import BaseAgent
from app.cot.base import COTLayerResult, COTResult
from typing import Dict, List, Any
from app.utils.logger import logger
import uuid


WORKFLOW_TEMPLATES = {
    "trip_planning": {
        "name": "行程规划",
        "steps": [
            {"agent": "intent", "action": "parse", "required": True, "parallel": False},
            {"agent": "intent", "action": "fill_missing", "required": False, "parallel": False},
            {"agent": "compliance", "action": "check_user_level", "required": True, "parallel": False},
            {"agent": "transportation", "action": "search", "required": True, "parallel": True},
            {"agent": "hotel", "action": "search", "required": False, "parallel": True},
            {"agent": "dining", "action": "search", "required": False, "parallel": True},
            {"agent": "compliance", "action": "check", "required": True, "parallel": False},
            {"agent": "approval", "action": "generate", "required": True, "parallel": False}
        ]
    },
    "invoice": {
        "name": "发票处理",
        "steps": [
            {"agent": "invoice", "action": "upload", "required": True, "parallel": False},
            {"agent": "invoice", "action": "recognize", "required": True, "parallel": False},
            {"agent": "approval", "action": "generate", "required": False, "parallel": False}
        ]
    },
    "mock_data": {
        "name": "Mock数据生成",
        "steps": [
            {"agent": "mock_data", "action": "fetch", "required": True, "parallel": False},
            {"agent": "mock_data", "action": "generate", "required": True, "parallel": False}
        ]
    }
}


class DispatcherAgent(BaseAgent):
    def __init__(self):
        super().__init__("DispatcherAgent")
        self.active_workflows: Dict[str, dict] = {}
        self.workflow_history: List[dict] = []

    async def process(self, input_data: dict) -> dict:
        if self.enable_cot:
            return await self.process_with_cot(input_data)
        return await self._simple_process(input_data)

    async def process_with_cot(self, input_data: dict) -> dict:
        cot_result = COTResult(
            request_id=f"dispatcher_{id(input_data)}",
            agent_name=self.name
        )

        try:
            layer1 = await self.intent_understanding_layer(input_data, cot_result)
            cot_result.layers.append(layer1)

            layer2_input = {**layer1.output_data, "original_input": input_data}
            layer2 = await self.knowledge_retrieval_layer(layer2_input, cot_result)
            cot_result.layers.append(layer2)

            layer3_input = {**layer2.output_data, "original_input": input_data}
            layer3 = await self.reasoning_decision_layer(layer3_input, cot_result)
            cot_result.layers.append(layer3)

            layer4_input = {**layer3.output_data, "original_input": input_data}
            layer4 = await self.response_generation_layer(layer4_input, cot_result)
            cot_result.layers.append(layer4)

            cot_result.final_output = layer4.output_data
            cot_result.is_complete = True

            return {
                **layer4.output_data,
                "cot": cot_result.to_dict()
            }
        except Exception as e:
            self.logger.error(f"DispatcherAgent COT error: {e}")
            import traceback
            traceback.print_exc()
            fallback = await self._simple_process(input_data)
            fallback["cot_error"] = str(e)
            return fallback

    async def intent_understanding_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        session_id = input_data.get("session_id")
        message = input_data.get("message") or ""
        intent_type = input_data.get("intent_type", "trip_planning")

        reasoning_steps = [
            f"接收用户消息: {message[:50]}..." if len(message) > 50 else f"接收用户消息: {message}",
            f"会话ID: {session_id}",
            f"初步意图判断: {intent_type}",
            f"准备创建工作流..."
        ]

        return COTLayerResult(
            layer_name="intent_understanding",
            input_data=input_data,
            output_data={
                "session_id": session_id,
                "message": message,
                "intent_type": intent_type,
                "workflow_type": intent_type
            },
            reasoning_steps=reasoning_steps,
            confidence=0.9
        )

    async def knowledge_retrieval_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        intent_type = input_data.get("intent_type", "trip_planning")

        workflow_template = WORKFLOW_TEMPLATES.get(intent_type, WORKFLOW_TEMPLATES["trip_planning"])

        parallel_agents = [s for s in workflow_template["steps"] if s.get("parallel")]
        sequential_agents = [s for s in workflow_template["steps"] if not s.get("parallel")]

        reasoning_steps = [
            f"检索工作流模板: {workflow_template['name']}",
            f"工作流步骤数: {len(workflow_template['steps'])}",
            f"可并行执行步骤: {len(parallel_agents)}",
            f"顺序执行步骤: {len(sequential_agents)}"
        ]

        return COTLayerResult(
            layer_name="knowledge_retrieval",
            input_data=input_data,
            output_data={
                "workflow_template": workflow_template,
                "parallel_agents": parallel_agents,
                "sequential_agents": sequential_agents,
                "total_steps": len(workflow_template["steps"]),
                "intent_type": intent_type
            },
            reasoning_steps=reasoning_steps,
            confidence=0.95
        )

    async def reasoning_decision_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        original_input = input_data.get("original_input", {})
        knowledge = input_data.get("knowledge_retrieval_output", input_data)
        workflow_template = knowledge.get("workflow_template", {})
        session_id = original_input.get("session_id") or input_data.get("session_id")
        intent_type = original_input.get("intent_type") or input_data.get("intent_type", "trip_planning")

        if not workflow_template:
            workflow_template = WORKFLOW_TEMPLATES.get(intent_type, WORKFLOW_TEMPLATES["trip_planning"])

        workflow_id = str(uuid.uuid4())
        workflow = {
            "id": workflow_id,
            "session_id": session_id,
            "intent_type": intent_type,
            "name": workflow_template.get("name", "未知"),
            "steps": workflow_template.get("steps", []),
            "status": "created",
            "created_at": str(uuid.uuid4()),
            "task_results": {}
        }

        if session_id:
            self.active_workflows[session_id] = workflow

        steps = workflow.get("steps", [])
        if not steps:
            steps = workflow_template.get("steps", [])

        task_assignments = []
        for step in steps:
            task_assignments.append({
                "agent": step["agent"],
                "action": step["action"],
                "required": step.get("required", True),
                "parallel": step.get("parallel", False)
            })

        reasoning_steps = [
            f"创建工作流ID: {workflow_id}",
            f"工作流名称: {workflow['name']}",
            f"总任务数: {len(task_assignments)}",
            f"分配任务到各Agent..."
        ]

        return COTLayerResult(
            layer_name="reasoning_decision",
            input_data=input_data,
            output_data={
                "workflow": workflow,
                "workflow_id": workflow_id,
                "task_assignments": task_assignments,
                "next_step": task_assignments[0] if task_assignments else None,
                "session_id": session_id,
                "intent_type": intent_type
            },
            reasoning_steps=reasoning_steps,
            confidence=0.9
        )

    async def response_generation_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        original_input = input_data.get("original_input", {})
        reasoning = input_data.get("reasoning_decision_output", input_data)
        workflow = reasoning.get("workflow", {})
        workflow_id = reasoning.get("workflow_id")
        task_assignments = reasoning.get("task_assignments", [])

        if not workflow_id:
            workflow_id = str(uuid.uuid4())
        if not task_assignments:
            task_assignments = []

        response_data = {
            "status": "created",
            "workflow_id": workflow_id,
            "workflow_name": workflow.get("name", "未知") if workflow else "未知",
            "intent_type": reasoning.get("intent_type", original_input.get("intent_type", "trip_planning")),
            "total_tasks": len(task_assignments),
            "tasks": [
                {"agent": t["agent"], "action": t["action"], "required": t["required"]}
                for t in task_assignments
            ],
            "next_action": {
                "agent": task_assignments[0]["agent"] if task_assignments else None,
                "action": task_assignments[0]["action"] if task_assignments else None
            },
            "message": f"工作流已创建，包含{len(task_assignments)}个任务"
        }

        reasoning_steps = [
            f"生成工作流创建响应",
            f"工作流ID: {workflow_id}",
            f"下一步执行: {task_assignments[0]['agent']}.{task_assignments[0]['action']}" if task_assignments else "无任务"
        ]

        return COTLayerResult(
            layer_name="response_generation",
            input_data=input_data,
            output_data=response_data,
            reasoning_steps=reasoning_steps,
            confidence=0.9
        )

    async def _simple_process(self, input_data: dict) -> dict:
        session_id = input_data.get("session_id")
        intent_type = input_data.get("intent_type", "trip_planning")

        workflow_template = WORKFLOW_TEMPLATES.get(intent_type, WORKFLOW_TEMPLATES["trip_planning"])
        workflow_id = str(uuid.uuid4())

        workflow = {
            "id": workflow_id,
            "session_id": session_id,
            "intent_type": intent_type,
            "name": workflow_template.get("name", "未知"),
            "steps": workflow_template.get("steps", []),
            "status": "created"
        }

        self.active_workflows[session_id] = workflow

        return {
            "workflow_id": workflow_id,
            "workflow_name": workflow["name"],
            "intent_type": intent_type,
            "tasks": [
                {"agent": s["agent"], "action": s["action"], "required": s.get("required", True)}
                for s in workflow["steps"]
            ],
            "status": "created"
        }

    async def dispatch_task(self, workflow_id: str, task: dict, input_data: dict) -> dict:
        agent_name = task["agent"]
        action = task["action"]

        self.logger.info(f"Dispatching task: {agent_name}.{action}")

        return {
            "task": f"{agent_name}.{action}",
            "status": "pending",
            "data": {}
        }

    async def aggregate_results(self, workflow_id: str) -> dict:
        for workflow in self.active_workflows.values():
            if workflow["id"] == workflow_id:
                results = workflow.get("task_results", {})
                return {
                    "workflow_id": workflow_id,
                    "status": workflow["status"],
                    "results": results,
                    "completed_tasks": len(results),
                    "total_tasks": len(workflow["steps"])
                }
        return {"error": "Workflow not found"}

    def get_workflow(self, session_id: str) -> dict:
        return self.active_workflows.get(session_id, {})

    def update_workflow_status(self, session_id: str, status: str):
        if session_id in self.active_workflows:
            self.active_workflows[session_id]["status"] = status

    def add_task_result(self, session_id: str, task_key: str, result: dict):
        if session_id in self.active_workflows:
            self.active_workflows[session_id]["task_results"][task_key] = result

    def complete_workflow(self, session_id: str):
        if session_id in self.active_workflows:
            self.active_workflows[session_id]["status"] = "completed"
            workflow = self.active_workflows[session_id]
            self.workflow_history.append(workflow)
            del self.active_workflows[session_id]