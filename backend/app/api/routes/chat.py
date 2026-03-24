from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
import asyncio
import uuid
import json
from datetime import datetime
from typing import Optional
from app.api.types import (
    ApiResponse, ChatSendRequest, ChatMessage,
    IntentParseRequest, IntentData, Entities, Question,
    ClarifyRequest
)
from app.llm.gateway import llm_gateway as gateway
from app.agents.intent import IntentUnderstandingAgent
from app.agents.transportation import TransportationAgent
from app.agents.hotel import HotelAgent
from app.agents.dining import DiningAgent
from app.agents.compliance import ComplianceAgent
from app.agents.approval import ApprovalAgent
from app.services.session_manager import session_manager
from app.utils.logger import logger

router = APIRouter(prefix="/api/chat", tags=["chat"])

intent_agent = IntentUnderstandingAgent()
transport_agent = TransportationAgent()
hotel_agent = HotelAgent()
dining_agent = DiningAgent()
compliance_agent = ComplianceAgent()
approval_agent = ApprovalAgent()


def get_current_time_info() -> str:
    now = datetime.now()
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday = weekdays[now.weekday()]
    date_str = now.strftime("%Y年%m月%d日")
    time_str = now.strftime("%H:%M:%S")
    return f"当前时间：{date_str} {weekday} {time_str}"


def build_system_prompt(time_info: str) -> str:
    return f"""你是一个智能商旅助手，帮助用户规划出差行程、预订酒店、安排宴请等。{time_info}"""


def build_stream_system_prompt(time_info: str) -> str:
    return f"""你是一个智能商旅助手，帮助用户规划出差行程。{time_info}"""


