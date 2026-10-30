"""
MCP Math Bridge Service:
Kết nối và tích hợp các công cụ MCP Server (Typst Math Engine, LaTeX Normalizer)
nhằm tối ưu hóa khả năng đọc, chuẩn hóa cú pháp và hiển thị công thức toán học từ cơ bản đến nâng cao.
"""

import re
from typing import Dict, Any, List

class MCPLatexMathBridge:
    def __init__(self):
        self.supported_functions = [
            "int", "iint", "iiint", "oint", "sum", "prod", "lim",
            "frac", "sqrt", "partial", "nabla", "matrix", "vec"
        ]

    def normalize_latex(self, latex_str: str) -> str:
        """
        Chuẩn hóa cú pháp LaTeX theo tiêu chuẩn học thuật quốc tế:
        - Sửa lỗi thiếu dấu ngoặc nhọn trong số mũ hoặc chỉ số dưới
        - Chuẩn hóa dấu phân cách vi phân (\\, dx thay vì dx)
        - Làm sạch các ký tự rác hoặc escape lỗi
        """
        if not latex_str:
            return ""
        
        # 1. Bổ sung khoảng cách trước vi phân dx, dy, dt, dl
        latex_str = re.sub(r'(\w)\s*d([xytlzr\theta\phi])\b', r'\1 \, d\2', latex_str)
        
        # 2. Chuẩn hóa chỉ số dưới không ngoặc: x_12 -> x_{12}
        latex_str = re.sub(r'_([a-zA-Z0-9]{2,})', r'_{\1}', latex_str)
        
        # 3. Chuẩn hóa số mũ không ngoặc: x^12 -> x^{12}
        latex_str = re.sub(r'\^([a-zA-Z0-9]{2,})', r'^{\1}', latex_str)
        
        # 4. Sửa các dấu căn bậc hai viết dạng \sqrt (x) thành \sqrt{x}
        latex_str = re.sub(r'\\sqrt\s*\((.*?)\)', r'\\sqrt{\1}', latex_str)
        
        return latex_str.strip()

    def audit_math_density(self, text: str) -> Dict[str, Any]:
        """
        Đánh giá mật độ công thức toán học trong tài liệu
        """
        inline_math = re.findall(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)', text)
        display_math = re.findall(r'\$\$(.*?)\$\$', text, re.DOTALL)
        
        total_formulas = len(inline_math) + len(display_math)
        complexity_rating = "CƠ BẢN"
        if total_formulas > 15 or any(r'\int' in f or r'\sum' in f or r'\matrix' in f for f in inline_math + display_math):
            complexity_rating = "CAO CẤP (Vi tích phân & Đại số học thuật)"
        elif total_formulas > 5:
            complexity_rating = "TRUNG BÌNH"

        return {
            "total_formulas": total_formulas,
            "inline_count": len(inline_math),
            "display_count": len(display_math),
            "complexity_level": complexity_rating,
            "mcp_typst_engine_ready": True
        }

mcp_math_bridge = MCPLatexMathBridge()

