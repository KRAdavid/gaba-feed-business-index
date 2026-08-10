/**
 * Cellpinda GABA Feed business inquiry receiver v2.
 *
 * One-time installation:
 * 1) Open the Apps Script project bound to GABA_Feed_Intelligence_Master_DB.
 * 2) Replace the previous Inquiry file with this entire source.
 * 3) Save and run setupGabaInquiryReceiver() once to authorize Sheets/Mail.
 * 4) Deploy > Manage deployments > Edit > New version > Deploy.
 * 5) Execute as: Me / Who has access: Anyone.
 */

const GABA_INQUIRY_CFG_V2 = Object.freeze({
  SPREADSHEET_ID: '1QOYtwlq6uHp54BXu0v3yf5eA5B04HON9GxfxdE830zw',
  SHEET_NAME: 'Inquiries',
  LEAD_SHEET_NAME: 'Lead_Pipeline',
  TO: 'feed@cellpinda.com',
  CC: 'dubaissday@gmail.com',
  TZ: 'Asia/Seoul',
  FORM_VERSION: 'GABA_FEED_INQUIRY_V3',
  MAX_FIELD_LENGTH: 5000,
  RATE_LIMIT_SECONDS: 30
});

const GABA_INQUIRY_HEADERS_V2 = [
  'Inquiry_ID', 'Received_At', 'Mail_Status', 'Mail_Error',
  'Company', 'Contact_Name', 'Department_Title', 'Email', 'Phone', 'Country_Region',
  'Collaboration_Type', 'Selected_Product', 'Selected_Specification', 'Order_Guide_Path',
  'Species', 'Farm_or_Feed_Volume', 'Current_Challenges', 'Preparation_Stage',
  'Desired_Start', 'Sample_Initial_Volume', 'Annual_Volume', 'Evaluation_KPIs',
  'Detailed_Request', 'Consent', 'Source_Page', 'Client_Timestamp', 'Form_Version',
  'Lead_ID', 'Lead_Status', 'Created_At', 'Country', 'Role', 'Interest', 'Product',
  'Expected_Volume', 'Project_Stage', 'Technical_Requirements', 'Message', 'DB_Status',
  'DB_Error', 'Source', 'UTM', 'Next_Action'
];

const GABA_LEAD_HEADERS_V2 = [
  'Lead_ID', 'Inquiry_ID', 'Created_At', 'Company', 'Contact', 'Country', 'Role',
  'Species', 'Product', 'Expected_Volume', 'Use_Case', 'Project_Stage',
  'Qualification_Status', 'Lead_Score', 'Owner', 'Next_Action', 'Next_Action_Date',
  'Buyer_Pack', 'Sample_Status', 'Pilot_Status', 'Quote_Status', 'PO_Status',
  'Last_Activity', 'Notes'
];

const GABA_KPI_HEADERS_V2 = ['Key', 'Value', 'Updated_At', 'Source'];

function setupGabaInquiryReceiver() {
  const sheet = gabaInquirySheetV2_();
  gabaRefreshB2bKpiV2_();
  const quota = MailApp.getRemainingDailyQuota();
  const now = Utilities.formatDate(new Date(), GABA_INQUIRY_CFG_V2.TZ, 'yyyy-MM-dd HH:mm:ss');

  MailApp.sendEmail({
    to: GABA_INQUIRY_CFG_V2.TO,
    cc: GABA_INQUIRY_CFG_V2.CC,
    name: 'Cellpinda GABA Feed',
    subject: '[GABA Feed 문의폼] Apps Script 수신 테스트',
    body:
      '문의 수신기가 정상 설치되었습니다.\n\n' +
      '설치 확인 시각: ' + now + '\n' +
      '남은 일일 발송 한도: ' + quota
  });

  return {
    ok: true,
    sheet: sheet.getName(),
    test_mail_sent_to: GABA_INQUIRY_CFG_V2.TO,
    cc: GABA_INQUIRY_CFG_V2.CC,
    remaining_daily_quota: MailApp.getRemainingDailyQuota()
  };
}

