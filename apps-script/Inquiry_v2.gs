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
  'Detailed_Request', 'Consent', 'Source_Page', 'Client_Timestamp', 'Form_Version'
];

function setupGabaInquiryReceiver() {
  const sheet = gabaInquirySheetV2_();
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

function doPost(e) {
  try {
    const params = (e && e.parameters) || {};
    if (gabaInquiryValueV2_(params, 'action').toLowerCase() !== 'inquiry') {
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
    Utilities.formatDate(now, GABA_INQUIRY_CFG_V2.TZ, 'yyyyMMdd-HHmmss') +
    '-' +
    Utilities.getUuid().replace(/-/g, '').slice(0, 6).toUpperCase();

  let mailStatus = 'sent';
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
    mailStatus = 'failed';
    mailError = String(error && error.message ? error.message : error).slice(0, 500);
  }

  let sheetError = '';
  try {
    gabaInquiryAppendV2_(inquiryId, receivedAt, mailStatus, mailError, data);
  } catch (error) {
    sheetError = String(error && error.message ? error.message : error).slice(0, 500);
  }

  if (mailStatus !== 'sent') {
    return gabaInquiryResponseV2_(
      false,
      '문의는 기록되었으나 이메일 발송에 실패했습니다. 메일 앱으로 보내기를 눌러 주세요.',
      inquiryId,
      {
        mail_status: mailStatus,
        sheet_saved: !sheetError,
        error: mailError
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
      sheet_saved: !sheetError
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

  if (sheet.getLastRow() === 0) {
    sheet
      .getRange(1, 1, 1, GABA_INQUIRY_HEADERS_V2.length)
      .setValues([GABA_INQUIRY_HEADERS_V2]);
    sheet.setFrozenRows(1);
    sheet
      .getRange(1, 1, 1, GABA_INQUIRY_HEADERS_V2.length)
      .setFontWeight('bold');
  }

  return sheet;
}

function gabaInquiryAppendV2_(
  inquiryId,
  receivedAt,
  mailStatus,
  mailError,
  data
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
      data.formVersion
    ].map(gabaInquirySheetValueV2_);

    gabaInquirySheetV2_().appendRow(row);
  } finally {
    lock.releaseLock();
  }
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
