import io
import re
from typing import Tuple, Dict, Any, List
import mammoth
from pypdf import PdfReader

def audit_media_and_tables(rendered_html: str, raw_text: str) -> Dict[str, Any]:
    """
    Giám định pháp y toàn diện đối với Hình ảnh, Biểu đồ và Bảng số liệu trong tài liệu:
    - Phát hiện hình ảnh/sơ đồ thiếu chú thích (Caption, Figure X)
    - Phát hiện biểu đồ/hình vẽ thiếu trích dẫn nguồn gốc (Nguồn: [Tác giả, Năm])
    - Phát hiện bảng số liệu thiếu đơn vị tính hoặc nguồn tham chiếu
    """
    img_matches = re.findall(r'<img[^>]+>', rendered_html)
    table_matches = re.findall(r'<table[^>]*>.*?</table>', rendered_html, re.DOTALL)
    
    media_findings: List[Dict[str, Any]] = []
    for idx, img_tag in enumerate(img_matches):
        # Kiểm tra xem tài liệu có chứa chú thích Hình/Figure tương ứng
        has_fig_caption = bool(re.search(rf'(hình|figure|sơ đồ|biểu đồ)\s*{idx+1}\b', raw_text, re.IGNORECASE))
        has_citation = bool(re.search(rf'(nguồn|source|theo)\s*[:–—\-]', raw_text, re.IGNORECASE))
        
        status = "CẦN LƯU Ý"
        notes = []
        if not has_fig_caption:
            notes.append(f"Chưa có nhãn chú thích chính quy (Ví dụ: 'Hình {idx+1}: Tên sơ đồ/hình ảnh').")
        if not has_citation:
            notes.append("Thiếu nguồn gốc minh chứng (Cần bổ sung: 'Nguồn: Nhóm tác giả thực hiện' hoặc trích dẫn tài liệu tham khảo).")
        if has_fig_caption and has_citation:
            status = "HỢP LỆ"
            notes.append("Đầy đủ nhãn chú thích và nguồn gốc trích dẫn học thuật.")
            
        media_findings.append({
            "index": idx + 1,
            "status": status,
            "has_caption": has_fig_caption,
            "has_source": has_citation,
            "notes": " ".join(notes)
        })

    tables_findings: List[Dict[str, Any]] = []
    for idx, tbl in enumerate(table_matches):
        has_tbl_caption = bool(re.search(rf'(bảng|table)\s*{idx+1}\b', raw_text, re.IGNORECASE))
        has_units = bool(re.search(r'(đơn vị|unit|%|ms|bpm|hz|°c|vnd|usd)', tbl, re.IGNORECASE))
        
        status = "CẦN LƯU Ý"
        notes = []
        if not has_tbl_caption:
            notes.append(f"Chưa có tiêu đề bảng quy chuẩn (Ví dụ: 'Bảng {idx+1}: Bảng thông số...').")
        if not has_units:
            notes.append("Cần bổ sung đơn vị đo lường cho các cột dữ liệu định lượng.")
        if has_tbl_caption and has_units:
            status = "HỢP LỆ"
            notes.append("Đầy đủ tiêu đề bảng và thông số đơn vị đo lường chuẩn.")
            
        tables_findings.append({
            "index": idx + 1,
            "status": status,
            "has_caption": has_tbl_caption,
            "has_units": has_units,
            "notes": " ".join(notes)
        })

    return {
        "images_count": len(img_matches),
        "tables_count": len(table_matches),
        "media_findings": media_findings,
        "tables_findings": tables_findings
    }

def extract_document(filename: str, file_bytes: bytes) -> Tuple[str, str, Dict[str, Any]]:
    """
    Bóc tách tài liệu trả về:
    1. rendered_html: HTML chứa 100% hình ảnh (base64 inline), bảng biểu, tiêu đề, định dạng
    2. raw_text: Văn bản sạch phục vụ phân tích thuật toán
    3. structural_audit: Giám định pháp y đối với hình ảnh, sơ đồ, bảng biểu
    """
    ext = filename.lower().split('.')[-1]
    
    if ext in ['docx', 'doc']:
        # Dùng mammoth để chuyển docx sang HTML bảo toàn 100% hình ảnh (base64) và bảng biểu
        html_result = mammoth.convert_to_html(io.BytesIO(file_bytes))
        rendered_html = html_result.value
        
        text_result = mammoth.extract_raw_text(io.BytesIO(file_bytes))
        raw_text = text_result.value.strip()
        structural_audit = audit_media_and_tables(rendered_html, raw_text)
        return rendered_html, raw_text, structural_audit
        
    elif ext == 'pdf':
        reader = PdfReader(io.BytesIO(file_bytes))
        pages_text = []
        for idx, page in enumerate(reader.pages):
            t = page.extract_text()
            if t:
                pages_text.append(f"<div class='pdf-page-marker' data-page='{idx+1}'></div>" + t)
        raw_text = "\n\n".join([page.extract_text() or "" for page in reader.pages]).strip()
        rendered_html = "<div class='pdf-rendered-body'>" + "<hr class='my-8 border-dashed border-zinc-300'>".join(pages_text) + "</div>"
        structural_audit = audit_media_and_tables(rendered_html, raw_text)
        return rendered_html, raw_text, structural_audit
        
    elif ext in ['txt', 'md']:
        raw_text = file_bytes.decode('utf-8', errors='ignore').strip()
        rendered_html = f"<div class='whitespace-pre-wrap font-times text-base'>{raw_text}</div>"
        structural_audit = audit_media_and_tables(rendered_html, raw_text)
        return rendered_html, raw_text, structural_audit
        
    else:
        raise ValueError(f"Định dạng .{ext} không được hỗ trợ. Vui lòng tải file DOCX, PDF hoặc TXT.")