/**
 * Receives the public GitHub Intelligence status snapshot and mirrors it into
 * the Master DB. Configure Script Properties:
 *   GABA_STATUS_SYNC_TOKEN = a long random token
 *
 * GitHub Actions sends { action: 'sync_status', token, payload } to the same
 * Web App endpoint. The token is never stored in a sheet or public snapshot.
 */
function gabaDashboardSyncV2_(e) {
  const expected = PropertiesService.getScriptProperties().getProperty('GABA_STATUS_SYNC_TOKEN');
  const body = e && e.postData && e.postData.contents ? e.postData.contents : '{}';
  let request;
  try {
    request = JSON.parse(body);
  } catch (error) {
    return gabaDashboardSyncResponseV2_(false, 'Invalid JSON payload', { status: 400 });
  }
  const supplied = String(request.token || (e && e.parameter && e.parameter.token) || '');
  if (!expected || !supplied || supplied !== expected) {
    return gabaDashboardSyncResponseV2_(false, 'Unauthorized', { status: 401 });
  }
  const payload = request.payload || request;
  if (!payload || typeof payload !== 'object' || !payload.last_run_at) {
    return gabaDashboardSyncResponseV2_(false, 'Missing status payload', { status: 422 });
  }

  const values = {
    'Operating Mode': payload.operating_mode || 'HYBRID_B2B',
    'Public Source of Truth': payload.source_of_truth || 'GITHUB_APPROVED_SNAPSHOT',
    'Public Engine Version': payload.engine_version || '2.0.0',
    'Last Run At': payload.last_run_at,
    'Last Success At': payload.last_success_at || '',
    'Last Content Change At': payload.last_content_change_at || '',
    'Published Count': payload.published_count || 0,
    'Review Count': payload.review_count || 0,
    'Sources Success': payload.sources_success || 0,
    'Sources Failed': payload.sources_failed || 0,
    'Health Status': payload.health_status || 'unknown',
    'Latest Workflow Run': payload.latest_workflow_run || '',
    'Latest Snapshot': payload.latest_snapshot || '',
    'Semantic Digest': payload.semantic_digest || '',
    'Execution Duration Seconds': payload.execution_duration_seconds || '',
    'Dashboard Updated At': Utilities.formatDate(new Date(), GABA_INQUIRY_CFG_V2.TZ, 'yyyy-MM-dd HH:mm:ss')
  };

  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const ss = SpreadsheetApp.openById(GABA_INQUIRY_CFG_V2.SPREADSHEET_ID);
    gabaUpsertStatusRowsV2_(ss, '00_Dashboard', values, 'GITHUB_APPROVED_SNAPSHOT');
    gabaUpsertStatusRowsV2_(ss, 'System_Config', {
      'Operating_Mode': values['Operating Mode'],
      'Public_Source_of_Truth': values['Public Source of Truth'],
      'Public_Intelligence_Engine': values['Public Engine Version']
    }, 'GitHub Intelligence v2');
  } finally {
    lock.releaseLock();
  }
  return gabaDashboardSyncResponseV2_(true, 'Dashboard status synchronized', {
    status: 200,
    updated_sheets: ['00_Dashboard', 'System_Config'],
    last_run_at: payload.last_run_at
  });
}

function gabaUpsertStatusRowsV2_(ss, sheetName, values, source) {
  let sheet = ss.getSheetByName(sheetName);
  if (!sheet) sheet = ss.insertSheet(sheetName);
  if (sheet.getLastRow() === 0) {
    sheet.getRange(1, 1, 1, 4).setValues([['Key', 'Value', 'Updated_At', 'Source']]);
    sheet.setFrozenRows(1);
    sheet.getRange(1, 1, 1, 4).setFontWeight('bold');
  }
  const lastRow = sheet.getLastRow();
  const keys = lastRow > 1 ? sheet.getRange(2, 1, lastRow - 1, 1).getValues() : [];
  const updatedAt = Utilities.formatDate(new Date(), GABA_INQUIRY_CFG_V2.TZ, 'yyyy-MM-dd HH:mm:ss');
  Object.keys(values).forEach(function(key) {
    const index = keys.findIndex(function(row) { return String(row[0]) === key; });
    const row = index >= 0 ? index + 2 : sheet.getLastRow() + 1;
    if (index < 0) keys.push([key]);
    sheet.getRange(row, 1, 1, 4).setValues([[
      gabaInquirySheetValueV2_(key),
      gabaInquirySheetValueV2_(values[key]),
      updatedAt,
      source
    ]]);
  });
}

