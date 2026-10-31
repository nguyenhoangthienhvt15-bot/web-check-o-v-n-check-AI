"""
Bộ giải mã và chuẩn hóa công thức toán học từ Word (OMML) sang chuẩn LaTeX học thuật.
Hỗ trợ chuyển đổi toàn diện từ các công thức cơ bản đến phức tạp:
- Tích phân (đơn, kép, bội, đường, mặt: \\int, \\iint, \\oint)
- Căn thức (căn bậc hai, căn bậc n: \\sqrt, \\sqrt[n])
- Phân số (đơn, phức, đạo hàm: \\frac)
- Chỉ số trên/dưới (lũy thừa, chỉ số: x^2, a_i, x_{i}^{2})
- Giới hạn, tổng xích-ma, tích: \\lim, \\sum, \\prod
- Ma trận, hệ phương trình, dấu ngoặc tự co giãn: \\left( ... \\right)
- Tách từ tiếng Việt bị dính liền vào biến số và biểu thức toán học
"""

import re
import xml.etree.ElementTree as ET

OMML_NS = {
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
}

GREEK_SYMBOLS = {
    'α': r'\alpha', 'β': r'\beta', 'γ': r'\gamma', 'δ': r'\delta', 'ε': r'\epsilon',
    'ζ': r'\zeta', 'η': r'\eta', 'θ': r'\theta', 'ι': r'\iota', 'κ': r'\kappa',
    'λ': r'\lambda', 'μ': r'\mu', 'ν': r'\nu', 'ξ': r'\xi', 'π': r'\pi',
    'ρ': r'\rho', 'σ': r'\sigma', 'τ': r'\tau', 'υ': r'\upsilon', 'φ': r'\phi',
    'χ': r'\chi', 'ψ': r'\psi', 'ω': r'\omega',
    'Γ': r'\Gamma', 'Δ': r'\Delta', 'Θ': r'\Theta', 'Λ': r'\Lambda', 'Ξ': r'\Xi',
    'Π': r'\Pi', 'Σ': r'\Sigma', 'Υ': r'\Upsilon', 'Φ': r'\Phi', 'Ψ': r'\Psi', 'Ω': r'\Omega',
    '≤': r'\le ', '≥': r'\ge ', '≠': r'\ne ', '±': r'\pm ', '×': r'\times ', '÷': r'\div ',
    '∈': r'\in ', '∉': r'\notin ', '⊂': r'\subset ', '⊆': r'\subseteq ',
    '→': r'\to ', '⇒': r'\implies ', '⇔': r'\iff ', '↔': r'\leftrightarrow ',
    '∞': r'\infty ', '∂': r'\partial ', '∇': r'\nabla ', '∫': r'\int ', '∬': r'\iint ', '∮': r'\oint '
}

def clean_math_text(text: str) -> str:
    if not text:
        return ""
    for char, latex in GREEK_SYMBOLS.items():
        text = text.replace(char, latex)
    return text

