(() => {
  'use strict';

  function ensureB2BOperationsAssets() {
    if (!document.querySelector('link[data-b2b-operations]')) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = 'assets/b2b-operations.css';
      link.dataset.b2bOperations = 'v1';
      document.head.append(link);
    }
    if (!document.querySelector('script[data-b2b-operations]')) {
      const script = document.createElement('script');
      script.src = 'assets/b2b-operations.js';
      script.dataset.b2bOperations = 'v1';
      script.async = false;
      document.head.append(script);
    }
  }

  ensureB2BOperationsAssets();

  const DATA_URL = 'data/technical_documents.json';
  let items = [];
  let activeCategory = '전체';
  let observer = null;
  let rendering = false;

  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  function buildCard(item) {
    const isNew = item.status === 'NEW';
    const primaryLabel = item.format === 'PDF' ? 'PDF 자료 열기' : '웹 자료 읽기';
    const mainUrl = item.url || item.web_url || '#';
    const webLink = item.web_url && item.web_url !== mainUrl
      ? `<div class="technical-document-extra"><a href="${escapeHtml(item.web_url)}">웹 사양서 보기</a></div>`
      : '';
    return `
      <article class="technical-document-card" data-tech-category="${escapeHtml(item.category)}">
        <a href="${escapeHtml(mainUrl)}" target="${item.format === 'PDF' ? '_blank' : '_self'}" rel="${item.format === 'PDF' ? 'noreferrer' : ''}" style="position:absolute;inset:0" aria-label="${escapeHtml(item.title)} ${primaryLabel}"></a>
        <div class="technical-document-meta">
          <span class="technical-document-category">${escapeHtml(item.category)}</span>
          <span class="technical-document-badges">
            ${isNew ? '<span class="new">NEW</span>' : ''}
            <span>${escapeHtml(item.format)}</span>
            <span>v${escapeHtml(item.version)}</span>
            <span>${escapeHtml(item.language)}</span>
          </span>
        </div>
        <h3>${escapeHtml(item.title)}</h3>
        <p>${escapeHtml(item.description)}</p>
        <div class="technical-document-action"><span>${primaryLabel}</span><b aria-hidden="true">→</b></div>
        ${webLink}
      </article>`;
  }

  function render() {
    const section = document.getElementById('downloads');
    if (!section || !items.length || rendering) return;
    rendering = true;

    const container = section.querySelector('.container');
    const oldList = section.querySelector('.doc-list');
    let shell = section.querySelector('.technical-documents-shell');
    if (!shell) {
      shell = document.createElement('div');
      shell.className = 'technical-documents-shell';
      if (oldList) oldList.replaceWith(shell);
      else container?.append(shell);
    }

    const categories = ['전체', ...new Set(items.map((item) => item.category))];
    const shown = activeCategory === '전체' ? items : items.filter((item) => item.category === activeCategory);
    shell.innerHTML = `
      <div class="technical-documents-toolbar">
        <div class="technical-documents-filter" role="group" aria-label="기술·사업 자료 분류">
          ${categories.map((category) => `<button type="button" class="${category === activeCategory ? 'active' : ''}" data-tech-filter="${escapeHtml(category)}">${escapeHtml(category)}</button>`).join('')}
        </div>
        <span class="technical-documents-updated">검증자료 ${items.length}건 · 2026-08-07</span>
      </div>
      <div class="technical-documents-grid">${shown.map(buildCard).join('')}</div>
      <div class="technical-documents-note"><strong>자료 사용 원칙</strong><br>가바크루드의 GABA 20% 외 수치형 품질한계와 축종별 효능은 상업 제조로트·분석법·목표국 규정 및 현장시험으로 최종 확정합니다. 웹 요약은 원자료의 핵심 구조를 보존해 정리한 사업검토용 문서입니다.</div>`;

    shell.querySelectorAll('[data-tech-filter]').forEach((button) => {
      button.addEventListener('click', () => {
        activeCategory = button.dataset.techFilter || '전체';
        render();
      });
    });

    section.dataset.technicalDocumentsReady = 'true';
    rendering = false;
  }

  async function load() {
    try {
      const response = await fetch(DATA_URL, { cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      items = Array.isArray(data.items) ? data.items : [];
      render();

      const section = document.getElementById('downloads');
      if (section && 'MutationObserver' in window) {
        observer = new MutationObserver(() => {
          if (rendering) return;
          const shell = section.querySelector('.technical-documents-shell');
          if (!shell || !section.dataset.technicalDocumentsReady) render();
        });
        observer.observe(section, { childList: true, subtree: true });
        window.setTimeout(() => observer?.disconnect(), 12000);
      }
    } catch (error) {
      console.warn('Technical documents index unavailable', error);
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load);
  else load();
})();