function gabaDashboardSyncResponseV2_(ok, message, extra) {
  const payload = Object.assign({ ok: Boolean(ok), message: String(message || '') }, extra || {});
  return ContentService.createTextOutput(JSON.stringify(payload)).setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    const params = (e && e.parameters) || {};
    let action = gabaInquiryValueV2_(params, 'action').toLowerCase();
    if (!action && e && e.postData && e.postData.contents) {
      try {
        const body = JSON.parse(e.postData.contents);
        action = String(body.action || '').toLowerCase();
      } catch (error) {
        // Inquiry requests use form encoding; malformed JSON falls through to
        // the standard unsupported-request response below.
      }
    }
    if (action === 'sync_status') {
      return gabaDashboardSyncV2_(e);
    }
    if (action !== 'inquiry') {
      return gabaInquiryResponseV2_(false, '지원하지 않는 요청입니다.', '');
    }
    return gabaInquiryProcessV2_(params);
  } catch (error) {
    console.error(error && error.stack ? error.stack : error);
    return gabaInquiryResponseV2_(
      false,
      '문의 처리 중 오류가 발생했습니다. 메일 앱 전송을 이용해 주세요.',
      ''
    );
  }
}

function gabaInquiryProcessV2_(params) {
  if (gabaInquiryValueV2_(params, '_honey') || gabaInquiryValueV2_(params, 'website')) {
    return gabaInquiryResponseV2_(true, '문의가 접수되었습니다.', '');
  }

  const data = {
    company: gabaInquiryValueV2_(params, '회사_기관명'),
    contactName: gabaInquiryValueV2_(params, '담당자명'),
    departmentTitle: gabaInquiryValueV2_(params, '직책_부서'),
    email: gabaInquiryValueV2_(params, 'email'),
    phone: gabaInquiryValueV2_(params, '연락처'),
    countryRegion: gabaInquiryValueV2_(params, '국가_지역'),
    collaborationType: gabaInquiryValueV2_(params, '협업_유형'),
    selectedProduct: gabaInquiryValueV2_(params, '선택제품'),
    selectedSpecification: gabaInquiryValueV2_(params, '선택규격_형태'),
    orderGuidePath: gabaInquiryValueV2_(params, '주문가이드_경로'),
    species: gabaInquiryValueV2_(params, '주요_축종'),
    farmFeedVolume: gabaInquiryValueV2_(params, '사육규모_사료물량'),
    currentChallenges: gabaInquiryValueV2_(params, '현재_과제'),
    preparationStage: gabaInquiryValueV2_(params, '현재_준비단계'),
    desiredStart: gabaInquiryValueV2_(params, '희망_시작시기'),
    sampleInitialVolume: gabaInquiryValueV2_(params, '예상_샘플_초도물량'),
    annualVolume: gabaInquiryValueV2_(params, '예상_연간물량'),
    evaluationKpis: gabaInquiryValueV2_(params, '핵심_평가지표'),
    detailedRequest: gabaInquiryValueV2_(params, '상세_요청사항'),
    consent: gabaInquiryValueV2_(params, '개인정보_전송동의'),
    sourcePage:
      gabaInquiryValueV2_(params, '접수페이지') ||
      gabaInquiryValueV2_(params, 'source_page'),
    clientTimestamp:
      gabaInquiryValueV2_(params, '접수시각') ||
      gabaInquiryValueV2_(params, 'client_timestamp'),
    utm: [
      gabaInquiryValueV2_(params, 'utm_source'),
      gabaInquiryValueV2_(params, 'utm_medium'),
      gabaInquiryValueV2_(params, 'utm_campaign')
    ].filter(Boolean).join(' / '),
    formVersion:
      gabaInquiryValueV2_(params, 'form_version') ||
      GABA_INQUIRY_CFG_V2.FORM_VERSION
  };

  const validationError = gabaInquiryValidateV2_(data);
  if (validationError) {
    return gabaInquiryResponseV2_(false, validationError, '');
  }

  if (!gabaInquiryAllowV2_(data.email, data.company)) {
    return gabaInquiryResponseV2_(
      false,
      '연속 제출이 감지되었습니다. 30초 후 다시 시도해 주세요.',
      ''
    );
  }

  const now = new Date();
  const receivedAt = Utilities.formatDate(
    now,
    GABA_INQUIRY_CFG_V2.TZ,
    'yyyy-MM-dd HH:mm:ss'
  );
  const inquiryId =
    'INQ-' +
    Utilities.formatDate(now, GABA_INQUIRY_CFG_V2.TZ, 'yyyyMMdd') +
    '-' +
    Utilities.getUuid().replace(/-/g, '').slice(0, 4).toUpperCase();

  let mailStatus = 'SENT';
  let mailError = '';
  let autoReplyWarning = '';

  try {
    if (MailApp.getRemainingDailyQuota() < 1) {
      throw new Error('MailApp daily quota exhausted');
    }

    const subject =
      '[GABA Feed 협업문의] ' +
      data.company +
      ' · ' +
      (data.collaborationType || '협업') +
      ' · ' +
      (data.species || '축종 미정');

    MailApp.sendEmail({
      to: GABA_INQUIRY_CFG_V2.TO,
      cc: GABA_INQUIRY_CFG_V2.CC,
      replyTo: data.email,
      name: 'Cellpinda GABA Feed',
      subject: subject,
      body: gabaInquiryPlainBodyV2_(inquiryId, receivedAt, data),
      htmlBody: gabaInquiryHtmlBodyV2_(inquiryId, receivedAt, data)
    });

    try {
      MailApp.sendEmail({
        to: data.email,
        name: 'Cellpinda',
        subject: '[셀핀다] GABA Feed 사업협업 문의가 접수되었습니다',
        body:
          data.contactName +
          '님, 문의가 접수되었습니다.\n' +
          '문의번호: ' +
          inquiryId +
          '\n' +
          '선택 제품: ' +
          (data.selectedProduct || '미정') +
          '\n' +
          '담당자가 검토 후 회신드리겠습니다.'
      });
    } catch (autoReplyError) {
      autoReplyWarning = String(
        autoReplyError && autoReplyError.message
          ? autoReplyError.message
          : autoReplyError
      );
    }
  } catch (error) {
    mailStatus = 'FAILED';
    mailError = String(error && error.message ? error.message : error).slice(0, 500);
  }

  let sheetError = '';
  let leadResult = { leadId: '', status: 'FAILED', error: '' };
  data.nextAction = gabaLeadContextV2_(data).nextAction;
  try {
    gabaInquiryAppendV2_(inquiryId, receivedAt, mailStatus, mailError, data, leadResult);
  } catch (error) {
    sheetError = String(error && error.message ? error.message : error).slice(0, 500);
  }

  // Lead creation is deliberately best-effort: an email or inquiry write must
  // never be rolled back because a downstream pipeline sheet is unavailable.
  try {
    if (!sheetError) leadResult = gabaCreateLeadV2_(inquiryId, receivedAt, data);
  } catch (error) {
    leadResult = {
      leadId: '',
      status: 'FAILED',
      error: String(error && error.message ? error.message : error).slice(0, 500)
    };
  }

  if (!sheetError) {
    try {
      gabaRefreshB2bKpiV2_();
    } catch (error) {
      console.error('B2B KPI refresh failed: ' + error);
    }
  }

  if (!sheetError) {
    try {
      gabaInquiryUpdateLeadV2_(inquiryId, leadResult);
    } catch (error) {
      console.error('Lead status update failed: ' + error);
    }
  }

  if (mailStatus !== 'SENT') {
    return gabaInquiryResponseV2_(
      false,
      '문의는 기록되었으나 이메일 발송에 실패했습니다. 메일 앱으로 보내기를 눌러 주세요.',
      inquiryId,
      {
        mail_status: mailStatus,
        sheet_saved: !sheetError,
        db_status: sheetError ? 'FAILED' : 'SAVED',
        db_error: sheetError,
        error: mailError,
        lead_id: leadResult.leadId,
        lead_status: leadResult.status
      }
    );
  }

  const warning = sheetError
    ? ' 이메일은 발송되었지만 관리시트 기록을 확인해야 합니다.'
    : autoReplyWarning
      ? ' 문의자 자동회신은 지연될 수 있습니다.'
      : '';

  return gabaInquiryResponseV2_(
    true,
    '문의가 정상 접수되었습니다.' + warning,
    inquiryId,
    {
      mail_status: mailStatus,
      sheet_saved: !sheetError,
      db_status: sheetError ? 'FAILED' : 'SAVED',
      db_error: sheetError,
      lead_id: leadResult.leadId,
      lead_status: leadResult.status,
      lead_error: leadResult.error || ''
    }
  );
}

