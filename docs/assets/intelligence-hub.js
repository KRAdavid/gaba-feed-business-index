(() => {
  'use strict';
  const DATA_URL = 'data/intelligence_evidence.json';
  const escapeHtml = (value) => String(value ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#039;');

  function ensureStyle() {
    if (document.querySelector('link[data-intelligence-hub]')) return;
    const link = document.createElement('link'); link.rel = 'stylesheet'; link.href = 'assets/intelligence-hub.css'; link.dataset.intelligenceHub = 'v1'; document.head.append(link);
  }

  function card(item) {
    return `<article class="intelligence-evidence-card"><div class="intelligence-evidence-meta"><span class="intelligence-evidence-species">${escapeHtml(item.species)}</span><span class="intelligence-evidence-level">${escapeHtml(item.evidence_level)}</span></div><h4>${escapeHtml(item.title)}</h4><p class="intelligence-evidence-stage">${escapeHtml(item.stage)} · ${escapeHtml(item.evidence_type)}</p><dl class="intelligence-evidence-facts"><div><dt>무슨 연구인가</dt><dd>${escapeHtml(item.research_question)}</dd></div><div><dt>누가 연구했나</dt><dd>${escapeHtml(item.researchers)}<br>${escapeHtml(item.institution)}</dd></div><div><dt>시험 설계·급여</dt><dd>${escapeHtml(item.design)}<br><strong>${escapeHtml(item.dose)}</strong></dd></div></dl><div class="intelligence-evidence-result"><strong>무슨 결과가 나왔나</strong>${escapeHtml(item.result)}</div><details><summary>한계와 산업 적용 방향</summary><p><b>한계:</b> ${escapeHtml(item.limitation)}<br><b>적용:</b> ${escapeHtml(item.industry_direction)}</p></details><div class="intelligence-evidence-source"><small>${escapeHtml(item.source)} · ${escapeHtml(item.year)}</small><a href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer">원문 확인 ↗</a></div></article>`;
  }

  function build(data) {
    const items = Array.isArray(data.items) ? data.items : [];
    const species = ['전체', ...new Set(items.map((item) => item.species))];
    return `<div class="intelligence-evidence-shell" id="intelligenceEvidenceHub"><div class="intelligence-evidence-head"><div><span class="product-label">EVIDENCE-FIRST SPECIES BRIEF</span><h3>축종별 적용 사례를 연구 설계부터 읽습니다.</h3></div><p>${escapeHtml(data.method_note || '')}</p></div><div class="intelligence-filters" role="tablist" aria-label="축종별 연구 필터">${species.map((name, index) => `<button type="button" class="${index === 0 ? 'active' : ''}" data-intelligence-species="${escapeHtml(name)}">${escapeHtml(name)}</button>`).join('')}</div><div class="intelligence-evidence-grid">${items.map(card).join('')}</div><p class="intelligence-evidence-note"><strong>읽는 법:</strong> ‘농장시험’과 ‘동물시험’을 구분하고, 결과의 p값·표본수·급여단위를 함께 확인하세요. 논문 결과는 제품 보장효능이나 모든 축종의 권장량이 아니며, 산업 적용 전에는 동일 축종·사료·환경의 대조시험이 필요합니다. 데이터 기준일 ${escapeHtml(data.updated_at || '')}</p></div>`;
  }

  async function init() {
    if (document.getElementById('intelligenceEvidenceHub')) return;
    const section = document.getElementById('knowledge'); if (!section) return;
    ensureStyle();
    try {
      const response = await fetch(DATA_URL, { cache: 'no-store' }); if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      const title = section.querySelector('.section-title'); if (!title) return;
      title.insertAdjacentHTML('afterend', build(data));
      const grid = document.querySelector('#intelligenceEvidenceHub .intelligence-evidence-grid');
      document.querySelectorAll('[data-intelligence-species]').forEach((button) => button.addEventListener('click', () => {
        document.querySelectorAll('[data-intelligence-species]').forEach((item) => item.classList.remove('active')); button.classList.add('active');
        const selected = button.dataset.intelligenceSpecies;
        [...grid.children].forEach((cardElement, index) => { cardElement.hidden = selected !== '전체' && data.items[index].species !== selected; });
      }));
    } catch (error) { console.warn('Intelligence evidence hub unavailable', error); }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
