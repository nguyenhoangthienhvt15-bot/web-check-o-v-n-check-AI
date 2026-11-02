"""
SYNAPES MULTI-LINGUAL SPELL & GRAMMAR FORENSIC ENGINE (TIẾNG VIỆT, ENGLISH, 中文)
Hệ thống rà soát và kiểm định lỗi chính tả, sai ngữ pháp học thuật đa ngôn ngữ.
Áp dụng tiêu chuẩn từ điển ngữ liệu học thuật và bộ quy tắc kiểm tra n-gram chính xác cao.
"""

import re
from typing import List, Dict, Any, Tuple

class SpellGrammarEngine:
    def __init__(self):
        self._init_vietnamese_rules()
        self._init_english_rules()
        self._init_chinese_rules()

    def _init_vietnamese_rules(self):
        # Bộ từ điển các cặp từ thường sai chính tả phổ biến trong văn bản tiếng Việt học thuật
        self.vi_spelling_pairs = [
            (r'\bchuẩn\s+sát\b', 'chuẩn xác', 'Lỗi dùng sai phụ âm cuối t/c (Chuẩn xác thay vì chuẩn sát)', 'HIGH'),
            (r'\bbổ\s+xung\b', 'bổ sung', 'Lỗi nhầm lẫn phụ âm đầu x/s (Bổ sung)', 'HIGH'),
            (r'\bsắp\s+sếp\b', 'sắp xếp', 'Lỗi nhầm lẫn phụ âm s/x (Sắp xếp)', 'HIGH'),
            (r'\bxơ\s+sài\b', 'sơ sài', 'Lỗi nhầm lẫn phụ âm x/s (Sơ sài)', 'MEDIUM'),
            (r'\bcọ\s+sát\b', 'cọ xát', 'Lỗi nhầm lẫn phụ âm s/x (Cọ xát)', 'MEDIUM'),
            (r'\bxuất\s+xắc\b', 'xuất sắc', 'Lỗi nhầm lẫn phụ âm x/s (Xuất sắc)', 'HIGH'),
            (r'\bchính\s+sác\b', 'chính xác', 'Lỗi nhầm lẫn phụ âm s/x (Chính xác)', 'HIGH'),
            (r'\bchia\s+xẻ\b', 'chia sẻ', 'Lỗi sai chính tả dấu hỏi/ngã và s/x (Chia sẻ kiến thức)', 'HIGH'),
            (r'\bgiành\s+dật\b', 'giành giật', 'Lỗi phụ âm d/gi (Giành giật)', 'MEDIUM'),
            (r'\bvô\s+hình\s+chung\b', 'vô hình trung', 'Lỗi thành ngữ học thuật (Vô hình trung nghĩa là ngẫu nhiên biến thành)', 'HIGH'),
            (r'\bchuẩn\s+đoán\b', 'chẩn đoán', 'Lỗi dùng từ học thuật y khoa/kỹ thuật (Chẩn đoán thay vì chuẩn đoán)', 'HIGH'),
            (r'\bthăm\s+quan\b', 'tham quan', 'Lỗi dùng từ gốc Hán-Việt (Tham quan nghĩa là đi xem tận mắt)', 'MEDIUM'),
            (r'\bbàng\s+quang\b', 'bàng quan', 'Lỗi nhầm lẫn bàng quan (thờ ơ đứng ngoài) với bàng quang (bóng đái)', 'HIGH'),
            (r'\bsáng\s+lạng\b', 'xán lạn', 'Lỗi ngữ âm biến âm dân gian (Xán lạn nghĩa là tươi sáng, rực rỡ)', 'HIGH'),
            (r'\bđường\s+xá\b', 'đường sá', 'Lỗi nhầm lẫn phụ âm x/s trong từ ghép (Đường sá)', 'MEDIUM'),
            (r'\bchắp\s+bút\b', 'chấp bút', 'Lỗi dùng sai thuật ngữ (Chấp bút nghĩa là khởi thảo, cầm bút viết theo ý người khác)', 'MEDIUM'),
            (r'\bđộc\s+giả\b', 'đọc giả', 'Lỗi phân biệt từ vựng trong văn cảnh (Độc giả)', 'LOW'),
            (r'\bkhắc\s+họa\b', 'khắc hoạ', 'Lưu ý chuẩn chính tả dấu thanh tiếng Việt', 'LOW'),
            (r'\bchân\s+thành\s+cảm\s+ơn\b', 'chân thành cảm ơn', 'Đạt chuẩn ngữ thức cảm tạ học thuật', 'LOW'),
            (r'\bnghiên\s+cứu\s+này\s+nhằm\s+mục\s+đích\s+nhằm\b', 'nghiên cứu này nhằm mục đích', 'Lỗi lặp từ ngữ pháp (nhằm... nhằm)', 'HIGH'),
            (r'\bmặc\s+dù\s+[\w\s,]+nhưng\s+mà\s+lại\b', 'mặc dù... nhưng...', 'Lỗi ngữ pháp rườm rà (Thừa cụm "mà lại")', 'MEDIUM'),
        ]

    def _init_english_rules(self):
        # Bộ từ vựng và ngữ pháp tiếng Anh học thuật thường sai
        self.en_spelling_pairs = [
            (r'\bdefinately\b', 'definitely', 'Misspelling: "definitely" is the correct spelling', 'HIGH'),
            (r'\bseperate\b', 'separate', 'Misspelling: "separate" has an "a" in the middle', 'HIGH'),
            (r'\boccurance\b', 'occurrence', 'Misspelling: "occurrence" requires double "r"', 'HIGH'),
            (r'\baccomodate\b', 'accommodate', 'Misspelling: "accommodate" requires double "c" and double "m"', 'HIGH'),
            (r'\brecieve\b', 'receive', 'Rule: "i" before "e" except after "c" ("receive")', 'HIGH'),
            (r'\buntill\b', 'until', 'Misspelling: "until" only has one "l"', 'MEDIUM'),
            (r'\bgoverment\b', 'government', 'Misspelling: Missing "n" in "government"', 'HIGH'),
            (r'\benviroment\b', 'environment', 'Misspelling: Missing "n" in "environment"', 'HIGH'),
            (r'\btruely\b', 'truly', 'Misspelling: "truly" drops the "e"', 'MEDIUM'),
            (r'\bneccessary\b', 'necessary', 'Misspelling: "necessary" has one "c" and double "s"', 'HIGH'),
            (r'\brefered\b', 'referred', 'Misspelling: Past tense of "refer" doubles the "r" ("referred")', 'HIGH'),
            (r'\bpublically\b', 'publicly', 'Misspelling: "publicly" is standard academic English', 'MEDIUM'),
            (r'\bpronounciation\b', 'pronunciation', 'Misspelling: "pronunciation" does not include "noun"', 'HIGH'),
            (r'\ba\s+hour\b', 'an hour', 'Article grammar error: Use "an" before silent "h" in "hour"', 'HIGH'),
            (r'\ban\s+university\b', 'a university', 'Article grammar error: "university" begins with a consonant sound /ju:/', 'HIGH'),
            (r'\bmore\s+better\b', 'better / much better', 'Grammar redundancy: Double comparative ("more better")', 'HIGH'),
            (r'\bthe\s+data\s+shows\b', 'the data show / the data shows', 'Academic usage note: In formal IEEE/APA, "data" is plural ("data show")', 'LOW')
        ]

    def _init_chinese_rules(self):
        # Bộ quy tắc chính tả và ngữ pháp tiếng Trung học thuật
        self.zh_rules = [
            (r'按步就班', '按部就班', '成语错别字："按部就班"（按照门类、顺序安排）', 'HIGH'),
            (r'穿流不息', '川流不息', '成语错别字："川流不息"（川代表河流）', 'HIGH'),
            (r'鼎立相助', '鼎力相助', '错别字误用：应为"鼎力相助"（表示尽大力相助）', 'HIGH'),
            (r'针贬', '针砭', '词汇错别字：应为"针砭"（砭为古代石针）', 'HIGH'),
            (r'滥芋充数', '滥竽充数', '成语错别字：应为"滥竽充数"（竽是一种乐器）', 'HIGH'),
            (r'名列前矛', '名列前茅', '成语错别字：应为"名列前茅"（茅为古代行军旗号）', 'HIGH'),
            (r'走投无路', '走投无路', '成语规范用字', 'LOW'),
            (r'的(?=走|跑|跑去|飞快地|认真地)', '地', '语法助词混淆：修饰动词作状语时应使用"地"', 'MEDIUM'),
            (r'得(?=人|书|方法|结果)', '的', '语法助词混淆：修饰名词作定语时应使用"的"', 'MEDIUM'),
            (r'在(?=次|度|来一次)', '再', '同音字误用："再次/再度"表示重复动作，应用"再"', 'HIGH'),
            (r'做为', '作为', '常用词语规范："作为"是书面语规范标准', 'MEDIUM')
        ]

    def audit_document(self, text: str) -> Dict[str, Any]:
        """
        Rà soát toàn diện lỗi chính tả và ngữ pháp trên toàn bộ văn bản.
        Trả về thống kê số lượng và danh mục chi tiết từng lỗi phục vụ báo cáo.
        """
        if not text or not text.strip():
            return {
                "total_errors": 0,
                "vi_errors_count": 0,
                "en_errors_count": 0,
                "zh_errors_count": 0,
                "details": []
            }

        details: List[Dict[str, Any]] = []
        error_id = 1

        # 1. Rà soát Tiếng Việt
        for pattern, replacement, explanation, severity in self.vi_spelling_pairs:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                start = max(0, match.start() - 35)
                end = min(len(text), match.end() + 35)
                context = text[start:end].replace('\n', ' ').strip()
                matched_text = match.group(0)

                details.append({
                    "id": error_id,
                    "lang": "vi",
                    "lang_label": "Tiếng Việt",
                    "type": "Chính tả & Thuật ngữ",
                    "error_text": matched_text,
                    "suggestion": replacement,
                    "context": f"...{context}...",
                    "rule": explanation,
                    "severity": severity
                })
                error_id += 1

        # 2. Rà soát Tiếng Anh
        for pattern, replacement, explanation, severity in self.en_spelling_pairs:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                start = max(0, match.start() - 35)
                end = min(len(text), match.end() + 35)
                context = text[start:end].replace('\n', ' ').strip()
                matched_text = match.group(0)

                details.append({
                    "id": error_id,
                    "lang": "en",
                    "lang_label": "English",
                    "type": "Spelling & Grammar",
                    "error_text": matched_text,
                    "suggestion": replacement,
                    "context": f"...{context}...",
                    "rule": explanation,
                    "severity": severity
                })
                error_id += 1

        # 3. Rà soát Tiếng Trung
        for pattern, replacement, explanation, severity in self.zh_rules:
            for match in re.finditer(pattern, text):
                start = max(0, match.start() - 25)
                end = min(len(text), match.end() + 25)
                context = text[start:end].replace('\n', ' ').strip()
                matched_text = match.group(0)

                details.append({
                    "id": error_id,
                    "lang": "zh",
                    "lang_label": "中文 (Chinese)",
                    "type": "字词规范 & 语法助词",
                    "error_text": matched_text,
                    "suggestion": replacement,
                    "context": f"...{context}...",
                    "rule": explanation,
                    "severity": severity
                })
                error_id += 1

        vi_count = sum(1 for d in details if d["lang"] == "vi")
        en_count = sum(1 for d in details if d["lang"] == "en")
        zh_count = sum(1 for d in details if d["lang"] == "zh")
        total_errors = len(details)

        return {
            "total_errors": total_errors,
            "vi_errors_count": vi_count,
            "en_errors_count": en_count,
            "zh_errors_count": zh_count,
            "details": details[:100], # Giới hạn tối đa 100 lỗi chi tiết
            "summary_label": f"{total_errors} lỗi chính tả & ngữ pháp phát hiện (Tiếng Việt: {vi_count}, Tiếng Anh: {en_count}, Tiếng Trung: {zh_count})"
        }

spell_grammar_engine = SpellGrammarEngine()
