/**
 * =========================================================================
 * SYNAPES EDU CHECK - AUTOMATED PAYMENT VERIFICATION & REVENUE AUDIT GATEWAY
 * =========================================================================
 * Tự động hóa giám sát Hộp thư Gmail (tài khoản nguyenhoangthien.hvt.15@gmail.com)
 * đối chiếu giao dịch Ngân hàng Timo và ghi sổ kế toán Google Sheets tự động.
 */

const CONFIG = {
  REVENUE_SHEET_NAME: "SYNAPES_REVENUE_AUDIT",
  TIMEOUT_WINDOW_MS: 30000, // Khung thời gian tìm kiếm thư gần nhất (ms)
  PACKAGES: {
    1: { name: "Gói 1 - Tiêu Chuẩn", amount: 3000, keyword: "SYNAPESEDU 1" },
    2: { name: "Gói 2 - Chuyên Gia Cao Cấp", amount: 10000, keyword: "SYNAPESEDU 2" }
  }
};

/**
 * Endpoint xử lý yêu cầu GET từ Webhook hoặc Web Client
 */
function doGet(e) {
  return handleRequest(e ? e.parameter : {});
}

/**
 * Endpoint xử lý yêu cầu POST từ Web Client / Fast API Backend
 */
function doPost(e) {
  var params = {};
  try {
    if (e && e.postData && e.postData.contents) {
      params = JSON.parse(e.postData.contents);
    } else if (e && e.parameter) {
      params = e.parameter;
    }
  } catch (err) {
    params = e ? e.parameter || {} : {};
  }
  return handleRequest(params);
}

/**
 * Bộ điều phối xử lý kiểm tra giao dịch và ghi nhận sổ cái
 */
function handleRequest(params) {
  var action = (params.action || "verify").toLowerCase();
  var clientIp = params.ip || "Unknown-IP";
  var requestedPkg = parseInt(params.package || params.pkg || "1", 10);
  var clientTime = params.timestamp ? parseInt(params.timestamp, 10) : Date.now();

  var response = {
    success: false,
    timestamp: new Date().toISOString(),
    ip: clientIp,
    package: requestedPkg,
    message: ""
  };

  try {
    if (action === "ping") {
      response.success = true;
      response.message = "SYNAPES PAYMENT SERVICE ONLINE";
      return createJsonResponse(response);
    }

    if (action === "verify" || action === "check") {
      var verification = checkTimoPaymentInGmail(requestedPkg, clientTime, clientIp);
      if (verification.found) {
        // Ghi sổ kế toán Google Sheets
        var auditRecord = logTransactionToSpreadsheet(clientIp, requestedPkg, verification);

        response.success = true;
        response.package = requestedPkg;
        response.amount = verification.amount;
        response.tx_id = verification.txId;
        response.total_revenue = auditRecord.totalRevenue;
        response.message = "Bạn đã thanh toán thành công ! Xin chúc mừng...";
      } else {
        response.success = false;
        response.message = verification.reason || "Chưa tìm thấy thông báo thanh toán hợp lệ trong thời gian quy định.";
      }
      return createJsonResponse(response);
    }

    if (action === "stats") {
      var stats = getRevenueStats();
      return createJsonResponse({ success: true, stats: stats });
    }

    response.message = "Action không hợp lệ: " + action;
  } catch (error) {
    response.success = false;
    response.error = error.toString();
    response.message = "Lỗi xử lý hệ thống: " + error.message;
  }

  return createJsonResponse(response);
}

/**
 * Quét hộp thư Gmail tìm thông báo giao dịch Timo tương ứng
 */
