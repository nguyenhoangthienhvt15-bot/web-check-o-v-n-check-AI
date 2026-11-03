/**
 * =========================================================================
 * SYNAPES EDU CHECK - AUTOMATED PAYMENT VERIFICATION & REVENUE AUDIT GATEWAY
 * =========================================================================
 * Tu dong hoa giam sat Hop thu Gmail (tai khoan nguyenhoangthien.hvt.15@gmail.com)
 * Doi chieu giao dich Ngan hang Timo va ghi so ke toan Google Sheets tu dong.
 */

const CONFIG = {
  REVENUE_SHEET_NAME: "SYNAPES_REVENUE_AUDIT",
  PACKAGES: {
    1: { name: "Goi 1 - Tieu Chuan", amount: 3000, keyword: "SYNAPESEDU 1" },
    2: { name: "Goi 2 - Chuyen Gia Cao Cap", amount: 10000, keyword: "SYNAPESEDU 2" }
  }
};

/**
 * Endpoint xu ly yeu cau GET
 */
function doGet(e) {
  return handleRequest(e ? e.parameter : {});
}

/**
 * Endpoint xu ly yeu cau POST
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
 * Bo dieu phoi xu ly kiem tra giao dich va ghi nhan so cai
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

    if (action === "debug_emails") {
      var threads = GmailApp.search('newer_than:3d', 0, 15);
      var list = [];
      for (var t = 0; t < threads.length; t++) {
        var msgs = threads[t].getMessages();
        for (var m = 0; m < msgs.length; m++) {
          var msg = msgs[m];
          list.push({
            id: msg.getId(),
            from: msg.getFrom(),
            subject: msg.getSubject(),
            date: msg.getDate().toISOString(),
            body: (msg.getPlainBody() || "").substring(0, 500)
          });
        }
      }
      return createJsonResponse({ success: true, count: list.length, emails: list });
    }

    if (action === "clear_cache") {
      PropertiesService.getScriptProperties().deleteAllProperties();
      return createJsonResponse({ success: true, message: "Cleared all processed transactions cache." });
    }

    if (action === "verify" || action === "check") {
      var verification = checkTimoPaymentInGmail(requestedPkg, clientTime, clientIp);
      if (verification.found) {
        var auditRecord = logTransactionToSpreadsheet(clientIp, requestedPkg, verification);

        response.success = true;
        response.package = requestedPkg;
        response.amount = verification.amount;
        response.tx_id = verification.txId;
        response.total_revenue = auditRecord.totalRevenue;
        response.message = "Ban da thanh toan thanh cong ! Xin chuc mung...";
      } else {
        response.success = false;
        response.message = verification.reason || "Chua tim thay thong bao thanh toan hop le.";
      }
      return createJsonResponse(response);
    }

    if (action === "stats") {
      var stats = getRevenueStats();
      return createJsonResponse({ success: true, stats: stats });
    }

    response.message = "Action khong hop le: " + action;
  } catch (error) {
    response.success = false;
    response.error = error.toString();
    response.message = "Loi xu ly he thong: " + error.message;
  }

  return createJsonResponse(response);
}

/**
 * Quet hop thu Gmail tim thong bao giao dich Timo tuong ung
 */
