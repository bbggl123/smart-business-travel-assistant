from app.llm.gateway import llm_gateway as gateway
from app.utils.logger import logger
import json


class COTPromptEngine:
    @staticmethod
    def get_intent_understanding_prompt(user_message: str, context: dict = None) -> str:
        context_str = ""
        if context:
            context_str = f"\n当前上下文：\n{json.dumps(context, ensure_ascii=False)}"

        return f"""你是一个专业的商旅助手，擅长分析用户的出差需求。

请分析用户的输入，进行以下推理：

1. 语义解析：提取用户消息中的实体（出发地、目的地、时间、人数、职级等）
2. 意图分类：判断用户的意图类型
   - trip_planning: 行程规划
   - invoice: 发票处理
   - mock_data: Mock数据生成
   - info_clarification: 信息确认
3. 信息提取：从用户消息中提取结构化信息
4. 完整性检查：与必填字段对比，识别缺失字段

用户输入：{user_message}{context_str}

请以JSON格式返回，包含：
- intent_type: 意图类型
- entities: 提取的实体信息
- missing_fields: 缺失字段列表
- questions: 需要追问的问题列表（每轮最多3个，每个问题包含field、question、options）

确保推理过程清晰，输出结果准确。"""

    @staticmethod
    def get_knowledge_retrieval_prompt(entities: dict, missing_fields: list) -> str:
        return f"""根据已提取的实体信息和缺失字段，检索相关知识：

已提取的信息：
{json.dumps(entities, ensure_ascii=False, indent=2)}

需要追问的字段：
{json.dumps(missing_fields, ensure_ascii=False, indent=2)}

请检索以下相关知识：
1. 公司差旅政策中关于职级的规定
2. 各城市的住宿和餐饮标准
3. 交通方式的选择建议
4. 历史出差案例参考

请返回检索到的相关知识要点，以便后续推理使用。"""

    @staticmethod
    def get_reasoning_decision_prompt(entities: dict, knowledge: dict, questions: list) -> str:
        return f"""基于已提取的实体信息、检索到的知识和已生成的追问，进行多步推理：

实体信息：
{json.dumps(entities, ensure_ascii=False, indent=2)}

相关知识：
{json.dumps(knowledge, ensure_ascii=False, indent=2)}

已生成的追问：
{json.dumps(questions, ensure_ascii=False, indent=2)}

请进行以下推理：
1. 验证已有信息的完整性和一致性
2. 评估信息缺失对后续规划的影响
3. 确定最佳的追问策略（哪些问题优先问）
4. 识别可能的冲突或歧义
5. 制定下一步行动计划

请返回推理结果，包括：
- 信息验证结果
- 冲突检测结果（如有）
- 推荐的追问顺序
- 行动计划"""

    @staticmethod
    def get_response_generation_prompt(intent_type: str, entities: dict, questions: list, reasoning: dict) -> str:
        return f"""基于之前的推理结果，生成最终响应：

意图类型：{intent_type}

实体信息：
{json.dumps(entities, ensure_ascii=False, indent=2)}

追问问题：
{json.dumps(questions, ensure_ascii=False, indent=2)}

推理结果：
{json.dumps(reasoning, ensure_ascii=False, indent=2)}

请生成自然语言响应：
1. 如果有追问问题：友好地询问用户缺失信息
2. 如果信息完整：确认理解并告知下一步操作
3. 如果有冲突：说明冲突并请求用户澄清
4. 如果是确认操作：给出清晰的确认信息

确保响应：
- 友好、专业、易于理解
- 符合商旅助手的角色定位
- 引导用户完成必要的输入"""


class COTEngine:
    def __init__(self, enable_debug: bool = False):
        self.enable_debug = enable_debug
        self.prompt_engine = COTPromptEngine()

    async def execute_layer(
        self,
        layer_name: str,
        layer_func,
        input_data: dict,
        context: dict = None
    ) -> dict:
        try:
            result = await layer_func(input_data, context)
            if self.enable_debug:
                logger.info(f"[COT] Layer '{layer_name}' executed successfully")
            return result
        except Exception as e:
            logger.error(f"[COT] Layer '{layer_name}' error: {e}")
            return {"error": str(e), "layer": layer_name}

    async def run_full_cot(
        self,
        user_message: str,
        context: dict = None,
        intent_func=None,
        knowledge_func=None,
        reasoning_func=None,
        response_func=None
    ) -> dict:
        layers_result = {}

        if intent_func:
            intent_prompt = self.prompt_engine.get_intent_understanding_prompt(user_message, context)
            intent_result = await intent_func(intent_prompt)
            layers_result["intent_understanding"] = intent_result

        if knowledge_func and intent_func:
            try:
                entities = json.loads(intent_result) if isinstance(intent_result, str) else intent_result
                knowledge_prompt = self.prompt_engine.get_knowledge_retrieval_prompt(
                    entities.get("entities", {}),
                    entities.get("missing_fields", [])
                )
                knowledge_result = await knowledge_func(knowledge_prompt)
                layers_result["knowledge_retrieval"] = knowledge_result
            except Exception as e:
                logger.error(f"[COT] Knowledge retrieval error: {e}")
                layers_result["knowledge_retrieval"] = {"error": str(e)}

        if reasoning_func and intent_func:
            try:
                entities = json.loads(intent_result) if isinstance(intent_result, str) else intent_result
                knowledge = layers_result.get("knowledge_retrieval", {})
                reasoning_prompt = self.prompt_engine.get_reasoning_decision_prompt(
                    entities.get("entities", {}),
                    knowledge,
                    entities.get("questions", [])
                )
                reasoning_result = await reasoning_func(reasoning_prompt)
                layers_result["reasoning_decision"] = reasoning_result
            except Exception as e:
                logger.error(f"[COT] Reasoning error: {e}")
                layers_result["reasoning_decision"] = {"error": str(e)}

        if response_func and intent_func:
            try:
                entities = json.loads(intent_result) if isinstance(intent_result, str) else intent_result
                reasoning = layers_result.get("reasoning_decision", {})
                response_prompt = self.prompt_engine.get_response_generation_prompt(
                    entities.get("intent_type", "trip_planning"),
                    entities.get("entities", {}),
                    entities.get("questions", []),
                    reasoning
                )
                response_result = await response_func(response_prompt)
                layers_result["response_generation"] = response_result
            except Exception as e:
                logger.error(f"[COT] Response generation error: {e}")
                layers_result["response_generation"] = {"error": str(e)}

        return layers_result
