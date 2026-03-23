from app.agents.base import BaseAgent
from app.cot.base import COTLayerResult, COTResult
from app.cot.knowledge_base import knowledge_base
from typing import Dict, List, Any
import json
from app.llm.gateway import llm_gateway as gateway
from app.utils.logger import logger


class IntentUnderstandingAgent(BaseAgent):
    def __init__(self):
        super().__init__("IntentUnderstandingAgent")
        self.context: Dict[str, dict] = {}

    async def process(self, input_data: dict) -> dict:
        if self.enable_cot:
            return await self.process_with_cot(input_data)
        return await self._simple_process(input_data)

    async def process_with_cot(self, input_data: dict) -> dict:
        cot_result = COTResult(
            request_id=f"intent_{id(input_data)}",
            agent_name=self.name
        )

        try:
            layer1 = await self.intent_understanding_layer(input_data, cot_result)
            cot_result.layers.append(layer1)

            layer2 = await self.knowledge_retrieval_layer(layer1.output_data, cot_result)
            cot_result.layers.append(layer2)

            layer3 = await self.reasoning_decision_layer(layer2.output_data, cot_result)
            cot_result.layers.append(layer3)

            layer4 = await self.response_generation_layer(layer3.output_data, cot_result)
            cot_result.layers.append(layer4)

            cot_result.final_output = layer4.output_data
            cot_result.is_complete = True

            return {
                **layer4.output_data,
                "cot": cot_result.to_dict()
            }
        except Exception as e:
            self.logger.error(f"IntentUnderstandingAgent COT error: {e}")
            import traceback
            traceback.print_exc()
            fallback = await self._simple_process(input_data)
            fallback["cot_error"] = str(e)
            return fallback

    async def intent_understanding_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        session_id = input_data.get("session_id")
        message = input_data.get("message")

        if session_id not in self.context:
            self.context[session_id] = {
                "entities": {},
                "missing_fields": [],
                "intent_type": "trip_planning",
                "pending_questions": []
            }

        context = self.context[session_id]

        if input_data.get("answers"):
            context["entities"].update(input_data["answers"])
            result_data = await self._update_understanding_with_llm(session_id, context)
        else:
            result_data = await self._parse_intent_with_llm(message, context, context.get("pending_questions", []))

        reasoning_steps = [
            f"分析用户输入: {message}",
            f"识别意图类型: {result_data.get('intent_type', 'trip_planning')}",
            f"提取实体: {list(result_data.get('entities', {}).keys())}",
            f"识别缺失字段: {result_data.get('missing_fields', [])}"
        ]

        context["intent_type"] = result_data.get("intent_type", "trip_planning")
        context["entities"].update(result_data.get("entities", {}))
        context["missing_fields"] = result_data.get("missing_fields", [])
        context["questions"] = result_data.get("questions", [])
        context["pending_questions"] = result_data.get("questions", [])

        self.logger.info(f"[Context] After update: entities={context['entities']}, missing={context['missing_fields']}")

        return COTLayerResult(
            layer_name="intent_understanding",
            input_data={"message": message, "context": context},
            output_data={
                "intent_type": context["intent_type"],
                "entities": context["entities"],
                "missing_fields": context["missing_fields"],
                "questions": context["questions"]
            },
            reasoning_steps=reasoning_steps,
            confidence=0.9
        )

    async def knowledge_retrieval_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        entities = input_data.get("entities", {})
        missing_fields = input_data.get("missing_fields", [])

        # 提取实体的纯字符串值
        clean_entities = {}
        for k, v in entities.items():
            if isinstance(v, dict):
                clean_entities[k] = v.get('value', str(v))
            else:
                clean_entities[k] = v

        knowledge = knowledge_base.retrieve_relevant_knowledge(clean_entities, missing_fields)

        similar_cases = knowledge_base.get_similar_cases(clean_entities)

        reasoning_steps = [
            f"检索目的地城市等级: {knowledge.get('city_tier', '未知')}",
            f"检索职级对应规则: {list(knowledge.get('level_info', {}).keys())}",
            f"检索相关政策: {list(knowledge.get('policies', {}).keys())}",
            f"查找相似历史案例: {len(similar_cases)}个"
        ]

        return COTLayerResult(
            layer_name="knowledge_retrieval",
            input_data=input_data,
            output_data={
                "entities": entities,
                "missing_fields": missing_fields,
                "knowledge": knowledge,
                "similar_cases": similar_cases,
                "city_tier": knowledge.get("city_tier"),
                "level_info": knowledge.get("level_info"),
                "policies": knowledge.get("policies"),
                "suggestions": knowledge.get("suggestions", [])
            },
            reasoning_steps=reasoning_steps,
            confidence=0.95
        )

    async def reasoning_decision_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        entities = input_data.get("entities", {})
        missing_fields = input_data.get("missing_fields", [])
        knowledge = input_data.get("knowledge", {})
        questions = input_data.get("questions", [])

        # 提取实体的纯字符串值
        clean_entities = {}
        for k, v in entities.items():
            if isinstance(v, dict):
                clean_entities[k] = v.get('value', str(v))
            else:
                clean_entities[k] = v

        reasoning_steps = []

        info_completeness = self._evaluate_info_completeness(clean_entities, missing_fields)
        reasoning_steps.append(f"信息完整性评估：{info_completeness:.0%}")

        priority_questions = self._determine_question_priority(questions, missing_fields, clean_entities)
        reasoning_steps.append(f"追问优先级：{priority_questions}")

        conflict_detected = self._detect_conflicts(clean_entities)
        if conflict_detected:
            reasoning_steps.append(f"检测到冲突：{conflict_detected}")

        next_action = "ask_questions" if priority_questions else "proceed_to_planning"
        reasoning_steps.append(f"决定下一步行动：{next_action}")

        return COTLayerResult(
            layer_name="reasoning_decision",
            input_data=input_data,
            output_data={
                "entities": clean_entities,
                "missing_fields": missing_fields,
                "questions": questions,
                "info_completeness": info_completeness,
                "priority_questions": priority_questions,
                "conflicts": conflict_detected,
                "next_action": next_action,
                "confidence": 0.85
            },
            reasoning_steps=reasoning_steps,
            confidence=0.85
        )

    async def response_generation_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        entities = input_data.get("entities", {})
        missing_fields = input_data.get("missing_fields", [])
        questions = input_data.get("questions", [])

        reasoning = {}
        knowledge = {}
        if len(cot_result.layers) >= 3:
            reasoning = cot_result.layers[2].output_data
        if len(cot_result.layers) >= 2:
            layer2_output = cot_result.layers[1].output_data
            knowledge = layer2_output.get("knowledge", {})

        next_action = reasoning.get("next_action", "ask_questions") if isinstance(reasoning, dict) else "ask_questions"
        priority_questions = reasoning.get("priority_questions", []) if isinstance(reasoning, dict) else []

        if missing_fields and not priority_questions:
            priority_questions = self._determine_question_priority(questions, missing_fields, entities)

        basic_required_fields = ["departure", "destination", "start_date", "user_level", "purpose"]
        extra_required_fields = ["customer_location", "transport_preference", "hotel_needed", "hotel_requirements"]
        dining_required_fields = ["dining_date", "dining_location", "dietary_requirements", "dining_budget"]
        
        missing_basic = [f for f in basic_required_fields if not entities.get(f)]
        missing_extra = [f for f in extra_required_fields if not entities.get(f)]
        missing_dining = [f for f in dining_required_fields if not entities.get(f)]
        
        all_missing = list(set(missing_fields + missing_basic))
        all_missing.extend([f for f in missing_extra if f not in all_missing])
        
        dining_needed = entities.get("dining_needed")
        dining_is_yes = dining_needed and dining_needed not in ["否", "不需要", "no", "No", "不需要宴请"]
        
        if not dining_needed:
            if "dining_needed" not in all_missing:
                all_missing.append("dining_needed")
        elif dining_is_yes and missing_dining:
            all_missing.extend([f for f in missing_dining if f not in all_missing and f != "dining_needed"])
        
        field_display_names = {
            "user_level": "职级", 
            "departure": "出发地", 
            "destination": "目的地",
            "start_date": "出发日期", 
            "end_date": "返回日期", 
            "purpose": "出差目的",
            "headcount": "出差人数", 
            "hotel_needed": "是否需要住宿", 
            "transport_preference": "出行方式",
            "hotel_requirements": "住宿要求",
            "customer_location": "客户位置",
            "dining_needed": "是否涉及宴请",
            "dining_date": "宴请时间",
            "dining_location": "宴请地点",
            "dietary_requirements": "饮食要求",
            "dining_budget": "计划花费金额"
        }
        all_missing_cn = [field_display_names.get(f, f) for f in all_missing if f in field_display_names]

        if all_missing_cn:
            display_questions = priority_questions[:3] if priority_questions else [
                {"field": f, "question": self._get_default_question(f, entities), "options": None}
                for f in all_missing_cn[:3]
            ]
            response_text = self._generate_questions_response(display_questions, entities, knowledge)
            is_complete = False
        elif next_action == "ask_questions" and priority_questions:
            response_text = self._generate_questions_response(priority_questions, entities, knowledge)
            is_complete = False
        elif next_action == "proceed_to_planning":
            response_text = self._generate_confirmation_response(entities)
            is_complete = True
        elif questions:
            response_text = self._generate_questions_response(questions[:3], entities, knowledge)
            is_complete = False
        else:
            response_text = self._generate_confirmation_response(entities)
            is_complete = True

        reasoning_steps = [
            f"生成响应类型: {'追问' if priority_questions else '确认'}",
            f"包含问题数: {len(priority_questions) if priority_questions else 0}",
            f"响应长度: {len(response_text)}字符"
        ]

        return COTLayerResult(
            layer_name="response_generation",
            input_data=input_data,
            output_data={
                "response_text": response_text,
                "intent_type": entities.get("intent_type", "trip_planning"),
                "entities": entities,
                "missing_fields": all_missing_cn,
                "questions": priority_questions or questions[:3],
                "is_complete": is_complete,
                "status": "completed"
            },
            reasoning_steps=reasoning_steps,
            confidence=0.9
        )

    async def _retry_parse_with_llm(self, message: str, context: dict, pending_questions: list = None) -> dict:
        retry_prompt = f"""用户输入：{message}

请从上面的用户输入中提取出差相关的信息。即使信息不完整，也要尽力提取。

请直接返回一个简洁的JSON对象，格式如下：
{{
    "intent_type": "trip_planning",
    "entities": {{
        "departure": "出发城市（如果有）",
        "destination": "目的城市（如果有）",
        "start_date": "出发日期（如果有）",
        "user_level": "职级（如果有）",
        "purpose": "出差目的（如果有）"
    }},
    "missing_fields": ["还缺失的字段名"],
    "questions": [{{"field": "字段名", "question": "追问问题"}}]
}}

只返回JSON，不要有其他文字。"""

        try:
            messages = [
                {"role": "system", "content": "你是一个专业的商旅助手。请直接返回JSON格式的结果，不要有解释性文字。"},
                {"role": "user", "content": retry_prompt}
            ]
            
            response = await gateway.chat_no_stream(messages)
            
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group(0))
                
                allowed_fields = {
                    "departure", "destination", "start_date", "user_level", "purpose", "end_date", 
                    "headcount", "hotel_needed", "transport_preference", "customer_location",
                    "hotel_requirements", "dining_needed", "dining_date", "dining_location",
                    "dietary_requirements", "dining_budget"
                }
                entities = result.get("entities", {})
                filtered = {k: v for k, v in entities.items() if k in allowed_fields and v}
                
                missing = result.get("missing_fields", [])
                priority_fields = ["user_level", "departure", "destination", "start_date", "end_date", "purpose",
                                  "customer_location", "transport_preference", "hotel_needed", "hotel_requirements",
                                  "dining_needed", "dining_date", "dining_location", "dietary_requirements", "dining_budget"]
                questions = []
                for f in priority_fields:
                    if f not in filtered and f in missing:
                        questions.append({
                            "field": f,
                            "question": {
                                "user_level": "请问您的职级是？",
                                "departure": "请问您从哪里出发？",
                                "destination": "请问您要去哪个城市？",
                                "start_date": "请问您计划哪天出发？",
                                "end_date": "请问您计划哪天返回？",
                                "purpose": "请问您出差的主要目的是什么？",
                                "customer_location": "请问客户的具体位置在哪里？",
                                "transport_preference": "您偏好什么出行方式（飞机/火车）？",
                                "hotel_needed": "请问是否需要为您预订酒店？",
                                "hotel_requirements": "您对酒店有什么要求（星级/位置）？",
                                "dining_needed": "请问是否涉及宴请客户？",
                                "dining_date": "请问宴请安排在什么时间？",
                                "dining_location": "请问宴请地点在哪里？",
                                "dietary_requirements": "请问对饮食有什么要求（菜系/忌口）？",
                                "dining_budget": "请问您计划宴请的预算人均是多少？"
                            }.get(f, f"请提供您的{f}"),
                            "options": None
                        })
                
                self.logger.info(f"[Retry Parse] Successfully parsed entities: {filtered}")
                return {
                    "intent_type": result.get("intent_type", "trip_planning"),
                    "entities": filtered,
                    "missing_fields": [q["field"] for q in questions],
                    "questions": questions[:3],
                    "is_complete": len(questions) == 0
                }
        except Exception as e:
            self.logger.warning(f"[Retry Parse] Failed: {e}")
        
        return {}

    async def _parse_intent_with_llm(self, message: str, context: dict, pending_questions: list = None) -> dict:
        pending_questions = pending_questions or []
        entities = context.get("entities", {})
        existing_info = "\n".join([f"- {k}: {v}" for k, v in entities.items() if v]) if entities else "无"

        if pending_questions:
            pending_fields = [q.get("field", "") for q in pending_questions if isinstance(q, dict)]
            pending_desc = "\n".join([f"- {q.get('field')}: {q.get('question', '')}" for q in pending_questions if isinstance(q, dict)])

            prompt = f"""用户正在回答您之前提出的问题。

用户已提供的信息：
{existing_info}

您之前询问的字段：{pending_fields}
具体问题：
{pending_desc}

用户现在的回复：{message}

请分析用户的回复，提取相关信息来回答之前的问题。

请以JSON格式返回：
- intent_type: 意图类型
- entities: 从用户回复中提取的字段值（如果用户回答了之前的问题，请将这些字段填入entities）
- missing_fields: 仍然缺失的字段列表
- questions: 如果还有未回答的问题，继续追问（每轮最多3个）

注意：如果用户提到了"北京"、"上海"等城市，而这些城市能回答之前的问题（如出发地或目的地），请正确提取。"""

            system_prompt = """你是一个专业的商旅助手，擅长从用户的自然语言回复中提取信息。"""
        else:
            prompt = f"""你是一个专业的商旅助手，擅长分析用户的出差需求。

请分析用户的输入，进行以下推理：
1. 语义解析：提取用户消息中的实体
2. 意图分类：判断用户的意图类型
3. 信息提取：从用户消息中提取结构化信息
4. 完整性检查：与必填字段对比，识别缺失字段

用户输入：{message}

请以JSON格式返回，包含：
- intent_type: 意图类型 (trip_planning/invoice/mock_data/info_clarification)
- entities: 提取的实体信息，包含所有以下字段（如果用户在消息中提到了相关信息）：
  * departure: 出发城市或地点
  * destination: 目的城市或地点
  * start_date: 出发日期（如"4月1号"、"下周一"、"明天"等）
  * end_date: 返回日期
  * user_level: 职级（如"基层员工"、"经理"、"总监"等，直接用中文）
  * purpose: 出差目的
  * transport_preference: 出行方式偏好（如"飞机"、"火车"、"高铁"等）
  * customer_location: 客户的具体位置或地址
  * hotel_needed: 是否需要酒店（如"是"、"需要"、"否"、"不需要"）
  * hotel_requirements: 酒店要求（如"五星级"、"四星级"等）
  * dining_needed: 是否涉及宴请（如"是"、"需要"、"否"、"不需要"）
  * dining_date: 宴请日期
  * dining_location: 宴请地点
  * dining_budget: 宴请人均预算
  * dietary_requirements: 饮食要求或口味偏好
- missing_fields: 仍然缺失的字段列表（从以下字段中选择：departure, destination, start_date, end_date, user_level, purpose, transport_preference, customer_location, hotel_needed, hotel_requirements, dining_needed, dining_date, dining_location, dining_budget, dietary_requirements）
- questions: 需要追问的问题列表（每轮最多3个）

重要：如果用户提到了职级（如"经理"、"总监"、"基层员工"），请同时提取并放入user_level字段。
重要：如果用户提到出行方式（如"高铁"、"火车"、"飞机"），请同时提取并放入transport_preference字段。
重要：如果用户提到客户位置或地址，请提取到customer_location字段。
重要：如果用户提到"需要宴请"或"不需要宴请"，请提取到dining_needed字段。
重要：如果用户提到宴请相关（时间、地点、预算、口味），请提取到对应字段。"""

            system_prompt = "你是一个专业的商旅助手，擅长分析用户的出差需求。"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        try:
            response_content = await gateway.chat_no_stream(messages)
            import re
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```|`([\s\S]*?)`|\{[\s\S]*\}', response_content)
            if json_match:
                json_str = json_match.group(1) or json_match.group(2)
                if not json_str:
                    json_str = json_match.group(0)
                result_data = json.loads(json_str)
            else:
                result_data = json.loads(response_content)

            field_mapping = {
                "position_level": "user_level",
                "departure_date": "start_date",
                "return_date": "end_date",
                "destination_city": "destination",
                "departure_city": "departure",
                "level": "user_level",
                "start_time": "start_date",
                "end_time": "end_date",
                "departure_date_specific": "start_date",
                "hotel_required": "hotel_needed",
                "departure_time_preference": "transport_preference",
                "职级": "user_level",
                "级别": "user_level",
                "出发地点": "departure",
                "出发城市": "departure",
                "目的地城市": "destination",
                "目的地点": "destination",
                "出差目的": "purpose",
                "目的": "purpose",
                "出发日期": "start_date",
                "返回日期": "end_date",
                "返程日期": "end_date",
                "出差日期": "start_date",
                "人数": "headcount",
                "出差人数": "headcount",
                "需要住宿": "hotel_needed",
                "酒店要求": "hotel_requirements",
                "住宿要求": "hotel_requirements",
                "出行方式": "transport_preference",
                "交通方式": "transport_preference",
                "交通工具": "transport_preference",
                "客户地点": "customer_location",
                "客户地址": "customer_location",
                "宴请需求": "dining_needed",
                "是否宴请": "dining_needed",
                "需要宴请": "dining_needed",
                "宴请日期": "dining_date",
                "宴请时间": "dining_date",
                "宴请地点": "dining_location",
                "宴请场所": "dining_location",
                "饮食要求": "dietary_requirements",
                "口味要求": "dietary_requirements",
                "菜系要求": "dietary_requirements",
                "宴请预算": "dining_budget",
                "人均预算": "dining_budget",
                "预算金额": "dining_budget"
            }

            allowed_fields = {
                "departure", "destination", "start_date", "user_level", "purpose", 
                "end_date", "headcount", "hotel_needed", "transport_preference",
                "customer_location", "hotel_requirements",
                "dining_needed", "dining_date", "dining_location", 
                "dietary_requirements", "dining_budget"
            }

            user_level_mapping = {
                "基层": "基层员工", "普通员工": "基层员工", "员工": "基层员工",
                "主管": "主管/资深专员", "资深专员": "主管/资深专员", "专员": "主管/资深专员",
                "经理": "经理级", "经理级": "经理级",
                "总监": "总监级", "总监级": "总监级",
                "副总": "副总/高管", "高管": "副总/高管"
            }

            transport_mapping = {
                "飞机": "飞机", "航班": "飞机", "坐飞机": "飞机", "flight": "飞机",
                "火车": "火车", "高铁": "火车", "火车票": "火车", "train": "火车",
                "都行": "都行", "都可以": "都行", "无所谓": "都行"
            }

            yes_no_mapping = {
                "是": "是", "需要": "是", "要": "是", "好": "是", "需要住宿": "是",
                "不需要": "否", "不需要住宿": "否", "否": "否", "不用": "否", "no": "否"
            }

            entities = result_data.get("entities", {})
            filtered_entities = {}
            for old_field, new_field in list(field_mapping.items()):
                if old_field in entities:
                    value = entities[old_field]
                    if new_field == "user_level" and value in user_level_mapping:
                        value = user_level_mapping[value]
                    elif new_field == "transport_preference" and value in transport_mapping:
                        value = transport_mapping[value]
                    elif new_field in ["hotel_needed", "dining_needed"] and value in yes_no_mapping:
                        value = yes_no_mapping[value]
                    if new_field and new_field in allowed_fields:
                        filtered_entities[new_field] = value
            for k, v in entities.items():
                if k in allowed_fields:
                    value = v
                    if k == "user_level" and v in user_level_mapping:
                        value = user_level_mapping[v]
                    elif k == "transport_preference" and v in transport_mapping:
                        value = transport_mapping[v]
                    elif k in ["hotel_needed", "dining_needed"] and v in yes_no_mapping:
                        value = yes_no_mapping[v]
                    filtered_entities[k] = value
            entities = filtered_entities

            missing_fields = result_data.get("missing_fields", [])
            allowed_missing = {
                "departure", "destination", "start_date", "user_level", "purpose", "end_date", 
                "headcount", "hotel_needed", "transport_preference", "customer_location", 
                "hotel_requirements", "dining_needed", "dining_date", "dining_location",
                "dietary_requirements", "dining_budget",
                "职级", "出发地", "目的地", "出发日期", "返回日期", "出差目的", "出差人数", 
                "是否需要住宿", "出行偏好", "客户位置", "住宿要求", "是否涉及宴请",
                "宴请时间", "宴请地点", "饮食要求", "计划花费金额"
            }
            display_names = {
                "user_level": "职级", "departure": "出发地", "destination": "目的地",
                "start_date": "出发日期", "end_date": "返回日期", "purpose": "出差目的",
                "headcount": "出差人数", "hotel_needed": "是否需要住宿", 
                "transport_preference": "出行方式", "customer_location": "客户位置",
                "hotel_requirements": "住宿要求", "dining_needed": "是否涉及宴请",
                "dining_date": "宴请时间", "dining_location": "宴请地点",
                "dietary_requirements": "饮食要求", "dining_budget": "计划花费金额"
            }
            mapped_missing = []
            for f in missing_fields:
                if f in allowed_missing:
                    mapped_missing.append(display_names.get(f, f))

            result_data["missing_fields"] = mapped_missing
            result_data["entities"] = entities
            self.logger.info(f"[LLM Parse] Raw response length: {len(response_content)}, Parsed entities: {result_data.get('entities', {})}")

            if not entities and pending_questions:
                self.logger.info(f"[LLM Parse] Entities empty, using fallback extraction")
                raise Exception("LLM returned empty entities, using fallback")
        except (json.JSONDecodeError, Exception) as e:
            self.logger.warning(f"LLM parse failed: {e}, response: {response_content[:200] if response_content else 'empty'}")
            
            retry_result = await self._retry_parse_with_llm(message, context, pending_questions)
            if retry_result and retry_result.get("entities"):
                return retry_result
            
            extracted_entities = {}
            remaining_questions = []

            self.logger.warning(f"[Intent] LLM解析失败，使用基于上下文的通用响应")
            
            existing = context.get("entities", {})
            
            all_fields = ["user_level", "departure", "destination", "start_date", "end_date", "purpose"]
            for f in all_fields:
                if f not in existing or not existing[f]:
                    remaining_questions.append({
                        "field": f,
                        "question": {
                            "user_level": "请问您的职级是？",
                            "departure": "请问您从哪个城市出发？",
                            "destination": "请问您的目的地是哪个城市？",
                            "start_date": "请问您计划什么时候出发？",
                            "end_date": "请问您计划什么时候返回？",
                            "purpose": "请问出差的主要目的是？"
                        }.get(f, f"请提供您的{f}"),
                        "options": None
                    })

            result_data = {
                "intent_type": "trip_planning",
                "entities": extracted_entities if extracted_entities else {},
                "missing_fields": [q["field"] for q in remaining_questions] if remaining_questions else [],
                "questions": remaining_questions[:3]
            }

        missing = result_data.get("missing_fields", [])
        if missing:
            missing_keys = {q.get("field") for q in result_data.get("questions", []) if isinstance(q, dict)}
            priority_fields = ["user_level", "departure", "destination", "start_date"]
            for field in priority_fields:
                if field in missing and field not in missing_keys:
                    questions_map = {
                        "departure": "请问您从哪里出发？",
                        "destination": "请问您要去哪个城市？",
                        "start_date": "请问您计划哪天出发？",
                        "end_date": "请问您计划哪天返回？",
                        "user_level": "请问您的职级是？",
                        "headcount": "请问有几人出差？",
                        "purpose": "请问出差的主要目的是？"
                    }
                    result_data.setdefault("questions", []).append({
                        "field": field,
                        "question": questions_map.get(field, f"请提供您的{field}"),
                        "options": None
                    })
            result_data["questions"] = result_data["questions"][:3]

        return result_data

    async def _update_understanding_with_llm(self, session_id: str, context: dict) -> dict:
        answers_text = "\n".join([f"{k}: {v}" for k, v in context["entities"].items()])

        prompt = f"""用户已提供以下信息：
{answers_text}

请分析这些信息，更新用户的出差需求，并检查是否还有缺失字段需要追问。

请以JSON格式返回：
- intent_type: 意图类型
- entities: 更新后的实体信息
- missing_fields: 仍然缺失的字段
- questions: 仍然需要追问的问题（每轮最多3个）"""

        messages = [
            {"role": "system", "content": "你是一个专业的商旅助手。"},
            {"role": "user", "content": prompt}
        ]

        try:
            response_content = await gateway.chat_no_stream(messages)
            result_data = json.loads(response_content)
        except (json.JSONDecodeError, Exception) as e:
            self.logger.warning(f"LLM update failed, using fallback: {e}")
            result_data = {
                "entities": context["entities"],
                "missing_fields": [],
                "questions": []
            }

        missing = result_data.get("missing_fields", [])
        if missing:
            missing_keys = {q.get("field") for q in result_data.get("questions", []) if isinstance(q, dict)}
            priority_fields = ["user_level", "departure", "destination", "start_date"]
            for field in priority_fields:
                if field in missing and field not in missing_keys:
                    questions_map = {
                        "departure": "请问您从哪里出发？",
                        "destination": "请问您要去哪个城市？",
                        "start_date": "请问您计划哪天出发？",
                        "end_date": "请问您计划哪天返回？",
                        "user_level": "请问您的职级是？",
                        "headcount": "请问有几人出差？",
                        "purpose": "请问出差的主要目的是？"
                    }
                    result_data.setdefault("questions", []).append({
                        "field": field,
                        "question": questions_map.get(field, f"请提供您的{field}"),
                        "options": None
                    })
            result_data["questions"] = result_data["questions"][:3]

        return result_data

    async def _simple_process(self, input_data: dict) -> dict:
        session_id = input_data.get("session_id")
        message = input_data.get("message")

        if session_id not in self.context:
            self.context[session_id] = {
                "entities": {},
                "missing_fields": [],
                "intent_type": "trip_planning"
            }

        context = self.context[session_id]

        if input_data.get("answers"):
            context["entities"].update(input_data["answers"])
            result = await self._update_understanding_with_llm(session_id, context)
        else:
            result = await self._parse_intent_with_llm(message, context)

        context["intent_type"] = result.get("intent_type", "trip_planning")
        context["entities"].update(result.get("entities", {}))
        context["missing_fields"] = result.get("missing_fields", [])
        context["questions"] = result.get("questions", [])

        missing_fields = context["missing_fields"]
        questions = context["questions"]

        if questions:
            response_text = self._generate_questions_response(questions, context["entities"], {})
        else:
            response_text = self._generate_confirmation_response(context["entities"])

        return {
            "intent_type": context["intent_type"],
            "entities": context["entities"],
            "missing_fields": missing_fields,
            "questions": questions,
            "response_text": response_text,
            "is_complete": len(missing_fields) == 0,
            "status": "completed"
        }

    def _evaluate_info_completeness(self, entities: dict, missing_fields: List[str]) -> float:
        required_fields = ["departure", "destination", "start_date", "user_level"]
        filled_count = sum(1 for f in required_fields if f in entities and entities[f])
        return filled_count / len(required_fields)

    def _determine_question_priority(
        self,
        questions: List[dict],
        missing_fields: List[str],
        entities: dict
    ) -> List[dict]:
        priority_fields = [
            "user_level", "departure", "destination", "purpose", 
            "start_date", "end_date", "transport_preference",
            "customer_location", "hotel_needed", "hotel_requirements"
        ]
        
        dining_needed = entities.get("dining_needed", True)
        if dining_needed:
            priority_fields.extend(["dining_date", "dining_location", "dietary_requirements", "dining_budget"])

        priority_questions = []
        for field in priority_fields:
            if field in missing_fields:
                question_text = self._get_default_question(field, entities)
                priority_questions.append({
                    "field": field,
                    "question": question_text,
                    "options": self._get_field_options(field)
                })

        for q in questions[:3]:
            if isinstance(q, dict) and q.get("field") not in [pq["field"] for pq in priority_questions]:
                priority_questions.append(q)

        return priority_questions[:5]

    def _get_default_question(self, field: str, entities: dict) -> str:
        questions_map = {
            "user_level": "请问您的职级是？",
            "departure": "请问您从哪个城市出发？",
            "destination": "请问您的目的地是哪个城市？",
            "purpose": "请问您出差的主要目的是什么？",
            "start_date": "请问您计划什么时候出发？",
            "end_date": "请问您计划什么时候返回？",
            "transport_preference": "您偏好哪种出行方式（飞机/火车）？",
            "hotel_requirements": "您对酒店有什么要求（星级/位置/价格）？",
            "hotel_needed": "请问是否需要为您预订酒店？",
            "headcount": "请问有几人出差？",
            "return_date": "请问您计划什么时候返回？",
            "具体出发日期": "请问您具体哪天出发？",
            "是否需要住宿": "请问是否需要为您预订酒店？",
            "出行时间偏好": "您偏好什么时间出发（上午/下午/晚上）？",
            "customer_location": "请问客户的具体位置在哪里？",
            "dining_needed": "请问此次出差是否涉及宴请客户？",
            "dining_date": "请问宴请安排在什么时间？",
            "dining_location": "请问宴请地点在哪里？",
            "dietary_requirements": "请问对饮食有什么要求（菜系/忌口等）？",
            "dining_budget": "请问您计划宴请的预算人均是多少？"
        }
        return questions_map.get(field, f"请提供您的{field}")

    def _get_field_options(self, field: str) -> List[str]:
        options_map = {
            "user_level": ["基层员工", "主管/资深专员", "经理级", "总监级", "副总/高管"],
            "transport_preference": ["飞机", "火车", "高铁", "都行"],
            "hotel_requirements": ["经济型", "三星级", "四星级", "五星级", "豪华型", "都行"],
            "hotel_needed": ["是", "否"],
            "dining_needed": ["是", "否"],
            "dietary_requirements": ["川菜", "粤菜", "湘菜", "鲁菜", "江浙菜", "西餐", "日料", "韩餐", "无特殊要求"]
        }
        return options_map.get(field, [])

    def _detect_conflicts(self, entities: dict) -> List[str]:
        conflicts = []

        if entities.get("start_date") and entities.get("end_date"):
            try:
                start = entities.get("start_date")
                end = entities.get("end_date")
                if start and end and start > end:
                    conflicts.append("出发日期晚于返回日期")
            except (TypeError, ValueError):
                pass

        return conflicts

    def _generate_questions_response(
        self,
        questions: List[dict],
        entities: dict,
        knowledge: dict
    ) -> str:
        if not questions:
            return "请问还有什么需要补充的信息吗？"

        response = "为了更好地为您规划行程，请补充以下信息：\n\n"
        for i, q in enumerate(questions, 1):
            field = q.get("field", "")
            question_text = q.get("question", f"请提供您的{field}")
            options = q.get("options", [])

            response += f"{i}. {question_text}\n"
            if options:
                response += f"   可选：{', '.join(options)}\n"

        if knowledge.get("city_tier"):
            city = entities.get("destination", "")
            tier = knowledge["city_tier"]
            response += f"\n💡 提示：{city}属于{tier}城市，对应的住宿和餐饮标准有所不同。"

        return response

    def _generate_confirmation_response(self, entities: dict) -> str:
        departure = entities.get("departure", "未知")
        destination = entities.get("destination", "未知")
        start_date = entities.get("start_date", "待定")
        end_date = entities.get("end_date", "待定")
        purpose = entities.get("purpose", "商务出差")

        return f"""✅ 已了解您的出差需求：

📍 行程：{departure} → {destination}
📅 时间：{start_date} 至 {end_date}
🎯 目的：{purpose}

正在为您搜索合适的出行方案..."""

    def get_context(self, session_id: str) -> dict:
        return self.context.get(session_id, {})

    def clear_context(self, session_id: str):
        if session_id in self.context:
            del self.context[session_id]