function checkTimoPaymentInGmail(pkgId, clientTimestamp, clientIp) {
  var targetPkg = CONFIG.PACKAGES[pkgId] || CONFIG.PACKAGES[1];
  var expectedAmount = targetPkg.amount; // 3000 hoặc 10000

  // Tìm kiếm email rộng rãi trong 2 ngày gần nhất:
  // 1. Chứa từ khóa SYNAPESEDU hoặc SYNAPES
  // 2. Hoặc từ Timo / BVBank / Spend Account / bien dong so du
  var query = 'newer_than:2d (SYNAPESEDU OR SYNAPES OR timo OR BVBank OR "Spend Account" OR "biến động" OR "tăng")';
  var threads = GmailApp.search(query, 0, 20);

  if (!threads || threads.length === 0) {
    return { found: false, reason: "Không tìm thấy email thông báo ngân hàng nào trong hộp thư 2 ngày gần đây." };
  }

  var scriptProps = PropertiesService.getScriptProperties();
  var now = Date.now();

  for (var i = 0; i < threads.length; i++) {
    var messages = threads[i].getMessages();
    for (var j = messages.length - 1; j >= 0; j--) {
      var msg = messages[j];
      var msgId = msg.getId();
      var msgDate = msg.getDate().getTime();
      var body = msg.getPlainBody() || "";
      var subject = msg.getSubject() || "";
      var fullText = subject + "\n" + body;

      // 1. Kiểm tra từ khóa gói:
      // Chuẩn hóa văn bản: bỏ toàn bộ khoảng trắng để so khớp linh hoạt
      // Ví dụ: "SYNAPESEDU 1", "SYNAPESEDU1", "SYNAPES EDU 1", "BUY CHECK SYNAPESEDU 1"
      var cleanFull = fullText.toUpperCase().replace(/[\s\-_.:,]+/g, '');
      var hasKeyword = false;

      if (pkgId === 1) {
        hasKeyword = cleanFull.indexOf("SYNAPESEDU1") !== -1 ||
                     cleanFull.indexOf("SYNAPES1") !== -1 ||
                     cleanFull.indexOf("SYNAPESEDU") !== -1;
      } else if (pkgId === 2) {
        hasKeyword = cleanFull.indexOf("SYNAPESEDU2") !== -1 ||
                     cleanFull.indexOf("SYNAPES2") !== -1 ||
                     cleanFull.indexOf("SYNAPESEDU") !== -1;
      }

      // 2. Kiểm tra số tiền:
      var hasAmount = false;
      if (expectedAmount === 3000) {
        hasAmount = /(?:3[.,]?000|3000)\s*(?:VND|VNĐ|Đ|D)?/i.test(fullText);
      } else if (expectedAmount === 10000) {
        hasAmount = /(?:10[.,]?000|10000)\s*(?:VND|VNĐ|Đ|D)?/i.test(fullText);
      }

      if (hasKeyword && hasAmount) {
        // Dùng Gmail Message ID làm khóa định danh duy nhất tuyệt đối để không bao giờ bị va chạm từ khóa
        var txId = "TIMO-" + msgId.substring(0, 16).toUpperCase();
        var propKey = "PROCESSED_MSG_" + msgId;

        if (scriptProps.getProperty(propKey)) {
          continue; // Đã tiêu thụ tin nhắn này, bỏ qua để chống double-spend
        }

        // Kiểm tra khung thời gian: cho phép trong vòng 24 giờ gần đây (86.400.000 ms)
        var timeDiff = Math.abs(now - msgDate);
        if (timeDiff <= 86400000) {
          scriptProps.setProperty(propKey, JSON.stringify({
            ip: clientIp,
            pkg: pkgId,
            usedAt: now,
            msgDate: msgDate
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

  return { found: false, reason: "Chưa nhận được giao dịch khớp với nội dung chuyển khoản 'SYNAPESEDU " + pkgId + "' và số tiền " + expectedAmount + "đ." };
}

/**
 * Ghi nhan giao dich vao Google Spreadsheet va tinh luy ke tong thu
 */
function logTransactionToSpreadsheet(clientIp, pkgId, verification) {
  var ss = getOrCreateAuditSpreadsheet();
  var sheet = ss.getSheetByName("NHAT KY THANH TOAN") || ss.getSheets()[0];
  if (sheet.getName() !== "NHAT KY THANH TOAN") {
    sheet.setName("NHAT KY THANH TOAN");
  }

  if (sheet.getLastRow() === 0) {
    sheet.appendRow([
      "STT",
      "Thoi Gian (UTC+7)",
      "Ma Giao Dich",
      "Dia Chi IP",
      "Goi Dich Vu",
      "So Tien (VND)",
      "Trang Thai",
      "Tong Thu Luy Ke (VND)"
    ]);
    sheet.getRange(1, 1, 1, 8).setFontWeight("bold").setBackground("#0f172a").setFontColor("#f8fafc");
  }

  var lastRow = sheet.getLastRow();
  var previousTotal = 0;
  if (lastRow > 1) {
    var val = sheet.getRange(lastRow, 8).getValue();
    previousTotal = parseFloat(val) || 0;
  }

  var currentAmount = verification.amount || 0;
  var newTotal = previousTotal + currentAmount;
  var stt = lastRow;

  var formattedTime = Utilities.formatDate(new Date(), "Asia/Ho_Chi_Minh", "yyyy-MM-dd HH:mm:ss");
  var pkgName = pkgId === 2 ? "Goi 2 - Cao Cap (10.000d)" : "Goi 1 - Tieu Chuan (3.000d)";

  sheet.appendRow([
    stt,
    formattedTime,
    verification.txId,
    clientIp,
    pkgName,
    currentAmount,
    "THANH CONG",
    newTotal
  ]);

  sheet.autoResizeColumns(1, 8);

  return {
    totalRevenue: newTotal,
    stt: stt
  };
}

function getOrCreateAuditSpreadsheet() {
  var files = DriveApp.getFilesByName(CONFIG.REVENUE_SHEET_NAME);
  if (files.hasNext()) {
    var file = files.next();
    return SpreadsheetApp.open(file);
  }
  var ss = SpreadsheetApp.create(CONFIG.REVENUE_SHEET_NAME);
  return ss;
}

function getRevenueStats() {
  try {
    var ss = getOrCreateAuditSpreadsheet();
    var sheet = ss.getSheetByName("NHAT KY THANH TOAN") || ss.getSheets()[0];
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

function createJsonResponse(data) {
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}