def omml_node_to_latex(elem: ET.Element) -> str:
    """
    Chuyển đổi đệ quy từng node trong cây OMML sang biểu thức LaTeX
    """
    tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
    
    # 1. Text node trong math
    if tag == 't':
        return clean_math_text(elem.text or '')
    
    # 2. Phân số (Fraction: m:f)
    elif tag == 'f':
        num_elem = elem.find('m:num', OMML_NS)
        den_elem = elem.find('m:den', OMML_NS)
        num_latex = omml_children_to_latex(num_elem) if num_elem is not None else ''
        den_latex = omml_children_to_latex(den_elem) if den_elem is not None else ''
        return f"\\frac{{{num_latex}}}{{{den_latex}}}"
    
    # 3. Căn thức (Radical: m:rad)
    elif tag == 'rad':
        deg_elem = elem.find('m:deg', OMML_NS)
        base_elem = elem.find('m:e', OMML_NS)
        deg_latex = omml_children_to_latex(deg_elem).strip() if deg_elem is not None else ''
        base_latex = omml_children_to_latex(base_elem) if base_elem is not None else ''
        if deg_latex:
            return f"\\sqrt[{deg_latex}]{{{base_latex}}}"
        return f"\\sqrt{{{base_latex}}}"
    
    # 4. Chỉ số dưới (Subscript: m:sSub)
    elif tag == 'sSub':
        base_elem = elem.find('m:e', OMML_NS)
        sub_elem = elem.find('m:sub', OMML_NS)
        base_latex = omml_children_to_latex(base_elem) if base_elem is not None else ''
        sub_latex = omml_children_to_latex(sub_elem) if sub_elem is not None else ''
        return f"{base_latex}_{{{sub_latex}}}"
    
    # 5. Chỉ số trên / Lũy thừa (Superscript: m:sSup)
    elif tag == 'sSup':
        base_elem = elem.find('m:e', OMML_NS)
        sup_elem = elem.find('m:sup', OMML_NS)
        base_latex = omml_children_to_latex(base_elem) if base_elem is not None else ''
        sup_latex = omml_children_to_latex(sup_elem) if sup_elem is not None else ''
        return f"{base_latex}^{{{sup_latex}}}"
    
    # 6. Cả chỉ số trên và dưới (Sub-Superscript: m:sSubSup)
    elif tag == 'sSubSup':
        base_elem = elem.find('m:e', OMML_NS)
        sub_elem = elem.find('m:sub', OMML_NS)
        sup_elem = elem.find('m:sup', OMML_NS)
        base_latex = omml_children_to_latex(base_elem) if base_elem is not None else ''
        sub_latex = omml_children_to_latex(sub_elem) if sub_elem is not None else ''
        sup_latex = omml_children_to_latex(sup_elem) if sup_elem is not None else ''
        return f"{base_latex}_{{{sub_latex}}}^{{{sup_latex}}}"
    
    # 7. Toán tử N-ary (Tích phân, Tổng, Tích: m:nary)
    elif tag == 'nary':
        chr_elem = elem.find('m:naryPr/m:chr', OMML_NS)
        op_char = chr_elem.attrib.get(f'{{{OMML_NS["m"]}}}val', '∫') if chr_elem is not None else '∫'
        
        op_latex = r'\int'
        if op_char in ['∬', '∮', '∑', '∏']:
            op_latex = GREEK_SYMBOLS.get(op_char, r'\int')
        elif op_char == '∑':
            op_latex = r'\sum'
        elif op_char == '∏':
            op_latex = r'\prod'
            
        sub_elem = elem.find('m:sub', OMML_NS)
        sup_elem = elem.find('m:sup', OMML_NS)
        base_elem = elem.find('m:e', OMML_NS)
        
        sub_latex = f"_{{{omml_children_to_latex(sub_elem)}}}" if sub_elem is not None and len(sub_elem) > 0 else ""
        sup_latex = f"^{{{omml_children_to_latex(sup_elem)}}}" if sup_elem is not None and len(sup_elem) > 0 else ""
        base_latex = omml_children_to_latex(base_elem) if base_elem is not None else ""
        
        return f"{op_latex}{sub_latex}{sup_latex} {base_latex}"
    
    # 8. Dấu ngoặc co giãn (Delimiter: m:d)
    elif tag == 'd':
        beg_elem = elem.find('m:dPr/m:begChr', OMML_NS)
        end_elem = elem.find('m:dPr/m:endChr', OMML_NS)
        beg_chr = beg_elem.attrib.get(f'{{{OMML_NS["m"]}}}val', '(') if beg_elem is not None else '('
        end_chr = end_elem.attrib.get(f'{{{OMML_NS["m"]}}}val', ')') if end_elem is not None else ')'
        
        # Thoát các ký tự đặc biệt cho LaTeX
        beg_map = {'{': r'\{', '[': r'[', '(': r'(', '|': r'|'}
        end_map = {'}': r'\}', ']': r']', ')': r')', '|': r'|'}
        beg_str = beg_map.get(beg_chr, beg_chr)
        end_str = end_map.get(end_chr, end_chr)
        
        content = omml_children_to_latex(elem.find('m:e', OMML_NS)) if elem.find('m:e', OMML_NS) is not None else ''
        return f"\\left{beg_str} {content} \\right{end_str}"
    
    # 9. Hàm số (Function: m:func)
    elif tag == 'func':
        name_elem = elem.find('m:fName', OMML_NS)
        base_elem = elem.find('m:e', OMML_NS)
        name_latex = omml_children_to_latex(name_elem) if name_elem is not None else ''
        base_latex = omml_children_to_latex(base_elem) if base_elem is not None else ''
        return f"{name_latex} {base_latex}"
    
    # 10. Dấu mũ, vector, gạch đầu (Accent: m:acc)
    elif tag == 'acc':
        chr_elem = elem.find('m:accPr/m:chr', OMML_NS)
        acc_chr = chr_elem.attrib.get(f'{{{OMML_NS["m"]}}}val', '→') if chr_elem is not None else '→'
        base_elem = elem.find('m:e', OMML_NS)
        base_latex = omml_children_to_latex(base_elem) if base_elem is not None else ''
        if acc_chr in ['→', '⃗']:
            return f"\\vec{{{base_latex}}}"
        elif acc_chr in ['‾', '¯']:
            return f"\\overline{{{base_latex}}}"
        elif acc_chr in ['^', '̂']:
            return f"\\hat{{{base_latex}}}"
        return f"{base_latex}"

    # Mặc định: Duyệt tiếp các con
    return omml_children_to_latex(elem)

