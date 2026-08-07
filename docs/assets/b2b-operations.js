(() => {
  'use strict';

  const OPERATIONS_URL = 'data/b2b_operations.json';
  const HEALTH_URL = 'data/platform_health.json';

  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  async function loadJson(url, fallback = {}) {
    try {
      const response = await fetch(url, { cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.warn(`B2B platform data unavailable: ${url}`, error);
      return fallback;
    }
  }

  function buildSection(data, health) {
    const stages = Array.isArray(data.stages) ? data.stages : [];
    const packs = Array.isArray(data.buyer_packs) ? data.buyer_packs : [];
    const services = Array.isArray(data.service_targets) ? data.service_targets : [];
    const documents = Array.isArray(data.document_status) ? data.document_status : [];
    const guardrails = Array.isArray(data.claim_guardrails) ? data.claim_guardrails : [];
    const healthStatus = health.status || 'unknown';
    const healthLabel = {
      healthy: '정상', partial: '부분 정상', degraded: '점검 필요', unknown: '확인 중'
    }[healthStatus] || healthStatus;

    return `
      <div class="container b2b-operations-container">
        <div class="b2b-operations-hero">
          <div>
            <span class="b2b-operations-eyebrow">BUYER DEAL ROOM · B2B OPERATIONS</span>
            <h2>${escapeHtml(data.platform_goal?.title || '제품 정보에서 구매 실행까지')}</h2>
            <p>${escapeHtml(data.platform_goal?.summary || '')}</p>
          </div>
          <div class="b2b-health-card ${escapeHtml(healthStatus)}">
            <span>PLATFORM HEALTH</span>
            <strong><i></i>${escapeHtml(healthLabel)}</strong>
            <small>${escapeHtml(health.public_note || '공개 운영상태를 확인하고 있습니다.')}</small>
          </div>
        </div>

        <div class="b2b-flow" aria-label="B2B 운영 단계">
          ${stages.map((stage) => `
            <article>
              <i>${escapeHtml(stage.no)}</i>
              <span>${escapeHtml(stage.name)}</span>
              <h3>${escapeHtml(stage.ko)}</h3>
              <p>${escapeHtml(stage.description)}</p>
              <small>완료기준 · ${escapeHtml(stage.exit)}</small>
            </article>`).join('')}
        </div>

        <div class="b2b-pack-heading">
          <div>
            <span>ROLE-SPECIFIC BUYER PACKS</span>
            <h3>내 역할에 맞는 검토팩부터 시작하세요.</h3>
          </div>
          <p>선택한 팩의 제품·단계·요청자료가 사업협업 문의에 자동 반영됩니다.</p>
        </div>

        <div class="b2b-pack-grid">
          ${packs.map((pack) => `
            <article class="b2b-pack-card">
              <span class="b2b-pack-role">${escapeHtml(pack.role)}</span>
              <h4>${escapeHtml(pack.title)}</h4>
              <p>${escapeHtml(pack.subtitle)}</p>
              <ul>${(pack.items || []).map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>
              <button type="button" data-b2b-pack="${escapeHtml(pack.id)}">${escapeHtml(pack.request)} <b>→</b></button>
            </article>`).join('')}
        </div>

        <div class="b2b-operation-bottom">
          <div class="b2b-service-card">
            <span>OPERATING TARGETS</span>
            <h3>바이어 대응 운영목표</h3>
            <div>${services.map((item) => `
              <p><strong>${escapeHtml(item.target)}</strong><span>${escapeHtml(item.label)}<small>${escapeHtml(item.note)}</small></span></p>`).join('')}</div>
          </div>
          <div class="b2b-document-card">
            <span>DOCUMENT READINESS</span>
            <h3>현재 제공 가능한 자료</h3>
            <div>${documents.map((item) => `
              <a href="${escapeHtml(item.url || '#contact')}" class="${escapeHtml(String(item.status || '').toLowerCase().replaceAll(' ', '-'))}">
                <span>${escapeHtml(item.name)}</span><strong>${escapeHtml(item.status)}</strong>
              </a>`).join('')}</div>
          </div>
        </div>

        <details class="b2b-guardrails">
          <summary>객관적 사업검토 원칙</summary>
          <ul>${guardrails.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>
        </details>
      </div>`;
  }

  function ensureHidden(form, name, value) {
    let field = form.querySelector(`input[type="hidden"][name="${name}"]`);
    if (!field) {
      field = document.createElement('input');
      field.type = 'hidden';
      field.name = name;
      form.append(field);
    }
    field.value = value;
  }

  function setSelect(form, name, value) {
    const select = form.elements.namedItem(name);
    if (!select || select.tagName !== 'SELECT') return;
    const option = [...select.options].find((item) => item.value === value || item.textContent.trim() === value);
    if (!option) return;
    select.value = option.value;
    select.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function checkCollaboration(form, values) {
    values.forEach((value) => {
      const field = [...form.querySelectorAll('input[name="협업_유형"]')]
        .find((item) => item.value === value);
      if (field) field.checked = true;
    });
  }

  function requestPack(pack, section) {
    const form = document.getElementById('businessInquiryForm');
    const contact = document.getElementById('contact') || document.querySelector('.inquiry-section');
    if (!form || !contact) {
      window.location.href = `mailto:feed@cellpinda.com?subject=${encodeURIComponent(`[GABA Feed] ${pack.request}`)}`;
      return;
    }

    ensureHidden(form, 'B2B_요청팩', pack.title);
    ensureHidden(form, 'B2B_바이어역할', pack.role);
    ensureHidden(form, '선택제품', pack.product);
    ensureHidden(form, '주문가이드_경로', pack.stage);
    setSelect(form, '현재_준비단계', pack.stage);

    const collaboration = pack.id === 'pilot'
      ? ['파일럿', '공동연구']
      : pack.id === 'importer'
        ? ['수출입']
        : pack.id === 'technical'
          ? ['원료', '공동개발']
          : ['원료'];
    checkCollaboration(form, collaboration);

    const message = form.elements.namedItem('상세_요청사항');
    const summary = [
      '[Buyer Deal Room 요청]',
      `- 바이어 역할: ${pack.role}`,
      `- 요청팩: ${pack.title}`,
      `- 제품: ${pack.product}`,
      `- 현재 단계: ${pack.stage}`,
      `- 요청자료: ${(pack.items || []).join(', ')}`,
      '- 요청사항: 제공 가능 자료, 추가로 필요한 입력정보, 예상 회신일정을 안내해 주세요.'
    ].join('\n');
    if (message && !message.value.includes('[Buyer Deal Room 요청]')) {
      message.value = message.value.trim() ? `${summary}\n\n${message.value.trim()}` : summary;
      message.dispatchEvent(new Event('input', { bubbles: true }));
    }

    contact.scrollIntoView({
      behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
      block: 'start'
    });

    const status = section.querySelector('.b2b-live-status');
    if (status) status.textContent = `${pack.title} 요청내용이 문의폼에 반영되었습니다.`;
  }

  function addNavigation(section) {
    const nav = document.getElementById('nav');
    if (!nav || nav.querySelector('[data-b2b-operations-nav]')) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = 'B2B 운영';
    button.dataset.b2bOperationsNav = 'true';
    const downloadButton = nav.querySelector('[data-scroll="downloads"]');
    if (downloadButton) downloadButton.before(button);
    else nav.append(button);
    button.addEventListener('click', () => {
      section.scrollIntoView({ behavior: 'smooth', block: 'start' });
      nav.classList.remove('open');
    });
  }

  async function init() {
    if (document.getElementById('b2b-operations')) return;
    const [data, health] = await Promise.all([
      loadJson(OPERATIONS_URL, {}),
      loadJson(HEALTH_URL, { status: 'unknown', public_note: '운영상태 파일을 생성하고 있습니다.' })
    ]);
    if (!data || !Array.isArray(data.stages)) return;

    const section = document.createElement('section');
    section.id = 'b2b-operations';
    section.className = 'b2b-operations-section';
    section.innerHTML = buildSection(data, health) + '<p class="b2b-live-status" role="status" aria-live="polite"></p>';

    const downloads = document.getElementById('downloads');
    const contact = document.getElementById('contact') || document.querySelector('.inquiry-section');
    if (downloads) downloads.before(section);
    else if (contact) contact.before(section);
    else document.querySelector('main')?.append(section);

    const packMap = new Map((data.buyer_packs || []).map((pack) => [pack.id, pack]));
    section.querySelectorAll('[data-b2b-pack]').forEach((button) => {
      button.addEventListener('click', () => {
        const pack = packMap.get(button.dataset.b2bPack);
        if (pack) requestPack(pack, section);
      });
    });

    addNavigation(section);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
