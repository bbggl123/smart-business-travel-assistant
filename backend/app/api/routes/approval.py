from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import uuid
import json
from app.api.types import ApiResponse
from app.utils.logger import logger

router = APIRouter(prefix="/api/approval", tags=["approval"])


class ApprovalGenerateRequest(BaseModel):
    trip_id: str


class ApprovalData(BaseModel):
    id: str
    trip_id: str
    employee: dict
    trip: dict
    items: list
    total_amount: float
    status: str
    created_at: str


@router.post("/generate")
async def generate_approval(request: ApprovalGenerateRequest):
    try:
        approval_id = f"approval_{uuid.uuid4().hex[:8]}"

        approval_data = {
            "approval_id": approval_id,
            "employee": {
                "name": "张三",
                "level": "经理级",
                "department": "销售部"
            },
            "trip": {
                "purpose": "客户拜访",
                "destination": "上海",
                "departure": "北京",
                "start_date": "2026-04-01",
                "end_date": "2026-04-03",
                "transport_type": "高铁"
            },
            "items": [
                {
                    "category": "交通",
                    "name": "G201 高铁",
                    "amount": 553.0,
                    "is_compliant": True,
                    "limit": 553.0
                },
                {
                    "category": "住宿",
                    "name": "上海金茂君悦大酒店",
                    "amount": 3150.0,
                    "is_compliant": True,
                    "limit": 3900.0
                },
                {
                    "category": "餐饮",
                    "name": "宴请客户（3人）",
                    "amount": 660.0,
                    "is_compliant": True,
                    "limit": 900.0
                }
            ],
            "total_amount": 4363.0,
            "status": "draft",
            "created_at": "2026-03-22"
        }

        return ApiResponse(
            code=0,
            message="success",
            data=approval_data
        )
    except Exception as e:
        logger.error(f"Approval generate error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{approval_id}")
async def get_approval(approval_id: str):
    try:
        approval_data = {
            "approval_id": approval_id,
            "employee": {
                "name": "张三",
                "level": "经理级",
                "department": "销售部"
            },
            "trip": {
                "purpose": "客户拜访",
                "destination": "上海",
                "departure": "北京",
                "start_date": "2026-04-01",
                "end_date": "2026-04-03",
                "transport_type": "高铁"
            },
            "items": [
                {
                    "category": "交通",
                    "name": "G201 高铁",
                    "amount": 553.0,
                    "is_compliant": True,
                    "limit": 553.0
                },
                {
                    "category": "住宿",
                    "name": "上海金茂君悦大酒店",
                    "amount": 3150.0,
                    "is_compliant": True,
                    "limit": 3900.0
                },
                {
                    "category": "餐饮",
                    "name": "宴请客户（3人）",
                    "amount": 660.0,
                    "is_compliant": True,
                    "limit": 900.0
                }
            ],
            "total_amount": 4363.0,
            "status": "pending",
            "created_at": "2026-03-22"
        }

        return ApiResponse(
            code=0,
            message="success",
            data=approval_data
        )
    except Exception as e:
        logger.error(f"Approval get error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{approval_id}/pdf")
async def export_approval_pdf(approval_id: str):
    try:
        html_content = f"""
        <html>
        <head><meta charset="UTF-8"><title>审批单 {approval_id}</title></head>
        <body>
        <h1>差旅审批单</h1>
        <p>审批单号: {approval_id}</p>
        <p>员工: 张三</p>
        <p>部门: 销售部</p>
        <p>职级: 经理级</p>
        <p>出差目的: 客户拜访</p>
        <p>目的地: 上海</p>
        <p>出发日期: 2026-04-01</p>
        <p>返回日期: 2026-04-03</p>
        <h2>费用明细</h2>
        <table border="1">
            <tr><th>类别</th><th>项目</th><th>金额</th><th>是否合规</th></tr>
            <tr><td>交通</td><td>G201 高铁</td><td>¥553.0</td><td>是</td></tr>
            <tr><td>住宿</td><td>上海金茂君悦大酒店</td><td>¥3150.0</td><td>是</td></tr>
            <tr><td>餐饮</td><td>宴请客户（3人）</td><td>¥660.0</td><td>是</td></tr>
        </table>
        <h2>总计: ¥4363.0</h2>
        </body>
        </html>
        """

        async def generate():
            yield html_content

        return StreamingResponse(
            generate(),
            media_type="text/html",
            headers={
                "Content-Disposition": f"attachment; filename=approval_{approval_id}.html"
            }
        )
    except Exception as e:
        logger.error(f"Approval PDF export error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