function gabaInquiryValidateV2_(data) {
  const required = [
    ['회사·기관명', data.company],
    ['담당자명', data.contactName],
    ['이메일', data.email],
    ['국가·지역', data.countryRegion],
    ['협업 유형', data.collaborationType],
    ['주요 축종', data.species],
    ['현재 과제', data.currentChallenges],
    ['현재 준비 단계', data.preparationStage],
    ['희망 시작 시기', data.desiredStart],
    ['상세 요청사항', data.detailedRequest],
    ['개인정보 전송동의', data.consent]
  ];

  const missing = required
    .filter(function (row) {
      return !row[1];
    })
    .map(function (row) {
      return row[0];
    });

  if (missing.length) {
    return '필수 항목을 확인해 주세요: ' + missing.join(', ');
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
    return '올바른 이메일 주소를 입력해 주세요.';
  }
  return '';
}

function gabaInquiryValueV2_(params, name) {
  const raw = params[name];
  const list = Array.isArray(raw) ? raw : raw == null ? [] : [raw];
  return list
    .map(function (value) {
      return String(value == null ? '' : value).trim();
    })
    .filter(Boolean)
    .join(', ')
    .slice(0, GABA_INQUIRY_CFG_V2.MAX_FIELD_LENGTH);
}

function gabaInquiryAllowV2_(email, company) {
  const cache = CacheService.getScriptCache();
  const digest = Utilities.computeDigest(
    Utilities.DigestAlgorithm.SHA_256,
    String(email).toLowerCase() + '|' + String(company).toLowerCase(),
    Utilities.Charset.UTF_8
  );
  const key =
    'gaba-inquiry-' +
    Utilities.base64EncodeWebSafe(digest).slice(0, 40);

  if (cache.get(key)) return false;
  cache.put(key, '1', GABA_INQUIRY_CFG_V2.RATE_LIMIT_SECONDS);
  return true;
}

