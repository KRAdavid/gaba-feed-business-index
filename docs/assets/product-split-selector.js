(() => {
  'use strict';

  const PRODUCT_COPY = {
    crude: {
      eyebrow: '원료를 직접 배합하려면',
      name: '가바크루드',
      en: 'GABA Crude',
      summary: 'GABA 20% 기준품과 5~20% 맞춤 농도로 공급하는 사료용 원료 솔루션',
      points: ['표준 규격·CoA', '프리믹스·배합사료 적용', '샘플·견적부터 시작'],
      action: '가바크루드 자세히 보기',
      theme: 'crude'
    },
    caremix: {
      eyebrow: '브랜드 제품을 개발하려면',
      name: '가바케어믹스',
      en: 'GABA Care Mix',
      summary: '축종별 GABA·미네랄 매트릭스를 공동 설계하는 OEM·ODM 솔루션',
      points: ['축종별 맞춤 설계', '농장 파일럿·검증', '브랜드 제품 공동출시'],
      action: '가바케어믹스 자세히 보기',
      theme: 'caremix'
    }
  };

  function enhanceSelector() {
    const selector = document.querySelector('.product-switch');
    if (!selector || selector.dataset.splitSelector === 'true') return false;

    selector.dataset.splitSelector = 'true';
    selector.classList.add('product-split-selector');
    selector.setAttribute('aria-label', '가바크루드와 가바케어믹스 중 제품 선택');

    const guide = document.createElement('div');
    guide.className = 'product-split-guide';
    guide.innerHTML = '<strong>원하는 도입 방식을 선택하세요</strong><span>좌우 카드를 누르면 아래 제품 설명이 바로 바뀝니다.</span>';
    selector.before(guide);

    selector.querySelectorAll('[data-product]').forEach((button) => {
      const key = button.dataset.product;
      const product = PRODUCT_COPY[key];
      if (!product) return;

      button.classList.add('product-split-card', `product-split-card--${product.theme}`);
      button.innerHTML = `
        <span class="product-split-eyebrow">${escapeHtml(product.eyebrow)}</span>
        <span class="product-split-title-row">
          <strong>${escapeHtml(product.name)}</strong>
          <small>${escapeHtml(product.en)}</small>
        </span>
        <span class="product-split-summary">${escapeHtml(product.summary)}</span>
        <span class="product-split-points">
          ${product.points.map((point) => `<i>${escapeHtml(point)}</i>`).join('')}
        </span>
        <span class="product-split-action">${escapeHtml(product.action)} <b aria-hidden="true">→</b></span>
        <span class="product-split-state" aria-live="polite"></span>`;

      button.setAttribute('aria-label', `${product.name} 제품 설명 보기`);
      button.addEventListener('click', () => {
        window.requestAnimationFrame(() => {
          syncState(selector);
          document.getElementById('productFeature')?.scrollIntoView({
            behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
            block: 'nearest'
          });
        });
      });
    });

    syncState(selector);
    return true;
  }

  function syncState(selector) {
    selector.querySelectorAll('[data-product]').forEach((button) => {
      const active = button.classList.contains('active');
      const state = button.querySelector('.product-split-state');
      button.setAttribute('aria-pressed', String(active));
      if (state) state.textContent = active ? '현재 선택됨' : '클릭해서 전환';
    });
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  function init() {
    if (enhanceSelector()) return;
    const observer = new MutationObserver(() => {
      if (enhanceSelector()) observer.disconnect();
    });
    observer.observe(document.documentElement, { childList: true, subtree: true });
    window.setTimeout(() => observer.disconnect(), 10000);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
