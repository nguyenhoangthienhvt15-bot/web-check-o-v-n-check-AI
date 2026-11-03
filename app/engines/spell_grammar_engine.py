"""
SYNAPES ADVANCED DUAL-LINGUAL SPELL & GRAMMAR FORENSIC ENGINE (TIẾNG VIỆT & TIẾNG ANH)
Hệ thống rà soát và kiểm định lỗi chính tả, cấu trúc âm tiết, ngữ pháp và thể thức học thuật chuyên sâu 2 ngôn ngữ (VI - EN).
Đã loại bỏ hoàn toàn tiếng Trung Quốc theo quy chuẩn cập nhật mới.
Áp dụng tiêu chuẩn ngữ liệu học thuật Viện Ngôn ngữ học / Bộ GD&ĐT (NĐ 30/2020/NĐ-CP)
và tiêu chuẩn văn phong học thuật quốc tế IEEE / APA / Chicago Manual of Style.
Quét 100% toàn văn tài liệu người dùng tải lên.
"""

import re
from typing import List, Dict, Any, Tuple, Set


class SpellGrammarEngine:
    def __init__(self):
        self._init_vietnamese_rules()
        self._init_english_rules()
        self._init_phonotactic_patterns()

    def _init_vietnamese_rules(self):
        """
        Quy chuẩn đối soát chính tả, thuật ngữ Hán-Việt, ngữ pháp & văn phong Tiếng Việt học thuật.
        """
        self.vi_spelling_pairs: List[Tuple[str, str, str, str]] = [
            # 1. Phụ âm đầu s/x, ch/tr, d/gi/r, l/n & Phụ âm cuối c/t, n/ng, p/t
            (r'\bchuẩn\s+sát\b', 'chuẩn xác', 'Lỗi dùng sai phụ âm cuối t/c ("chuẩn xác" nghĩa là đúng đắn, chính xác)', 'HIGH'),
            (r'\bbổ\s+xung\b', 'bổ sung', 'Lỗi nhầm lẫn phụ âm đầu x/s ("bổ sung" nghĩa là thêm vào cho đầy đủ)', 'HIGH'),
            (r'\bsắp\s+sếp\b', 'sắp xếp', 'Lỗi nhầm lẫn phụ âm đầu s/x ("sắp xếp" theo trật tự, bố cục)', 'HIGH'),
            (r'\bxơ\s+sài\b', 'sơ sài', 'Lỗi nhầm lẫn phụ âm đầu x/s ("sơ sài" nghĩa là đơn giản, thiếu thấu đáo)', 'MEDIUM'),
            (r'\bcọ\s+sát\b', 'cọ xát', 'Lỗi nhầm lẫn phụ âm đầu s/x ("cọ xát" mang tính tương tác hoặc ma sát)', 'HIGH'),
            (r'\bxuất\s+xắc\b', 'xuất sắc', 'Lỗi nhầm lẫn phụ âm đầu x/s ("xuất sắc" nghĩa là vượt trội, ưu tú)', 'HIGH'),
            (r'\bchính\s+sác\b', 'chính xác', 'Lỗi nhầm lẫn phụ âm đầu s/x ("chính xác" là từ chuẩn)', 'HIGH'),
            (r'\bchia\s+xẻ\b', 'chia sẻ', 'Lỗi nhầm lẫn phụ âm đầu x/s ("chia sẻ" thông tin, dữ liệu)', 'HIGH'),
            (r'\bgiành\s+dật\b', 'giành giật', 'Lỗi nhầm lẫn phụ âm đầu d/gi ("giành giật")', 'MEDIUM'),
            (r'\bxăm\s+xoi\b', 'săm soi', 'Lỗi nhầm lẫn phụ âm đầu x/s ("săm soi")', 'MEDIUM'),
            (r'\bxơ\s+suất\b', 'sơ suất', 'Lỗi nhầm lẫn phụ âm đầu x/s ("sơ suất" trong quy trình thực nghiệm)', 'HIGH'),
            (r'\bđường\s+xá\b', 'đường sá', 'Lỗi nhầm lẫn phụ âm x/s trong từ ghép ("đường sá")', 'MEDIUM'),
            (r'\btrao\s+chuốt\b', 'trau chuốt', 'Lỗi nhầm lẫn nguyên âm ao/au ("trau chuốt" câu chữ)', 'MEDIUM'),
            (r'\bchăn\s+chở\b', 'trăn trở', 'Lỗi nhầm lẫn phụ âm đầu ch/tr ("trăn trở" về bài toán nghiên cứu)', 'HIGH'),
            (r'\bdè\s+xẻn\b', 'dè sẻn', 'Lỗi nhầm lẫn phụ âm x/s ("dè sẻn")', 'MEDIUM'),
            (r'\brút\s+cuộc\b', 'rốt cuộc', 'Lỗi biến âm phương ngữ ("rốt cuộc" là từ chuẩn biểu thị kết quả cuối cùng)', 'MEDIUM'),
            (r'\bdấu\s+diếm\b', 'giấu giếm', 'Lỗi nhầm lẫn phụ âm đầu d/gi ("giấu giếm")', 'HIGH'),
            (r'\blăng\s+xuất\b', 'năng suất', 'Lỗi nhầm lẫn phụ âm l/n và x/s ("năng suất")', 'HIGH'),
            (r'\bnăng\s+xuất\b', 'năng suất', 'Lỗi nhầm lẫn phụ âm x/s ("năng suất" nghĩa là hiệu quả tạo ra trên đơn vị)', 'HIGH'),
            (r'\bhiệu\s+xuất\b', 'hiệu suất', 'Lỗi nhầm lẫn phụ âm x/s ("hiệu suất" hệ thống)', 'HIGH'),
            (r'\btần\s+xuất\b', 'tần suất', 'Lỗi nhầm lẫn phụ âm x/s ("tần suất" xuất hiện)', 'HIGH'),
            (r'\bxác\s+xuất\b', 'xác suất', 'Lỗi nhầm lẫn phụ âm x/s ("xác suất" thống kê)', 'HIGH'),
            (r'\bsác\s+suất\b', 'xác suất', 'Lỗi nhầm lẫn phụ âm s/x ("xác suất" thống kê)', 'HIGH'),
            (r'\bsác\s+thực\b', 'xác thực', 'Lỗi nhầm lẫn phụ âm s/x ("xác thực" dữ liệu)', 'HIGH'),
            (r'\bsử\s+lý\b', 'xử lý', 'Lỗi nhầm lẫn phụ âm đầu s/x ("xử lý" dữ liệu/thông tin)', 'HIGH'),
            (r'\bxử\s+dụng\b', 'sử dụng', 'Lỗi nhầm lẫn phụ âm đầu x/s ("sử dụng" công cụ/phương pháp)', 'HIGH'),
            (r'\bxản\s+xuất\b', 'sản xuất', 'Lỗi nhầm lẫn phụ âm đầu x/s ("sản xuất")', 'HIGH'),
            (r'\bsản\s+suất\b', 'sản xuất', 'Lỗi nhầm lẫn phụ âm đầu s/x ("sản xuất")', 'HIGH'),
            (r'\bkiểm\s+xoát\b', 'kiểm soát', 'Lỗi nhầm lẫn phụ âm x/s ("kiểm soát" biến số)', 'HIGH'),
            (r'\bđối\s+xoát\b', 'đối soát', 'Lỗi nhầm lẫn phụ âm x/s ("đối soát" dữ liệu)', 'HIGH'),
            (r'\bkhảo\s+xát\b', 'khảo sát', 'Lỗi nhầm lẫn phụ âm x/s ("khảo sát" thực nghiệm)', 'HIGH'),
            (r'\bxâu\s+sắc\b', 'sâu sắc', 'Lỗi nhầm lẫn phụ âm đầu x/s ("sâu sắc")', 'HIGH'),
            (r'\bchung\s+thực\b', 'trung thực', 'Lỗi phụ âm đầu ch/tr ("trung thực" học thuật)', 'HIGH'),
            (r'\bchi\s+thức\b', 'tri thức', 'Lỗi phụ âm đầu ch/tr ("tri thức" khoa học)', 'HIGH'),
            (r'\bchình\s+bày\b', 'trình bày', 'Lỗi phụ âm đầu ch/tr ("trình bày" luận điểm)', 'HIGH'),
            (r'\bquá\s+chình\b', 'quá trình', 'Lỗi phụ âm đầu ch/tr ("quá trình" nghiên cứu)', 'HIGH'),
            (r'\bchương\s+chình\b', 'chương trình', 'Lỗi phụ âm ch/tr ("chương trình")', 'HIGH'),
            (r'\bphát\s+chiển\b', 'phát triển', 'Lỗi phụ âm ch/tr ("phát triển")', 'HIGH'),
            (r'\btriển\s+khai\b' if False else r'\bchiển\s+khai\b', 'triển khai', 'Lỗi phụ âm đầu ch/tr ("triển khai" mô hình)', 'HIGH'),
            (r'\bchích\s+dẫn\b', 'trích dẫn', 'Lỗi phụ âm đầu ch/tr ("trích dẫn" tài liệu tham khảo)', 'HIGH'),
            (r'\bchọng\s+tâm\b', 'trọng tâm', 'Lỗi phụ âm đầu ch/tr ("trọng tâm" nghiên cứu)', 'HIGH'),
            (r'\bchực\s+tiếp\b', 'trực tiếp', 'Lỗi phụ âm đầu ch/tr ("trực tiếp")', 'HIGH'),
            (r'\bchừu\s+tượng\b', 'trừu tượng', 'Lỗi phụ âm đầu ch/tr ("trừu tượng")', 'HIGH'),
            (r'\bnguồng\s+gốc\b', 'nguồn gốc', 'Lỗi phụ âm cuối ng/n ("nguồn gốc" dữ liệu)', 'HIGH'),
            (r'\bnghiên\s+kíu\b', 'nghiên cứu', 'Lỗi chính tả viết sai vần ("nghiên cứu" khoa học)', 'HIGH'),
            (r'\bnguyên\s+cứu\b', 'nghiên cứu', 'Lỗi nhầm âm đầu/vần ("nghiên cứu" thay vì "nguyên cứu")', 'HIGH'),
            (r'\bphương\s+fáp\b', 'phương pháp', 'Lỗi viết tắt không chuẩn mực ("phương pháp")', 'HIGH'),
            (r'\bthực\s+ngiệm\b', 'thực nghiệm', 'Lỗi quy tắc chính tả ngh/ng trước i/e/ê ("thực nghiệm")', 'HIGH'),
            (r'\bý\s+ngĩa\b', 'ý nghĩa', 'Lỗi quy tắc chính tả ngh/ng trước i/e/ê ("ý nghĩa")', 'HIGH'),
            (r'\bkhái\s+liệm\b', 'khái niệm', 'Lỗi nhầm lẫn phụ âm đầu l/n ("khái niệm")', 'HIGH'),
            (r'\blội\s+dung\b', 'nội dung', 'Lỗi nhầm lẫn phụ âm đầu l/n ("nội dung")', 'HIGH'),
            (r'\blăng\s+lực\b', 'năng lực', 'Lỗi nhầm lẫn phụ âm đầu l/n ("năng lực")', 'HIGH'),
            (r'\bkỹ\s+lăng\b', 'kỹ năng', 'Lỗi nhầm lẫn phụ âm l/n ("kỹ năng")', 'HIGH'),
            (r'\blền\s+tảng\b', 'nền tảng', 'Lỗi nhầm lẫn phụ âm đầu l/n ("nền tảng")', 'HIGH'),
            (r'\bgiữ\s+liệu\b', 'dữ liệu', 'Lỗi nhầm lẫn phụ âm đầu gi/d ("dữ liệu" nghiên cứu)', 'HIGH'),
            (r'\bdả\s+thuyết\b', 'giả thuyết', 'Lỗi nhầm lẫn phụ âm đầu d/gi ("giả thuyết" khoa học)', 'HIGH'),
            (r'\bdải\s+quyết\b', 'giải quyết', 'Lỗi nhầm lẫn phụ âm đầu d/gi ("giải quyết" vấn đề)', 'HIGH'),
            (r'\bbắt\s+buột\b', 'bắt buộc', 'Lỗi nhầm lẫn phụ âm cuối t/c ("bắt buộc")', 'HIGH'),
            (r'\bràng\s+buột\b', 'ràng buộc', 'Lỗi nhầm lẫn phụ âm cuối t/c ("ràng buộc")', 'HIGH'),
            (r'\bvược\s+trội\b', 'vượt trội', 'Lỗi nhầm lẫn phụ âm cuối c/t ("vượt trội")', 'HIGH'),
            (r'\bđặt\s+biệt\b', 'đặc biệt', 'Lỗi nhầm lẫn phụ âm cuối t/c ("đặc biệt")', 'HIGH'),
            (r'\bđặc\s+ra\b', 'đặt ra', 'Lỗi nhầm lẫn phụ âm cuối c/t ("đặt ra" vấn đề)', 'HIGH'),
            (r'\bmặc\s+khác\b', 'mặt khác', 'Lỗi nhầm lẫn phụ âm cuối c/t ("mặt khác")', 'HIGH'),
            (r'\bmặt\s+dù\b', 'mặc dù', 'Lỗi nhầm lẫn phụ âm cuối t/c ("mặc dù")', 'HIGH'),
            (r'\bthiếc\s+lập\b', 'thiết lập', 'Lỗi nhầm lẫn phụ âm cuối c/t ("thiết lập")', 'HIGH'),
            (r'\bchặc\s+chẽ\b', 'chặt chẽ', 'Lỗi nhầm lẫn phụ âm cuối c/t ("chặt chẽ")', 'HIGH'),
            (r'\bchặt\s+chẻ\b', 'chặt chẽ', 'Lỗi nhầm thanh hỏi/ngã ("chặt chẽ")', 'HIGH'),
            (r'\bkhuân\s+khổ\b', 'khuôn khổ', 'Lỗi nhầm vần uân/uôn ("khuôn khổ")', 'MEDIUM'),
            (r'\bkhuân\s+mẫu\b', 'khuôn mẫu', 'Lỗi nhầm vần uân/uôn ("khuôn mẫu")', 'MEDIUM'),

            # 2. Lỗi thanh Hỏi / Ngã trong văn bản học thuật
            (r'\bsữa\s+chữa\b', 'sửa chữa', 'Lỗi thanh điệu hỏi/ngã ("sửa chữa")', 'HIGH'),
            (r'\bchỉnh\s+sữa\b', 'chỉnh sửa', 'Lỗi thanh điệu hỏi/ngã ("chỉnh sửa")', 'HIGH'),
            (r'\bkỷ\s+thuật\b', 'kỹ thuật', 'Lỗi thanh điệu hỏi/ngã ("kỹ thuật" mang thanh ngã)', 'HIGH'),
            (r'\bkỉ\s+thuật\b', 'kỹ thuật', 'Lỗi thanh điệu hỏi/ngã ("kỹ thuật" mang thanh ngã)', 'HIGH'),
            (r'\bkỷ\s+năng\b', 'kỹ năng', 'Lỗi thanh điệu hỏi/ngã ("kỹ năng" mang thanh ngã)', 'HIGH'),
            (r'\bkỉ\s+năng\b', 'kỹ năng', 'Lỗi thanh điệu hỏi/ngã ("kỹ năng" mang thanh ngã)', 'HIGH'),
            (r'\bthực\s+tiển\b', 'thực tiễn', 'Lỗi thanh điệu hỏi/ngã ("thực tiễn" mang thanh ngã)', 'HIGH'),
            (r'\btiêu\s+chuẫn\b', 'tiêu chuẩn', 'Lỗi thanh điệu hỏi/ngã ("tiêu chuẩn" mang thanh hỏi)', 'HIGH'),
            (r'\bphỗ\s+biến\b', 'phổ biến', 'Lỗi thanh điệu hỏi/ngã ("phổ biến" mang thanh hỏi)', 'HIGH'),
            (r'\bbiễu\s+diễn\b', 'biểu diễn', 'Lỗi thanh điệu hỏi/ngã ("biểu diễn")', 'HIGH'),
            (r'\bbiểu\s+diển\b', 'biểu diễn', 'Lỗi thanh điệu hỏi/ngã ("biểu diễn")', 'HIGH'),
            (r'\bdiển\s+ra\b', 'diễn ra', 'Lỗi thanh điệu hỏi/ngã ("diễn ra")', 'HIGH'),
            (r'\bhổ\s+trợ\b', 'hỗ trợ', 'Lỗi thanh điệu hỏi/ngã ("hỗ trợ" mang thanh ngã)', 'HIGH'),
            (r'\bmẩu\s+thử\b', 'mẫu thử', 'Lỗi thanh điệu hỏi/ngã ("mẫu thử" nghiên cứu)', 'HIGH'),
            (r'\bdử\s+liệu\b', 'dữ liệu', 'Lỗi thanh điệu hỏi/ngã ("dữ liệu" mang thanh ngã)', 'HIGH'),
            (r'\blỉnh\s+vực\b', 'lĩnh vực', 'Lỗi thanh điệu hỏi/ngã ("lĩnh vực" mang thanh ngã)', 'HIGH'),
            (r'\bngử\s+nghĩa\b', 'ngữ nghĩa', 'Lỗi thanh điệu hỏi/ngã ("ngữ nghĩa")', 'HIGH'),
            (r'\bngử\s+pháp\b', 'ngữ pháp', 'Lỗi thanh điệu hỏi/ngã ("ngữ pháp")', 'HIGH'),
            (r'\bảnh\s+hưỡng\b', 'ảnh hưởng', 'Lỗi thanh điệu hỏi/ngã ("ảnh hưởng" mang thanh hỏi)', 'HIGH'),
            (r'\bbão\s+đảm\b', 'bảo đảm', 'Lỗi thanh điệu hỏi/ngã ("bảo đảm" mang thanh hỏi)', 'HIGH'),
            (r'\bquãn\s+lý\b', 'quản lý', 'Lỗi thanh điệu hỏi/ngã ("quản lý" mang thanh hỏi)', 'HIGH'),
            (r'\bxữ\s+lý\b', 'xử lý', 'Lỗi thanh điệu hỏi/ngã ("xử lý" mang thanh hỏi)', 'HIGH'),
            (r'\bthẫm\s+định\b', 'thẩm định', 'Lỗi thanh điệu hỏi/ngã ("thẩm định" mang thanh hỏi)', 'HIGH'),
            (r'\bkiễm\s+tra\b', 'kiểm tra', 'Lỗi thanh điệu hỏi/ngã ("kiểm tra" mang thanh hỏi)', 'HIGH'),
            (r'\bkiễm\s+định\b', 'kiểm định', 'Lỗi thanh điệu hỏi/ngã ("kiểm định" mang thanh hỏi)', 'HIGH'),
            (r'\bphãn\s+biện\b', 'phản biện', 'Lỗi thanh điệu hỏi/ngã ("phản biện" mang thanh hỏi)', 'HIGH'),
            (r'\btỗng\s+hợp\b', 'tổng hợp', 'Lỗi thanh điệu hỏi/ngã ("tổng hợp" mang thanh hỏi)', 'HIGH'),
            (r'\bcụ\s+thễ\b', 'cụ thể', 'Lỗi thanh điệu hỏi/ngã ("cụ thể" mang thanh hỏi)', 'HIGH'),
            (r'\bkết\s+quả\s+khã\s+quan\b', 'kết quả khả quan', 'Lỗi thanh điệu hỏi/ngã ("khả quan" mang thanh hỏi)', 'HIGH'),
            (r'\bkhã\s+năng\b', 'khả năng', 'Lỗi thanh điệu hỏi/ngã ("khả năng" mang thanh hỏi)', 'HIGH'),

            # 3. Thuật ngữ Hán - Việt & Ngữ nghĩa học thuật
            (r'\bvô\s+hình\s+chung\b', 'vô hình trung', 'Lỗi thành ngữ Hán-Việt ("vô hình trung" nghĩa là ngẫu nhiên biến thành)', 'HIGH'),
            (r'\bchuẩn\s+đoán\b', 'chẩn đoán', 'Lỗi thuật ngữ chuyên ngành ("chẩn đoán" mới là từ chuẩn xác)', 'HIGH'),
            (r'\bthăm\s+quan\b', 'tham quan', 'Lỗi từ Hán-Việt ("tham quan" nghĩa là đi xem tận mắt, "thăm quan" là sai)', 'HIGH'),
            (r'\bsáng\s+lạng\b', 'xán lạn', 'Lỗi biến âm ("xán lạn" nghĩa là rạng rỡ, tươi sáng)', 'HIGH'),
            (r'\bchắp\s+bút\b', 'chấp bút', 'Lỗi thuật ngữ ("chấp bút" nghĩa là khởi thảo văn bản)', 'HIGH'),
            (r'\bsát\s+nhập\b', 'sáp nhập', 'Lỗi thuật ngữ hành chính/pháp lý ("sáp nhập" mới là từ chuẩn)', 'HIGH'),
            (r'\btựu\s+chung\b', 'tựu trung', 'Lỗi thành ngữ học thuật ("tựu trung" nghĩa là tóm lại, cốt lõi là)', 'HIGH'),
            (r'\bkhuyến\s+mãi\b' if False else r'\bkhuyến\s+mại\s+cho\s+người\s+tiêu\s+dùng\b', 'khuyến mãi cho người tiêu dùng', 'Lỗi thuật ngữ thương mại ("khuyến mãi" hướng tới người mua, "khuyến mại" hướng tới đại lý)', 'LOW'),
            (r'\bđề\s+cập\s+đến\s+vấn\s+đề\s+này\s+một\s+cách\s+tương\s+đối\s+hoàn\s+toàn\b', 'đề cập toàn diện đến vấn đề này', 'Lỗi mâu thuẫn ngữ nghĩa ("tương đối" đối lập với "hoàn toàn")', 'MEDIUM'),

            # 4. Lỗi Ngữ pháp, Trùng lặp Liên từ & Văn phong Khoa học (Bộ GD&ĐT)
            (r'\bnghiên\s+cứu\s+này\s+nhằm\s+mục\s+đích\s+nhằm\b', 'nghiên cứu này nhằm mục đích', 'Lỗi lặp từ liên tiếp ("nhằm... nhằm")', 'HIGH'),
            (r'\bmặc\s+dù\s+[\w\s,]{2,40}\s+nhưng\s+mà\s+lại\b', 'mặc dù... nhưng...', 'Lỗi ngữ pháp rườm rà (Thừa cụm liên từ "mà lại")', 'MEDIUM'),
            (r'\btuy\s+nhiên\s+nhưng\b', 'tuy nhiên (hoặc: nhưng)', 'Lỗi trùng lặp liên từ tương phản (Chỉ dùng một trong hai)', 'HIGH'),
            (r'\bnhưng\s+tuy\s+nhiên\b', 'tuy nhiên (hoặc: nhưng)', 'Lỗi trùng lặp liên từ tương phản (Chỉ dùng một trong hai)', 'HIGH'),
            (r'\bdo\s+vì\b', 'do (hoặc: vì)', 'Lỗi trùng lặp liên từ chỉ nguyên nhân (Chỉ dùng "do" hoặc "vì")', 'HIGH'),
            (r'\bbởi\s+vì\s+do\b', 'bởi vì (hoặc: do)', 'Lỗi trùng lặp liên từ chỉ nguyên nhân', 'HIGH'),
            (r'\bđể\s+nhằm\b', 'nhằm (hoặc: để)', 'Lỗi trùng lặp liên từ chỉ mục đích (Chỉ dùng "để" hoặc "nhằm")', 'MEDIUM'),
            (r'\bnhằm\s+để\b', 'nhằm (hoặc: để)', 'Lỗi trùng lặp liên từ chỉ mục đích (Chỉ dùng "nhằm" hoặc "để")', 'MEDIUM'),
            (r'\bngoài\s+ra\s+thêm\s+vào\s+đó\b', 'ngoài ra (hoặc: thêm vào đó)', 'Lỗi trùng lặp cụm chuyển tiếp câu trong văn phong học thuật', 'MEDIUM'),
            (r'\bqua\s+đó\s+từ\s+đó\b', 'qua đó (hoặc: từ đó)', 'Lỗi trùng lặp liên từ kết luận', 'MEDIUM'),
            (r'\bcực\s+kỳ\b', 'đáng kể / ở mức độ cao', 'Lỗi văn phong: Từ "cực kỳ" mang tính khẩu ngữ, nên thay bằng từ học thuật trung tính', 'MEDIUM'),
            (r'\bcực\s+kì\b', 'đáng kể / ở mức độ cao', 'Lỗi văn phong: Từ "cực kì" mang tính khẩu ngữ, nên thay bằng từ học thuật trung tính', 'MEDIUM'),
            (r'\brất\s+là\b', 'rất / đáng kể', 'Lỗi văn phong: Cụm "rất là" mang tính văn nói, không phù hợp văn bản khoa học', 'MEDIUM'),
            (r'\bnói\s+chung\s+là\b', 'nhìn chung / tổng quan lại', 'Lỗi văn phong: Cụm "nói chung là" mang tính khẩu ngữ, nên dùng "nhìn chung"', 'MEDIUM'),
            (r'\bthì\s+là\s+mà\b', 'do đó / cụ thể là', 'Lỗi văn phong khẩu ngữ trong bài viết học thuật', 'HIGH'),
        ]

    def _init_english_rules(self):
        """
        Quy chuẩn đối soát chính tả, ngữ pháp & văn phong Tiếng Anh học thuật (IEEE / APA / Chicago).
        """
        self.en_spelling_pairs: List[Tuple[str, str, str, str]] = [
            # 1. Academic & Technical Misspellings
            (r'\babberation\b', 'aberration', 'Misspelling: "aberration" has one "b" and double "r"', 'HIGH'),
            (r'\babscence\b', 'absence', 'Misspelling: "absence" is spelled with "s", not "sc"', 'HIGH'),
            (r'\baccomodate\b', 'accommodate', 'Misspelling: "accommodate" requires double "c" and double "m"', 'HIGH'),
            (r'\baccomodation\b', 'accommodation', 'Misspelling: "accommodation" requires double "c" and double "m"', 'HIGH'),
            (r'\bachive\b', 'achieve', 'Misspelling: "achieve" requires "i" before "e"', 'HIGH'),
            (r'\bachievment\b', 'achievement', 'Misspelling: "achievement" retains the "e" after "v"', 'HIGH'),
            (r'\backnowlege\b', 'acknowledge', 'Misspelling: Missing "d" in "acknowledge"', 'HIGH'),
            (r'\backnowlegement\b', 'acknowledgement', 'Misspelling: Missing "d" in "acknowledgement"', 'HIGH'),
            (r'\baquire\b', 'acquire', 'Misspelling: "acquire" requires "cq"', 'HIGH'),
            (r'\balgoritm\b', 'algorithm', 'Misspelling: "algorithm" requires "th"', 'HIGH'),
            (r'\banalize\b', 'analyze', 'Misspelling: "analyze" (US) or "analyse" (UK) is standard academic spelling', 'HIGH'),
            (r'\baparent\b', 'apparent', 'Misspelling: "apparent" requires double "p"', 'HIGH'),
            (r'\baproximate\b', 'approximate', 'Misspelling: "approximate" requires double "p"', 'HIGH'),
            (r'\bapproximatly\b', 'approximately', 'Misspelling: Missing "e" in "approximately"', 'HIGH'),
            (r'\barguement\b', 'argument', 'Misspelling: "argument" drops the "e" from "argue"', 'HIGH'),
            (r'\bartifical\b', 'artificial', 'Misspelling: Missing "i" in "artificial"', 'HIGH'),
            (r'\bassymetry\b', 'asymmetry', 'Misspelling: "asymmetry" has one "s" and double "m"', 'HIGH'),
            (r'\bbeleive\b', 'believe', 'Misspelling: "believe" requires "i" before "e"', 'HIGH'),
            (r'\bcalender\b', 'calendar', 'Misspelling: "calendar" ends with "-ar"', 'HIGH'),
            (r'\bcatagory\b', 'category', 'Misspelling: "category" has an "e", not an "a", after "t"', 'HIGH'),
            (r'\bcollegue\b', 'colleague', 'Misspelling: "colleague" requires "-eague"', 'HIGH'),
            (r'\bcommited\b', 'committed', 'Misspelling: "committed" requires double "m" and double "t"', 'HIGH'),
            (r'\bcommitee\b', 'committee', 'Misspelling: "committee" requires double "m", double "t", and double "e"', 'HIGH'),
            (r'\bcomparision\b', 'comparison', 'Misspelling: "comparison" does not have an "i" after "r"', 'HIGH'),
            (r'\bcompatable\b', 'compatible', 'Misspelling: "compatible" ends with "-ible"', 'HIGH'),
            (r'\bconcieve\b', 'conceive', 'Rule: "e" before "i" after "c" ("conceive")', 'HIGH'),
            (r'\bconcious\b', 'conscious', 'Misspelling: "conscious" requires "sc"', 'HIGH'),
            (r'\bconscensus\b', 'consensus', 'Misspelling: "consensus" is spelled with "s", not "sc"', 'HIGH'),
            (r'\bconsistant\b', 'consistent', 'Misspelling: "consistent" ends with "-ent"', 'HIGH'),
            (r'\binconsistant\b', 'inconsistent', 'Misspelling: "inconsistent" ends with "-ent"', 'HIGH'),
            (r'\bcontraversy\b', 'controversy', 'Misspelling: "controversy" has an "o" after "tr"', 'HIGH'),
            (r'\bcorrellation\b', 'correlation', 'Misspelling: "correlation" has double "r" and single "l"', 'HIGH'),
            (r'\bcorelation\b', 'correlation', 'Misspelling: "correlation" requires double "r"', 'HIGH'),
            (r'\bcritisism\b', 'criticism', 'Misspelling: "criticism" is spelled with "c", not "s"', 'HIGH'),
            (r'\bcurricullum\b', 'curriculum', 'Misspelling: "curriculum" has a single "l"', 'HIGH'),
            (r'\bdecieve\b', 'deceive', 'Rule: "e" before "i" after "c" ("deceive")', 'HIGH'),
            (r'\bdefinately\b', 'definitely', 'Misspelling: "definitely" is spelled with "-ite-", not "-ate-"', 'HIGH'),
            (r'\bdefinitly\b', 'definitely', 'Misspelling: Missing "e" in "definitely"', 'HIGH'),
            (r'\bdependance\b', 'dependence', 'Misspelling: "dependence" ends with "-ence"', 'HIGH'),
            (r'\bdevelopement\b', 'development', 'Misspelling: "development" has no "e" after "p"', 'HIGH'),
            (r'\bdiffrence\b', 'difference', 'Misspelling: Missing "e" in "difference"', 'HIGH'),
            (r'\bdilema\b', 'dilemma', 'Misspelling: "dilemma" requires double "m"', 'HIGH'),
            (r'\bdisapear\b', 'disappear', 'Misspelling: "disappear" requires single "s" and double "p"', 'HIGH'),
            (r'\bdisapoint\b', 'disappoint', 'Misspelling: "disappoint" requires double "p"', 'HIGH'),
            (r'\bdiscrepency\b', 'discrepancy', 'Misspelling: "discrepancy" ends with "-ancy"', 'HIGH'),
            (r'\befficent\b', 'efficient', 'Misspelling: "efficient" requires "-icient"', 'HIGH'),
            (r'\bembarass\b', 'embarrass', 'Misspelling: "embarrass" has double "r" and double "s"', 'HIGH'),
            (r'\bempahsis\b', 'emphasis', 'Misspelling: "emphasis" is the correct spelling', 'HIGH'),
            (r'\benviroment\b', 'environment', 'Misspelling: Missing "n" before "m" in "environment"', 'HIGH'),
            (r'\benviromental\b', 'environmental', 'Misspelling: Missing "n" before "m" in "environmental"', 'HIGH'),
            (r'\bequiptment\b', 'equipment', 'Misspelling: "equipment" has no "t" after "p"', 'HIGH'),
            (r'\bexagerate\b', 'exaggerate', 'Misspelling: "exaggerate" requires double "g"', 'HIGH'),
            (r'\bexcellance\b', 'excellence', 'Misspelling: "excellence" ends with "-ence"', 'HIGH'),
            (r'\bexistance\b', 'existence', 'Misspelling: "existence" ends with "-ence"', 'HIGH'),
            (r'\bexperiance\b', 'experience', 'Misspelling: "experience" ends with "-ence"', 'HIGH'),
            (r'\bfascilitate\b', 'facilitate', 'Misspelling: "facilitate" is spelled with "c", not "sc"', 'HIGH'),
            (r'\bfeasable\b', 'feasible', 'Misspelling: "feasible" ends with "-ible"', 'HIGH'),
            (r'\bforiegn\b', 'foreign', 'Misspelling: "foreign" is spelled "-ei-"', 'HIGH'),
            (r'\bfourty\b', 'forty', 'Misspelling: "forty" drops the "u"', 'MEDIUM'),
            (r'\bfundemental\b', 'fundamental', 'Misspelling: "fundamental" has an "a" after "d"', 'HIGH'),
            (r'\bgeneraly\b', 'generally', 'Misspelling: "generally" requires double "l"', 'MEDIUM'),
            (r'\bgoverment\b', 'government', 'Misspelling: Missing "n" in "government"', 'HIGH'),
            (r'\bgrammer\b', 'grammar', 'Misspelling: "grammar" ends with "-ar"', 'HIGH'),
            (r'\bguarentee\b', 'guarantee', 'Misspelling: "guarantee" is spelled "guar-"', 'HIGH'),
            (r'\bharrass\b', 'harass', 'Misspelling: "harass" has one "r" and double "s"', 'HIGH'),
            (r'\bhiearchy\b', 'hierarchy', 'Misspelling: Missing "r" after "e" in "hierarchy"', 'HIGH'),
            (r'\bimmediatly\b', 'immediately', 'Misspelling: Missing "e" before "-ly" in "immediately"', 'HIGH'),
            (r'\bimplementaion\b', 'implementation', 'Misspelling: Missing "t" in "implementation"', 'HIGH'),
            (r'\bindependant\b', 'independent', 'Misspelling: "independent" ends with "-ent"', 'HIGH'),
            (r'\bindependantly\b', 'independently', 'Misspelling: "independently" ends with "-ently"', 'HIGH'),
            (r'\bindispensible\b', 'indispensable', 'Misspelling: "indispensable" ends with "-able"', 'HIGH'),
            (r'\binfluencial\b', 'influential', 'Misspelling: "influential" is spelled with "t", not "c"', 'HIGH'),
            (r'\binitally\b', 'initially', 'Misspelling: Missing "i" before "-ally" in "initially"', 'HIGH'),
            (r'\bintelegence\b', 'intelligence', 'Misspelling: "intelligence" requires double "l" and "-igence"', 'HIGH'),
            (r'\binteligence\b', 'intelligence', 'Misspelling: "intelligence" requires double "l"', 'HIGH'),
            (r'\bintergrate\b', 'integrate', 'Misspelling: "integrate" has no "r" before "g"', 'HIGH'),
            (r'\bintergration\b', 'integration', 'Misspelling: "integration" has no "r" before "g"', 'HIGH'),
            (r'\binterupt\b', 'interrupt', 'Misspelling: "interrupt" requires double "r"', 'HIGH'),
            (r'\birrelevent\b', 'irrelevant', 'Misspelling: "irrelevant" ends with "-ant"', 'HIGH'),
            (r'\bknowlege\b', 'knowledge', 'Misspelling: Missing "d" in "knowledge"', 'HIGH'),
            (r'\blabratory\b', 'laboratory', 'Misspelling: Missing "o" in "laboratory"', 'HIGH'),
            (r'\blibary\b', 'library', 'Misspelling: Missing first "r" in "library"', 'HIGH'),
            (r'\bmaintainance\b', 'maintenance', 'Misspelling: "maintenance" is spelled "-ten-"', 'HIGH'),
            (r'\bmanagment\b', 'management', 'Misspelling: Missing "e" after "g" in "management"', 'HIGH'),
            (r'\bmathmatics\b', 'mathematics', 'Misspelling: Missing "e" in "mathematics"', 'HIGH'),
            (r'\bmeasurment\b', 'measurement', 'Misspelling: Missing "e" after "r" in "measurement"', 'HIGH'),
            (r'\bmethodolgy\b', 'methodology', 'Misspelling: Missing "o" in "methodology"', 'HIGH'),
            (r'\bmispell\b', 'misspell', 'Misspelling: "misspell" requires double "s"', 'MEDIUM'),
            (r'\bneccessary\b', 'necessary', 'Misspelling: "necessary" has one "c" and double "s"', 'HIGH'),
            (r'\bunneccessary\b', 'unnecessary', 'Misspelling: "unnecessary" has one "c" and double "s"', 'HIGH'),
            (r'\bnoticable\b', 'noticeable', 'Misspelling: "noticeable" retains the "e"', 'MEDIUM'),
            (r'\boccurance\b', 'occurrence', 'Misspelling: "occurrence" requires double "r" and "-ence"', 'HIGH'),
            (r'\boccured\b', 'occurred', 'Misspelling: Past tense of "occur" doubles the "r" ("occurred")', 'HIGH'),
            (r'\bomision\b', 'omission', 'Misspelling: "omission" requires double "s"', 'HIGH'),
            (r'\bommision\b', 'omission', 'Misspelling: "omission" has one "m" and double "s"', 'HIGH'),
            (r'\boptimze\b', 'optimize', 'Misspelling: Missing "i" in "optimize"', 'HIGH'),
            (r'\borigional\b', 'original', 'Misspelling: "original" has no "o" after "i"', 'HIGH'),
            (r'\bpercieve\b', 'perceive', 'Rule: "e" before "i" after "c" ("perceive")', 'HIGH'),
            (r'\bperfromance\b', 'performance', 'Misspelling: Typo in "performance"', 'HIGH'),
            (r'\bperformence\b', 'performance', 'Misspelling: "performance" ends with "-ance"', 'HIGH'),
            (r'\bpermenant\b', 'permanent', 'Misspelling: "permanent" has an "a" after "m"', 'HIGH'),
            (r'\bpersistant\b', 'persistent', 'Misspelling: "persistent" ends with "-ent"', 'HIGH'),
            (r'\bphenomenom\b', 'phenomenon', 'Misspelling: Singular is "phenomenon" (ends with "n")', 'HIGH'),
            (r'\bplagarism\b', 'plagiarism', 'Misspelling: Missing "i" in "plagiarism"', 'HIGH'),
            (r'\bposession\b', 'possession', 'Misspelling: "possession" requires double "s" twice', 'HIGH'),
            (r'\bpreceed\b', 'precede', 'Misspelling: "precede" is spelled "-cede"', 'HIGH'),
            (r'\bpresense\b', 'presence', 'Misspelling: "presence" ends with "-ence"', 'HIGH'),
            (r'\bpriviledge\b', 'privilege', 'Misspelling: "privilege" has no "d"', 'HIGH'),
            (r'\bprobablity\b', 'probability', 'Misspelling: Missing "i" in "probability"', 'HIGH'),
            (r'\bpronounciation\b', 'pronunciation', 'Misspelling: "pronunciation" is spelled "-nun-", not "-noun-"', 'HIGH'),
            (r'\bpsuedo\b', 'pseudo', 'Misspelling: "pseudo" starts with "ps-eu-"', 'HIGH'),
            (r'\bpublically\b', 'publicly', 'Misspelling: "publicly" is standard academic English', 'MEDIUM'),
            (r'\bquestionaire\b', 'questionnaire', 'Misspelling: "questionnaire" requires double "n"', 'HIGH'),
            (r'\brecieve\b', 'receive', 'Rule: "e" before "i" after "c" ("receive")', 'HIGH'),
            (r'\brecieved\b', 'received', 'Rule: "e" before "i" after "c" ("received")', 'HIGH'),
            (r'\breccommend\b', 'recommend', 'Misspelling: "recommend" has one "c" and double "m"', 'HIGH'),
            (r'\brecomend\b', 'recommend', 'Misspelling: "recommend" requires double "m"', 'HIGH'),
            (r'\breferance\b', 'reference', 'Misspelling: "reference" ends with "-ence"', 'HIGH'),
            (r'\brefered\b', 'referred', 'Misspelling: "referred" doubles the "r"', 'HIGH'),
            (r'\brelevent\b', 'relevant', 'Misspelling: "relevant" ends with "-ant"', 'HIGH'),
            (r'\brepitition\b', 'repetition', 'Misspelling: "repetition" has an "e" after "p"', 'HIGH'),
            (r'\bresistence\b', 'resistance', 'Misspelling: "resistance" ends with "-ance"', 'HIGH'),
            (r'\brythm\b', 'rhythm', 'Misspelling: "rhythm" requires "h" after "r"', 'HIGH'),
            (r'\bseperate\b', 'separate', 'Misspelling: "separate" has an "a" in the middle, not an "e"', 'HIGH'),
            (r'\bseperately\b', 'separately', 'Misspelling: "separately" has an "a" after "p"', 'HIGH'),
            (r'\bsignificient\b', 'significant', 'Misspelling: "significant" ends with "-cant"', 'HIGH'),
            (r'\bsimiliar\b', 'similar', 'Misspelling: "similar" has no "i" after "l"', 'HIGH'),
            (r'\bstatisitcs\b', 'statistics', 'Misspelling: Typo in "statistics"', 'HIGH'),
            (r'\bsubsequant\b', 'subsequent', 'Misspelling: "subsequent" ends with "-ent"', 'HIGH'),
            (r'\bsuccesful\b', 'successful', 'Misspelling: "successful" requires double "c" and double "s"', 'HIGH'),
            (r'\bsuccessfull\b', 'successful', 'Misspelling: "successful" ends with a single "l"', 'HIGH'),
            (r'\bsucessful\b', 'successful', 'Misspelling: "successful" requires double "c"', 'HIGH'),
            (r'\bsufficent\b', 'sufficient', 'Misspelling: Missing "i" after "c" in "sufficient"', 'HIGH'),
            (r'\bsupercede\b', 'supersede', 'Misspelling: "supersede" is spelled with "s", not "c"', 'HIGH'),
            (r'\bsupress\b', 'suppress', 'Misspelling: "suppress" requires double "p"', 'HIGH'),
            (r'\bsuprise\b', 'surprise', 'Misspelling: Missing first "r" in "surprise"', 'HIGH'),
            (r'\btechnichal\b', 'technical', 'Misspelling: "technical" has no "h" after "c"', 'HIGH'),
            (r'\btemperture\b', 'temperature', 'Misspelling: Missing "a" in "temperature"', 'HIGH'),
            (r'\btendancy\b', 'tendency', 'Misspelling: "tendency" ends with "-ency"', 'HIGH'),
            (r'\btherefor\b', 'therefore', 'Misspelling: "therefore" ends with an "e"', 'HIGH'),
            (r'\bthreshhold\b', 'threshold', 'Misspelling: "threshold" has only one "h" in the middle', 'MEDIUM'),
            (r'\btransfered\b', 'transferred', 'Misspelling: "transferred" doubles the final "r"', 'HIGH'),
            (r'\btruely\b', 'truly', 'Misspelling: "truly" drops the "e"', 'MEDIUM'),
            (r'\bunforseen\b', 'unforeseen', 'Misspelling: Missing "e" after "r" in "unforeseen"', 'HIGH'),
            (r'\bunfortunatly\b', 'unfortunately', 'Misspelling: Missing "e" in "unfortunately"', 'HIGH'),
            (r'\buntill\b', 'until', 'Misspelling: "until" ends with a single "l"', 'MEDIUM'),
            (r'\bvarience\b', 'variance', 'Misspelling: "variance" ends with "-ance"', 'HIGH'),
            (r'\bvisable\b', 'visible', 'Misspelling: "visible" ends with "-ible"', 'HIGH'),
            (r'\bwether\b', 'whether', 'Misspelling: Missing "h" in "whether"', 'HIGH'),
            (r'\bwithold\b', 'withhold', 'Misspelling: "withhold" requires double "h"', 'HIGH'),

            # 2. Academic English Grammar, Uncountable Nouns & Subject-Verb Agreement (IEEE / APA)
            (r'\binformations\b', 'information', 'Grammar error: "information" is an uncountable noun in English and cannot be pluralized', 'HIGH'),
            (r'\bresearches\b', 'research / studies', 'Academic grammar: "research" is uncountable; use "research" or "studies"', 'HIGH'),
            (r'\bequipments\b', 'equipment', 'Grammar error: "equipment" is an uncountable noun and has no plural form', 'HIGH'),
            (r'\bevidences\b', 'evidence', 'Academic grammar: "evidence" is uncountable in standard academic prose', 'HIGH'),
            (r'\bknowledges\b', 'knowledge', 'Grammar error: "knowledge" is an uncountable noun', 'HIGH'),
            (r'\bsoftwares\b', 'software', 'Grammar error: "software" is uncountable; use "software" or "software packages"', 'HIGH'),
            (r'\bhardwares\b', 'hardware', 'Grammar error: "hardware" is an uncountable noun', 'HIGH'),
            (r'\bfeedbacks\b', 'feedback', 'Grammar error: "feedback" is an uncountable noun', 'HIGH'),
            (r'\badvices\b', 'advice', 'Grammar error: "advice" is an uncountable noun', 'HIGH'),
            (r'\ba\s+hour\b', 'an hour', 'Article grammar error: Use "an" before silent "h" in "hour"', 'HIGH'),
            (r'\ba\s+honest\b', 'an honest', 'Article grammar error: Use "an" before silent "h" in "honest"', 'HIGH'),
            (r'\ba\s+honor\b', 'an honor', 'Article grammar error: Use "an" before silent "h" in "honor"', 'HIGH'),
            (r'\ban\s+university\b', 'a university', 'Article grammar error: "university" begins with consonant sound /ju:/', 'HIGH'),
            (r'\ban\s+european\b', 'a European', 'Article grammar error: "European" begins with consonant sound /ju:/', 'HIGH'),
            (r'\ban\s+unique\b', 'a unique', 'Article grammar error: "unique" begins with consonant sound /ju:/', 'HIGH'),
            (r'\ban\s+useful\b', 'a useful', 'Article grammar error: "useful" begins with consonant sound /ju:/', 'HIGH'),
            (r'\bmore\s+better\b', 'better / much better', 'Grammar redundancy: Double comparative ("more better")', 'HIGH'),
            (r'\bmore\s+easier\b', 'easier', 'Grammar redundancy: Double comparative ("more easier")', 'HIGH'),
            (r'\bmore\s+faster\b', 'faster', 'Grammar redundancy: Double comparative ("more faster")', 'HIGH'),
            (r'\bmore\s+higher\b', 'higher', 'Grammar redundancy: Double comparative ("more higher")', 'HIGH'),
            (r'\bmore\s+accurate\s+than\s+more\b', 'more accurate than', 'Grammar redundancy in comparative clause', 'MEDIUM'),
            (r'\birregardless\b', 'regardless', 'Non-standard word: Use "regardless" in academic writing', 'HIGH'),
            (r'\bcould\s+of\b', 'could have', 'Grammar error: Use modal auxiliary "could have", not "could of"', 'HIGH'),
            (r'\bshould\s+of\b', 'should have', 'Grammar error: Use modal auxiliary "should have", not "should of"', 'HIGH'),
            (r'\bwould\s+of\b', 'would have', 'Grammar error: Use modal auxiliary "would have", not "would of"', 'HIGH'),
            (r'\bmust\s+of\b', 'must have', 'Grammar error: Use modal auxiliary "must have", not "must of"', 'HIGH'),
            (r'\bthis\s+(?:results|findings|methods|models|experiments|studies|approaches|parameters|factors|values)\b', 'these + plural noun', 'Determiner-noun number disagreement: "this" (singular) used before plural noun', 'HIGH'),
            (r'\bthese\s+(?:result|finding|method|model|experiment|study|approach|parameter|factor)\b', 'this + singular noun', 'Determiner-noun number disagreement: "these" (plural) used before singular noun', 'HIGH'),
            (r'\bmany\s+(?:information|research|evidence|equipment|knowledge|literature)\b', 'much / a large amount of', 'Quantifier error: "many" cannot modify uncountable nouns', 'HIGH'),
            (r'\bdepend\s+in\b', 'depend on', 'Preposition collocation error: Standard academic usage is "depend on"', 'HIGH'),
            (r'\bfocus\s+in\b', 'focus on', 'Preposition collocation error: Standard usage is "focus on"', 'MEDIUM'),
            (r'\baccording\s+with\b', 'according to / in accordance with', 'Preposition collocation error: Use "according to" or "in accordance with"', 'HIGH'),
            (r'\bdifferent\s+than\b', 'different from', 'Academic style (APA/IEEE): Prefer "different from" over "different than"', 'MEDIUM'),
            (r'\bsuperior\s+than\b', 'superior to', 'Comparative collocation error: "superior" takes preposition "to", not "than"', 'HIGH'),
            (r'\binferior\s+than\b', 'inferior to', 'Comparative collocation error: "inferior" takes preposition "to", not "than"', 'HIGH'),
            (r'\bprior\s+than\b', 'prior to', 'Preposition collocation error: "prior" takes "to", not "than"', 'HIGH'),
            (r'\bcapable\s+to\s+\w+\b', 'capable of + V-ing', 'Collocation error: Use "capable of [gerund]" instead of "capable to"', 'HIGH'),
            (r'\bto\s+loose\s+(?:data|accuracy|information|weight|control|precision)\b', 'to lose', 'Word confusion: "loose" (adjective) vs "lose" (verb)', 'HIGH'),
            (r'\bhave\s+an\s+affect\s+on\b', 'have an effect on', 'Word confusion: "effect" is the noun, "affect" is the verb', 'HIGH'),
        ]

    def _init_phonotactic_patterns(self):
        """
        Khởi tạo bộ quy tắc kiểm tra hình thái âm tiết Tiếng Việt (Vietnamese Phonotactics),
        lỗi bộ gõ Telex/VNI, lỗi lặp từ liền kề và quy chuẩn dấu câu học thuật.
        """
        self.vi_accented_chars = set(
            "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩị"
            "òóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
            "ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊ"
            "ÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ"
        )
        # Các nguyên âm mang thanh Huyền, Hỏi, Ngã (không bao giờ đứng trước -c, -ch, -p, -t trong tiếng Việt)
        self.non_checked_tone_vowels = set(
            "àảãằẳẵầẩẫèẻẽềểễìỉĩòỏõồổỗờởỡùủũừửữỳỷỹ"
            "ÀẢÃẰẲẴẦẨẪÈẺẼỀỂỄÌỈĨÒỎÕỒỔỖỜỞỠÙỦŨỪỬỮỲỶỸ"
        )
        # Tập âm cuối hợp lệ trong tiếng Việt
        self.valid_vi_endings = (
            'a', 'à', 'á', 'ả', 'ã', 'ạ',
            'ă', 'ằ', 'ắ', 'ẳ', 'ẵ', 'ặ',
            'â', 'ầ', 'ấ', 'ẩ', 'ẫ', 'ậ',
            'e', 'è', 'é', 'ẻ', 'ẽ', 'ẹ',
            'ê', 'ề', 'ế', 'ể', 'ễ', 'ệ',
            'i', 'ì', 'í', 'ỉ', 'ĩ', 'ị',
            'o', 'ò', 'ó', 'ỏ', 'õ', 'ọ',
            'ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ',
            'ơ', 'ờ', 'ớ', 'ở', 'ỡ', 'ợ',
            'u', 'ù', 'ú', 'ủ', 'ũ', 'ụ',
            'ư', 'ừ', 'ứ', 'ử', 'ữ', 'ự',
            'y', 'ỳ', 'ý', 'ỷ', 'ỹ', 'ỵ',
            'c', 'ch', 'm', 'n', 'ng', 'nh', 'p', 't'
        )
        # Các từ mượn học thuật hợp lệ có dấu hoặc viết nối không coi là lỗi
        self.loanword_whitelist: Set[str] = {
            "internet", " logic", "kilo", "mét", "axit", "bazơ", "oxit", "protein", "vitamin",
            "enzyme", "radar", "laser", "pixel", "module", "vector", "tensor", "matrix"
        }

    def _check_vietnamese_syllable_validity(self, word: str) -> Tuple[bool, str, str]:
        """
        Kiểm tra 1 từ có chứa ký tự dấu tiếng Việt xem có vi phạm quy tắc âm tiết tiếng Việt hay không.
        Trả về: (is_error, suggestion, rule_explanation)
        """
        lower_w = word.lower()
        if lower_w in self.loanword_whitelist or len(lower_w) < 2 or len(lower_w) > 10:
            return False, "", ""

        # Chỉ kiểm tra các từ thực sự có ký tự dấu Tiếng Việt
        if not any(ch in self.vi_accented_chars for ch in word):
            return False, "", ""

        # Nếu chứa chữ số bên trong từ có dấu tiếng Việt (lỗi gõ VNI/dính số)
        if any(ch.isdigit() for ch in word):
            cleaned = re.sub(r'\d+', '', word)
            return True, cleaned, "Lỗi gõ xen chữ số (VNI/Telex) vào giữa âm tiết Tiếng Việt"

        # Kiểm tra phụ âm lặp cuối từ do gõ đúp phím (ví dụ: họcj, nghiênn, trườngg, phápp)
        if len(lower_w) >= 3 and lower_w[-1] == lower_w[-2] and lower_w[-1] in "bcdfghjklmnpqrstvwxz":
            fixed = word[:-1]
            return True, fixed, f"Lỗi gõ đúp phụ âm cuối ('{word[-2:]}') trong âm tiết Tiếng Việt"

        # Kiểm tra âm cuối không tồn tại trong hệ thống âm vị Tiếng Việt (như -f, -j, -r, -s, -x, -w, -z, -k, -l, -b, -d, -v)
        if not lower_w.endswith(self.valid_vi_endings):
            # Nếu kết thúc bằng phím dấu Telex bị dư (f, s, r, x, j, w)
            if lower_w[-1] in ('f', 's', 'r', 'x', 'j', 'w') and len(word) >= 3:
                return True, word[:-1], f"Lỗi dư phím gõ dấu Telex ('{word[-1]}') ở cuối âm tiết Tiếng Việt"
            return True, word[:-1], f"Cấu trúc âm cuối không hợp lệ trong chuẩn chính tả Tiếng Việt ('{word}')"

        # Kiểm tra quy tắc C/K, G/GH, NG/NGH đầu âm tiết
        if re.match(r'^c[ieêìíỉĩịèéẻẽẹềếểễệ]', lower_w):
            fixed = ('K' if word[0].isupper() else 'k') + word[1:]
            return True, fixed, "Quy tắc chính tả Tiếng Việt: Trước nguyên âm i, e, ê phải viết bằng 'k' thay vì 'c'"
        if re.match(r'^k[aăâoôơuưàáảãạằắẳẵặầấẩẫậòóỏõọồốổỗộờớởỡợùúủũụừứửữự]', lower_w):
            fixed = ('C' if word[0].isupper() else 'c') + word[1:]
            return True, fixed, "Quy tắc chính tả Tiếng Việt: Trước nguyên âm a, ă, â, o, ô, ơ, u, ư phải viết bằng 'c' thay vì 'k'"
        if re.match(r'^ng[ieêìíỉĩịèéẻẽẹềếểễệ]', lower_w):
            fixed = word[:2] + 'h' + word[2:]
            return True, fixed, "Quy tắc chính tả Tiếng Việt: Trước nguyên âm i, e, ê phải viết là 'ngh' thay vì 'ng'"
        if re.match(r'^ngh[aăâoôơuưàáảãạằắẳẵặầấẩẫậòóỏõọồốổỗộờớởỡợùúủũụừứửữự]', lower_w):
            fixed = word[:2] + word[3:]
            return True, fixed, "Quy tắc chính tả Tiếng Việt: Trước nguyên âm a, o, ô, ơ, u, ư phải viết là 'ng' thay vì 'ngh'"
        if re.match(r'^gh[aăâoôơuưàáảãạằắẳẵặầấẩẫậòóỏõọồốổỗộờớởỡợùúủũụừứửữự]', lower_w):
            fixed = word[0] + word[2:]
            return True, fixed, "Quy tắc chính tả Tiếng Việt: Trước nguyên âm a, o, ô, ơ, u, ư phải viết là 'g' thay vì 'gh'"

        # Kiểm tra quy tắc thanh điệu trên âm tiết khép (-c, -ch, -p, -t chỉ đi với thanh Sắc hoặc Nặng)
        if lower_w.endswith(('c', 'ch', 'p', 't')):
            if any(ch in self.non_checked_tone_vowels for ch in lower_w):
                return True, word, "Lỗi thanh điệu âm tiết khép: Vần kết thúc bằng -c, -ch, -p, -t chỉ kết hợp với thanh Sắc hoặc Nặng"

        return False, "", ""

    def audit_document(self, text: str) -> Dict[str, Any]:
        """
        Rà soát toàn diện 100% văn bản đã tải lên.
        Chỉ kiểm định 2 ngôn ngữ: Tiếng Việt (VI) và Tiếng Anh (EN).
        Trả về thống kê chi tiết và danh mục lỗi phục vụ gạch chân trực tiếp + xuất báo cáo Pháp y PDF.
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
        seen_spans: List[Tuple[int, int]] = []

        def _is_overlapping(s: int, e: int) -> bool:
            for a, b in seen_spans:
                if not (e <= a or s >= b):
                    return True
            return False

        def _add_error(
            lang: str,
            lang_label: str,
            err_type: str,
            error_text: str,
            suggestion: str,
            m_start: int,
            m_end: int,
            rule: str,
            severity: str = "HIGH"
        ):
            if _is_overlapping(m_start, m_end):
                return
            seen_spans.append((m_start, m_end))
            c_start = max(0, m_start - 38)
            c_end = min(len(text), m_end + 38)
            context = re.sub(r'\s+', ' ', text[c_start:c_end]).strip()
            details.append({
                "id": len(details) + 1,
                "lang": lang,
                "language": lang,
                "lang_label": lang_label,
                "type": err_type,
                "error_text": error_text,
                "suggestion": suggestion,
                "context": f"...{context}...",
                "rule": rule,
                "rule_description": rule,
                "severity": severity,
                "char_start": m_start,
                "char_end": m_end
            })

        # -----------------------------------------------------------------
        # TẦNG 1: RÀ SOÁT CẶP TỪ CHÍNH TẢ, HÁN-VIỆT & VĂN PHONG TIẾNG VIỆT
        # -----------------------------------------------------------------
        for pattern, replacement, explanation, severity in self.vi_spelling_pairs:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE | re.UNICODE):
                _add_error(
                    lang="vi",
                    lang_label="Tiếng Việt",
                    err_type="Chính tả & Thuật ngữ",
                    error_text=match.group(0),
                    suggestion=replacement,
                    m_start=match.start(),
                    m_end=match.end(),
                    rule=explanation,
                    severity=severity
                )

        # -----------------------------------------------------------------
        # TẦNG 2: RÀ SOÁT CHÍNH TẢ & NGỮ PHÁP HỌC THUẬT TIẾNG ANH (EN)
        # -----------------------------------------------------------------
        for pattern, replacement, explanation, severity in self.en_spelling_pairs:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE | re.UNICODE):
                _add_error(
                    lang="en",
                    lang_label="Tiếng Anh",
                    err_type="Spelling & Grammar",
                    error_text=match.group(0),
                    suggestion=replacement,
                    m_start=match.start(),
                    m_end=match.end(),
                    rule=explanation,
                    severity=severity
                )

        # -----------------------------------------------------------------
        # TẦNG 3: PHÂN TÍCH HÌNH THÁI ÂM TIẾT TIẾNG VIỆT TOÀN VĂN (100% TEXT)
        # -----------------------------------------------------------------
        for match in re.finditer(r'\b[^\W_]+\b', text, flags=re.UNICODE):
            word = match.group(0)
            m_start, m_end = match.start(), match.end()
            if _is_overlapping(m_start, m_end):
                continue
            is_err, sugg, rule_desc = self._check_vietnamese_syllable_validity(word)
            if is_err:
                _add_error(
                    lang="vi",
                    lang_label="Tiếng Việt",
                    err_type="Cấu trúc âm tiết",
                    error_text=word,
                    suggestion=sugg,
                    m_start=m_start,
                    m_end=m_end,
                    rule=rule_desc,
                    severity="HIGH"
                )

        # -----------------------------------------------------------------
        # TẦNG 4: PHÁT HIỆN LỖI LẶP TỪ LIỀN KỀ (TIẾNG VIỆT & TIẾNG ANH)
        # -----------------------------------------------------------------
        vi_repeat_pattern = r'\b(và|của|là|trong|cho|với|được|các|những|một|có|để|khi|về|theo|từ|tại|trên|dưới|bởi|như)\s+\1\b'
        for match in re.finditer(vi_repeat_pattern, text, flags=re.IGNORECASE | re.UNICODE):
            w = match.group(1)
            _add_error(
                lang="vi",
                lang_label="Tiếng Việt",
                err_type="Lỗi lặp từ",
                error_text=match.group(0),
                suggestion=w,
                m_start=match.start(),
                m_end=match.end(),
                rule=f"Lỗi lặp từ chức năng liên tiếp ('{match.group(0)}') trong câu",
                severity="MEDIUM"
            )

        en_repeat_pattern = r'\b(the|a|an|in|on|at|to|for|of|with|by|is|are|was|were|be|been|and|or|that|this|it|we|they|from|as)\s+\1\b'
        for match in re.finditer(en_repeat_pattern, text, flags=re.IGNORECASE | re.UNICODE):
            w = match.group(1)
            _add_error(
                lang="en",
                lang_label="Tiếng Anh",
                err_type="Word Repetition",
                error_text=match.group(0),
                suggestion=w,
                m_start=match.start(),
                m_end=match.end(),
                rule=f"Duplicate consecutive word ('{match.group(0)}') in academic prose",
                severity="MEDIUM"
            )

        # -----------------------------------------------------------------
        # TẦNG 5: DẠNG VIẾT TẮT KHẨU NGỮ TIẾNG ANH TRONG VĂN BẢN HỌC THUẬT
        # -----------------------------------------------------------------
        contraction_map = {
            "don't": "do not",
            "doesn't": "does not",
            "didn't": "did not",
            "can't": "cannot",
            "won't": "will not",
            "wouldn't": "would not",
            "shouldn't": "should not",
            "couldn't": "could not",
            "isn't": "is not",
            "aren't": "are not",
            "wasn't": "was not",
            "weren't": "were not",
            "hasn't": "has not",
            "haven't": "have not",
        }
        for c_word, full_form in contraction_map.items():
            for match in re.finditer(r'\b' + re.escape(c_word) + r'\b', text, flags=re.IGNORECASE):
                _add_error(
                    lang="en",
                    lang_label="Tiếng Anh",
                    err_type="Academic Style",
                    error_text=match.group(0),
                    suggestion=full_form,
                    m_start=match.start(),
                    m_end=match.end(),
                    rule=f"IEEE/APA Academic Style: Avoid informal contraction '{match.group(0)}'; use full form '{full_form}'",
                    severity="LOW"
                )

        # -----------------------------------------------------------------
        # TẦNG 6: QUY CHUẨN THỂ THỨC DẤU CÂU HỌC THUẬT (NĐ 30/2020/NĐ-CP)
        # -----------------------------------------------------------------
        # 6a. Khoảng trắng thừa trước dấu phẩy / chấm phẩy / chấm hỏi / chấm than (kèm từ phía trước)
        for match in re.finditer(r'([a-zA-ZÀ-ỹ]{2,})\s+([,;?!])(?=\s+[a-zA-ZÀ-ỹ])', text):
            word_part = match.group(1)
            punct_part = match.group(2)
            _add_error(
                lang="vi",
                lang_label="Tiếng Việt",
                err_type="Thể thức văn bản",
                error_text=match.group(0),
                suggestion=f"{word_part}{punct_part}",
                m_start=match.start(),
                m_end=match.end(),
                rule="Lỗi thể thức văn bản (NĐ 30/2020/NĐ-CP): Dấu câu phải viết sát vào từ đứng trước, không để khoảng trắng thừa phía trước",
                severity="LOW"
            )

        # 6b. Thiếu khoảng trắng sau dấu phẩy giữa 2 từ chữ cái
        for match in re.finditer(r'([a-zA-ZÀ-ỹ]{2,}),([a-zA-ZÀ-ỹ]{2,})', text):
            w1, w2 = match.group(1), match.group(2)
            _add_error(
                lang="vi" if any(c in self.vi_accented_chars for c in match.group(0)) else "en",
                lang_label="Tiếng Việt" if any(c in self.vi_accented_chars for c in match.group(0)) else "Tiếng Anh",
                err_type="Thể thức dấu câu",
                error_text=match.group(0),
                suggestion=f"{w1}, {w2}",
                m_start=match.start(),
                m_end=match.end(),
                rule="Lỗi quy chuẩn chế bản học thuật: Phải có 01 khoảng trắng đơn sau dấu phẩy ngăn cách các từ",
                severity="LOW"
            )

        # Sắp xếp toàn bộ lỗi theo đúng thứ tự xuất hiện từ đầu đến cuối tài liệu
        details.sort(key=lambda d: d.get("char_start", 0))
        for idx, d in enumerate(details):
            d["id"] = idx + 1

        vi_count = sum(1 for d in details if d["lang"] == "vi")
        en_count = sum(1 for d in details if d["lang"] == "en")
        total_errors = len(details)

        summary_label = (
            f"Phát hiện {total_errors} điểm nghi vấn chính tả, ngữ pháp & thể thức (Tiếng Việt: {vi_count}, Tiếng Anh: {en_count})"
            if total_errors > 0
            else "Chưa phát hiện lỗi chính tả hoặc sai lệch ngữ pháp trong văn bản (100% Đạt chuẩn)."
        )

        return {
            "total_errors": total_errors,
            "vi_errors_count": vi_count,
            "en_errors_count": en_count,
            "details": details[:200],
            "summary_label": summary_label
        }


spell_grammar_engine = SpellGrammarEngine()