function gabaInquirySheetV2_() {
  const ss = SpreadsheetApp.openById(GABA_INQUIRY_CFG_V2.SPREADSHEET_ID);
  let sheet = ss.getSheetByName(GABA_INQUIRY_CFG_V2.SHEET_NAME);

  if (!sheet) {
    sheet = ss.insertSheet(GABA_INQUIRY_CFG_V2.SHEET_NAME);
  }

  gabaEnsureHeadersV2_(sheet, GABA_INQUIRY_HEADERS_V2);

  return sheet;
}

function gabaInquiryAppendV2_(
  inquiryId,
  receivedAt,
  mailStatus,
  mailError,
  data,
  leadResult
) {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);

  try {
    const row = [
      inquiryId,
      receivedAt,
      mailStatus,
      mailError,
      data.company,
      data.contactName,
      data.departmentTitle,
      data.email,
      data.phone,
      data.countryRegion,
      data.collaborationType,
      data.selectedProduct,
      data.selectedSpecification,
      data.orderGuidePath,
      data.species,
      data.farmFeedVolume,
      data.currentChallenges,
      data.preparationStage,
      data.desiredStart,
      data.sampleInitialVolume,
      data.annualVolume,
      data.evaluationKpis,
      data.detailedRequest,
      data.consent,
      data.sourcePage,
      data.clientTimestamp,
      data.formVersion,
      leadResult && leadResult.leadId || '',
      leadResult && leadResult.status || 'PENDING',
      receivedAt,
      data.countryRegion,
      data.departmentTitle,
      data.collaborationType,
      data.selectedProduct,
      data.annualVolume || data.farmFeedVolume,
      data.preparationStage,
      data.selectedSpecification || data.evaluationKpis,
      data.detailedRequest,
      'SAVED',
      '',
      data.sourcePage,
      data.utm,
      data.nextAction
    ].map(gabaInquirySheetValueV2_);

    gabaInquirySheetV2_().appendRow(row);
  } finally {
    lock.releaseLock();
  }
}

