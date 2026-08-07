(() => {
  'use strict';

  let scheduled = false;

  function setButton(id, text, options = {}) {
    const button = document.getElementById(id);
    if (!button || button.dataset.ctaEnhanced === 'true') return;
    button.textContent = text;
    button.dataset.ctaEnhanced = 'true';
    if (options.arrow) button.classList.add('cta-arrow');
    if (options.attention) button.classList.add('cta-attention');
    if (options.label) button.setAttribute('aria-label', options.label);
  }

  function setLink(link, text, options = {}) {
    if (!link || link.dataset.ctaEnhanced === 'true') return;
    link.textContent = text;
    link.dataset.ctaEnhanced = 'true';
    if (options.arrow) link.classList.add('cta-arrow');
    if (options.attention) link.classList.add('cta-attention');
    if (options.label) link.setAttribute('aria-label', options.label);
  }

  function addHelper(container, text, marker) {
    if (!container || container.querySelector(`[data-cta-helper="${marker}"]`)) return;
    const helper = document.createElement('p');
    helper.className = 'cta-helper';
    helper.dataset.ctaHelper = marker;
    helper.textContent = text;
    const actions = container.querySelector('.visitor-result-actions, .order-guide-actions, .inquiry-actions');
    if (actions) actions.before(helper);
    else container.append(helper);
  }

  function enhanceHero() {
    const primary = document.querySelector('.hero .primary');
    if (primary && primary.dataset.ctaEnhanced !== 'true') {
      primary.textContent = '솔루션 빠르게 보기';
      primary.classList.add('cta-arrow');
      primary.dataset.ctaEnhanced = 'true';
      primary.setAttribute('aria-label', '가바크루드와 가바케어믹스 솔루션 빠르게 보기');
    }

    const navCta = document.querySelector('.nav-cta');
    setLink(navCta, '협업문의', {
      arrow: true,
      label: '사업협업 문의 작성으로 이동'
    });
  }

  function enhanceVisitorGuide() {
    setButton('visitorStart', '2분 도입진단 시작', {
      arrow: true,
      attention: true,
      label: '방문자 맞춤형 2분 도입진단 시작'
    });
    setButton('visitorApplyOrder', '추천 제품·도입경로 보기', {
      arrow: true,
      label: '추천 제품과 도입경로를 주문 가이드에서 확인'
    });
    setButton('visitorStartInquiry', '이 조건으로 상담 요청', {
      arrow: true,
      label: '진단 결과를 문의 폼에 적용해 상담 요청'
    });
    setButton('visitorCopyResult', '진단 결과 복사', {
      label: '진단 결과를 클립보드에 복사'
    });

    const intro = document.querySelector('.visitor-intro-card');
    if (intro && !intro.querySelector('[data-cta-helper="visitor-intro"]')) {
      const helper = document.createElement('p');
      helper.className = 'cta-helper';
      helper.dataset.ctaHelper = 'visitor-intro';
      helper.textContent = '어떤 제품이 맞는지 잘 모르시면, 이 진단부터 시작하세요. 답변 6개로 자료검토·샘플·파일럿·상업협의 경로를 안내합니다.';
      const start = intro.querySelector('#visitorStart');
      if (start) start.before(helper);
    }

    const result = document.querySelector('.visitor-result-card');
    addHelper(result, '추천 결과를 주문 가이드에서 자세히 확인하거나, 선택 내용을 그대로 상담 문의에 연결할 수 있습니다.', 'visitor-result');
  }

  function enhanceOrderGuide() {
    setButton('orderToInquiry', '이 선택으로 견적·주문 문의', {
      arrow: true,
      label: '선택한 제품과 조건으로 견적 및 주문 문의 시작'
    });
    setButton('orderCopySummary', '선택 내용 복사', {
      label: '선택한 주문 조건 복사'
    });

    document.querySelectorAll('.order-guide-shortcut').forEach((button) => {
      if (button.dataset.ctaEnhanced === 'true') return;
      button.textContent = button.textContent.replace(/\s*→\s*$/, '');
      button.classList.add('cta-arrow');
      button.dataset.ctaEnhanced = 'true';
    });

    const config = document.querySelector('.order-guide-config');
    addHelper(config, '제품을 선택한 뒤 축종·물량·시기를 입력하면 담당자가 확인할 수 있는 견적 문의 내용으로 자동 정리됩니다.', 'order-guide');
  }

  function enhanceInquiry() {
    setButton('inquiryNextButton', '다음 단계', {
      arrow: true,
      label: '다음 문의 작성 단계로 이동'
    });
    setButton('inquirySubmit', '협업문의 보내기', {
      arrow: true,
      attention: true,
      label: '작성한 사업협업 문의 전송'
    });
    setButton('inquiryMailFallback', '이메일로 바로 보내기', {
      label: '기본 이메일 앱으로 문의 내용 보내기'
    });

    const form = document.getElementById('businessInquiryForm');
    if (form) addHelper(form, '필수 정보를 입력하면 feed@cellpinda.com으로 전달되며, 문의번호와 접수 결과를 확인할 수 있습니다.', 'inquiry-form');
  }

  function enhanceCalculator() {
    const download = document.getElementById('downloadCalcCsv');
    if (download && download.dataset.ctaEnhanced !== 'true') {
      download.textContent = '계산 결과 저장';
      download.classList.add('cta-arrow');
      download.dataset.ctaEnhanced = 'true';
      download.setAttribute('aria-label', '현재 계산 결과를 CSV 파일로 저장');
    }
  }

  function createMobileActionBar() {
    if (document.getElementById('mobileActionBar')) return;

    const bar = document.createElement('div');
    bar.id = 'mobileActionBar';
    bar.className = 'mobile-action-bar';
    bar.setAttribute('role', 'navigation');
    bar.setAttribute('aria-label', '빠른 행동 메뉴');
    bar.innerHTML = `
      <button type="button" class="mobile-action-primary">2분 도입진단 →</button>
      <button type="button" class="mobile-action-secondary">협업문의</button>`;

    const [diagnosisButton, inquiryButton] = bar.querySelectorAll('button');
    diagnosisButton.addEventListener('click', () => scrollToSection('visitor-decision'));
    inquiryButton.addEventListener('click', () => scrollToSection('contact'));

    document.body.append(bar);
    document.body.classList.add('has-mobile-action-bar');

    const contact = document.getElementById('contact') || document.querySelector('.inquiry-section');
    if ('IntersectionObserver' in window && contact) {
      const observer = new IntersectionObserver((entries) => {
        const visible = entries.some((entry) => entry.isIntersecting && entry.intersectionRatio > 0.12);
        bar.classList.toggle('is-hidden', visible);
      }, { threshold: [0, .12, .4] });
      observer.observe(contact);
    }
  }

  function scrollToSection(id) {
    const target = document.getElementById(id);
    if (!target) return;
    target.scrollIntoView({
      behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
      block: 'start'
    });
    const nav = document.getElementById('nav');
    const menu = document.getElementById('menuBtn');
    nav?.classList.remove('open');
    if (menu) menu.textContent = '☰';
  }

  function enhanceAll() {
    scheduled = false;
    enhanceHero();
    enhanceVisitorGuide();
    enhanceOrderGuide();
    enhanceInquiry();
    enhanceCalculator();
    createMobileActionBar();
  }

  function scheduleEnhance() {
    if (scheduled) return;
    scheduled = true;
    window.requestAnimationFrame(enhanceAll);
  }

  function init() {
    enhanceAll();
    const observer = new MutationObserver(scheduleEnhance);
    observer.observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
