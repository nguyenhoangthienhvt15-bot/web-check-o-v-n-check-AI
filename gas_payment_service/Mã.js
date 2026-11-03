/**
 * =========================================================================
 * SYNAPES EDU CHECK - AUTOMATED PAYMENT VERIFICATION & REVENUE AUDIT GATEWAY
 * =========================================================================
 * Tu dong hoa giam sat Hop thu Gmail (tai khoan nguyenhoangthien.hvt.15@gmail.com)
 * Doi chieu giao dich Ngan hang Timo (chi kiem tra thu bao tai khoan tang tu Timo
 * trong khung thoi gian [-10s, +15s] quanh thoi diem xac nhan) va ghi so Google Sheets.
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
      var verification = checkTimoPaymentInGmailWithWindow(requestedPkg, clientTime, clientIp);
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
        response.message = verification.reason || "Chua tim thay thong bao thanh toan hop le tu Timo trong khung thoi gian xac nhan.";
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
 * Quet hop thu Gmail tim thong bao giao dich Timo bao TAI KHOAN TANG
 * trong khung thoi gian [-10 giay (kem dem chuyen khoan), +15 giay] tinh tu thoi diem bam nut.
 */
function checkTimoPaymentInGmailWithWindow(pkgId, clickTimestamp, clientIp) {
  var targetPkg = CONFIG.PACKAGES[pkgId] || CONFIG.PACKAGES[1];
  var expectedAmount = targetPkg.amount; // 3000 hoac 10000
  var baseClickTime = clickTimestamp || Date.now();

  // Khung thoi gian kiem tra:
  // Truoc 10 giay (kem bu sai lech dong ho / thao tac chuyen khoan 45s) den Sau 15 giay
  var windowStart = baseClickTime - 45000;
  var strictWindowEnd = baseClickTime + 15000;

  var scriptProps = PropertiesService.getScriptProperties();
  var maxAttempts = 4;

  for (var attempt = 0; attempt < maxAttempts; attempt++) {
    var query = 'newer_than:1d (from:timo.vn OR "Timo Support" OR "Thông báo thay đổi số dư tài khoản")';
    var threads = GmailApp.search(query, 0, 10);

    if (threads && threads.length > 0) {
      for (var i = 0; i < threads.length; i++) {
        var messages = threads[i].getMessages();
        for (var j = messages.length - 1; j >= 0; j--) {
          var msg = messages[j];
          var msgId = msg.getId();
          var msgDate = msg.getDate().getTime();
          var sender = (msg.getFrom() || "").toLowerCase();
          var subject = msg.getSubject() || "";
          var body = msg.getPlainBody() || "";
          var fullText = subject + "\n" + body;

          // 1. CHI kiem tra cac thu thong bao tu Ngan hang Timo
          if (sender.indexOf("timo.vn") === -1 && sender.indexOf("timo") === -1) {
            continue;
          }

          // 2. CHI kiem tra thu bao TAI KHOAN TANG (khong phai giao dich giam tien)
          var lowerBody = body.toLowerCase();
          if (lowerBody.indexOf("vừa tăng") === -1 && lowerBody.indexOf("tăng ") === -1) {
            continue;
          }
          if (lowerBody.indexOf("vừa giảm") !== -1) {
            continue;
          }

          // 3. Kiem tra khung thoi gian [-10s (buffer 45s), +15s]
          if (msgDate < windowStart || msgDate > strictWindowEnd + 5000) {
            continue;
          }

          // 4. Kiem tra noi dung mo ta chuyen khoan dinh kem QR Code
          var cleanFull = fullText.toUpperCase().replace(/[^A-Z0-9]/g, '');
          var hasKeyword = false;
          if (pkgId === 1) {
            hasKeyword = (cleanFull.indexOf("BUYCHECKSYNAPESEDU1") !== -1 || cleanFull.indexOf("SYNAPESEDU1") !== -1) &&
                         cleanFull.indexOf("SYNAPESEDU2") === -1;
          } else if (pkgId === 2) {
            hasKeyword = (cleanFull.indexOf("BUYCHECKSYNAPESEDU2") !== -1 || cleanFull.indexOf("SYNAPESEDU2") !== -1) &&
                         cleanFull.indexOf("SYNAPESEDU1") === -1;
          }

          // 5. Kiem tra chinh xac so tien tang
          var hasAmount = false;
          if (expectedAmount === 3000) {
            hasAmount = /(?:vừa\s+tăng|tăng)\s*(?:3[.,]?000|3000)\s*(?:VND|VNĐ|Đ|D)?/i.test(body);
          } else if (expectedAmount === 10000) {
            hasAmount = /(?:vừa\s+tăng|tăng)\s*(?:10[.,]?000|10000)\s*(?:VND|VNĐ|Đ|D)?/i.test(body);
          }

          if (hasKeyword && hasAmount) {
            var propKey = "PROCESSED_MSG_" + msgId;
            if (scriptProps.getProperty(propKey)) {
              continue; // Thu nay da duoc cap cho IP khac truoc do
            }

            var txId = "TIMO-" + msgId.toUpperCase();
            scriptProps.setProperty(propKey, JSON.stringify({
              ip: clientIp,
              pkg: pkgId,
              amount: expectedAmount,
              usedAt: Date.now(),
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

    // Neu chua het 15 giay sau khi bam nut, doi 3.5 giay roi quet lai Gmail
    if (Date.now() + 3500 <= strictWindowEnd && attempt < maxAttempts - 1) {
      Utilities.sleep(3500);
    } else {
      break;
    }
  }

  return {
    found: false,
    reason: "Chưa tìm thấy thư thông báo biến động số dư tăng " + expectedAmount + "đ từ Ngân hàng Timo với nội dung 'BUY CHECK SYNAPESEDU " + pkgId + "' trong khung thời gian xác nhận (-10s đến +15s)."
  };
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