function gabaEnsureHeadersV2_(sheet, headers) {
  if (sheet.getLastRow() === 0) {
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    sheet.setFrozenRows(1);
    sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold');
    return;
  }
  const current = sheet.getRange(1, 1, 1, Math.max(sheet.getLastColumn(), 1)).getValues()[0];
  headers.forEach(function(header) {
    if (current.indexOf(header) === -1) {
      sheet.getRange(1, sheet.getLastColumn() + 1).setValue(header).setFontWeight('bold');
      current.push(header);
    }
  });
}

function gabaCreateLeadV2_(inquiryId, receivedAt, data) {
  const ss = SpreadsheetApp.openById(GABA_INQUIRY_CFG_V2.SPREADSHEET_ID);
  let sheet = ss.getSheetByName(GABA_INQUIRY_CFG_V2.LEAD_SHEET_NAME);
  if (!sheet) sheet = ss.insertSheet(GABA_INQUIRY_CFG_V2.LEAD_SHEET_NAME);
  gabaEnsureHeadersV2_(sheet, GABA_LEAD_HEADERS_V2);

  const leadId = 'LEAD-' + receivedAt.replace(/[^0-9]/g, '').slice(0, 8) + '-' +
    Utilities.getUuid().replace(/-/g, '').slice(0, 4).toUpperCase();
  const context = gabaLeadContextV2_(data);
  const values = {
    Lead_ID: leadId,
    Inquiry_ID: inquiryId,
    Created_At: receivedAt,
    Company: data.company,
    Contact: data.contactName,
    Country: data.countryRegion,
    Role: data.departmentTitle,
    Species: data.species,
    Product: data.selectedProduct,
    Expected_Volume: data.annualVolume || data.farmFeedVolume,
    Use_Case: data.currentChallenges,
    Project_Stage: data.preparationStage,
    Qualification_Status: 'New',
    Lead_Score: context.score,
    Owner: '',
    Next_Action: context.nextAction,
    Next_Action_Date: '',
    Buyer_Pack: context.buyerPack,
    Sample_Status: 'Not Started',
    Pilot_Status: 'Not Started',
    Quote_Status: 'Not Started',
    PO_Status: 'Not Started',
    Last_Activity: receivedAt,
    Notes: 'Created automatically from ' + inquiryId + '. ' + data.detailedRequest
  };
  const row = GABA_LEAD_HEADERS_V2.map(function(header) {
    return gabaInquirySheetValueV2_(values[header] || '');
  });
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    sheet.appendRow(row);
  } finally {
    lock.releaseLock();
  }
  return { leadId: leadId, status: 'CREATED', error: '' };
}

function gabaLeadContextV2_(data) {
  const text = [data.collaborationType, data.preparationStage, data.currentChallenges].join(' ').toLowerCase();
  let buyerPack = 'Technical Validation Pack';
  let nextAction = 'Review inquiry and confirm technical requirements';
  if (/pilot|farm|field/.test(text)) {
    buyerPack = 'Farm Pilot Pack';
    nextAction = 'Confirm pilot scope, KPI and sample requirement';
  } else if (/purchase|procurement|quote|price|commercial/.test(text)) {
    buyerPack = 'Commercial Supply Pack';
    nextAction = 'Confirm specification, MOQ, price and lead time';
  } else if (/import|export|regulatory|importer/.test(text)) {
    buyerPack = 'Importer Readiness Pack';
    nextAction = 'Review regulatory, import and specification requirements';
  }
  const score = Math.min(100, 20 + (data.company ? 10 : 0) + (data.annualVolume || data.farmFeedVolume ? 20 : 0) +
    (data.preparationStage ? 15 : 0) + (data.detailedRequest ? 20 : 0) + (data.evaluationKpis ? 15 : 0));
  return { buyerPack: buyerPack, nextAction: nextAction, score: score };
}