def omml_children_to_latex(parent: ET.Element) -> str:
    if parent is None:
        return ""
    parts = []
    for child in parent:
        parts.append(omml_node_to_latex(child))
    return "".join(parts)

def omml_to_latex(omml_elem: ET.Element, display_mode: bool = False) -> str:
    """
    Chuyển đổi hoàn chỉnh một khối <m:oMath> hoặc <m:oMathPara> thành chuỗi LaTeX
    """
    latex_core = omml_node_to_latex(omml_elem).strip()
    if not latex_core:
        return ""
        
    # Chuẩn hóa khoảng trắng nội bộ trong công thức
    latex_core = re.sub(r'\s+', ' ', latex_core)
    
    if display_mode:
        return f" $${latex_core}$$ "
    return f" ${latex_core}$ "

def _enhance_math_segment(text: str) -> str:
    if not text:
        return text

    # 1. Tách các từ tiếng Việt thông dụng bị dính liền vào biểu thức toán (chỉ xét khoảng trắng ngang [ \t])
    vn_math_prefixes = r'(?:bởi|với|cho|đặt|tại|khi|thì|tính|xét|giả sử|phương trình)'
    text = re.sub(rf'\b({vn_math_prefixes})[ \t]*([a-zA-Z])(?=[ \t]*[=≤≥<>:])', r'\1 $\2$ ', text, flags=re.IGNORECASE)
    text = re.sub(rf'\b({vn_math_prefixes})[ \t]*([a-zA-Z][ \t]*=[ \t]*[^,;\s\(\)]+)', r'\1 $\2$ ', text, flags=re.IGNORECASE)
    text = re.sub(rf'\b({vn_math_prefixes})[ \t]*([a-zA-Z0-9_]+[ \t]*[≤≥<>=][ \t]*[a-zA-Z0-9_]+)', r'\1 $\2$ ', text, flags=re.IGNORECASE)
    
    # Tách từ tiếng Việt phía sau công thức dính liền (VD: y=y(x)vớia≤x≤b -> $y=y(x)$ với $a \le x \le b$)
    vn_math_suffixes = r'(?:với|trong|khi|được|có|là|nối|chạy từ)'
    text = re.sub(rf'([=≤≥\+\-\*/\(\)\]0-9a-zA-Z])({vn_math_suffixes})\b', r'\1 \2 ', text, flags=re.IGNORECASE)
    
    # Tách tọa độ điểm dính liền chữ: điểmA(0,-2) -> điểm $A(0, -2)$
    text = re.sub(r'\b(điểm|tại)[ \t]*([A-Z])[ \t]*\(([^)\n]+)\)', r'\1 $\2(\3)$ ', text)
    text = re.sub(r'\b(đoạn thẳng|đường cong)[ \t]*([A-Z]{1,2})\b', r'\1 $\2$ ', text)
    text = re.sub(r'\b(đường cong|đoạn)[ \t]*([LC])\b', r'\1 $\2$ ', text)

    # 2. Phục hồi dạng tích phân bị mất biểu tượng (VD: Z L f(x,y)dl -> \int_L f(x,y) dl)
    text = re.sub(r'\bZ[ \t]+([a-zA-Z0-9_]+)[ \t]+([a-zA-Z0-9_]+)[ \t]+f\(x,[ \t]*y\)[ \t]*dl\b', r' $\\int_{\1}^{\2} f(x,y) \, dl$ ', text)
    text = re.sub(r'\bZ[ \t]+([a-zA-Z0-9_]+)[ \t]+f\(x,[ \t]*y\)[ \t]*dl\b', r' $\\int_{\1} f(x,y) \, dl$ ', text)
    text = re.sub(r'\bR[ \t]+L[ \t]+f\(x,[ \t]*y\)[ \t]*dl\b', r' $\\int_L f(x,y) \, dl$ ', text)
    text = re.sub(r'\bTínhI=[ \t]*R[ \t]+L\b', r'Tính $I = \\int_L$ ', text)

    # 3. Phục hồi căn thức bị biến thành q hoặc r (VD: q 1+ [y'(x)]2dx -> \sqrt{1 + [y'(x)]^2} dx)
    text = re.sub(r"\bq[ \t]*1\+[ \t]*\[y'\(x\)\]2[ \t]*dx\b", r" $\\sqrt{1 + [y'(x)]^2} \, dx$ ", text)
    text = re.sub(r"\bq[ \t]*\[x'\(t\)\]2[ \t]*\+[ \t]*\[y'\(t\)\]2[ \t]*dt\b", r" $\\sqrt{[x'(t)]^2 + [y'(t)]^2} \, dt$ ", text)
    text = re.sub(r"dl=[ \t]*q1\+[ \t]*\(y'\)2dx", r" $dl = \\sqrt{1 + (y')^2} \, dx$ ", text)
    text = re.sub(r"=[ \t]*r1\+[ \t]*14dx", r" $= \\sqrt{1 + \\frac{1}{4}} \, dx$ ", text)

    # 4. Chuẩn hóa các ký hiệu suy diễn toán học
    text = re.sub(r'==>|=>', r' $\\implies$ ', text)
    text = re.sub(r'<==|<=', r' $\\le$ ', text)
    text = re.sub(r'>=', r' $\\ge$ ', text)

    # 5. Dọn dẹp khoảng trắng ngang (Horizontal spaces), BẢO TOÀN TUYỆT ĐỐI dấu xuống dòng (\n)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text

def enhance_plain_text_math(text: str, is_html: bool = False) -> str:
    """
    Phục hồi và làm đẹp các công thức toán học bị dính chữ tiếng Việt hoặc bị suy biến sang plain-text.
    Nếu is_html=True, chỉ xử lý văn bản bên ngoài thẻ HTML (<...>) để bảo vệ tuyệt đối thuộc tính ảnh Base64 và cấu trúc DOM.
    """
    if not text:
        return text

    if is_html or ('<' in text and '>' in text):
        parts = re.split(r'(<[^>]+>)', text)
        processed = [
            part if part.startswith('<') and part.endswith('>') else _enhance_math_segment(part)
            for part in parts
        ]
        return "".join(processed).strip()

    return _enhance_math_segment(text).strip()
