(() => {
  'use strict';

  const APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbxnLIZGWbJDiDPMlUJ3yef8cXI1jgZC5cZsaCBUbYBR6bNAdXskVTZBSrxSHZiIpCDYPA/exec';
  const MESSAGE_SOURCE = 'cellpinda-gaba-inquiry';
  const IFRAME_NAME = 'cellpindaInquiryReceiver';
  const RESPONSE_TIMEOUT_MS = 30000;
  let responseTimer = null;

  function ensureHidden(form, name, value) {
    let field = form.querySelector(`input[type="hidden"][name="${name}"]`);
    if (!field) {
      field = document.createElement('input');
      field.type = 'hidden';
      field.name = name;
      form.append(field);
    }
    field.value = value;
    return field;
  }

  function ensureReceiverFrame() {
    let frame = document.querySelector(`iframe[name="${IFRAME_NAME}"]`);
    if (frame) return frame;
    frame = document.createElement('iframe');
    frame.name = IFRAME_NAME;
    frame.title = '문의 전송 결과';
    frame.hidden = true;
    frame.setAttribute('aria-hidden', 'true');
    document.body.append(frame);
    return frame;
  }

  function updateDeliveryNotice(form) {
    let note = form.querySelector('.inquiry-delivery-route');
    if (!note) {
      note = document.createElement('div');
      note.className = 'inquiry-delivery-route';
      const actions = form.querySelector('.inquiry-actions');
      if (actions) actions.before(note);
      else form.append(note);
    }
    note.innerHTML = `
      <strong>셀핀다 직접 수신</strong>
      <span>문의는 셀핀다 Google 시스템에서 처리되어 <b>dubaissday@cellpinda.com</b>과 백업 수신함으로 전달되고, Master DB의 Inquiries 시트에도 기록됩니다.</span>`;
  }

  function patchForm() {
    const form = document.getElementById('businessInquiryForm');
    if (!form) return false;

    ensureReceiverFrame();
    form.action = APPS_SCRIPT_URL;
    form.method = 'POST';
    form.target = IFRAME_NAME;
    form.dataset.deliveryRoute = 'google-apps-script';
    ensureHidden(form, 'action', 'inquiry');
    ensureHidden(form, 'form_version', 'GABA_FEED_INQUIRY_V2');
    ensureHidden(form, 'source_page', window.location.href.split('#')[0]);
    updateDeliveryNotice(form);

    if (!form.dataset.appsScriptBound) {
      form.addEventListener('submit', (event) => {
        // inquiry-form.js performs validation first. Do nothing when it rejected the form.
        if (event.defaultPrevented) return;
        form.action = APPS_SCRIPT_URL;
        form.target = IFRAME_NAME;
        ensureHidden(form, 'action', 'inquiry');
        ensureHidden(form, 'form_version', 'GABA_FEED_INQUIRY_V2');
        ensureHidden(form, 'source_page', window.location.href.split('#')[0]);
        ensureHidden(form, 'client_timestamp', new Date().toISOString());
        startWaiting(form);
      });
      form.dataset.appsScriptBound = 'true';
    }
    return true;
  }

  function startWaiting(form) {
    window.clearTimeout(responseTimer);
    const errorBox = form.querySelector('#inquiryError');
    if (errorBox) errorBox.hidden = true;
    responseTimer = window.setTimeout(() => {
      showFailure(form, '메일 서버 응답이 지연되고 있습니다. 입력 내용은 유지되어 있으므로 “메일 앱으로 보내기”를 눌러 주세요.');
    }, RESPONSE_TIMEOUT_MS);
  }

  function trustedGoogleOrigin(origin) {
    try {
      const url = new URL(origin);
      return url.protocol === 'https:' && (
        url.hostname === 'script.google.com' ||
        url.hostname === 'script.googleusercontent.com' ||
        url.hostname.endsWith('.googleusercontent.com')
      );
    } catch (_error) {
      return false;
    }
  }

  function handleResponse(event) {
    const data = event.data;
    if (!data || data.source !== MESSAGE_SOURCE || !trustedGoogleOrigin(event.origin)) return;
    const form = document.getElementById('businessInquiryForm');
    if (!form) return;
    window.clearTimeout(responseTimer);
    if (data.ok) showSuccess(form, data);
    else showFailure(form, data.message || '문의 이메일 발송에 실패했습니다. 메일 앱 전송을 이용해 주세요.');
  }

  function showSuccess(form, data) {
    const success = form.closest('.inquiry-card')?.querySelector('#inquirySuccess');
    const errorBox = form.querySelector('#inquiryError');
    const submit = form.querySelector('#inquirySubmit');
    if (errorBox) errorBox.hidden = true;
    if (success) {
      success.hidden = false;
      const strong = success.querySelector('strong');
      const span = success.querySelector('span');
      if (strong) strong.textContent = '문의가 정상 접수되었습니다.';
      if (span) span.textContent = data.inquiry_id
        ? `문의번호 ${data.inquiry_id} · 담당자가 확인한 후 회신드립니다.`
        : '담당자가 내용을 확인한 후 회신드립니다.';
      success.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    if (submit) {
      submit.disabled = true;
      submit.textContent = '접수 완료';
    }
  }

  function showFailure(form, message) {
    const errorBox = form.querySelector('#inquiryError');
    const submit = form.querySelector('#inquirySubmit');
    const fallback = form.querySelector('#inquiryMailFallback');
    if (errorBox) {
      errorBox.textContent = message;
      errorBox.hidden = false;
      errorBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    if (submit) {
      submit.disabled = false;
      submit.textContent = '협업문의 다시 전송';
    }
    if (fallback) fallback.hidden = false;
  }

  function init() {
    window.addEventListener('message', handleResponse);
    if (patchForm()) return;
    const observer = new MutationObserver(() => {
      if (patchForm()) observer.disconnect();
    });
    observer.observe(document.documentElement, { childList: true, subtree: true });
    window.setTimeout(() => observer.disconnect(), 10000);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
