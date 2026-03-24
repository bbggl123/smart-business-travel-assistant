from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.api.types import ApiResponse
from app.services.reimbursement import reimbursement_service, ReimbursementStatus, ReimbursementType
from app.utils.logger import logger

router = APIRouter(prefix="/api/reimbursement", tags=["reimbursement"])


class CreateReimbursementRequest(BaseModel):
    user_info: dict
    items: List[dict]
    expense_type: Optional[str] = None


class SubmitReimbursementRequest(BaseModel):
    reimbursement_id: str
    approval_chain: Optional[List[str]] = None


class ApproveReimbursementRequest(BaseModel):
    reimbursement_id: str
    approver: str
    comments: Optional[str] = None


class RejectReimbursementRequest(BaseModel):
    reimbursement_id: str
    rejector: str
    reason: str


class MarkReimbursedRequest(BaseModel):
    reimbursement_id: str
    payment_reference: Optional[str] = None


class AddInvoiceRequest(BaseModel):
    reimbursement_id: str
    invoice_data: dict


@router.post("/create")
async def create_reimbursement(request: CreateReimbursementRequest):
    try:
        expense_type = ReimbursementType(request.expense_type) if request.expense_type else None
        result = reimbursement_service.create_reimbursement(
            user_info=request.user_info,
            items=request.items,
            expense_type=expense_type
        )
        return ApiResponse(code=0, message="success", data=result)
    except Exception as e:
        logger.error(f"Create reimbursement error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit")
async def submit_reimbursement(request: SubmitReimbursementRequest):
    try:
        result = reimbursement_service.submit_reimbursement(
            reimbursement_id=request.reimbursement_id,
            approval_chain=request.approval_chain
        )
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
        return ApiResponse(code=0, message="success", data=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Submit reimbursement error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve")
async def approve_reimbursement(request: ApproveReimbursementRequest):
    try:
        result = reimbursement_service.approve_reimbursement(
            reimbursement_id=request.reimbursement_id,
            approver=request.approver,
            comments=request.comments
        )
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
        return ApiResponse(code=0, message="success", data=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Approve reimbursement error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reject")
async def reject_reimbursement(request: RejectReimbursementRequest):
    try:
        result = reimbursement_service.reject_reimbursement(
            reimbursement_id=request.reimbursement_id,
            rejector=request.rejector,
            reason=request.reason
        )
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
        return ApiResponse(code=0, message="success", data=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reject reimbursement error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reimburse")
async def mark_reimbursed(request: MarkReimbursedRequest):
    try:
        payment_info = {"reference": request.payment_reference} if request.payment_reference else None
        result = reimbursement_service.mark_reimbursed(
            reimbursement_id=request.reimbursement_id,
            payment_info=payment_info
        )
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
        return ApiResponse(code=0, message="success", data=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mark reimbursed error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cancel")
async def cancel_reimbursement(reimbursement_id: str, reason: Optional[str] = None):
    try:
        result = reimbursement_service.cancel_reimbursement(
            reimbursement_id=reimbursement_id,
            reason=reason
        )
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
        return ApiResponse(code=0, message="success", data=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cancel reimbursement error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{reimbursement_id}")
async def get_reimbursement(reimbursement_id: str):
    try:
        result = reimbursement_service.get_reimbursement(reimbursement_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"Reimbursement {reimbursement_id} not found")
        return ApiResponse(code=0, message="success", data=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get reimbursement error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_reimbursements(
    status: Optional[str] = None,
    user_id: Optional[str] = None,
    expense_type: Optional[str] = None
):
    try:
        status_enum = ReimbursementStatus(status) if status else None
        type_enum = ReimbursementType(expense_type) if expense_type else None
        results = reimbursement_service.list_reimbursements(
            status=status_enum,
            user_id=user_id,
            expense_type=type_enum
        )
        return ApiResponse(code=0, message="success", data=results)
    except Exception as e:
        logger.error(f"List reimbursements error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{reimbursement_id}/form")
async def get_reimbursement_form(reimbursement_id: str):
    try:
        result = reimbursement_service.generate_reimbursement_form(reimbursement_id)
        if result.get("status") == "error":
            raise HTTPException(status_code=404, detail=result.get("message"))
        return ApiResponse(code=0, message="success", data=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get reimbursement form error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add-invoice")
async def add_invoice_to_reimbursement(request: AddInvoiceRequest):
    try:
        result = reimbursement_service.add_invoice_to_reimbursement(
            reimbursement_id=request.reimbursement_id,
            invoice_data=request.invoice_data
        )
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
        return ApiResponse(code=0, message="success", data=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add invoice error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
