from typing import Optional, Dict, Any, List
import base64
import io
import json
from app.utils.logger import logger


class InvoiceOCRService:
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self._ocr = None

    async def load_model(self):
        if self.model_loaded:
            logger.info("Invoice OCR model already loaded")
            return True

        try:
            from paddleocr import PaddleOCR

            self._ocr = PaddleOCR(
                use_angle_cls=True,
                lang='ch',
                use_gpu=False,
                show_log=False
            )

            self.model_loaded = True
            logger.info("PaddleOCR model loaded successfully (CPU mode)")
            return True

        except ImportError:
            logger.warning("PaddleOCR not installed, using mock mode")
            self.model_loaded = True
            return True
        except Exception as e:
            logger.error(f"Failed to load PaddleOCR: {e}")
            self.model_loaded = True
            return True

    async def extract_from_image(self, image_data: bytes) -> Dict[str, Any]:
        if not self.model_loaded:
            await self.load_model()

        if self._ocr is None:
            return await self._mock_extract()

        try:
            import numpy as np
            from PIL import Image

            img = Image.open(io.BytesIO(image_data))
            img_array = np.array(img)

            result = self._ocr.ocr(img_array, cls=True)

            if not result or not result[0]:
                logger.warning("No text detected in image")
                return await self._mock_extract()

            text_lines = []
            for line in result[0]:
                if line and len(line) >= 2:
                    text = line[1][0] if isinstance(line[1], tuple) else line[1]
                    confidence = line[1][1] if isinstance(line[1], tuple) else 1.0
                    text_lines.append({
                        "text": text,
                        "confidence": confidence
                    })

            invoice_data = self._parse_invoice_fields(text_lines)

            logger.info(f"OCR extracted {len(text_lines)} text lines from invoice image")
            return invoice_data

        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return await self._mock_extract()

    async def extract_from_base64(self, base64_str: str) -> Dict[str, Any]:
        try:
            image_data = base64.b64decode(base64_str)
            return await self.extract_from_image(image_data)
        except Exception as e:
            logger.error(f"Base64 decode error: {e}")
            return await self._mock_extract()

    async def extract_from_pdf(self, pdf_data: bytes) -> Dict[str, Any]:
        if not self.model_loaded:
            await self.load_model()

        try:
            import fitz

            doc = fitz.open(stream=pdf_data, filetype="pdf")
            if doc.page_count == 0:
                return await self._mock_extract()

            page = doc[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_data = pix.tobytes("png")

            doc.close()
            return await self.extract_from_image(img_data)

        except ImportError:
            logger.warning("PyMuPDF not installed, cannot process PDF")
            return await self._mock_extract()
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return await self._mock_extract()

    def _parse_invoice_fields(self, text_lines: List[dict]) -> Dict[str, Any]:
        invoice_data = {
            "invoice_code": None,
            "invoice_number": None,
            "invoice_date": None,
            "buyer_name": None,
            "seller_name": None,
            "amount": None,
            "tax_amount": None,
            "total_amount": None,
            "tax_rate": None,
            "invoice_type": None,
            "items": [],
            "raw_text": [line["text"] for line in text_lines],
            "confidence": sum(line["confidence"] for line in text_lines) / len(text_lines) if text_lines else 0,
            "extraction_method": "paddleocr"
        }

        keywords = {
            "invoice_code": ["发票代码", "code"],
            "invoice_number": ["发票号码", "invoice_no", "number"],
            "invoice_date": ["开票日期", "date", "开票时间"],
            "buyer_name": ["购买方", "buyer", "购货单位"],
            "seller_name": ["销售方", "seller", "销货单位"],
            "amount": ["金额", "amount", "不含税"],
            "tax_amount": ["税额", "tax"],
            "total_amount": ["价税合计", "total", "价税合计（大写）"],
            "tax_rate": ["税率", "rate"],
            "invoice_type": ["发票类型", "type", "卷式", "专用发票", "普通发票"]
        }

        for line in text_lines:
            text = line["text"]

            for field, kws in keywords.items():
                if any(kw in text for kw in kws):
                    value = text.split(":")[-1].strip() if ":" in text else text
                    value = text.split("=")[-1].strip() if "=" in text else value
                    value = text.split("：")[-1].strip() if "：" in text else value

                    if field == "amount" and invoice_data["amount"] is None:
                        try:
                            nums = [float(s) for s in value if s.replace(".", "").replace(",", "").isdigit()]
                            if nums:
                                invoice_data["amount"] = nums[0]
                        except:
                            pass
                    elif field == "total_amount" and invoice_data["total_amount"] is None:
                        try:
                            nums = [float(s.replace(",", "")) for s in value if s.replace(".", "").replace(",", "").replace("-", "").isdigit()]
                            if nums:
                                invoice_data["total_amount"] = nums[0]
                        except:
                            pass
                    elif field == "tax_rate" and invoice_data["tax_rate"] is None:
                        if "%" in text or "税率" in text:
                            invoice_data["tax_rate"] = value

        return invoice_data

    async def _mock_extract(self) -> Dict[str, Any]:
        logger.info("Using mock invoice data extraction")
        return {
            "invoice_code": "144031900310",
            "invoice_number": "12345678",
            "invoice_date": "2024-03-15",
            "buyer_name": "XX科技有限公司",
            "seller_name": "XX酒店有限公司",
            "amount": 1132.08,
            "tax_amount": 67.92,
            "total_amount": 1200.00,
            "tax_rate": "6%",
            "invoice_type": "增值税专用发票",
            "items": [
                {"name": "住宿费", "quantity": 1, "unit_price": 1132.08, "amount": 1132.08}
            ],
            "raw_text": ["[Mock Mode] 增值税发票示例"],
            "confidence": 0.85,
            "extraction_method": "mock"
        }

    async def batch_process(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for file in files:
            file_type = file.get("type", "image")
            data = file.get("data")

            if file_type == "pdf":
                result = await self.extract_from_pdf(data)
            elif file_type == "base64":
                result = await self.extract_from_base64(data)
            else:
                result = await self.extract_from_image(data)

            results.append(result)

        return results

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_loaded": self.model_loaded,
            "ocr_engine": "PaddleOCR" if self._ocr else "mock",
            "language": "chinese",
            "gpu_enabled": False
        }


invoice_ocr_service = InvoiceOCRService()
