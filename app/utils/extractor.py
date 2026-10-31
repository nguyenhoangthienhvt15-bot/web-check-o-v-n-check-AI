import io
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import Tuple, Dict, Any, List
import mammoth
from pypdf import PdfReader
from app.utils.omml_latex import omml_to_latex, enhance_plain_text_math
from app.services.mcp_latex_bridge import mcp_math_bridge

def validate_and_sanitize_upload(filename: str, file_bytes: bytes) -> str:
    """
    KIỂM DUYỆT TỆP KHÔNG TIN CẬY (ZERO-TRUST FILE SANITIZATION):
    1. Giới hạn kích thước tối đa 20MB.
    2. Kiểm tra Magic Bytes nhị phân (bảo đảm tệp không bị đổi tên giả mạo thành trojan/shell).
    3. Chống tấn công bom giải nén Zip Bomb (Decompression Ratio & Size Limit).
    4. Chống tấn công nhị phân ngụy trang mã độc vào văn bản thô.
    """
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValueError(f"Tường lửa an ninh: Tệp tải lên vượt quá dung lượng cho phép (tối đa 20MB).")

    if not filename or '.' not in filename:
        raise ValueError("Tên tệp không hợp lệ: Thiếu phần mở rộng.")

    ext = filename.lower().split('.')[-1]

    if ext in ['docx', 'doc']:
        # Kiểm tra Magic Bytes chuẩn của ZIP container (PK\x03\x04)
        if not file_bytes.startswith(b'PK\x03\x04'):
            raise ValueError("Cảnh báo an ninh: Chữ ký nhị phân (Magic Bytes) không khớp với tệp Word DOCX chuẩn (thiếu PK header). Tệp có dấu hiệu bị ngụy trang.")
        
        # Phòng thủ chống Zip Bomb & Kiểm tra tính toàn vẹn cấu trúc
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes), 'r') as zf:
                total_uncompressed = 0
                file_count = 0
                for info in zf.infolist():
                    file_count += 1
                    total_uncompressed += info.file_size
                    # Giới hạn kích thước tệp con tối đa 25MB
                    if info.file_size > 25 * 1024 * 1024:
                        raise ValueError("Cảnh báo an ninh: Tệp con trong tài liệu nén vượt quá ngưỡng an toàn.")

                if total_uncompressed > 35 * 1024 * 1024:
                    raise ValueError("Cảnh báo an ninh: Kích thước giải nén vượt quá 35MB (Chống tấn công Zip Bomb).")

                if file_count > 300:
                    raise ValueError("Cảnh báo an ninh: Số lượng thành phần trong tệp vượt quá ngưỡng bình thường.")

                if 'word/document.xml' not in zf.namelist():
                    raise ValueError("Tệp DOCX không hợp lệ: Thiếu phân đoạn bắt buộc word/document.xml.")
        except zipfile.BadZipFile:
            raise ValueError("Tệp DOCX bị lỗi hoặc bị hư hỏng cấu trúc nhị phân.")

    elif ext == 'pdf':
        # Kiểm tra Magic Bytes chuẩn PDF: %PDF-
        if b'%PDF-' not in file_bytes[:1024]:
            raise ValueError("Cảnh báo an ninh: Chữ ký nhị phân không khớp với tệp PDF chuẩn (thiếu header %PDF-).")

    elif ext in ['txt', 'md']:
        # Tệp văn bản thuần không được phép chứa ký tự null byte (thường thấy ở tệp thực thi ngụy trang)
        if b'\x00' in file_bytes[:4096]:
            raise ValueError("Cảnh báo an ninh: Tệp văn bản chứa ký tự nhị phân (Null bytes) nghi vấn là mã nhị phân ngụy trang.")

    else:
        raise ValueError(f"Định dạng .{ext} không được hỗ trợ. Vui lòng tải file DOCX, PDF hoặc TXT.")

    return ext

