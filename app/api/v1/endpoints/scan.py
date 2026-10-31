from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime, timezone, timedelta
from app.workers.tasks import run_full_document_scan, celery_app, plagiarism_engine
from app.engines.ai_detector import DeepForensicAcademicAIDetector
from app.engines.source_verifier import AcademicSourceVerificationEngine
from app.utils.extractor import extract_document

router = APIRouter()
ai_detector = DeepForensicAcademicAIDetector()
source_verifier = AcademicSourceVerificationEngine()

# Bộ định thời gian chuẩn múi giờ Việt Nam (Asia/Ho_Chi_Minh - UTC+7)
VN_TZ = timezone(timedelta(hours=7))

class ScanSubmissionRequest(BaseModel):
    content: str = Field(..., min_length=20, description="Nội dung văn bản cần kiểm tra")

def analyze_document_content(
    text: str, 
    filename: Optional[str] = None, 
    rendered_html: Optional[str] = None,
    structural_audit: Optional[Dict[str, Any]] = None
):
    # 1. Chạy giám định pháp y học thuật trên 100% tài liệu từ đầu đến cuối
    ai_result = ai_detector.analyze_full_document(text)
    
    # 2. So khớp Đạo văn với kho tài liệu đối sánh học thuật (MinHash LSH)
    candidate_doc_ids = plagiarism_engine.query_similar(text)
    matches = []
    top_similarity = 0.0
    
    for cand_id, cand_text in plagiarism_engine.corpus_storage.items():
        sim, matched_sents = plagiarism_engine.calculate_sentence_overlap(text, cand_text)
        if sim > 0:
            matches.append({
                "doc_id": cand_id,
                "similarity_score": round(sim * 100, 1),
                "overlap_sentences": matched_sents
            })
            if sim > top_similarity:
                top_similarity = sim

    plag_percentage = round(top_similarity * 100, 1)
    
    # 3. Tính chỉ số Độ thuần Nguyên bản: Đảm bảo tính nhất quán toán học 100% (Originality = 100% - AI% - Plag%)
    ai_percentage = ai_result["ai_percentage"]
    originality_score = max(0.0, round(100.0 - ai_percentage - plag_percentage, 1))

    # Gán nhãn đạo văn vào từng câu nếu có
    plagiarized_texts = set()
    for m in matches:
        for s in m["overlap_sentences"]:
            plagiarized_texts.add(s["text"].strip().lower())

    enriched_sentences = []
    plag_sentence_count = 0

    for s in ai_result["sentences"]:
        is_header = s.get("is_header", False)
        s_text_clean = s["text"].strip().lower()
        is_plag = (not is_header) and (s_text_clean in plagiarized_texts)

        if is_plag:
            plag_sentence_count += 1
            risk_level = "plagiarism"
            diag = ["Trùng khớp cấu trúc với tài liệu tham chiếu trong cơ sở dữ liệu đối sánh"]
            rewrite = "Cần trích dẫn nguồn học thuật chuẩn (IEEE / APA) tại cuối câu hoặc viết lại bằng ngôn ngữ riêng."
            guidance = "Bổ sung trích dẫn tài liệu tham khảo chính thức."
        else:
            risk_level = s["risk_level"]
            diag = s["diagnostics"]
            rewrite = s.get("rewrite_suggestion")
            guidance = s.get("revision_guidance")

        enriched_sentences.append({
            "id": s["id"],
            "text": s["text"],
            "is_header": is_header,
            "word_count": s.get("word_count", 0),
            "ai_confidence": s.get("ai_confidence", 0),
            "is_ai": s.get("is_ai", False),
            "is_plagiarism": is_plag,
            "risk_level": risk_level,
            "diagnostics": diag,
            "rewrite_suggestion": rewrite,
            "revision_guidance": guidance
        })

    struct = structural_audit or {
        "images_count": 0,
        "tables_count": 0,
        "media_findings": [],
        "tables_findings": []
    }

    # 4. Thẩm tra và Đối soát Nguồn Trích dẫn Đa tầng (3 Dạng: Thiếu kiểm chứng, Khoa học uy tín, Tổng hợp)
    sources_audit = source_verifier.verify_sources(text, enriched_sentences)

    # 5. Bộ định thời gian giám định chuẩn (UTC+7 / Việt Nam)
    now_vn = datetime.now(VN_TZ)
    report_date_vn = f"ngày {now_vn.day:02d} tháng {now_vn.month:02d} năm {now_vn.year}"
    report_date = now_vn.strftime("%d/%m/%Y")
    report_time = now_vn.strftime("%H:%M:%S")
    report_datetime = f"{report_time} {report_date}"

    return {
        "status": "COMPLETED",
        "filename": filename or "Tài liệu học thuật",
        "report_date_vn": report_date_vn,
        "report_date": report_date,
        "report_time": report_time,
        "report_datetime": report_datetime,
        "total_words": len(text.split()),
        "total_characters": len(text),
        "total_sentences": len(enriched_sentences),
        "ai_sentence_count": ai_result["ai_sentence_count"],
        "plag_sentence_count": plag_sentence_count,
        "full_text": text,
        "rendered_html": rendered_html or "", # Bảo toàn 100% hình ảnh (base64) và bảng biểu
        "structural_audit": struct,           # Thẩm định pháp y hình ảnh, sơ đồ và bảng biểu
        "sources_verification": sources_audit, # Hệ thống trích dẫn & kiểm chứng nguồn 3 dạng
        "ai_detection": {
            "binoculars_score": ai_result["binoculars_score"],
            "is_ai_generated": ai_result["is_ai_generated"],
            "ai_percentage": ai_percentage,
            "perplexity": ai_result["perplexity"],
            "burstiness": ai_result["burstiness"],
            "lexical_diversity": ai_result["lexical_diversity"],
            "section_distribution": ai_result["section_distribution"],
            "actual_sections": ai_result.get("actual_sections", []),
            "radar_metrics": ai_result["radar_metrics"],
            "stylometric_consistency": ai_result["stylometric_consistency"],
            "cliche_count": ai_result["cliche_count"]
        },
        "plagiarism": {
            "candidates_found": len(matches),
            "max_similarity_percentage": plag_percentage,
            "matches": matches
        },
        "originality_percentage": originality_score,
        "sentences": enriched_sentences
    }

@router.post("/scan/upload")
async def submit_file_scan(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        rendered_html, extracted_text, structural_audit = extract_document(file.filename, file_bytes)
        
        if len(extracted_text.strip()) < 20:
            raise HTTPException(
                status_code=400,
                detail="Tệp tải lên không chứa đủ nội dung văn bản (tối thiểu 20 ký tự)."
            )
            
        result = analyze_document_content(
            extracted_text, 
            filename=file.filename, 
            rendered_html=rendered_html,
            structural_audit=structural_audit
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi bóc tách tệp: {str(e)}")

@router.post("/scan/direct")
async def scan_direct_sync(request: ScanSubmissionRequest):
    result = analyze_document_content(request.content)
    return result

@router.get("/self-test")
def run_regression_self_test():
    """Chạy bộ kiểm chuẩn pháp y tự động (Automated Forensic Regression Suite)"""
    from app.engines.regression_harness import ForensicRegressionHarness
    harness = ForensicRegressionHarness()
    return harness.run_all_benchmarks()
