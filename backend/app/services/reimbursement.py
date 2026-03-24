from typing import Optional, Dict, Any, List
from enum import Enum
import uuid
from datetime import datetime
from app.utils.logger import logger


class ReimbursementStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVING = "approving"
    APPROVED = "approved"
    REJECTED = "rejected"
    REIMBURSED = "reimbursed"
    CANCELLED = "cancelled"


class ReimbursementType(str, Enum):
    TRANSPORT = "transport"
    HOTEL = "hotel"
    DINING = "dining"
    OTHER = "other"
    MIXED = "mixed"


class ReimbursementService:
    def __init__(self):
        self._reimbursements: Dict[str, dict] = {}

    def create_reimbursement(self, user_info: dict, items: List[dict], expense_type: ReimbursementType = None) -> dict:
        reimbursement_id = f"REIMB-{uuid.uuid4().hex[:12].upper()}"

        total_amount = sum(item.get("amount", 0) for item in items)

        reimbursement_data = {
            "reimbursement_id": reimbursement_id,
            "type": expense_type or ReimbursementType.MIXED if len(items) > 1 else (items[0].get("type", ReimbursementType.OTHER) if items else ReimbursementType.OTHER),
            "user": user_info,
            "items": items,
            "total_amount": total_amount,
            "status": ReimbursementStatus.DRAFT,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "submitted_at": None,
            "approved_at": None,
            "reimbursed_at": None,
            "approval_history": [],
            "remarks": None
        }

        self._reimbursements[reimbursement_id] = reimbursement_data
        logger.info(f"Created reimbursement draft: {reimbursement_id}, total: {total_amount}")
        return reimbursement_data

    def add_invoice_to_reimbursement(self, reimbursement_id: str, invoice_data: dict) -> dict:
        reimbursement = self._reimbursements.get(reimbursement_id)
        if not reimbursement:
            return {"status": "error", "message": f"Reimbursement {reimbursement_id} not found"}

        if reimbursement["status"] not in [ReimbursementStatus.DRAFT, ReimbursementStatus.REJECTED]:
            return {"status": "error", "message": f"Cannot modify reimbursement in status {reimbursement['status']}"}

        invoice_item = {
            "invoice_id": invoice_data.get("invoice_id", f"INV-{uuid.uuid4().hex[:8].upper()}"),
            "invoice_code": invoice_data.get("invoice_code"),
            "invoice_number": invoice_data.get("invoice_number"),
            "invoice_date": invoice_data.get("invoice_date"),
            "buyer_name": invoice_data.get("buyer_name"),
            "seller_name": invoice_data.get("seller_name"),
            "amount": invoice_data.get("amount"),
            "tax_amount": invoice_data.get("tax_amount"),
            "total_amount": invoice_data.get("total_amount"),
            "invoice_type": invoice_data.get("invoice_type"),
            "added_at": datetime.now().isoformat()
        }

        reimbursement["items"].append(invoice_item)
        reimbursement["total_amount"] = sum(item.get("total_amount", 0) for item in reimbursement["items"])
        reimbursement["updated_at"] = datetime.now().isoformat()

        logger.info(f"Added invoice {invoice_item['invoice_id']} to reimbursement {reimbursement_id}")
        return reimbursement

    def submit_reimbursement(self, reimbursement_id: str, approval_chain: List[str] = None) -> dict:
        reimbursement = self._reimbursements.get(reimbursement_id)
        if not reimbursement:
            return {"status": "error", "message": f"Reimbursement {reimbursement_id} not found"}

        if reimbursement["status"] != ReimbursementStatus.DRAFT:
            return {"status": "error", "message": f"Cannot submit reimbursement in status {reimbursement['status']}"}

        if not reimbursement["items"]:
            return {"status": "error", "message": "Cannot submit reimbursement without items"}

        default_approval_chain = approval_chain or ["直属主管"]
        reimbursement["status"] = ReimbursementStatus.PENDING
        reimbursement["submitted_at"] = datetime.now().isoformat()
        reimbursement["updated_at"] = datetime.now().isoformat()
        reimbursement["approval_chain"] = default_approval_chain
        reimbursement["approval_history"].append({
            "action": "submitted",
            "timestamp": datetime.now().isoformat(),
            "from_status": ReimbursementStatus.DRAFT,
            "to_status": ReimbursementStatus.PENDING
        })

        logger.info(f"Submitted reimbursement {reimbursement_id} for approval")
        return reimbursement

    def approve_reimbursement(self, reimbursement_id: str, approver: str, comments: str = None) -> dict:
        reimbursement = self._reimbursements.get(reimbursement_id)
        if not reimbursement:
            return {"status": "error", "message": f"Reimbursement {reimbursement_id} not found"}

        if reimbursement["status"] not in [ReimbursementStatus.PENDING, ReimbursementStatus.APPROVING]:
            return {"status": "error", "message": f"Cannot approve reimbursement in status {reimbursement['status']}"}

        reimbursement["status"] = ReimbursementStatus.APPROVED
        reimbursement["approved_at"] = datetime.now().isoformat()
        reimbursement["updated_at"] = datetime.now().isoformat()
        reimbursement["approved_by"] = approver
        reimbursement["approval_comments"] = comments
        reimbursement["approval_history"].append({
            "action": "approved",
            "timestamp": datetime.now().isoformat(),
            "approver": approver,
            "comments": comments
        })

        logger.info(f"Reimbursement {reimbursement_id} approved by {approver}")
        return reimbursement

    def reject_reimbursement(self, reimbursement_id: str, rejector: str, reason: str) -> dict:
        reimbursement = self._reimbursements.get(reimbursement_id)
        if not reimbursement:
            return {"status": "error", "message": f"Reimbursement {reimbursement_id} not found"}

        if reimbursement["status"] not in [ReimbursementStatus.PENDING, ReimbursementStatus.APPROVING]:
            return {"status": "error", "message": f"Cannot reject reimbursement in status {reimbursement['status']}"}

        reimbursement["status"] = ReimbursementStatus.REJECTED
        reimbursement["updated_at"] = datetime.now().isoformat()
        reimbursement["rejected_by"] = rejector
        reimbursement["rejection_reason"] = reason
        reimbursement["approval_history"].append({
            "action": "rejected",
            "timestamp": datetime.now().isoformat(),
            "rejector": rejector,
            "reason": reason
        })

        logger.info(f"Reimbursement {reimbursement_id} rejected by {rejector}: {reason}")
        return reimbursement

    def mark_reimbursed(self, reimbursement_id: str, payment_info: dict = None) -> dict:
        reimbursement = self._reimbursements.get(reimbursement_id)
        if not reimbursement:
            return {"status": "error", "message": f"Reimbursement {reimbursement_id} not found"}

        if reimbursement["status"] != ReimbursementStatus.APPROVED:
            return {"status": "error", "message": f"Cannot mark as reimbursed in status {reimbursement['status']}"}

        reimbursement["status"] = ReimbursementStatus.REIMBURSED
        reimbursement["reimbursed_at"] = datetime.now().isoformat()
        reimbursement["updated_at"] = datetime.now().isoformat()
        if payment_info:
            reimbursement["payment_info"] = payment_info
        reimbursement["approval_history"].append({
            "action": "reimbursed",
            "timestamp": datetime.now().isoformat(),
            "payment_reference": payment_info.get("reference") if payment_info else None
        })

        logger.info(f"Reimbursement {reimbursement_id} marked as reimbursed")
        return reimbursement

    def cancel_reimbursement(self, reimbursement_id: str, reason: str = None) -> dict:
        reimbursement = self._reimbursements.get(reimbursement_id)
        if not reimbursement:
            return {"status": "error", "message": f"Reimbursement {reimbursement_id} not found"}

        if reimbursement["status"] in [ReimbursementStatus.REIMBURSED, ReimbursementStatus.CANCELLED]:
            return {"status": "error", "message": f"Cannot cancel reimbursement in status {reimbursement['status']}"}

        old_status = reimbursement["status"]
        reimbursement["status"] = ReimbursementStatus.CANCELLED
        reimbursement["updated_at"] = datetime.now().isoformat()
        reimbursement["cancellation_reason"] = reason
        reimbursement["approval_history"].append({
            "action": "cancelled",
            "timestamp": datetime.now().isoformat(),
            "from_status": old_status,
            "reason": reason
        })

        logger.info(f"Reimbursement {reimbursement_id} cancelled: {reason}")
        return reimbursement

    def get_reimbursement(self, reimbursement_id: str) -> Optional[dict]:
        return self._reimbursements.get(reimbursement_id)

    def list_reimbursements(
        self,
        status: ReimbursementStatus = None,
        user_id: str = None,
        expense_type: ReimbursementType = None
    ) -> List[dict]:
        results = []
        for reimb in self._reimbursements.values():
            if status and reimb["status"] != status:
                continue
            if user_id and reimb["user", {}].get("user_id") != user_id:
                continue
            if expense_type and reimb["type"] != expense_type:
                continue
            results.append(reimb)
        return results

    def generate_reimbursement_form(self, reimbursement_id: str) -> dict:
        reimbursement = self._reimbursements.get(reimbursement_id)
        if not reimbursement:
            return {"status": "error", "message": f"Reimbursement {reimbursement_id} not found"}

        form_data = {
            "form_id": f"FORM-{reimbursement_id}",
            "reimbursement_id": reimbursement_id,
            "applicant": {
                "name": reimbursement["user"].get("name", "未知"),
                "department": reimbursement["user"].get("department", "未知"),
                "position": reimbursement["user"].get("position", "未知"),
                "employee_id": reimbursement["user"].get("employee_id", "未知")
            },
            "expense_summary": {
                "type": reimbursement["type"],
                "total_amount": reimbursement["total_amount"],
                "item_count": len(reimbursement["items"]),
                "items": reimbursement["items"]
            },
            "timeline": {
                "created_at": reimbursement["created_at"],
                "submitted_at": reimbursement.get("submitted_at"),
                "approved_at": reimbursement.get("approved_at"),
                "reimbursed_at": reimbursement.get("reimbursed_at")
            },
            "status": reimbursement["status"],
            "approval_chain": reimbursement.get("approval_chain", []),
            "remarks": reimbursement.get("remarks")
        }

        return form_data


reimbursement_service = ReimbursementService()
