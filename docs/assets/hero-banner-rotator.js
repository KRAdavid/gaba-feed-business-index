(() => {
  'use strict';

  const SLIDES = [
    {
      kicker: 'FERMENTED GABA 20',
      title: '<span class="hero-banner-phrase">유산균 발효 <span class="hero-banner-accent">GABA 20</span></span>',
      subtitle: '발효 유래 GABA를 20% 기준으로 표준화한 바이오액티브 사료 솔루션',
      caption: 'FERMENTED GABA 20'
    },
    {
      kicker: 'INTEGRATED NUTRITION',
      title: '<span class="hero-banner-phrase">스트레스 대응부터</span><br><span class="hero-banner-phrase hero-banner-accent">사료효율·장 건강 관리까지</span>',
      subtitle: '축종별 파일럿과 데이터로 검증하는 통합 영양 솔루션',
      caption: 'INTEGRATED FEED SOLUTION'
    },
    {
      kicker: 'SUSTAINABLE FEED STRATEGY',
      title: '<span class="hero-banner-phrase">항생제 사용 저감을 지향하는</span>',
      subtitle: '동물의 컨디션과 생산성을 함께 고려하는 지속가능한 사양전략',
      caption: 'SUSTAINABLE FEED STRATEGY'
    }
  ];

  const ROTATION_MS = 3000;
  const TRANSITION_MS = 210;

  function init() {
    const hero = document.querySelector('.hero');
    const heroCopy = hero?.querySelector('.hero-copy');
    if (!hero || !heroCopy || heroCopy.querySelector('.hero-banner-rotator')) return;

    const title = heroCopy.querySelector('h1');
    const description = title?.nextElementSibling?.matches('p') ? title.nextElementSibling : heroCopy.querySelector('p');
    const actions = heroCopy.querySelector('.hero-actions');
    if (!title || !description || !actions) return;

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const pauseReasons = new Set();
    let currentIndex = 0;
    let timer = null;
    let deadline = 0;
    let remaining = ROTATION_MS;
    let transitionToken = 0;
    let pointerStartX = null;

    const originalDescription = description.textContent.trim();
    const context = document.createElement('p');
    context.className = 'hero-banner-context';
    context.textContent = originalDescription;

    const rotator = document.createElement('section');
    rotator.className = 'hero-banner-rotator';
    rotator.dataset.slide = '0';
    rotator.setAttribute('role', 'region');
    rotator.setAttribute('aria-roledescription', 'carousel');
    rotator.setAttribute('aria-label', '셀핀다 GABA Feed 핵심 메시지');
    rotator.style.setProperty('--hero-rotation-ms', `${ROTATION_MS}ms`);

    const kicker = document.createElement('span');
    kicker.className = 'hero-banner-kicker';

    const frame = document.createElement('div');
    frame.className = 'hero-banner-frame';

    title.className = 'hero-banner-title';
    description.className = 'hero-banner-subtitle';
    frame.append(title, description);

    const controls = document.createElement('div');
    controls.className = 'hero-banner-controls';
    controls.setAttribute('role', 'tablist');
    controls.setAttribute('aria-label', '메인 메시지 선택');

    const progress = document.createElement('div');
    progress.className = 'hero-banner-progress';
    progress.setAttribute('aria-hidden', 'true');
    progress.innerHTML = '<i></i>';

    const status = document.createElement('span');
    status.className = 'hero-banner-status';
    status.setAttribute('aria-live', 'polite');
    status.setAttribute('aria-atomic', 'true');

    SLIDES.forEach((slide, index) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.dataset.heroBannerIndex = String(index);
      button.setAttribute('role', 'tab');
      button.setAttribute('aria-label', `${index + 1}번 메시지: ${stripHtml(slide.title)}`);
      button.innerHTML = `<strong>${String(index + 1).padStart(2, '0')}</strong><span></span>`;
      button.addEventListener('click', () => {
        render(index, true);
        restartAutoRotation();
      });
      button.addEventListener('keydown', (event) => {
        let targetIndex = null;
        if (event.key === 'ArrowRight') targetIndex = (index + 1) % SLIDES.length;
        if (event.key === 'ArrowLeft') targetIndex = (index - 1 + SLIDES.length) % SLIDES.length;
        if (event.key === 'Home') targetIndex = 0;
        if (event.key === 'End') targetIndex = SLIDES.length - 1;
        if (targetIndex === null) return;
        event.preventDefault();
        controls.querySelector(`[data-hero-banner-index="${targetIndex}"]`)?.focus();
        render(targetIndex, true);
        restartAutoRotation();
      });
      controls.append(button);
    });

    rotator.append(kicker, frame, controls, progress, status);
    heroCopy.insertBefore(rotator, actions);
    heroCopy.insertBefore(context, actions);
    hero.classList.add('has-rotating-banner');

    const caption = hero.querySelector('.hero-caption');

    function render(index, announce = false, immediate = false) {
      const normalized = (index + SLIDES.length) % SLIDES.length;
      const slide = SLIDES[normalized];
      const token = ++transitionToken;
      currentIndex = normalized;

      const applyContent = () => {
        if (token !== transitionToken) return;
        rotator.dataset.slide = String(normalized);
        kicker.textContent = slide.kicker;
        title.innerHTML = slide.title;
        description.textContent = slide.subtitle;
        if (caption) caption.textContent = slide.caption;

        controls.querySelectorAll('[data-hero-banner-index]').forEach((button, buttonIndex) => {
          const active = buttonIndex === normalized;
          button.classList.toggle('active', active);
          button.setAttribute('aria-selected', String(active));
          button.setAttribute('tabindex', active ? '0' : '-1');
        });

        if (announce) status.textContent = `${normalized + 1}번 메시지. ${stripHtml(slide.title)}. ${slide.subtitle}`;
        rotator.classList.remove('is-changing');
        window.requestAnimationFrame(() => rotator.classList.add('is-entered'));
        restartProgress();
      };

      rotator.classList.remove('is-entered');
      if (immediate || reducedMotion.matches) {
        applyContent();
        return;
      }

      rotator.classList.add('is-changing');
      window.setTimeout(applyContent, TRANSITION_MS);
    }

    function stripHtml(value) {
      const temporary = document.createElement('div');
      temporary.innerHTML = value;
      return temporary.textContent.trim();
    }

    function restartProgress() {
      rotator.classList.remove('is-progressing');
      void rotator.offsetWidth;
      rotator.classList.add('is-progressing');
      rotator.classList.toggle('is-paused', pauseReasons.size > 0);
    }

    function clearTimer() {
      if (timer !== null) {
        window.clearTimeout(timer);
        timer = null;
      }
    }

    function schedule(delay = ROTATION_MS) {
      clearTimer();
      remaining = Math.max(120, delay);
      if (reducedMotion.matches || pauseReasons.size > 0) return;
      deadline = Date.now() + remaining;
      timer = window.setTimeout(() => {
        render(currentIndex + 1);
        schedule(ROTATION_MS);
      }, remaining);
    }

    function restartAutoRotation() {
      remaining = ROTATION_MS;
      restartProgress();
      schedule(ROTATION_MS);
    }

    function setPaused(reason, paused) {
      const wasPaused = pauseReasons.size > 0;
      if (paused) pauseReasons.add(reason);
      else pauseReasons.delete(reason);
      const isPaused = pauseReasons.size > 0;

      if (!wasPaused && isPaused) {
        remaining = timer === null ? remaining : Math.max(120, deadline - Date.now());
        clearTimer();
      } else if (wasPaused && !isPaused) {
        schedule(remaining || ROTATION_MS);
      }
      rotator.classList.toggle('is-paused', isPaused);
    }

    rotator.addEventListener('mouseenter', () => setPaused('hover', true));
    rotator.addEventListener('mouseleave', () => setPaused('hover', false));
    rotator.addEventListener('focusin', () => setPaused('focus', true));
    rotator.addEventListener('focusout', () => {
      window.setTimeout(() => setPaused('focus', rotator.contains(document.activeElement)), 0);
    });

    rotator.addEventListener('pointerdown', (event) => {
      pointerStartX = event.pointerType === 'mouse' ? null : event.clientX;
    });
    rotator.addEventListener('pointerup', (event) => {
      if (pointerStartX === null) return;
      const delta = event.clientX - pointerStartX;
      pointerStartX = null;
      if (Math.abs(delta) < 48) return;
      render(currentIndex + (delta < 0 ? 1 : -1), true);
      restartAutoRotation();
    });

    document.addEventListener('visibilitychange', () => setPaused('visibility', document.hidden));
    reducedMotion.addEventListener?.('change', () => {
      setPaused('reduced-motion', reducedMotion.matches);
      if (!reducedMotion.matches) restartAutoRotation();
    });

    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver((entries) => {
        const visible = entries.some((entry) => entry.isIntersecting && entry.intersectionRatio > 0.2);
        setPaused('offscreen', !visible);
      }, { threshold: [0, 0.2, 0.55] });
      observer.observe(hero);
    }

    if (reducedMotion.matches) pauseReasons.add('reduced-motion');
    render(0, false, true);
    schedule(ROTATION_MS);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();