@router.post("/send")
async def send_message(request: ChatSendRequest):
    try:
        session_id = request.session_id
        user_message = request.message

        time_info = get_current_time_info()
        system_content = build_system_prompt(time_info)

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_message}
        ]

        response_content = await gateway.chat_no_stream(messages)

        response_msg = ChatMessage(
            message_id=str(uuid.uuid4()),
            role="assistant",
            content=response_content,
            agent_id="intent",
            card_type=None
        )

        return ApiResponse(
            code=0,
            message="success",
            data=response_msg.model_dump()
        )
    except Exception as e:
        logger.error(f"Chat send error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def stream_message(request: ChatSendRequest):
    async def event_generator():
        try:
            session_id = request.session_id or str(uuid.uuid4())
            user_message = request.message

            if session_manager.has_active_selection(session_id):
                planning_results = session_manager.get_planning_results(session_id)
                selection_options = session_manager.get_selection_options(session_id)
                
                if planning_results and selection_options:
                    selected = session_manager.parse_user_selection(user_message, selection_options)
                    
                    session_manager.update_session(session_id, awaiting_selection=False)
                    
                    approval_text = "正在根据您的选择生成审批单...\n\n"
                    for char in approval_text:
                        yield {"event": "message", "data": json.dumps({"content": char})}
                        await asyncio.sleep(0.02)
                    
                    session_state = session_manager.get_session(session_id)
                    intent_data = session_state.intent_data if session_state else {}
                    transport_result = planning_results.get("transport")
                    hotel_result = planning_results.get("hotel")
                    dining_result = planning_results.get("dining")
                    
                    approval_input = {
                        "trip_data": {
                            "departure": intent_data.get("departure"),
                            "destination": intent_data.get("destination"),
                            "start_date": intent_data.get("start_date"),
                            "end_date": intent_data.get("end_date"),
                            "purpose": intent_data.get("purpose"),
                            "user_level": intent_data.get("user_level")
                        },
                        "transport": transport_result,
                        "hotel": hotel_result,
                        "dining": dining_result,
                        "selections": selected
                    }
                    
                    approval_result = await approval_agent.process(approval_input)
                    
                    if approval_result:
                        approval_content = approval_result.get("approval_content", "")
                        html_content = approval_result.get("html", "")
                        
                        summary_text = "✅ 审批单已生成！\n\n"
                        summary_text += f"📄 审批单内容预览：\n"
                        summary_text += f"{approval_content[:500]}...\n\n" if len(approval_content) > 500 else f"{approval_content}\n\n"
                        summary_text += "审批单已保存，您可以查看详情或提交审批。\n"
                        
                        for char in summary_text:
                            yield {"event": "message", "data": json.dumps({"content": char})}
                            await asyncio.sleep(0.02)
                        
                        yield {"event": "message_end", "data": json.dumps({
                            "type": "end",
                            "content": summary_text,
                            "is_complete": True,
                            "approval_generated": True,
                            "approval_data": {
                                "approval_id": approval_result.get("approval_id"),
                                "content": approval_content,
                                "html": html_content[:200] if html_content else ""
                            }
                        })}
                        return

            intent_result = await intent_agent.process({
                "session_id": session_id,
                "message": user_message
            })

            response_text = intent_result.get("response_text", "")
            missing_fields = intent_result.get("missing_fields", [])
            questions = intent_result.get("questions", [])
            is_complete = intent_result.get("is_complete", False)
            entities = intent_result.get("entities", {})

            if not is_complete and (missing_fields or questions):
                if response_text:
                    for char in response_text:
                        yield {"event": "message", "data": json.dumps({"content": char})}
                        await asyncio.sleep(0.02)
                    yield {"event": "message_end", "data": json.dumps({
                        "type": "end",
                        "content": response_text,
                        "is_complete": is_complete,
                        "missing_fields": missing_fields,
                        "questions": questions,
                        "intent_data": entities
                    })}
                else:
                    follow_up_text = "为了更好地为您规划行程，请补充以下信息：\n\n"
                    for i, q in enumerate(questions[:3], 1):
                        question_text = q.get("question", "请补充信息")
                        follow_up_text += f"{i}. {question_text}\n"
                    
                    for char in follow_up_text:
                        yield {"event": "message", "data": json.dumps({"content": char})}
                        await asyncio.sleep(0.02)
                    yield {"event": "message_end", "data": json.dumps({
                        "type": "end",
                        "content": follow_up_text,
                        "is_complete": False,
                        "missing_fields": missing_fields,
                        "questions": questions,
                        "intent_data": entities
                    })}
                return

            await asyncio.sleep(0.1)
            yield {"event": "message_start", "data": json.dumps({"type": "start"})}

            if is_complete or not missing_fields:
                planning_text = "正在为您规划行程...\n\n"
                for char in planning_text:
                    yield {"event": "message", "data": json.dumps({"content": char})}
                    await asyncio.sleep(0.02)

                transport_result = await transport_agent.process({
                    "departure": entities.get("departure"),
                    "destination": entities.get("destination"),
                    "date": entities.get("start_date"),
                    "user_level": entities.get("user_level", "基层员工"),
                    "type": entities.get("transport_preference", "both")
                })

                hotel_result = await hotel_agent.process({
                    "city": entities.get("destination"),
                    "check_in": entities.get("start_date"),
                    "check_out": entities.get("end_date"),
                    "user_level": entities.get("user_level", "基层员工"),
                    "customer_location": entities.get("customer_location", "")
                })

                dining_result = None
                if entities.get("dining_needed"):
                    dining_result = await dining_agent.process({
                        "city": entities.get("destination"),
                        "date": entities.get("dining_date"),
                        "headcount": entities.get("headcount", 1),
                        "budget": entities.get("dining_budget"),
                        "user_level": entities.get("user_level", "基层员工")
                    })

                approval_input = {
                    "trip_data": {
                        "departure": entities.get("departure"),
                        "destination": entities.get("destination"),
                        "start_date": entities.get("start_date"),
                        "end_date": entities.get("end_date"),
                        "purpose": entities.get("purpose"),
                        "user_level": entities.get("user_level")
                    },
                    "transport": transport_result,
                    "hotel": hotel_result,
                    "dining": dining_result
                }
                approval_result = await approval_agent.process(approval_input)

                summary_text = f"✅ 行程规划完成！\n\n"
                summary_text += f"📍 行程：{entities.get('departure', '待定')} → {entities.get('destination', '待定')}\n"
                summary_text += f"📅 时间：{entities.get('start_date', '待定')} 至 {entities.get('end_date', '待定')}\n"
                summary_text += f"🎯 目的：{entities.get('purpose', '商务出差')}\n\n"

                transport_selection_options = []
                if transport_result:
                    transport_options = transport_result.get("recommendations", [])
                    if transport_options:
                        summary_text += "✈️ 交通方案：\n"
                        for idx, opt in enumerate(transport_options[:3], 1):
                            opt_data = opt.get("option", {})
                            category = opt.get("category", "")
                            reason = opt.get("reason", "")
                            transport_selection_options.append({
                                "type": "transport",
                                "index": idx,
                                "id": opt_data.get("id", f"transport_{idx}"),
                                "description": f"{opt_data.get('provider', '')} {opt_data.get('flight_no', opt_data.get('train_no', ''))}"
                            })
                            summary_text += f"  {idx}. [{category}] {opt_data.get('provider', '')} {opt_data.get('flight_no', opt_data.get('train_no', ''))}: {opt_data.get('departure', {}).get('city', '')} → {opt_data.get('arrival', {}).get('city', '')}, 价格: ¥{opt_data.get('price', 0)}, {reason}\n"
                        summary_text += "\n"

                hotel_selection_options = []
                if hotel_result:
                    compliant_hotels = hotel_result.get("compliant_hotels", [])
                    alternative_hotels = hotel_result.get("alternative_hotels", [])
                    budget_limit = hotel_result.get("budget_limit", 0)
                    
                    if compliant_hotels or alternative_hotels:
                        summary_text += "🏨 酒店方案：\n"
                        hotel_idx = 1
                        if compliant_hotels:
                            summary_text += f"  [合规方案 - 预算¥{budget_limit}/晚以内]\n"
                            for opt in compliant_hotels[:3]:
                                hotel_selection_options.append({
                                    "type": "hotel",
                                    "index": hotel_idx,
                                    "id": opt.get("id", f"hotel_{hotel_idx}"),
                                    "name": opt.get("name", ""),
                                    "description": f"{opt.get('name', '')} ({opt.get('stars', '')}星)"
                                })
                                summary_text += f"  {hotel_idx}. {opt.get('name', '')} ({opt.get('stars', '')}星): ¥{opt.get('price', 0)}/晚, 距客户位置 {opt.get('distance_km', 0)}km\n"
                                summary_text += f"    设施: {', '.join(opt.get('facilities', [])[:3])}\n"
                                hotel_idx += 1
                        if alternative_hotels:
                            summary_text += f"  [替代方案 - 豪华型酒店]\n"
                            for opt in alternative_hotels[:3]:
                                hotel_selection_options.append({
                                    "type": "hotel",
                                    "index": hotel_idx,
                                    "id": opt.get("id", f"hotel_{hotel_idx}"),
                                    "name": opt.get("name", ""),
                                    "description": f"{opt.get('name', '')} ({opt.get('stars', '')}星) - 位置较远"
                                })
                                summary_text += f"  {hotel_idx}. {opt.get('name', '')} ({opt.get('stars', '')}星): ¥{opt.get('price', 0)}/晚, 距客户位置 {opt.get('distance_km', 0)}km\n"
                                summary_text += f"    交通: {opt.get('transport_info', '待确认')}\n"
                                hotel_idx += 1
                        summary_text += "\n"

                dining_selection_options = []
                dining_result = None
                dining_needed = entities.get("dining_needed")
                if dining_needed and dining_needed != "否":
                    dining_result = await dining_agent.process({
                        "city": entities.get("destination"),
                        "date": entities.get("dining_date"),
                        "headcount": entities.get("headcount", 1),
                        "cuisine": entities.get("dietary_requirements"),
                        "budget_per_person": entities.get("dining_budget"),
                        "user_level": entities.get("user_level", "基层员工")
                    })
                    
                if dining_result:
                    compliant_restaurants = dining_result.get("compliant_restaurants", [])
                    over_budget_restaurants = dining_result.get("over_budget_restaurants", [])
                    dining_limit = dining_result.get("dining_limit", 0)
                    is_over_budget = dining_result.get("is_over_budget", False)
                    
                    if compliant_restaurants or over_budget_restaurants:
                        summary_text += "🍽️ 宴请方案：\n"
                        dining_idx = 1
                        if is_over_budget:
                            summary_text += f"  [超标提示] 您的预算超出差标上限¥{dining_limit}/人\n"
                        if compliant_restaurants:
                            summary_text += f"  [合规方案 - 预算¥{dining_limit}/人以内]\n"
                            for opt in compliant_restaurants[:3]:
                                dining_selection_options.append({
                                    "type": "dining",
                                    "index": dining_idx,
                                    "id": opt.get("id", f"dining_{dining_idx}"),
                                    "name": opt.get("restaurant", ""),
                                    "description": f"{opt.get('restaurant', '')} - 人均¥{opt.get('price_per_person', 0)}"
                                })
                                summary_text += f"  {dining_idx}. {opt.get('restaurant', '')}: 人均¥{opt.get('price_per_person', 0)}, 总计¥{opt.get('total_amount', 0)}\n"
                                dishes = opt.get('suggested_dishes', [])
                                if dishes:
                                    summary_text += f"    推荐菜品: {', '.join(dishes[:3])}\n"
                                dining_idx += 1
                        if over_budget_restaurants:
                            summary_text += f"  [替代方案 - 符合您预算要求]\n"
                            for opt in over_budget_restaurants[:3]:
                                dining_selection_options.append({
                                    "type": "dining",
                                    "index": dining_idx,
                                    "id": opt.get("id", f"dining_{dining_idx}"),
                                    "name": opt.get("restaurant", ""),
                                    "description": f"{opt.get('restaurant', '')} - 人均¥{opt.get('price_per_person', 0)}"
                                })
                                summary_text += f"  {dining_idx}. {opt.get('restaurant', '')}: 人均¥{opt.get('price_per_person', 0)}, 总计¥{opt.get('total_amount', 0)}\n"
                                dishes = opt.get('suggested_dishes', [])
                                if dishes:
                                    summary_text += f"    推荐菜品: {', '.join(dishes[:3])}\n"
                                dining_idx += 1

                summary_text += "\n请确认您的选择（交通、酒店、宴请），我会为您生成审批单。\n"
                summary_text += "例如：请选择方案1、2、3"

                session_manager.create_session(session_id)
                session_manager.update_session(
                    session_id,
                    intent_data=entities,
                    planning_results={
                        "transport": transport_result,
                        "hotel": hotel_result,
                        "dining": dining_result
                    },
                    selection_options={
                        "transport": transport_selection_options,
                        "hotel": hotel_selection_options,
                        "dining": dining_selection_options
                    },
                    awaiting_selection=True
                )

                for char in summary_text:
                    yield {"event": "message", "data": json.dumps({"content": char})}
                    await asyncio.sleep(0.02)

                yield {"event": "message_end", "data": json.dumps({
                    "type": "end",
                    "content": summary_text,
                    "is_complete": True,
                    "missing_fields": [],
                    "questions": [],
                    "intent_data": entities,
                    "awaiting_selection": True,
                    "selection_options": {
                        "transport": transport_selection_options,
                        "hotel": hotel_selection_options,
                        "dining": dining_selection_options
                    },
                    "planning_results": {
                        "transport": transport_result,
                        "hotel": hotel_result,
                        "dining": dining_result
                    }
                })}
            else:
                default_text = "我已了解您的需求，正在为您准备行程规划..."
                if response_text:
                    for char in response_text:
                        yield {"event": "message", "data": json.dumps({"content": char})}
                        await asyncio.sleep(0.02)
                else:
                    for char in default_text:
                        yield {"event": "message", "data": json.dumps({"content": char})}
                        await asyncio.sleep(0.02)

                yield {"event": "message_end", "data": json.dumps({
                    "type": "end",
                    "content": response_text or default_text,
                    "is_complete": is_complete,
                    "missing_fields": missing_fields,
                    "questions": questions,
                    "intent_data": entities
                })}

        except Exception as e:
            logger.error(f"Stream error: {str(e)}")
            import traceback
            traceback.print_exc()
            error_text = f"处理您的请求时出现错误：{str(e)}"
            for char in error_text:
                yield {"event": "message", "data": json.dumps({"content": char})}
                await asyncio.sleep(0.02)
            yield {"event": "message_end", "data": json.dumps({
                "type": "end",
                "content": error_text,
                "is_complete": False,
                "error": str(e)
            })}

    return EventSourceResponse(event_generator())


@router.post("/intent/parse")
async def parse_intent(request: IntentParseRequest):
    try:
        session_id = request.session_id
        user_message = request.message

        intent_prompt = f"""请分析用户的出差需求，提取以下信息：
- 出发地 (departure)
- 目的地 (destination)
- 出发日期 (start_date)
- 返回日期 (end_date)
- 出差人数 (headcount)
- 用户职级 (user_level)
- 出差目的 (purpose)

用户输入: {user_message}

请以JSON格式返回，包含：
- intent_type: 意图类型 (trip_planning/invoice/mock_data)
- entities: 提取的实体信息
- missing_fields: 缺失字段列表
- questions: 需要追问的问题列表（每轮最多3个）"""

        messages = [
            {"role": "system", "content": "你是一个专业的商旅助手，擅长分析用户的出差需求。"},
            {"role": "user", "content": intent_prompt}
        ]

        response_content = await gateway.chat_no_stream(messages)

        try:
            result_data = json.loads(response_content)
        except json.JSONDecodeError:
            result_data = {
                "intent_type": "trip_planning",
                "entities": {
                    "departure": None,
                    "destination": None,
                    "start_date": None,
                    "end_date": None,
                    "headcount": None,
                    "user_level": None,
                    "purpose": user_message
                },
                "missing_fields": ["departure", "destination", "start_date", "user_level"],
                "questions": [
                    {"field": "departure", "question": "请问您从哪个城市出发？", "options": None},
                    {"field": "destination", "question": "请问您要去哪个城市？", "options": None},
                    {"field": "start_date", "question": "请问您计划哪天出发？", "options": None}
                ]
            }

        entities = Entities(**result_data.get("entities", {}))
        questions = [Question(**q) for q in result_data.get("questions", [])]
        missing_fields = result_data.get("missing_fields", [])

        intent_data = IntentData(
            intent_type=result_data.get("intent_type", "trip_planning"),
            entities=entities,
            missing_fields=missing_fields,
            questions=questions
        )

        return ApiResponse(
            code=0,
            message="success",
            data=intent_data.model_dump()
        )
    except Exception as e:
        logger.error(f"Intent parse error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/intent/clarify")
async def clarify_intent(request: ClarifyRequest):
    try:
        session_id = request.session_id
        answers = request.answers

        answers_text = "\n".join([f"{k}: {v}" for k, v in answers.items()])

        clarification_prompt = f"""用户已回答了以下问题：
{answers_text}

请分析这些回答，更新用户的出差信息，并检查是否还有缺失字段需要追问。

请以JSON格式返回：
- entities: 更新后的实体信息
- missing_fields: 仍然缺失的字段
- questions: 仍然需要追问的问题（每轮最多3个）"""

        messages = [
            {"role": "system", "content": "你是一个专业的商旅助手。"},
            {"role": "user", "content": clarification_prompt}
        ]

        response_content = await gateway.chat_no_stream(messages)

        try:
            result_data = json.loads(response_content)
        except json.JSONDecodeError:
            result_data = {
                "entities": {k: v for k, v in answers.items()},
                "missing_fields": [],
                "questions": []
            }

        entities = Entities(**result_data.get("entities", {}))
        questions = [Question(**q) for q in result_data.get("questions", [])]

        intent_data = IntentData(
            intent_type="trip_planning",
            entities=entities,
            missing_fields=result_data.get("missing_fields", []),
            questions=questions
        )

        return ApiResponse(
            code=0,
            message="success",
            data=intent_data.model_dump()
        )
    except Exception as e:
        logger.error(f"Clarify error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


class SelectionConfirmRequest(BaseModel):
    session_id: Optional[str] = None
    transport_selection: Optional[dict] = None
    hotel_selection: Optional[dict] = None
    dining_selection: Optional[dict] = None
    trip_data: Optional[dict] = None


@router.post("/selection/confirm")
async def confirm_selection(request: SelectionConfirmRequest):
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        trip_data = request.trip_data or {}
        
        transport_data = None
        if request.transport_selection:
            transport_data = request.transport_selection.get("option", {})
        
        hotel_data = None
        if request.hotel_selection:
            hotel_data = request.hotel_selection
        
        dining_data = None
        if request.dining_selection:
            dining_data = request.dining_selection
        
        approval_input = {
            "trip_data": {
                "departure": trip_data.get("departure"),
                "destination": trip_data.get("destination"),
                "start_date": trip_data.get("start_date"),
                "end_date": trip_data.get("end_date"),
                "purpose": trip_data.get("purpose"),
                "user_level": trip_data.get("user_level")
            },
            "transport": transport_data,
            "hotel": hotel_data,
            "dining": dining_data
        }
        
        approval_result = await approval_agent.process(approval_input)
        
        return ApiResponse(
            code=0,
            message="success",
            data={
                "status": "completed",
                "approval_form": approval_result.get("approval_form", {}),
                "total_cost": approval_result.get("total_cost", 0),
                "html": approval_result.get("html", ""),
                "pdf_size": approval_result.get("pdf_size", 0)
            }
        )
    except Exception as e:
        logger.error(f"Selection confirm error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