function gabaInquiryUpdateLeadV2_(inquiryId, leadResult) {
  const sheet = gabaInquirySheetV2_();
  const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  const inquiryColumn = headers.indexOf('Inquiry_ID') + 1;
  const leadColumn = headers.indexOf('Lead_ID') + 1;
  const statusColumn = headers.indexOf('Lead_Status') + 1;
  if (!inquiryColumn || !leadColumn || !statusColumn) return;
  const match = sheet.getRange(2, inquiryColumn, Math.max(sheet.getLastRow() - 1, 1), 1)
    .getValues().findIndex(function(row) { return String(row[0]) === inquiryId; });
  if (match < 0) return;
  const rowNumber = match + 2;
  sheet.getRange(rowNumber, leadColumn).setValue(leadResult.leadId || '');
  sheet.getRange(rowNumber, statusColumn).setValue(leadResult.status || 'FAILED');
}

function gabaRefreshB2bKpiV2_() {
  const ss = SpreadsheetApp.openById(GABA_INQUIRY_CFG_V2.SPREADSHEET_ID);
  const leadSheet = ss.getSheetByName(GABA_INQUIRY_CFG_V2.LEAD_SHEET_NAME);
  const now = Utilities.formatDate(new Date(), GABA_INQUIRY_CFG_V2.TZ, 'yyyy-MM-dd HH:mm:ss');
  const source = 'Lead_Pipeline / automated calculation';
  const empty = {
    total_leads: 0, new_leads: 0, qualified_leads: 0, samples: 0,
    active_pilots: 0, completed_pilots: 0, quotes: 0, pos: 0, reorders: 0,
    lead_to_qualified_rate: '', qualified_to_sample_rate: '', sample_to_pilot_rate: '',
    pilot_to_quote_rate: '', quote_to_po_rate: '', average_first_response_hours: '',
    overdue_next_actions: 0, evidence_reviews: 'Pending Verification',
    regulatory_reviews: 'Pending Verification', failed_sources: 'Pending Sync'
  };
  if (!leadSheet || leadSheet.getLastRow() < 2) {
    gabaUpsertStatusRowsV2_(ss, 'B2B_KPI', empty, source);
    return empty;
  }
  const lastColumn = leadSheet.getLastColumn();
  const headers = leadSheet.getRange(1, 1, 1, lastColumn).getValues()[0].map(String);
  const rows = leadSheet.getRange(2, 1, leadSheet.getLastRow() - 1, lastColumn).getValues();
  const col = function(name) { return headers.indexOf(name); };
  const value = function(row, name) { const index = col(name); return index < 0 ? '' : String(row[index] || '').trim(); };
  const nonEmpty = function(text) { return text && !/^(not started|none|no|n\/a|pending)$/i.test(text); };
  const count = function(name, predicate) { return rows.filter(function(row) { return predicate(value(row, name)); }).length; };
  const qualified = count('Qualification_Status', function(status) { return /qualified|technical|sample|pilot|quote|po|supply|reorder/i.test(status); });
  const samples = count('Sample_Status', nonEmpty);
  const activePilots = count('Pilot_Status', function(status) { return /active|in progress|running|started/i.test(status); });
  const completedPilots = count('Pilot_Status', function(status) { return /complete|completed|done/i.test(status); });
  const quotes = count('Quote_Status', nonEmpty);
  const pos = count('PO_Status', function(status) { return /received|approved|issued|complete|done/i.test(status); });
  const reorders = count('Last_Activity', function(activity) { return /reorder|repeat/i.test(activity); });
  const total = rows.length;
  const ratio = function(numerator, denominator) { return denominator ? Math.round(numerator / denominator * 10000) / 100 : ''; };
  const overdue = rows.filter(function(row) {
    const date = value(row, 'Next_Action_Date');
    return date && new Date(date).getTime() < new Date().getTime();
  }).length;
  const metrics = Object.assign(empty, {
    total_leads: total,
    new_leads: count('Qualification_Status', function(status) { return /^new$/i.test(status); }),
    qualified_leads: qualified,
    samples: samples,
    active_pilots: activePilots,
    completed_pilots: completedPilots,
    quotes: quotes,
    pos: pos,
    reorders: reorders,
    lead_to_qualified_rate: ratio(qualified, total),
    qualified_to_sample_rate: ratio(samples, qualified),
    sample_to_pilot_rate: ratio(activePilots + completedPilots, samples),
    pilot_to_quote_rate: ratio(quotes, activePilots + completedPilots),
    quote_to_po_rate: ratio(pos, quotes),
    overdue_next_actions: overdue
  });
  gabaUpsertStatusRowsV2_(ss, 'B2B_KPI', metrics, source);
  return metrics;
}

