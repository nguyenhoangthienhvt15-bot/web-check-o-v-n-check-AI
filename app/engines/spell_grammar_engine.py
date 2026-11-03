"""
SYNAPES ADVANCED DUAL-LINGUAL SPELL & GRAMMAR FORENSIC ENGINE (TIẾNG VIỆT & ENGLISH)
Hệ thống rà soát và kiểm định lỗi chính tả, sai ngữ pháp học thuật chuyên sâu 2 ngôn ngữ.
Áp dụng tiêu chuẩn ngữ liệu học thuật, chuẩn chính tả Viện Ngôn ngữ học / Bộ GD&ĐT
và tiêu chuẩn văn phong học thuật quốc tế IEEE / APA / Chicago Manual of Style.
"""

import re
from typing import List, Dict, Any, Tuple, Optional

class SpellGrammarEngine:
    def __init__(self):
        self._init_vietnamese_rules()
        self._init_english_rules()

    def _init_vietnamese_rules(self):
        """
        Quy chuẩn đối soát chính tả & ngữ pháp Tiếng Việt học thuật toàn diện.
        Tập trung vào:
        1. Phụ âm đầu hay nhầm lẫn (s/x, d/gi/r, ch/tr, l/n)
        2. Phụ âm cuối hay nhầm lẫn (c/t, n/ng, p/t)
        3. Thuật ngữ Hán - Việt & Từ ngữ học thuật hay dùng sai
        4. Lỗi lặp từ và liên từ rườm rà trong văn phong khoa học
        5. Lỗi chuẩn hóa khoảng trắng trước dấu câu
        """
        self.vi_spelling_pairs: List[Tuple[str, str, str, str]] = [
            # 1. Phụ âm đầu & Phụ âm cuối
            (r'\bchuẩn\s+sát\b', 'chuẩn xác', 'Lỗi dùng sai phụ âm cuối t/c (Chuẩn xác nghĩa là đúng đắn, chính xác)', 'HIGH'),
            (r'\bbổ\s+xung\b', 'bổ sung', 'Lỗi nhầm lẫn phụ âm đầu x/s (Bổ sung nghĩa là thêm vào cho đủ)', 'HIGH'),
            (r'\bsắp\s+sếp\b', 'sắp xếp', 'Lỗi nhầm lẫn phụ âm s/x (Sắp xếp theo thứ tự/bố cục)', 'HIGH'),
            (r'\bxơ\s+sài\b', 'sơ sài', 'Lỗi nhầm lẫn phụ âm x/s (Sơ sài nghĩa là đơn giản, thiếu thấu đáo)', 'MEDIUM'),
            (r'\bcọ\s+sát\b', 'cọ xát', 'Lỗi nhầm lẫn phụ âm s/x (Cọ xát mang tính tương tác hoặc ma sát vật lý)', 'HIGH'),
            (r'\bxuất\s+xắc\b', 'xuất sắc', 'Lỗi nhầm lẫn phụ âm x/s (Xuất sắc nghĩa là vượt trội, xuất chúng)', 'HIGH'),
            (r'\bchính\s+sác\b', 'chính xác', 'Lỗi nhầm lẫn phụ âm s/x (Chính xác)', 'HIGH'),
            (r'\bchia\s+xẻ\b', 'chia sẻ', 'Lỗi phụ âm s/x và dấu thanh (Chia sẻ thông tin/dữ liệu)', 'HIGH'),
            (r'\bgiành\s+dật\b', 'giành giật', 'Lỗi phụ âm d/gi (Giành giật)', 'MEDIUM'),
            (r'\bxăm\s+xoi\b', 'săm soi', 'Lỗi nhầm lẫn phụ âm x/s (Săm soi)', 'MEDIUM'),
            (r'\bxơ\s+suất\b', 'sơ suất', 'Lỗi nhầm lẫn phụ âm x/s (Sơ suất trong thao tác thực nghiệm)', 'HIGH'),
            (r'\bđường\s+xá\b', 'đường sá', 'Lỗi nhầm lẫn phụ âm x/s trong từ ghép (Đường sá)', 'MEDIUM'),
            (r'\btrao\s+chuốt\b', 'trau chuốt', 'Lỗi nhầm lẫn nguyên âm ao/au (Trau chuốt câu từ)', 'MEDIUM'),
            (r'\bchăn\s+chở\b', 'trăn trở', 'Lỗi phụ âm ch/tr (Trăn trở về vấn đề nghiên cứu)', 'HIGH'),
            (r'\bchắt\s+chiu\b', 'chắt chiu', 'Đạt chuẩn chính tả', 'LOW'),
            (r'\bphong\s+phanh\b', 'phong thanh', 'Lỗi dùng từ (Phong thanh nghĩa là nghe loáng thoáng, khác phong phanh nghĩa là mặc áo mỏng)', 'HIGH'),
            (r'\bdè\s+xẻn\b', 'dè sẻn', 'Lỗi phụ âm x/s (Dè sẻn)', 'MEDIUM'),
            (r'\brút\s+cuộc\b', 'rốt cuộc', 'Lỗi ngữ âm biến âm (Rốt cuộc là từ chuẩn xác, biểu thị kết quả cuối cùng)', 'MEDIUM'),
            (r'\bdấu\s+diếm\b', 'giấu giếm', 'Lỗi phụ âm d/gi (Giấu giếm)', 'HIGH'),
            (r'\bgiẫm\s+đạp\b', 'dẫm đạp', 'Lỗi phụ âm d/gi (Dẫm đạp)', 'LOW'),
            (r'\blăng\s+xuất\b', 'năng suất', 'Lỗi phụ âm l/n và x/s (Năng suất tính toán)', 'HIGH'),
            (r'\bchung\s+thực\b', 'trung thực', 'Lỗi phụ âm ch/tr (Liêm chính và trung thực học thuật)', 'HIGH'),
            (r'\bchi\s+thức\b', 'tri thức', 'Lỗi phụ âm ch/tr (Tri thức khoa học)', 'HIGH'),
            (r'\bnguồng\s+gốc\b', 'nguồn gốc', 'Lỗi phụ âm cuối ng/n (Nguồn gốc dữ liệu)', 'HIGH'),
            (r'\bnghiên\s+kíu\b', 'nghiên cứu', 'Lỗi chính tả viết sai âm (Nghiên cứu khoa học)', 'HIGH'),
            (r'\bnguyên\s+cứu\b', 'nghiên cứu', 'Lỗi dùng sai âm (Nghiên cứu thay vì nguyên cứu)', 'HIGH'),
            (r'\bphương\s+fáp\b', 'phương pháp', 'Lỗi viết tắt/ký tự không chuẩn (Phương pháp luận)', 'HIGH'),
            (r'\bthực\s+ngiệm\b', 'thực nghiệm', 'Lỗi chính tả nguyên âm ngh/ng (Thực nghiệm)', 'HIGH'),
            (r'\bkhái\s+liệm\b', 'khái niệm', 'Lỗi phụ âm l/n (Khái niệm lý thuyết)', 'HIGH'),

            # 2. Thuật ngữ Hán - Việt & Ngữ nghĩa học thuật
            (r'\bvô\s+hình\s+chung\b', 'vô hình trung', 'Lỗi thành ngữ học thuật (Vô hình trung nghĩa là ngẫu nhiên biến thành)', 'HIGH'),
            (r'\bchuẩn\s+đoán\b', 'chẩn đoán', 'Lỗi dùng từ y khoa/kỹ thuật (Chẩn đoán: xác định bệnh trạng/lỗi, chuẩn đoán là sai)', 'HIGH'),
            (r'\bthăm\s+quan\b', 'tham quan', 'Lỗi dùng từ gốc Hán-Việt (Tham quan nghĩa là đi xem tận mắt, thăm quan là sai)', 'HIGH'),
            (r'\bbàng\s+quang\b', 'bàng quan', 'Lỗi nhầm lẫn: Bàng quan (thờ ơ đứng ngoài cuộc) khác bàng quang (bóng đái)', 'HIGH'),
            (r'\bsáng\s+lạng\b', 'xán lạn', 'Lỗi biến âm dân gian (Xán lạn: tươi sáng, rạng rỡ, bắt nguồn từ chữ Hán 灿烂)', 'HIGH'),
            (r'\bchắp\s+bút\b', 'chấp bút', 'Lỗi dùng sai thuật ngữ (Chấp bút: khởi thảo bài viết, chắp bút là sai)', 'HIGH'),
            (r'\bsát\s+nhập\b', 'sáp nhập', 'Lỗi dùng từ hành chính/luật pháp (Sáp nhập: gộp lại làm một, sát nhập là sai)', 'HIGH'),
            (r'\btựu\s+chung\b', 'tựu trung', 'Lỗi thành ngữ học thuật (Tựu trung: tóm lại, cốt lõi là, bắt nguồn từ 就中)', 'HIGH'),

            # 3. Lỗi lặp từ & Cấu trúc liên từ ngữ pháp rườm rà
            (r'\bnghiên\s+cứu\s+này\s+nhằm\s+mục\s+đích\s+nhằm\b', 'nghiên cứu này nhằm mục đích', 'Lỗi lặp từ liên tiếp (nhằm... nhằm)', 'HIGH'),
            (r'\bmặc\s+dù\s+[\w\s,]{2,40}\s+nhưng\s+mà\s+lại\b', 'mặc dù... nhưng...', 'Lỗi ngữ pháp rườm rà (Thừa liên từ "mà lại")', 'MEDIUM'),
            (r'\btuy\s+nhiên\s+nhưng\b', 'tuy nhiên / nhưng', 'Lỗi trùng lặp liên từ chỉ quan hệ tương phản (Chỉ dùng một trong hai)', 'HIGH'),
            (r'\bdo\s+vì\b', 'do / vì', 'Lỗi trùng lặp liên từ chỉ nguyên nhân (Chỉ dùng "do" hoặc "vì")', 'HIGH'),
            (r'\bđể\s+nhằm\b', 'để / nhằm', 'Lỗi trùng lặp liên từ chỉ mục đích (Chỉ dùng "để" hoặc "nhằm")', 'MEDIUM'),
        ]

    def _init_english_rules(self):
        """
        Quy chuẩn đối soát chính tả & ngữ pháp Tiếng Anh học thuật (Academic English).
        Tập trung vào:
        1. Từ vựng học thuật thường mắc lỗi chính tả phổ biến (Academic Misspellings)
        2. Mạo từ trước danh từ (Articles: a/an rules)
        3. So sánh hơn trùng lặp (Double Comparatives)
        4. Các cặp từ dễ gây nhầm lẫn (Confused Academic Collocations: affect/effect, its/it's, loose/lose)
        """
        self.en_spelling_pairs: List[Tuple[str, str, str, str]] = [
            # 1. Academic Misspellings
            (r'\bdefinately\b', 'definitely', 'Misspelling: "definitely" is the correct spelling in academic English', 'HIGH'),
            (r'\bseperate\b', 'separate', 'Misspelling: "separate" has an "a" in the middle, not an "e"', 'HIGH'),
            (r'\bseperately\b', 'separately', 'Misspelling: "separately" is derived from "separate"', 'HIGH'),
            (r'\boccurance\b', 'occurrence', 'Misspelling: "occurrence" requires double "r" and double "c"', 'HIGH'),
            (r'\boccured\b', 'occurred', 'Misspelling: Past tense of "occur" doubles the "r" ("occurred")', 'HIGH'),
            (r'\baccomodate\b', 'accommodate', 'Misspelling: "accommodate" requires double "c" and double "m"', 'HIGH'),
            (r'\baccomodation\b', 'accommodation', 'Misspelling: "accommodation" requires double "c" and double "m"', 'HIGH'),
            (r'\brecieve\b', 'receive', 'Rule: "i" before "e" except after "c" ("receive")', 'HIGH'),
            (r'\brecieved\b', 'received', 'Rule: "i" before "e" except after "c" ("received")', 'HIGH'),
            (r'\buntill\b', 'until', 'Misspelling: "until" only has one "l"', 'MEDIUM'),
            (r'\bgoverment\b', 'government', 'Misspelling: Missing "n" in "government" (from "govern")', 'HIGH'),
            (r'\benviroment\b', 'environment', 'Misspelling: Missing "n" in "environment"', 'HIGH'),
            (r'\btruely\b', 'truly', 'Misspelling: "truly" drops the "e"', 'MEDIUM'),
            (r'\bneccessary\b', 'necessary', 'Misspelling: "necessary" has one "c" and double "s"', 'HIGH'),
            (r'\bunneccessary\b', 'unnecessary', 'Misspelling: "unnecessary" has one "c" and double "s"', 'HIGH'),
            (r'\brefered\b', 'referred', 'Misspelling: Past tense of "refer" doubles the "r" ("referred")', 'HIGH'),
            (r'\bpublically\b', 'publicly', 'Misspelling: "publicly" is standard academic English', 'MEDIUM'),
            (r'\bpronounciation\b', 'pronunciation', 'Misspelling: "pronunciation" does not include "noun"', 'HIGH'),
            (r'\bmispell\b', 'misspell', 'Misspelling: "misspell" has double "s"', 'MEDIUM'),
            (r'\bindependant\b', 'independent', 'Misspelling: "independent" ends with "-ent"', 'HIGH'),
            (r'\bindependantly\b', 'independently', 'Misspelling: "independently" ends with "-ently"', 'HIGH'),
            (r'\bconsistant\b', 'consistent', 'Misspelling: "consistent" ends with "-ent"', 'HIGH'),
            (r'\binconsistant\b', 'inconsistent', 'Misspelling: "inconsistent" ends with "-ent"', 'HIGH'),
            (r'\bexistance\b', 'existence', 'Misspelling: "existence" ends with "-ence"', 'HIGH'),
            (r'\bmaintainance\b', 'maintenance', 'Misspelling: "maintenance" drops the "ai" from "maintain"', 'HIGH'),
            (r'\bpersistant\b', 'persistent', 'Misspelling: "persistent" ends with "-ent"', 'HIGH'),
            (r'\brelevent\b', 'relevant', 'Misspelling: "relevant" has an "a" in the second syllable', 'HIGH'),
            (r'\birrelevent\b', 'irrelevant', 'Misspelling: "irrelevant" has an "a" in the second syllable', 'HIGH'),
            (r'\bsupercede\b', 'supersede', 'Misspelling: "supersede" is spelled with "s", not "c"', 'HIGH'),
            (r'\btendancy\b', 'tendency', 'Misspelling: "tendency" has an "e" in the second syllable', 'HIGH'),
            (r'\btransfered\b', 'transferred', 'Misspelling: "transferred" doubles the final "r"', 'HIGH'),
            (r'\bwithold\b', 'withhold', 'Misspelling: "withhold" requires double "h"', 'HIGH'),
            (r'\barguement\b', 'argument', 'Misspelling: "argument" drops the "e" from "argue"', 'HIGH'),
            (r'\bachive\b', 'achieve', 'Misspelling: "achieve" requires "i" before "e"', 'HIGH'),
            (r'\bachievment\b', 'achievement', 'Misspelling: "achievement" requires "i" before "e"', 'HIGH'),
            (r'\bbeleive\b', 'believe', 'Misspelling: "believe" requires "i" before "e"', 'HIGH'),
            (r'\bconcious\b', 'conscious', 'Misspelling: "conscious" requires "sc"', 'HIGH'),
            (r'\bcalender\b', 'calendar', 'Misspelling: "calendar" ends with "-ar"', 'HIGH'),
            (r'\bcollegue\b', 'colleague', 'Misspelling: "colleague" requires "-eague"', 'HIGH'),
            (r'\bembarass\b', 'embarrass', 'Misspelling: "embarrass" has double "r" and double "s"', 'HIGH'),
            (r'\bharrass\b', 'harass', 'Misspelling: "harass" has one "r" and double "s"', 'HIGH'),
            (r'\bguarentee\b', 'guarantee', 'Misspelling: "guarantee" begins with "gua-"', 'HIGH'),
            (r'\bpriviledge\b', 'privilege', 'Misspelling: "privilege" has no "d"', 'HIGH'),
            (r'\brythm\b', 'rhythm', 'Misspelling: "rhythm" requires "h" after "r"', 'HIGH'),
            (r'\banalize\b', 'analyze', 'Misspelling: "analyze" is standard (or "analyse" in British English)', 'HIGH'),
            (r'\bmethodolgy\b', 'methodology', 'Misspelling: Missing "o" in "methodology"', 'HIGH'),
            (r'\bsignificient\b', 'significant', 'Misspelling: "significant" ends with "-ant"', 'HIGH'),
            (r'\befficent\b', 'efficient', 'Misspelling: "efficient" requires "-icient"', 'HIGH'),
            (r'\bartifical\b', 'artificial', 'Misspelling: Missing "i" in "artificial"', 'HIGH'),
            (r'\bintelegence\b', 'intelligence', 'Misspelling: "intelligence" has double "l"', 'HIGH'),
            (r'\balgoritm\b', 'algorithm', 'Misspelling: "algorithm" requires "th"', 'HIGH'),

            # 2. Grammar, Articles & Comparatives
            (r'\ba\s+hour\b', 'an hour', 'Article grammar error: Use "an" before silent "h" sound in "hour"', 'HIGH'),
            (r'\ba\s+honest\b', 'an honest', 'Article grammar error: Use "an" before silent "h" in "honest"', 'HIGH'),
            (r'\ba\s+honor\b', 'an honor', 'Article grammar error: Use "an" before silent "h" in "honor"', 'HIGH'),
            (r'\ban\s+university\b', 'a university', 'Article grammar error: "university" begins with consonant sound /ju:/', 'HIGH'),
            (r'\ban\s+european\b', 'a European', 'Article grammar error: "European" begins with consonant sound /ju:/', 'HIGH'),
            (r'\ban\s+unique\b', 'a unique', 'Article grammar error: "unique" begins with consonant sound /ju:/', 'HIGH'),
            (r'\bmore\s+better\b', 'better / much better', 'Grammar redundancy: Double comparative ("more better")', 'HIGH'),
            (r'\bmore\s+easier\b', 'easier', 'Grammar redundancy: Double comparative ("more easier")', 'HIGH'),
            (r'\bmore\s+faster\b', 'faster', 'Grammar redundancy: Double comparative ("more faster")', 'HIGH'),
            (r'\birregardless\b', 'regardless', 'Non-standard usage: Use "regardless" in academic writing', 'HIGH'),
            (r'\bcould\s+of\b', 'could have', 'Grammar error: Use modal auxiliary "could have", not "could of"', 'HIGH'),
            (r'\bshould\s+of\b', 'should have', 'Grammar error: Use modal auxiliary "should have", not "should of"', 'HIGH'),
            (r'\bwould\s+of\b', 'would have', 'Grammar error: Use modal auxiliary "would have", not "would of"', 'HIGH'),
            (r'\bto\s+loose\s+(?:data|accuracy|information|weight|control)\b', 'to lose data/accuracy', 'Word confusion: "loose" (unfastened) vs "lose" (misplace or fail to keep)', 'HIGH'),
            (r'\bhave\s+an\s+affect\s+on\b', 'have an effect on', 'Word confusion: "effect" is the noun meaning outcome/impact, "affect" is the verb', 'HIGH'),
        ]

    def audit_document(self, text: str) -> Dict[str, Any]:
        """
        Rà soát toàn diện lỗi chính tả và ngữ pháp trên 100% văn bản đã tải lên.
        Hỗ trợ 2 ngôn ngữ: Tiếng Việt và Tiếng Anh.
        Trả về thống kê số lượng và danh mục chi tiết từng lỗi phục vụ gạch chân và xuất báo cáo.
        """
        if not text or not text.strip():
            return {
                "total_errors": 0,
                "vi_errors_count": 0,
                "en_errors_count": 0,
                "details": [],
                "summary_label": "Chưa phát hiện lỗi chính tả hoặc ngữ pháp trong văn bản."
            }

        details: List[Dict[str, Any]] = []
        error_id = 1
        seen_matches = set()

        # 1. Rà soát Tiếng Việt
        for pattern, replacement, explanation, severity in self.vi_spelling_pairs:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                m_start, m_end = match.start(), match.end()
                key = (m_start, m_end)
                if key in seen_matches:
                    continue
                seen_matches.add(key)

                start = max(0, m_start - 35)
                end = min(len(text), m_end + 35)
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
                    "severity": severity,
                    "char_start": m_start,
                    "char_end": m_end
                })
                error_id += 1

        # 2. Rà soát Tiếng Anh
        for pattern, replacement, explanation, severity in self.en_spelling_pairs:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                m_start, m_end = match.start(), match.end()
                key = (m_start, m_end)
                if key in seen_matches:
                    continue
                seen_matches.add(key)

                start = max(0, m_start - 35)
                end = min(len(text), m_end + 35)
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
                    "severity": severity,
                    "char_start": m_start,
                    "char_end": m_end
                })
                error_id += 1

        # Sắp xếp các lỗi theo thứ tự xuất hiện trong văn bản
        details.sort(key=lambda d: d.get("char_start", 0))
        # Cập nhật lại ID sau khi sort
        for idx, d in enumerate(details):
            d["id"] = idx + 1

        vi_count = sum(1 for d in details if d["lang"] == "vi")
        en_count = sum(1 for d in details if d["lang"] == "en")
        total_errors = len(details)

        summary_label = (
            f"Phát hiện {total_errors} lỗi chính tả & ngữ pháp (Tiếng Việt: {vi_count}, Tiếng Anh: {en_count})"
            if total_errors > 0
            else "Chưa phát hiện lỗi chính tả hoặc ngữ pháp trong văn bản (100% Đạt chuẩn)."
        )

        return {
            "total_errors": total_errors,
            "vi_errors_count": vi_count,
            "en_errors_count": en_count,
            "details": details[:150], # Lưu tối đa 150 lỗi chi tiết
            "summary_label": summary_label
        }

spell_grammar_engine = SpellGrammarEngine()