def convert_omml_in_xml(xml_bytes: bytes) -> bytes:
    """
    Chuyển đổi toàn bộ các thẻ công thức toán học Word (m:oMath, m:oMathPara)
    thành các đoạn văn bản chuẩn LaTeX ($...$ hoặc $$...$$) bên trong file XML.
    Bảo vệ chống tấn công XXE (XML External Entity Injection) và Billion Laughs.
    """
    try:
        # Khử độc XML: Vô hiệu hóa DTD Entity Expansion độc hại
        if b'<!DOCTYPE' in xml_bytes or b'<!ENTITY' in xml_bytes:
            xml_bytes = re.sub(b'<!DOCTYPE[^>]*>', b'', xml_bytes)
            xml_bytes = re.sub(b'<!ENTITY[^>]*>', b'', xml_bytes)

        root = ET.fromstring(xml_bytes)
        ns = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'
        }
        
        # 1. Chuyển đổi khối công thức độc lập (Display Math: m:oMathPara)
        for para in root.findall('.//m:oMathPara', ns):
            math_parts = []
            for omath in para.findall('.//m:oMath', ns):
                l = omml_to_latex(omath, display_mode=True)
                if l:
                    math_parts.append(l)
            if math_parts:
                combined_latex = " ".join(math_parts)
                t = ET.Element(f'{{{ns["w"]}}}t')
                t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                t.text = f" {combined_latex} "
                para.clear()
                para.tag = f'{{{ns["w"]}}}r'
                para.append(t)
                
        # 2. Chuyển đổi công thức toán nội dòng (Inline Math: m:oMath)
        for omath in root.findall('.//m:oMath', ns):
            l = omml_to_latex(omath, display_mode=False)
            if l:
                t = ET.Element(f'{{{ns["w"]}}}t')
                t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                t.text = f" {l} "
                omath.clear()
                omath.tag = f'{{{ns["w"]}}}r'
                omath.append(t)
                
        return ET.tostring(root, encoding='utf-8')
    except Exception as e:
        print(f"Lỗi phân tích XML document: {e}")
        return xml_bytes

def preprocess_docx_math(file_bytes: bytes) -> bytes:
    """
    Tiền xử lý file DOCX trong bộ nhớ:
    Giải nén, chuyển đổi công thức toán sang chuẩn LaTeX, sau đó đóng gói lại.
    """
    try:
        in_buf = io.BytesIO(file_bytes)
        if not zipfile.is_zipfile(in_buf):
            return file_bytes
            
        out_buf = io.BytesIO()
        with zipfile.ZipFile(in_buf, 'r') as zin, zipfile.ZipFile(out_buf, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == 'word/document.xml':
                    data = convert_omml_in_xml(data)
                zout.writestr(item, data)
                
        return out_buf.getvalue()
    except Exception as e:
        print(f"Lỗi tiền xử lý OMML sang LaTeX: {e}")
        return file_bytes

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
    # 0. Kiểm duyệt tệp an ninh đa tầng (Magic bytes, Size, Zip Bomb, Null bytes)
    ext = validate_and_sanitize_upload(filename, file_bytes)
    
    if ext in ['docx', 'doc']:
        # 1. Tiền xử lý công thức toán học từ Word OMML sang chuẩn LaTeX học thuật ($...$, $$...$$)
        processed_bytes = preprocess_docx_math(file_bytes)

        # 2. Dùng mammoth để chuyển docx sang HTML bảo toàn 100% hình ảnh (base64) và bảng biểu
        html_result = mammoth.convert_to_html(io.BytesIO(processed_bytes))
        rendered_html = html_result.value
        
        text_result = mammoth.extract_raw_text(io.BytesIO(processed_bytes))
        raw_text = text_result.value.strip()
        
        # 3. Phục hồi biểu thức toán học và tách từ tiếng Việt dính biến
        rendered_html = enhance_plain_text_math(rendered_html)
        raw_text = enhance_plain_text_math(raw_text)

        structural_audit = audit_media_and_tables(rendered_html, raw_text)
        structural_audit["math_audit"] = mcp_math_bridge.audit_math_density(raw_text)
        return rendered_html, raw_text, structural_audit
        
    elif ext == 'pdf':
        reader = PdfReader(io.BytesIO(file_bytes))
        pages_text = []
        for idx, page in enumerate(reader.pages):
            t = page.extract_text()
            if t:
                t = enhance_plain_text_math(t)
                pages_text.append(f"<div class='pdf-page-marker' data-page='{idx+1}'></div>" + t)
        raw_text = "\n\n".join([page.extract_text() or "" for page in reader.pages]).strip()
        raw_text = enhance_plain_text_math(raw_text)
        rendered_html = "<div class='pdf-rendered-body'>" + "<hr class='my-8 border-dashed border-zinc-300'>".join(pages_text) + "</div>"
        structural_audit = audit_media_and_tables(rendered_html, raw_text)
        structural_audit["math_audit"] = mcp_math_bridge.audit_math_density(raw_text)
        return rendered_html, raw_text, structural_audit
        
    elif ext in ['txt', 'md']:
        raw_text = file_bytes.decode('utf-8', errors='ignore').strip()
        raw_text = enhance_plain_text_math(raw_text)
        rendered_html = f"<div class='whitespace-pre-wrap font-times text-base'>{raw_text}</div>"
        structural_audit = audit_media_and_tables(rendered_html, raw_text)
        structural_audit["math_audit"] = mcp_math_bridge.audit_math_density(raw_text)
        return rendered_html, raw_text, structural_audit
        
    else:
        raise ValueError(f"Định dạng .{ext} không được hỗ trợ. Vui lòng tải file DOCX, PDF hoặc TXT.")