function gabaInquirySheetValueV2_(value) {
  const text = String(value == null ? '' : value);
  return /^[=+\-@]/.test(text) ? "'" + text : text;
}

function gabaInquiryRowsV2_(inquiryId, receivedAt, data) {
  return [
    ['문의번호', inquiryId],
    ['접수시각', receivedAt],
    ['회사·기관명', data.company],
    ['담당자명', data.contactName],
    ['직책·부서', data.departmentTitle],
    ['이메일', data.email],
    ['연락처', data.phone],
    ['국가·지역', data.countryRegion],
    ['협업 유형', data.collaborationType],
    ['선택 제품', data.selectedProduct],
    ['선택 규격·형태', data.selectedSpecification],
    ['주문 가이드 경로', data.orderGuidePath],
    ['주요 축종', data.species],
    ['사육규모·사료물량', data.farmFeedVolume],
    ['현재 해결 과제', data.currentChallenges],
    ['현재 준비 단계', data.preparationStage],
    ['희망 시작 시기', data.desiredStart],
    ['예상 샘플·초도 물량', data.sampleInitialVolume],
    ['예상 연간 물량', data.annualVolume],
    ['핵심 평가지표', data.evaluationKpis],
    ['상세 요청사항', data.detailedRequest],
    ['개인정보 전송동의', data.consent],
    ['접수 페이지', data.sourcePage],
    ['클라이언트 시각', data.clientTimestamp]
  ];
}

function gabaInquiryPlainBodyV2_(inquiryId, receivedAt, data) {
  return gabaInquiryRowsV2_(inquiryId, receivedAt, data)
    .map(function (row) {
      return row[0] + ': ' + (row[1] || '미입력');
    })
    .join('\n\n');
}

function gabaInquiryHtmlBodyV2_(inquiryId, receivedAt, data) {
  const rows = gabaInquiryRowsV2_(inquiryId, receivedAt, data)
    .map(function (row) {
      return (
        '<tr>' +
        '<th style="padding:9px 12px;text-align:left;background:#f2f7f4;border:1px solid #dce7e1;white-space:nowrap">' +
        gabaInquiryEscapeHtmlV2_(row[0]) +
        '</th>' +
        '<td style="padding:9px 12px;border:1px solid #dce7e1;line-height:1.55">' +
        gabaInquiryEscapeHtmlV2_(row[1] || '미입력').replace(/\n/g, '<br>') +
        '</td>' +
        '</tr>'
      );
    })
    .join('');

  return (
    '<div style="font-family:Arial,\'Noto Sans KR\',sans-serif;color:#17372b">' +
    '<h2 style="margin:0 0 8px">GABA Feed 사업협업 문의</h2>' +
    '<p style="margin:0 0 18px;color:#65766e">문의자 이메일로 바로 회신할 수 있습니다.</p>' +
    '<table style="border-collapse:collapse;width:100%;max-width:820px">' +
    rows +
    '</table>' +
    '</div>'
  );
}

function gabaInquiryEscapeHtmlV2_(value) {
  return String(value == null ? '' : value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function gabaInquiryResponseV2_(ok, message, inquiryId, extra) {
  const payload = Object.assign(
    {
      source: 'cellpinda-gaba-inquiry',
      ok: Boolean(ok),
      message: String(message || ''),
      inquiry_id: String(inquiryId || '')
    },
    extra || {}
  );

  const json = JSON.stringify(payload).replace(/</g, '\\u003c');
  const html =
    '<!doctype html><html><head><meta charset="utf-8"><title>Inquiry response</title></head>' +
    '<body><script>window.parent.postMessage(' +
    json +
    ', "*");<\/script>' +
    '<p style="font-family:sans-serif">' +
    gabaInquiryEscapeHtmlV2_(message) +
    '</p></body></html>';

  return HtmlService.createHtmlOutput(html)
    .setTitle('Cellpinda inquiry response')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}