function checkTimoPaymentInGmail(pkgId, clientTimestamp, clientIp) {
  var targetPkg = CONFIG.PACKAGES[pkgId] || CONFIG.PACKAGES[1];
  var expectedAmount = targetPkg.amount;
  var expectedKeyword = targetPkg.keyword; // "SYNAPESEDU 1" hoặc "SYNAPESEDU 2"

  // Tìm kiếm các email mới nhất trong 1 ngày gần đây từ Timo
  var query = 'newer_than:1d (from:timo OR from:no-reply@timo.vn OR "Spend Account" OR "tăng")';
  var threads = GmailApp.search(query, 0, 10);

  if (!threads || threads.length === 0) {
    return { found: false, reason: "Không tìm thấy email thông báo ngân hàng mới trong hộp thư." };
  }

  var scriptProps = PropertiesService.getScriptProperties();
  var now = Date.now();

  for (var i = 0; i < threads.length; i++) {
    var messages = threads[i].getMessages();
    for (var j = messages.length - 1; j >= 0; j--) {
      var msg = messages[j];
      var msgDate = msg.getDate().getTime();
      var body = msg.getPlainBody() || "";
      var subject = msg.getSubject() || "";
      var fullText = subject + "\n" + body;

      // Kiểm tra xem email có chứa từ khóa của gói không
      var hasKeyword = fullText.toUpperCase().indexOf(expectedKeyword.toUpperCase()) !== -1 ||
                       fullText.toUpperCase().indexOf("SYNAPESEDU " + pkgId) !== -1 ||
                       fullText.toUpperCase().indexOf("SYNAPESEDU" + pkgId) !== -1;

      // Kiểm tra số tiền tăng
      var hasAmount = false;
      if (expectedAmount === 3000) {
        hasAmount = fullText.indexOf("3.000") !== -1 || fullText.indexOf("3,000") !== -1 || fullText.indexOf("3000 VND") !== -1;
      } else if (expectedAmount === 10000) {
        hasAmount = fullText.indexOf("10.000") !== -1 || fullText.indexOf("10,000") !== -1 || fullText.indexOf("10000 VND") !== -1;
      }

      if (hasKeyword && hasAmount) {
        // Trích xuất mã giao dịch (ví dụ: ZPBV7DF262QNPS)
        var txMatch = fullText.match(/Mô tả:\s*([A-Z0-9]+)\s+BUY\s+CHECK/i) ||
                      fullText.match(/Mô tả:\s*([A-Z0-9]+)/i) ||
                      fullText.match(/([A-Z0-9]{8,20})/);
        var txId = txMatch ? txMatch[1] : ("TX-" + msgDate);

        // Kiểm tra xem mã giao dịch đã được sử dụng trước đó chưa
        var propKey = "PROCESSED_TX_" + txId;
        if (scriptProps.getProperty(propKey)) {
          continue; // Đã tiêu thụ, bỏ qua để chống double-spend
        }

        // Kiểm tra khung thời gian: trong vòng 10 phút gần đây
        var timeDiff = Math.abs(now - msgDate);
        if (timeDiff <= 600000) { // 10 phút
          // Đánh dấu đã sử dụng
          scriptProps.setProperty(propKey, JSON.stringify({
            ip: clientIp,
            pkg: pkgId,
            usedAt: now
          }));

          return {
            found: true,
            txId: txId,
            amount: expectedAmount,
            msgDate: msgDate,
            rawSnippet: fullText.substring(0, 200)
          };
        }
      }
    }
  }

  return { found: false, reason: "Chưa nhận được giao dịch khớp với nội dung chuyển khoản '" + expectedKeyword + "' và số tiền " + expectedAmount + "đ." };
}

/**
 * Ghi nhận giao dịch vào Google Spreadsheet và tính lũy kế tổng thu
 */
function logTransactionToSpreadsheet(clientIp, pkgId, verification) {
  var ss = getOrCreateAuditSpreadsheet();
  var sheet = ss.getSheetByName("NHẬT KÝ THANH TOÁN") || ss.getSheets()[0];
  if (sheet.getName() !== "NHẬT KÝ THANH TOÁN") {
    sheet.setName("NHẬT KÝ THANH TOÁN");
  }

  // Khởi tạo tiêu đề nếu chưa có
  if (sheet.getLastRow() === 0) {
    sheet.appendRow([
      "STT",
      "Thời Gian (UTC+7)",
      "Mã Giao Dịch Timo",
      "Địa Chỉ IP",
      "Gói Dịch Vụ",
      "Số Tiền (VND)",
      "Trạng Thái",
      "Tổng Thu Lũy Kế (VND)"
    ]);
    sheet.getRange(1, 1, 1, 8).setFontWeight("bold").setBackground("#0f172a").setFontColor("#f8fafc");
  }

  // Tính tổng thu lũy kế
  var lastRow = sheet.getLastRow();
  var previousTotal = 0;
  if (lastRow > 1) {
    var val = sheet.getRange(lastRow, 8).getValue();
    previousTotal = parseFloat(val) || 0;
  }

  var currentAmount = verification.amount || 0;
  var newTotal = previousTotal + currentAmount;
  var stt = lastRow; // Dòng thứ (lastRow) chính là STT tiếp theo

  var formattedTime = Utilities.formatDate(new Date(), "Asia/Ho_Chi_Minh", "yyyy-MM-dd HH:mm:ss");
  var pkgName = pkgId === 2 ? "Gói 2 - Cao Cấp (10.000đ)" : "Gói 1 - Tiêu Chuẩn (3.000đ)";

  sheet.appendRow([
    stt,
    formattedTime,
    verification.txId,
    clientIp,
    pkgName,
    currentAmount,
    "THÀNH CÔNG",
    newTotal
  ]);

  // Tự động căn chỉnh độ rộng cột
  sheet.autoResizeColumns(1, 8);

  return {
    totalRevenue: newTotal,
    stt: stt
  };
}

/**
 * Tìm hoặc tạo mới Google Spreadsheet doanh thu
 */
function getOrCreateAuditSpreadsheet() {
  var files = DriveApp.getFilesByName(CONFIG.REVENUE_SHEET_NAME);
  if (files.hasNext()) {
    var file = files.next();
    return SpreadsheetApp.open(file);
  }
  var ss = SpreadsheetApp.create(CONFIG.REVENUE_SHEET_NAME);
  return ss;
}

/**
 * Lấy số liệu thống kê doanh thu
 */
function getRevenueStats() {
  try {
    var ss = getOrCreateAuditSpreadsheet();
    var sheet = ss.getSheetByName("NHẬT KÝ THANH TOÁN") || ss.getSheets()[0];
    var lastRow = sheet.getLastRow();
    if (lastRow <= 1) return { totalRevenue: 0, totalTransactions: 0 };
    var total = sheet.getRange(lastRow, 8).getValue() || 0;
    return {
      totalRevenue: total,
      totalTransactions: lastRow - 1
    };
  } catch (e) {
    return { totalRevenue: 0, totalTransactions: 0, error: e.message };
  }
}

/**
 * Trả về phản hồi dạng JSON chuẩn
 */
function createJsonResponse(data) {
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}
