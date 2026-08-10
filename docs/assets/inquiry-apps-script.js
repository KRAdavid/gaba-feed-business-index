(() => {
  'use strict';

  const APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbyNO1bwsnuHDMJsKpcCU2KUVMESnSD2_ZaauD_-sbqVE_X031-_oWS3ujh3zhYbMuCoqQ/exec';
  const PRIMARY_RECIPIENT = 'feed@cellpinda.com';
  const LEGACY_RECIPIENT = 'dubaissday@cellpinda.com';
  const MESSAGE_SOURCE = 'cellpinda-gaba-inquiry';
  const IFRAME_NAME = 'cellpindaInquiryReceiver';
  const RESPONSE_TIMEOUT_MS = 60000;
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

  function replaceLegacyRecipient(root) {
    if (!root) return;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const nodes = [];
    let node = walker.nextNode();
    while (node) {
      if (node.nodeValue && node.nodeValue.includes(LEGACY_RECIPIENT)) nodes.push(node);
      node = walker.nextNode();
    }
    nodes.forEach((textNode) => {
      textNode.nodeValue = textNode.nodeValue.replaceAll(LEGACY_RECIPIENT, PRIMARY_RECIPIENT);
    });
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
      <strong>셀핀다 사료사업 전용 수신</strong>
      <span>문의는 셀핀다 Google 시스템에서 처리되어 <b>${PRIMARY_RECIPIENT}</b>과 백업 수신함으로 전달되고, Master DB의 Inquiries 시트에도 기록됩니다.</span>`;
    replaceLegacyRecipient(form.closest('.inquiry-section') || form);
  }

  function values(form, name) {
    return [...form.querySelectorAll(`[name="${name}"]:checked`)].map((field) => field.value);
  }

  function buildFallbackBody(form) {
    const data = new FormData(form);
    const grouped = new Map();
    for (const [key, raw] of data.entries()) {
      if (key.startsWith('_') || key === 'action' || key === 'form_version') continue;
      const value = String(raw).trim();
      if (!value) continue;
      if (!grouped.has(key)) grouped.set(key, []);
      grouped.get(key).push(value);
    }
    return [...grouped.entries()]
      .map(([key, entries]) => `${key.replaceAll('_', ' ')}: ${entries.join(', ')}`)
      .join('\n\n');
  }

  function bindFallbackRecipient(form) {
    const fallback = form.querySelector('#inquiryMailFallback');
    if (!fallback || fallback.dataset.feedRecipientBound === 'true') return;

    fallback.addEventListener('click', (event) => {
      event.preventDefault();
      event.stopImmediatePropagation();

      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }
      const emptyGroup = [...form.querySelectorAll('[data-required-group]')]
        .find((group) => !group.querySelector('input[type="checkbox"]:checked'));
      if (emptyGroup) {
        const errorBox = form.querySelector('#inquiryError');
        if (errorBox) {
          errorBox.textContent = '필수 선택 항목에서 한 가지 이상 선택해 주세요.';
          errorBox.hidden = false;
        }
        emptyGroup.scrollIntoView({ behavior: 'smooth', block: 'center' });
        emptyGroup.querySelector('input')?.focus();
        return;
      }

      const company = form.querySelector('#inquiryCompany')?.value.trim() || '회사 미입력';
      const species = form.querySelector('#inquirySpecies')?.value || '축종 미정';
      const collaboration = values(form, '협업_유형').join('·') || '협업';
      const subject = `[GABA Feed 협업문의] ${company} · ${collaboration} · ${species}`;
      const body = buildFallbackBody(form);
      window.location.href = `mailto:${PRIMARY_RECIPIENT}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    }, { capture: true });

    fallback.dataset.feedRecipientBound = 'true';
  }

  function patchForm() {
    const form = document.getElementById('businessInquiryForm');
    if (!form) return false;

    ensureReceiverFrame();
    form.action = APPS_SCRIPT_URL;
    form.method = 'POST';
    form.target = IFRAME_NAME;
    form.dataset.deliveryRoute = 'google-apps-script';
    form.dataset.primaryRecipient = PRIMARY_RECIPIENT;
    ensureHidden(form, 'action', 'inquiry');
    ensureHidden(form, 'form_version', 'GABA_FEED_INQUIRY_V3');
    ensureHidden(form, 'source_page', window.location.href.split('#')[0]);
    updateDeliveryNotice(form);
    bindFallbackRecipient(form);

    if (!form.dataset.appsScriptBound) {
      form.addEventListener('submit', (event) => {
        if (event.defaultPrevented) return;
        form.action = APPS_SCRIPT_URL;
        form.target = IFRAME_NAME;
        ensureHidden(form, 'action', 'inquiry');
        ensureHidden(form, 'form_version', 'GABA_FEED_INQUIRY_V3');
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
    const submit = form.querySelector('#inquirySubmit');
    if (errorBox) {
      errorBox.textContent = '문의 내용을 셀핀다 메일 서버로 전송하고 있습니다. 잠시만 기다려 주세요.';
      errorBox.hidden = false;
    }
    if (submit) {
      submit.disabled = true;
      submit.textContent = '전송 확인 중…';
    }
    responseTimer = window.setTimeout(() => {
      showFailure(form, '서버의 접수 확인이 60초 안에 도착하지 않았습니다. 중복 제출을 피하기 위해 먼저 메일함과 Master DB의 Inquiries 시트를 확인한 뒤, 기록이 없을 때만 “협업문의 다시 전송” 또는 “메일 앱으로 보내기”를 이용해 주세요.');
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
    const frame = document.querySelector(`iframe[name="${IFRAME_NAME}"]`);
    const fromReceiverFrame = Boolean(frame && frame.contentWindow && event.source === frame.contentWindow);
    const trustedOrigin = event.origin === 'null' || trustedGoogleOrigin(event.origin);
    if (!data || data.source !== MESSAGE_SOURCE || !fromReceiverFrame || !trustedOrigin) return;

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
