from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import uuid
import json
from app.api.types import ApiResponse
from app.utils.logger import logger

router = APIRouter(prefix="/api/invoice", tags=["invoice"])


class InvoiceConfirmRequest(BaseModel):
    invoice_id: str
    fields: dict


@router.post("/upload")
async def upload_invoice(files: list[UploadFile] = File(...)):
    try:
        results = []

        for file in files:
            invoice_id = f"invoice_{uuid.uuid4().hex[:8]}"

            results.append({
                "invoice_id": invoice_id,
                "status": "recognized",
                "fields": {
                    "invoice_code": "144031900110",
                    "invoice_number": "NO.12345678",
                    "invoice_date": "2026-03-15",
                    "buyer_name": "示例公司",
                    "seller_name": "XX酒店",
                    "total_amount": 3150.0,
                    "tax_rate": 0.06
                },
                "confidence": {
                    "invoice_code": 0.95,
                    "invoice_number": 0.92,
                    "invoice_date": 0.98,
                    "buyer_name": 0.90,
                    "seller_name": 0.88,
                    "total_amount": 0.96,
                    "tax_rate": 0.94
                },
                "low_confidence_fields": []
            })

        return ApiResponse(
            code=0,
            message="success",
            data=results
        )
    except Exception as e:
        logger.error(f"Invoice upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/confirm")
async def confirm_invoice(request: InvoiceConfirmRequest):
    try:
        return ApiResponse(
            code=0,
            message="success",
            data={"invoice_id": request.invoice_id, "status": "confirmed"}
        )
    except Exception as e:
        logger.error(f"Invoice confirm error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{invoice_id}")
async def get_invoice(invoice_id: str):
    try:
        invoice_data = {
            "invoice_id": invoice_id,
            "status": "recognized",
            "fields": {
                "invoice_code": "144031900110",
                "invoice_number": "NO.12345678",
                "invoice_date": "2026-03-15",
                "buyer_name": "示例公司",
                "seller_name": "XX酒店",
                "total_amount": 3150.0,
                "tax_rate": 0.06
            },
            "confidence": {
                "invoice_code": 0.95,
                "invoice_number": 0.92,
                "invoice_date": 0.98,
                "buyer_name": 0.90,
                "seller_name": 0.88,
                "total_amount": 0.96,
                "tax_rate": 0.94
            },
            "low_confidence_fields": []
        }

        return ApiResponse(
            code=0,
            message="success",
            data=invoice_data
        )
    except Exception as e:
        logger.error(f"Invoice get error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
