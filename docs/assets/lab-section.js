(() => {
  'use strict';

  const STEPS = {
    strain: {
      index: '01',
      en: 'STRAIN',
      ko: '균주 보존',
      title: '연구의 출발점을 안정적으로 보존합니다.',
      body: '초저온 보존 시스템을 기반으로 연구용 균주를 관리하고, 후속 배양을 위한 Seed Culture 조건을 준비합니다.',
      equipment: ['Ultra-Low Temperature Freezer · DF8502 / 40 L', 'Seed Culture', 'Electronic Balance · EPG2102G']
    },
    culture: {
      index: '02',
      en: 'CULTURE',
      ko: '무균 배양',
      title: '접종부터 배양까지 오염 가능성을 낮춥니다.',
      body: 'Clean Bench 무균조작, 100 L Autoclave 멸균, 저온배양 시스템을 연결해 미생물 배양의 기초조건을 관리합니다.',
      equipment: ['Clean Bench · BC-11B', 'Autoclave · ST-105G / 100 L', 'Low Temperature Incubator · NIR-153 / 150 L']
    },
    fermentation: {
      index: '03',
      en: 'FERMENTATION',
      ko: '정밀 발효',
      title: '배지·시간·온도·기질공급 조건을 수치로 설계합니다.',
      body: '2CH 실험용 발효기와 정량 Feed Pump를 활용해 5 L 발효, 배양시간, 배지조성 및 Fed-batch 기질공급 조건을 연구합니다.',
      equipment: ['Laboratory Fermentor · 2CH', 'Digital Peristaltic Pump · EMP-100A ×2', 'EMH-1000 Head ×2 · Fed-batch']
    },
    separation: {
      index: '04',
      en: 'SEPARATION',
      ko: '분리·회수',
      title: '배양 결과를 분석 가능한 연구시료로 전환합니다.',
      body: '고속냉장원심분리, 교반, 냉각과 진공건조를 이용해 배양 후 균체 분리, 시료 회수 및 건조조건을 검토합니다.',
      equipment: ['Velospin 17R · 6×500 mL Rotor', 'Water Cooling Chiller · RW-0525G', 'Vacuum Dryer · KVO-24B / 24 L']
    },
    analysis: {
      index: '05',
      en: 'ANALYSIS',
      ko: '정량 분석',
      title: '발효 결과를 감각이 아닌 정량 데이터로 판단합니다.',
      body: 'Shimadzu HPLC의 UV/Vis 및 RI 검출 시스템과 아미노산 분석기를 활용해 GABA, 아미노산 및 발효 관련 성분을 분석합니다.',
      equipment: ['Shimadzu 20 Series HPLC Full System', 'UV/Vis · SPD-20A', 'RI Detector · RID-40A', 'Amino Acid Analyzer']
    },
    standardization: {
      index: '06',
      en: 'STANDARDIZATION',
      ko: '표준화',
      title: '분석 데이터를 공정 재현성과 원료 규격으로 연결합니다.',
      body: '공정 전후의 정량 결과를 비교하고 회수·건조 조건을 함께 검토해 연구시료와 원료의 표준화 방향을 설정합니다.',
      equipment: ['HPLC·아미노산 Profile', '공정 전후 비교', '연구시료 회수·건조', '원료 규격화 검토']
    }
  };

  const CAPABILITIES = [
    {
      no: '01',
      en: 'Precision Fermentation',
      ko: '정밀발효',
      body: '2CH 실험용 발효기와 정량 Feed Pump를 활용해 배양조건, 발효시간, 배지조성 및 Fed-batch 기질공급 조건을 연구합니다.',
      tag: 'FERMENTATION DESIGN'
    },
    {
      no: '02',
      en: 'Microbial Research',
      ko: '미생물 연구',
      body: '초저온 균주 보존, Clean Bench 무균조작, 100 L Autoclave 멸균 및 저온배양 시스템을 기반으로 미생물 연구를 수행합니다.',
      tag: 'ASEPTIC CULTURE'
    },
    {
      no: '03',
      en: 'Downstream Process',
      ko: '분리·회수 공정',
      body: '고속냉장원심분리, 교반, 냉각 및 진공건조를 통해 배양 후 균체 분리와 연구시료 회수·건조 조건을 검토합니다.',
      tag: 'SEPARATION & RECOVERY'
    },
    {
      no: '04',
      en: 'Analytical Validation',
      ko: '분석 검증',
      body: 'Shimadzu HPLC의 UV/Vis·RI 검출 시스템과 아미노산 분석기를 활용해 GABA, 아미노산 및 발효 관련 성분을 분석합니다.',
      tag: 'QUANTITATIVE ANALYSIS'
    }
  ];

  const EQUIPMENT = [
    ['HPLC', 'Shimadzu 20 Series', 'GABA·발효성분 정량'],
    ['RI', 'Shimadzu RID-40A', '당류 등 RI 성분 분석'],
    ['FERMENTOR', '2CH Laboratory Fermentor', '배양·발효조건 최적화'],
    ['FEED PUMP', 'EMP-100A ×2', 'Fed-batch 정량공급'],
    ['CENTRIFUGE', 'Velospin 17R', '6×500 mL 균체 분리'],
    ['AUTOCLAVE', 'ST-105G / 100 L', '배지·용기 고압멸균'],
    ['VACUUM DRYER', 'KVO-24B / 24 L', '연구시료 진공건조'],
    ['PURE WATER', 'Direct-Q 5 UV', 'HPLC·시약조제']
  ];

  function init() {
    if (document.getElementById('lab')) return;
    const story = document.getElementById('story') || document.querySelector('.story-section');
    if (!story) return;

    const section = document.createElement('section');
    section.id = 'lab';
    section.className = 'lab-section';
    section.innerHTML = buildSection();
    story.insertAdjacentElement('afterend', section);

    addNavigation(section);
    bindInteractions(section);
    activateStep(section, 'fermentation');
  }

  function buildSection() {
    return `
      <div class="container lab-container">
        <div class="lab-hero">
          <div class="lab-hero-copy">
            <span class="lab-eyebrow">CELLPINDA LIFE SCIENCE LAB</span>
            <h2>정밀발효를,<br><em>분석 가능한 원료로.</em></h2>
            <p>미생물 발효 기반 바이오액티브 소재의 개발·공정 최적화·성분 분석을 하나의 연구 플랫폼으로 연결합니다.</p>
            <div class="lab-proof-strip" aria-label="연구소 핵심 인프라">
              <span><b>2CH</b> Laboratory Fermentor</span>
              <span><b>5 L</b> Lab Fermentation</span>
              <span><b>UV/Vis + RI</b> HPLC Detection</span>
              <span><b>100 L</b> Autoclave</span>
            </div>
            <div class="lab-actions">
              <a class="lab-primary" href="materials/cellpinda-life-science-lab.html">연구역량·장비 전체보기 <b>→</b></a>
              <button type="button" class="lab-secondary" id="labInquiry">공동연구·시험 문의</button>
            </div>
          </div>
          <div class="lab-data-visual" aria-label="발효와 분석 데이터 시각화">
            <div class="lab-data-grid" aria-hidden="true"></div>
            <div class="lab-signal lab-signal-a"><i></i><i></i><i></i><i></i><i></i></div>
            <div class="lab-signal lab-signal-b"><i></i><i></i><i></i><i></i><i></i></div>
            <div class="lab-core">
              <span>FERMENTATION</span>
              <strong>DATA</strong>
              <small>→ ANALYTICAL VALIDATION</small>
            </div>
            <div class="lab-orbit orbit-one"></div>
            <div class="lab-orbit orbit-two"></div>
            <div class="lab-orbit-dot dot-one"></div>
            <div class="lab-orbit-dot dot-two"></div>
          </div>
        </div>

        <div class="lab-process-shell">
          <div class="lab-process-heading">
            <div>
              <span>R&D WORKFLOW</span>
              <h3>한 번의 배양이 아니라, 재현 가능한 공정을 설계합니다.</h3>
            </div>
            <p>단계를 눌러 연구 목적과 핵심 장비를 확인하세요.</p>
          </div>
          <div class="lab-process-layout">
            <div class="lab-process-nav" role="tablist" aria-label="연구개발 단계">
              ${Object.entries(STEPS).map(([key, step]) => `
                <button type="button" role="tab" data-lab-step="${key}" aria-selected="false">
                  <i>${step.index}</i>
                  <span><b>${step.en}</b><small>${step.ko}</small></span>
                </button>`).join('')}
            </div>
            <article class="lab-step-detail" id="labStepDetail" aria-live="polite"></article>
          </div>
        </div>

        <div class="lab-capability-heading">
          <span>CORE CAPABILITIES</span>
          <h3>연구소의 네 가지 핵심 역량</h3>
        </div>
        <div class="lab-capability-grid">
          ${CAPABILITIES.map((item) => `
            <article class="lab-capability-card">
              <div class="lab-capability-top"><i>${item.no}</i><span>${item.tag}</span></div>
              <small>${item.en}</small>
              <h4>${item.ko}</h4>
              <p>${item.body}</p>
            </article>`).join('')}
        </div>

        <div class="lab-equipment-wall">
          <div class="lab-equipment-intro">
            <span>RESEARCH & ANALYTICAL EQUIPMENT</span>
            <h3>발효·분리·분석을 연결하는 주요 장비</h3>
            <p>장비 보유 자체보다, 공정 전후 데이터를 하나의 연구 흐름으로 연결하는 데 초점을 둡니다.</p>
          </div>
          <div class="lab-equipment-grid">
            ${EQUIPMENT.map(([type, model, use]) => `
              <div class="lab-equipment-item">
                <span>${type}</span>
                <strong>${model}</strong>
                <small>${use}</small>
              </div>`).join('')}
          </div>
        </div>

        <blockquote class="lab-principle">
          <span>FROM FERMENTATION TO ANALYTICAL VALIDATION</span>
          <p>“발효 결과를 감각적으로 판단하지 않고, 분리·정량분석 데이터를 기반으로 공정 재현성과 원료 규격화를 검토합니다.”</p>
        </blockquote>
      </div>`;
  }

  function activateStep(section, key) {
    const step = STEPS[key] || STEPS.fermentation;
    section.querySelectorAll('[data-lab-step]').forEach((button) => {
      const active = button.dataset.labStep === key;
      button.classList.toggle('active', active);
      button.setAttribute('aria-selected', String(active));
      button.tabIndex = active ? 0 : -1;
    });

    const detail = section.querySelector('#labStepDetail');
    detail.innerHTML = `
      <div class="lab-step-index"><span>${step.index}</span><small>${step.en}</small></div>
      <div class="lab-step-copy">
        <span>${step.ko}</span>
        <h4>${step.title}</h4>
        <p>${step.body}</p>
        <div class="lab-step-equipment">
          ${step.equipment.map((item) => `<i>${item}</i>`).join('')}
        </div>
      </div>`;
  }

  function bindInteractions(section) {
    section.querySelectorAll('[data-lab-step]').forEach((button) => {
      button.addEventListener('click', () => activateStep(section, button.dataset.labStep));
      button.addEventListener('keydown', (event) => {
        if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(event.key)) return;
        event.preventDefault();
        const buttons = [...section.querySelectorAll('[data-lab-step]')];
        const current = buttons.indexOf(button);
        const delta = ['ArrowRight', 'ArrowDown'].includes(event.key) ? 1 : -1;
        const next = buttons[(current + delta + buttons.length) % buttons.length];
        next.focus();
        next.click();
      });
    });

    section.querySelector('#labInquiry')?.addEventListener('click', () => {
      const target = document.getElementById('contact') || document.querySelector('.inquiry-section');
      if (target) {
        target.scrollIntoView({
          behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
          block: 'start'
        });
        return;
      }
      window.location.href = 'mailto:feed@cellpinda.com?subject=' + encodeURIComponent('[Cellpinda Lab] 공동연구·시험 문의');
    });
  }

  function addNavigation(section) {
    const nav = document.getElementById('nav');
    if (!nav || nav.querySelector('[data-lab-nav]')) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = '연구소';
    button.dataset.labNav = 'true';
    const model = nav.querySelector('[data-scroll="model"]');
    if (model) model.before(button);
    else nav.append(button);
    button.addEventListener('click', () => {
      section.scrollIntoView({
        behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
        block: 'start'
      });
      nav.classList.remove('open');
      const menu = document.getElementById('menuBtn');
      if (menu) menu.textContent = '☰';
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
