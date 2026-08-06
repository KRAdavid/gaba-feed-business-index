(() => {
  'use strict';

  // FormSubmit activation and delivery are more reliable when the primary
  // mailbox is a Gmail inbox. The official Cellpinda mailbox remains CC'd.
  const PRIMARY_RECIPIENT = 'dubaissday@gmail.com';
  const BUSINESS_RECIPIENT = 'dubaissday@cellpinda.com';
  const FORM_ENDPOINT = `https://formsubmit.co/${PRIMARY_RECIPIENT}`;

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

  function addDeliveryNotice(form) {
    if (form.querySelector('.inquiry-delivery-route')) return;
    const note = document.createElement('div');
    note.className = 'inquiry-delivery-route';
    note.setAttribute('role', 'note');
    note.innerHTML = `
      <strong>이중 수신 경로</strong>
      <span>문의는 <b>${BUSINESS_RECIPIENT}</b>과 백업 수신함으로 함께 전달됩니다. 최초 1회 FormSubmit 활성화가 필요합니다.</span>`;

    const submitNote = form.querySelector('.inquiry-submit-note');
    if (submitNote) submitNote.insertAdjacentElement('afterend', note);
    else form.querySelector('.inquiry-actions')?.insertAdjacentElement('beforebegin', note);
  }

  function patchForm() {
    const form = document.getElementById('businessInquiryForm');
    if (!form) return false;

    form.action = FORM_ENDPOINT;
    form.dataset.deliveryRoute = 'gmail-primary-cellpinda-cc';
    ensureHidden(form, '_cc', BUSINESS_RECIPIENT);
    ensureHidden(form, '_url', window.location.href.split('#')[0]);
    addDeliveryNotice(form);

    // Re-apply immediately before submission in case another script mutated it.
    if (!form.dataset.deliveryGuardBound) {
      form.addEventListener('submit', () => {
        form.action = FORM_ENDPOINT;
        ensureHidden(form, '_cc', BUSINESS_RECIPIENT);
        ensureHidden(form, '_url', window.location.href.split('#')[0]);
      }, { capture: true });
      form.dataset.deliveryGuardBound = 'true';
    }
    return true;
  }

  function init() {
    if (patchForm()) return;
    // inquiry-form.js builds the form dynamically. Observe briefly if needed.
    const observer = new MutationObserver(() => {
      if (patchForm()) observer.disconnect();
    });
    observer.observe(document.documentElement, { childList: true, subtree: true });
    window.setTimeout(() => observer.disconnect(), 10000);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
