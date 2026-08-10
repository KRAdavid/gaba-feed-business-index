(() => {
  'use strict';

  const PANEL_ID = 'smartConditionalFields';
  const START = '[스마트 상담 자동설정]';
  const END = '[자동설정 끝]';
  let inputTimer = null;

  function css(value) {
    return window.CSS?.escape ? window.CSS.escape(String(value)) : String(value).replace(/["\\]/g, '\\$&');
  }

  function ensureHidden(form, name, value) {
    let field = form.querySelector(`input[type="hidden"][name="${css(name)}"]`);
    if (!field) {
      field = document.createElement('input');
      field.type = 'hidden';
      field.name = name;
      field.dataset.smartConsultation = 'true';
      form.append(field);
    }
    field.value = value;
  }

  function labelOf(field) {
    return field.closest('label')?.querySelector(':scope > span')?.textContent?.trim() || field.name;
  }

  function selectedText(field) {
    if (field.tagName === 'SELECT') return field.options[field.selectedIndex]?.textContent?.trim() || field.value;
    return String(field.value || '').trim();
  }

  function sync(form) {
    if (!form || form.id !== 'businessInquiryForm') return;
    const panel = form.querySelector(`#${PANEL_ID}`);
    if (!panel) return;

    const rows = [...panel.querySelectorAll('input[name], select[name], textarea[name]')]
      .map((field) => ({ name: field.name, label: labelOf(field), value: selectedText(field) }))
      .filter((row) => row.value);
    const conditionSummary = rows.map((row) => `${row.label}: ${row.value}`).join(' · ');
    ensureHidden(form, '스마트상담_조건별설정', conditionSummary);

    const specification = rows.find((row) => row.name === '희망_GABA_규격' || row.name === '희망_제품형태');
    if (specification) ensureHidden(form, '선택규격_형태', specification.value);

    const detail = form.elements.namedItem('상세_요청사항');
    if (!detail || !conditionSummary) return;
    const line = `- 조건별 자동설정: ${conditionSummary}`;
    let text = String(detail.value || '');
    if (!text.includes(START) || !text.includes(END)) return;
    if (/^- 조건별 자동설정:.*$/m.test(text)) text = text.replace(/^- 조건별 자동설정:.*$/m, line);
    else text = text.replace(END, `${line}\n${END}`);
    detail.value = text;
    detail.dispatchEvent(new Event('input', { bubbles: true }));
  }

  document.addEventListener('change', (event) => {
    const panel = event.target.closest?.(`#${PANEL_ID}`);
    if (panel) sync(panel.closest('form'));
  }, true);

  document.addEventListener('input', (event) => {
    const panel = event.target.closest?.(`#${PANEL_ID}`);
    if (!panel) return;
    window.clearTimeout(inputTimer);
    inputTimer = window.setTimeout(() => sync(panel.closest('form')), 180);
  }, true);

  document.addEventListener('submit', (event) => {
    if (event.target?.id === 'businessInquiryForm') sync(event.target);
  }, true);

  window.CellpindaSmartConsultationSync = { sync };
})();
