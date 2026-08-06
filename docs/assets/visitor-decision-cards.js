(() => {
  'use strict';

  const QUESTIONS = [
    {
      id: 'role',
      eyebrow: '방문자 유형',
      title: '어떤 입장에서 GABA 사료 원료를 검토하고 계신가요?',
      help: '같은 제품이라도 연구개발, 구매, 농장, 수입·유통 담당자가 먼저 확인해야 할 정보가 다릅니다.',
      options: [
        { value: 'rd', label: '사료회사 R&D·제품기획', detail: '배합 적합성, 시험설계, 제품 차별화가 중요합니다.', icon: 'R' },
        { value: 'purchase', label: '구매·원료조달·유통', detail: '규격, CoA, MOQ, 단가, 공급안정성이 중요합니다.', icon: 'P' },
        { value: 'farm', label: '농장·비육장 운영', detail: '현장 적용법, 측정지표, 비용효과가 중요합니다.', icon: 'F' },
        { value: 'importer', label: '해외 수입·유통 파트너', detail: '국가별 분류, 표시, 문서와 공급조건이 중요합니다.', icon: 'I' },
        { value: 'research', label: '연구기관·시험 파트너', detail: '대조군, 급여수준, 기간, 데이터 품질이 중요합니다.', icon: 'S' }
      ]
    },
    {
      id: 'goal',
      eyebrow: '해결 과제',
      title: '가장 먼저 해결하고 싶은 과제는 무엇인가요?',
      help: '한 가지를 우선 선택하면 추천 제품과 파일럿 KPI를 더 명확하게 제안할 수 있습니다.',
      options: [
        { value: 'heat', label: '고온·환경 스트레스', detail: '여름철 섭취 저하, 행동·생리지표 변화를 확인합니다.', icon: 'H' },
        { value: 'intake', label: '사료섭취·컨디션 유지', detail: '섭취량, 체중변화, 회복상태를 중심으로 봅니다.', icon: 'D' },
        { value: 'performance', label: '성장·사료효율', detail: 'ADG·FCR은 고정효과가 아니라 대조시험으로 확인합니다.', icon: 'G' },
        { value: 'quality', label: '육질·항산화·등급 안정', detail: '육색, TBARS, 보수력, 등급 같은 최종 생산물 지표를 봅니다.', icon: 'Q' },
        { value: 'reproduction', label: '번식기 컨디션 관리', detail: '직접 번식효능을 단정하지 않고 스트레스·섭취·정액지표를 함께 봅니다.', icon: 'B' },
        { value: 'brand', label: '신제품·브랜드 차별화', detail: '가바크루드 또는 가바케어믹스 공동개발 경로가 적합합니다.', icon: 'N' }
      ]
    },
    {
      id: 'species',
      eyebrow: '적용 대상',
      title: '주요 적용 축종을 선택해 주세요.',
      help: '축종과 생산단계에 따라 사료섭취량, 적용기간, 우선 KPI가 달라집니다.',
      options: [
        { value: 'pig', label: '비육돈·육성돈', detail: '성장, 소화율, 행동·스트레스 지표', icon: 'P' },
        { value: 'breederPig', label: '씨돼지·번식돈', detail: '고온기 4~8주 파일럿과 번식 관련 지표', icon: 'B' },
        { value: 'poultry', label: '육계·산란계·종계', detail: '열 스트레스, 증체, FCR, 폐사·산화지표', icon: 'C' },
        { value: 'beef', label: '한우·육우·와규', detail: '장기비육, DMI, 성장, 육질·항산화', icon: 'W' },
        { value: 'dairyCalf', label: '젖소·송아지', detail: '열 스트레스, 섭취, 유생산·성장·건강지표', icon: 'D' },
        { value: 'other', label: '기타·복수 축종', detail: '축종별 근거와 사료섭취량을 별도로 검토합니다.', icon: 'M' }
      ]
    },
    {
      id: 'use',
      eyebrow: '도입 방식',
      title: '어떤 방식으로 적용하려고 하나요?',
      help: '가바크루드는 원료형 제품이며, 자체 배합 역량과 원하는 제품 형태에 따라 도입 경로가 달라집니다.',
      options: [
        { value: 'standard', label: 'GABA 20% 기준품을 자체 배합', detail: '표준 규격 원료를 구매해 프리믹스·배합사료에 적용합니다.', icon: '20' },
        { value: 'custom', label: '5~20% 맞춤 프리믹스 필요', detail: 'GABA 농도, 담체, 포장과 제조공정을 협의합니다.', icon: '%' },
        { value: 'caremix', label: '축종별 브랜드 제품 공동개발', detail: 'GABA와 기능 매트릭스를 조합한 OEM·ODM 경로입니다.', icon: 'C' },
        { value: 'pilot', label: '제품보다 농장시험부터', detail: '대조군과 KPI를 정한 뒤 샘플·파일럿부터 시작합니다.', icon: 'T' },
        { value: 'unknown', label: '아직 잘 모르겠습니다', detail: '규격·적용량·문서를 먼저 비교하는 것이 적합합니다.', icon: '?' }
      ]
    },
    {
      id: 'stage',
      eyebrow: '현재 준비도',
      title: '현재 어느 단계까지 준비되어 있나요?',
      help: '정답은 없습니다. 현재 단계에 맞는 다음 행동을 제안하기 위한 질문입니다.',
      options: [
        { value: 'learn', label: '처음 검토 중', detail: '제품 구조와 근거, 적용범위를 먼저 이해해야 합니다.', icon: '1' },
        { value: 'spec', label: '규격서·CoA·샘플 검토 가능', detail: '제품 적합성 확인 후 파일럿 또는 견적으로 이동할 수 있습니다.', icon: '2' },
        { value: 'pilot', label: '대조시험·파일럿 실행 가능', detail: '축종·기간·KPI·급여수준을 문서화할 수 있습니다.', icon: '3' },
        { value: 'commercial', label: '상업 물량·발주 협의 가능', detail: 'MOQ, 단가, 납기, 계약과 로트 품질을 확인합니다.', icon: '4' }
      ]
    },
    {
      id: 'criterion',
      eyebrow: '최종 결정 기준',
      title: '도입 결정을 위해 가장 부족한 정보는 무엇인가요?',
      help: '결과 화면에서 가장 먼저 확인할 자료와 질문을 제시합니다.',
      options: [
        { value: 'evidence', label: '논문·축종별 근거', detail: '직접근거와 타 축종 보조근거를 구분해야 합니다.', icon: 'E' },
        { value: 'quality', label: '규격·CoA·품질관리', detail: '함량, 수분, 미생물, 중금속, 보관조건을 확인합니다.', icon: 'Q' },
        { value: 'economics', label: '단가·MOQ·경제성', detail: '선택한 성장·FCR 가정과 실제 사료량으로 비교합니다.', icon: '$' },
        { value: 'regulatory', label: '국가별 규제·표시', detail: '사료원료·첨가제 분류와 효능 표현을 먼저 검토합니다.', icon: 'R' },
        { value: 'supply', label: 'CAPA·납기·공급안정성', detail: '초도·연간 물량과 생산 리드타임을 확인합니다.', icon: 'S' }
      ]
    }
  ];

  const ROLE_COPY = {
    rd: '사료회사 R&D 관점에서는 원료 자체보다 배합 적합성, 시험설계와 반복 가능한 제품 규격이 핵심입니다.',
    purchase: '구매·조달 관점에서는 로트별 품질자료, MOQ, 단가, 납기와 공급안정성을 먼저 잠가야 합니다.',
    farm: '농장 관점에서는 제품 설명보다 적용기간, 기록 가능한 KPI와 도입비 대비 현장 변화가 중요합니다.',
    importer: '수입·유통 관점에서는 국가별 분류와 표시, 영문 기술문서, 공급조건을 먼저 확인해야 합니다.',
    research: '연구기관 관점에서는 대조군, 급여수준, 통계계획과 데이터 사용범위를 명확히 해야 합니다.'
  };

  const GOAL_KPIS = {
    heat: ['사료섭취량', '체온·호흡수', 'cortisol 또는 스트레스 지표', '폐사·생산성'],
    intake: ['일일 사료섭취량', '체중변화', '행동·컨디션', '회복기간'],
    performance: ['ADG', 'FCR', '출하일', '건물소화율'],
    quality: ['육색', 'TBARS', '보수력·가열감량', '등급·감가율'],
    reproduction: ['사료섭취량', '체중변화', 'cortisol', '정액량·운동성·이상정자율'],
    brand: ['샘플 적합성', '제품 규격', '고객 수용성', '재주문 의향']
  };

  const SPECIES_LABELS = {
    pig: '비육돈·육성돈', breederPig: '씨돼지·번식돈', poultry: '육계·산란계·종계',
    beef: '한우·육우·와규', dairyCalf: '젖소·송아지', other: '기타·복수 축종'
  };

  const GOAL_LABELS = {
    heat: '고온·환경 스트레스', intake: '사료섭취·컨디션 유지', performance: '성장·사료효율',
    quality: '육질·항산화·등급 안정', reproduction: '번식기 컨디션 관리', brand: '신제품·브랜드 차별화'
  };

  const STAGE_LABELS = {
    learn: '처음 검토 중', spec: '규격·샘플 검토 단계', pilot: '파일럿 실행 단계', commercial: '상업 발주 협의 단계'
  };

  const ROUTES = {
    crude20: {
      product: '가바크루드 20% 기준품', badge: '표준 원료 경로',
      headline: '표준 규격과 공급조건을 확인한 뒤 빠르게 샘플·견적으로 이동할 수 있습니다.',
      orderProduct: 'crude20', collaboration: ['원료'],
      checks: ['목표 사료농도와 총 사료량', '로트별 CoA·포장·보관조건', 'MOQ·단가·납기']
    },
    customCrude: {
      product: '주문형 가바크루드 5~20%', badge: '맞춤 프리믹스 경로',
      headline: '자체 공정과 목표농도에 맞춰 담체·농도·포장 규격을 먼저 정의하는 것이 적합합니다.',
      orderProduct: 'customCrude', collaboration: ['원료', 'OEM'],
      checks: ['희망 GABA 농도와 담체', '혼합·펠릿·열공정 조건', '초도·연간 예상물량']
    },
    caremix: {
      product: 'GABA Care Mix OEM·ODM', badge: '공동개발 경로',
      headline: '원료 구매보다 축종별 콘셉트·KPI·브랜드 제품을 함께 설계하는 경로가 적합합니다.',
      orderProduct: 'caremix', collaboration: ['OEM', '공동개발'],
      checks: ['브랜드 콘셉트와 대상 축종', '기능 매트릭스와 제조공정', '파일럿·출시 일정']
    },
    pilot: {
      product: '농장 파일럿·공동실증', badge: '현장 검증 경로',
      headline: '효과를 고정하지 말고 대조군과 KPI를 정한 소규모 파일럿으로 도입 여부를 판단하는 것이 적합합니다.',
      orderProduct: 'pilot', collaboration: ['파일럿'],
      checks: ['대조군과 기초 성적', '급여수준·기간·중단기준', '측정 가능한 KPI와 경제성']
    },
    review: {
      product: '기술·규제자료 우선 검토', badge: '검토 후 결정',
      headline: '지금 바로 물량을 결정하기보다 제품 규격, 근거와 국가별 분류를 먼저 확인하는 것이 안전합니다.',
      orderProduct: 'crude20', collaboration: ['원료'],
      checks: ['제품 규격서·대표 CoA', '축종별 근거와 한계', '판매국 규제·표시·수입요건']
    }
  };

  let answers = {};
  let stepIndex = -1;
  let lastResult = null;

  function init() {
    if (document.getElementById('visitor-decision')) return;
    const productSection = document.getElementById('products') || document.querySelector('.product-section');
    if (!productSection) return;

    const section = document.createElement('section');
    section.id = 'visitor-decision';
    section.className = 'visitor-decision-section';
    section.innerHTML = buildShell();

    const orderGuide = document.getElementById('order-guide');
    if (orderGuide) orderGuide.insertAdjacentElement('beforebegin', section);
    else productSection.insertAdjacentElement('afterend', section);

    addNavShortcut(section);
    bind(section);
    renderIntro(section);
  }

  function addNavShortcut(section) {
    const nav = document.getElementById('nav');
    if (!nav || nav.querySelector('[data-visitor-decision-nav]')) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = '빠른 도입진단';
    button.dataset.visitorDecisionNav = 'true';
    const calculatorButton = nav.querySelector('[data-scroll="calculator"]');
    if (calculatorButton) calculatorButton.before(button);
    else nav.append(button);
    button.addEventListener('click', () => {
      section.scrollIntoView({ behavior: 'smooth', block: 'start' });
      nav.classList.remove('open');
      const menuButton = document.getElementById('menuBtn');
      if (menuButton) menuButton.textContent = '☰';
    });
  }

  function buildShell() {
    return `
      <div class="container visitor-decision-container">
        <div class="visitor-decision-heading">
          <span>2-MINUTE DECISION GUIDE</span>
          <h2>6개의 선택으로<br>가바크루드 도입 경로를 찾습니다.</h2>
          <p>방문자의 역할, 목표, 축종과 준비단계를 묻고 <b>자료검토·샘플·파일럿·상업협의</b> 중 가장 적합한 다음 행동을 안내합니다.</p>
        </div>
        <div class="visitor-decision-shell">
          <div class="visitor-decision-main">
            <div class="visitor-progress" aria-label="진행률">
              <div><i id="visitorProgressBar"></i></div>
              <span id="visitorProgressText">시작 전</span>
            </div>
            <div id="visitorDecisionContent" aria-live="polite"></div>
          </div>
          <aside class="visitor-decision-aside">
            <span>GABA CRUDE IN 30 SECONDS</span>
            <h3>가바크루드는 무엇인가요?</h3>
            <dl>
              <div><dt>제품</dt><dd>GABA 20% 기준의 발효 유래 사료용 원료</dd></div>
              <div><dt>적용</dt><dd>표준 원료, 5~20% 맞춤 프리믹스, Care Mix, 파일럿</dd></div>
              <div><dt>확인근거</dt><dd>돼지의 스트레스·호르몬 및 일부 성장·소화율, 타 축종의 열 스트레스·항산화 연구</dd></div>
              <div><dt>주의</dt><dd>ADG·FCR·번식효과를 모든 농장에 고정해 적용하지 않음</dd></div>
            </dl>
            <p>이 세션은 구매를 자동 승인하지 않습니다. 현재 조건에서 가장 빠르게 검증할 경로를 제안합니다.</p>
          </aside>
        </div>
      </div>`;
  }

  function bind(section) {
    section.addEventListener('click', (event) => {
      const option = event.target.closest('[data-visitor-option]');
      if (option) {
        const question = QUESTIONS[stepIndex];
        answers[question.id] = option.dataset.visitorOption;
        renderQuestion(section, stepIndex + 1);
        return;
      }
      if (event.target.closest('#visitorStart')) {
        answers = {};
        renderQuestion(section, 0);
      } else if (event.target.closest('#visitorBack')) {
        renderQuestion(section, Math.max(0, stepIndex - 1));
      } else if (event.target.closest('#visitorRestart')) {
        answers = {};
        renderIntro(section);
      } else if (event.target.closest('#visitorApplyOrder')) {
        applyToOrderGuide(section);
      } else if (event.target.closest('#visitorStartInquiry')) {
        applyToInquiry(section);
      } else if (event.target.closest('#visitorCopyResult')) {
        copyResult(section);
      }
    });
  }

  function renderIntro(section) {
    stepIndex = -1;
    updateProgress(section, 0, '시작 전');
    section.querySelector('#visitorDecisionContent').innerHTML = `
      <article class="visitor-intro-card">
        <span class="visitor-card-eyebrow">방문자 맞춤 안내</span>
        <h3>긴 설명보다, 지금 필요한 질문부터 시작합니다.</h3>
        <p>약 2분 안에 방문자에게 맞는 제품 형태, 검증 단계, 확인자료와 다음 행동을 한 화면으로 정리합니다.</p>
        <div class="visitor-intro-points">
          <div><b>01</b><span>내 역할과 목표 정리</span></div>
          <div><b>02</b><span>제품·파일럿 경로 추천</span></div>
          <div><b>03</b><span>주문·문의 내용 자동 연결</span></div>
        </div>
        <button type="button" id="visitorStart" class="visitor-primary">객관식 가이드 시작 →</button>
      </article>`;
  }

  function renderQuestion(section, nextIndex) {
    if (nextIndex >= QUESTIONS.length) {
      renderResult(section);
      return;
    }
    stepIndex = nextIndex;
    const question = QUESTIONS[stepIndex];
    updateProgress(section, stepIndex + 1, `${stepIndex + 1} / ${QUESTIONS.length}`);
    section.querySelector('#visitorDecisionContent').innerHTML = `
      <article class="visitor-question-card">
        <div class="visitor-question-head">
          <span class="visitor-card-eyebrow">${escapeHtml(question.eyebrow)}</span>
          <h3>${escapeHtml(question.title)}</h3>
          <p>${escapeHtml(question.help)}</p>
        </div>
        <div class="visitor-option-grid">
          ${question.options.map((option) => `
            <button type="button" class="visitor-option" data-visitor-option="${escapeHtml(option.value)}">
              <i>${escapeHtml(option.icon)}</i>
              <span><strong>${escapeHtml(option.label)}</strong><small>${escapeHtml(option.detail)}</small></span>
              <b>선택</b>
            </button>`).join('')}
        </div>
        <div class="visitor-question-actions">
          ${stepIndex > 0 ? '<button type="button" id="visitorBack" class="visitor-text-button">← 이전 질문</button>' : '<span></span>'}
          <small>선택 즉시 다음 질문으로 이동합니다.</small>
        </div>
      </article>`;
  }

  function chooseRoute() {
    if (answers.stage === 'learn' && (answers.criterion === 'evidence' || answers.criterion === 'regulatory' || answers.use === 'unknown')) return 'review';
    if (answers.use === 'pilot' || answers.stage === 'pilot' || answers.role === 'farm' || answers.role === 'research') return 'pilot';
    if (answers.use === 'caremix' || answers.goal === 'brand') return 'caremix';
    if (answers.use === 'custom') return 'customCrude';
    if (answers.stage === 'commercial' || answers.use === 'standard' || answers.role === 'purchase') return 'crude20';
    return answers.criterion === 'regulatory' ? 'review' : 'pilot';
  }

  function chooseDecisionStage(routeKey) {
    if (routeKey === 'review') return { key: 'review', label: '자료검토 우선', text: '제품 규격·근거·규제를 확인한 후 샘플 여부를 결정하세요.' };
    if (answers.stage === 'commercial' && routeKey !== 'pilot') return { key: 'commercial', label: '상업협의 가능', text: 'MOQ·견적·납기·계약조건을 바로 확인할 수 있습니다.' };
    if (answers.stage === 'pilot' || routeKey === 'pilot') return { key: 'pilot', label: '파일럿 권장', text: '대조군과 KPI를 정한 시험으로 도입 여부를 판단하세요.' };
    return { key: 'sample', label: '샘플·규격 검토', text: '규격서·CoA·샘플을 확인한 뒤 파일럿 또는 견적으로 이동하세요.' };
  }

  function renderResult(section) {
    stepIndex = QUESTIONS.length;
    const routeKey = chooseRoute();
    const route = ROUTES[routeKey];
    const decision = chooseDecisionStage(routeKey);
    const kpis = GOAL_KPIS[answers.goal] || [];
    const roleCopy = ROLE_COPY[answers.role] || '';
    lastResult = { routeKey, route, decision, kpis, answers: { ...answers } };
    updateProgress(section, QUESTIONS.length, '결과 완료');
    section.querySelector('#visitorDecisionContent').innerHTML = `
      <article class="visitor-result-card">
        <div class="visitor-result-status ${escapeHtml(decision.key)}"><span>${escapeHtml(route.badge)}</span><strong>${escapeHtml(decision.label)}</strong></div>
        <h3>${escapeHtml(route.product)}</h3>
        <p class="visitor-result-lead">${escapeHtml(route.headline)}</p>
        <div class="visitor-result-profile">
          <div><small>방문자 관점</small><strong>${escapeHtml(roleCopy)}</strong></div>
          <div><small>대상·목표</small><strong>${escapeHtml(SPECIES_LABELS[answers.species] || '')} · ${escapeHtml(GOAL_LABELS[answers.goal] || '')}</strong></div>
          <div><small>현재 단계</small><strong>${escapeHtml(STAGE_LABELS[answers.stage] || '')}</strong></div>
        </div>
        <div class="visitor-result-columns">
          <div><h4>도입 전 먼저 확인할 것</h4><ul>${route.checks.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul></div>
          <div><h4>파일럿 권장 KPI</h4><ul>${kpis.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul></div>
        </div>
        <div class="visitor-result-caution"><strong>객관적 판단 원칙</strong><span>${escapeHtml(decision.text)} 성장·FCR·번식 결과는 농장과 시험조건에 따라 달라질 수 있으므로 고정효과로 간주하지 않습니다.</span></div>
        <div class="visitor-result-actions">
          <button type="button" id="visitorApplyOrder" class="visitor-primary">추천 경로 자세히 보기</button>
          <button type="button" id="visitorStartInquiry" class="visitor-secondary">이 결과로 상담 시작</button>
          <button type="button" id="visitorCopyResult" class="visitor-secondary">결과 복사</button>
          <button type="button" id="visitorRestart" class="visitor-text-button">처음부터 다시</button>
        </div>
        <p id="visitorResultStatus" class="visitor-live-status" role="status"></p>
      </article>`;
  }

  function updateProgress(section, value, label) {
    const pct = QUESTIONS.length ? Math.min(100, (value / QUESTIONS.length) * 100) : 0;
    const bar = section.querySelector('#visitorProgressBar');
    const text = section.querySelector('#visitorProgressText');
    if (bar) bar.style.width = `${pct}%`;
    if (text) text.textContent = label;
  }

  function applyToOrderGuide(section) {
    if (!lastResult) return;
    const guide = document.getElementById('order-guide');
    const button = guide?.querySelector(`[data-order-product="${lastResult.route.orderProduct}"]`);
    if (!button) {
      setStatus(section, '주문 가이드를 불러오는 중입니다. 잠시 후 다시 눌러 주세요.');
      return;
    }
    button.click();
    const speciesSelect = guide.querySelector('#orderSpecies');
    if (speciesSelect) setSelect(speciesSelect, speciesForOrder(lastResult.answers.species));
    const stageSelect = guide.querySelector('#orderStage');
    if (stageSelect) stageSelect.value = stageForOrder(lastResult.decision.key);
    guide.scrollIntoView({ behavior: 'smooth', block: 'start' });
    setStatus(section, '추천 제품과 단계가 주문 가이드에 적용되었습니다. 물량·국가·시기를 추가해 주세요.');
  }

  function applyToInquiry(section) {
    if (!lastResult) return;
    const form = document.getElementById('businessInquiryForm');
    const contact = document.getElementById('contact') || document.querySelector('.contact-section');
    if (!form || !contact) {
      setStatus(section, '문의 폼을 불러오는 중입니다. 잠시 후 다시 눌러 주세요.');
      return;
    }
    ensureHidden(form, '방문자_의사결정_경로', lastResult.route.badge);
    ensureHidden(form, '방문자_추천제품', lastResult.route.product);
    ensureHidden(form, '방문자_결정단계', lastResult.decision.label);
    ensureHidden(form, '방문자_최우선기준', criterionLabel(lastResult.answers.criterion));
    ensureHidden(form, '선택제품', lastResult.route.product);
    ensureHidden(form, '주문가이드_경로', lastResult.decision.label);
    setSelect(form.elements.namedItem('주요_축종'), speciesForInquiry(lastResult.answers.species));
    setSelect(form.elements.namedItem('현재_준비단계'), stageForInquiry(lastResult.decision.key));
    checkValues(form, '협업_유형', lastResult.route.collaboration);
    checkGoal(form, lastResult.answers.goal);
    checkKpis(form, lastResult.kpis);
    const message = form.elements.namedItem('상세_요청사항');
    const summary = resultText(lastResult);
    if (message && typeof message.value === 'string' && !message.value.includes('[방문자 객관식 결정 가이드]')) {
      message.value = message.value.trim() ? `${summary}\n\n${message.value.trim()}` : summary;
      message.dispatchEvent(new Event('input', { bubbles: true }));
    }
    contact.scrollIntoView({ behavior: 'smooth', block: 'start' });
    setStatus(section, '결과가 문의 폼에 반영되었습니다. 회사·담당자 정보만 추가해 전송해 주세요.');
  }

  function resultText(result) {
    return [
      '[방문자 객관식 결정 가이드]',
      `- 추천 제품·경로: ${result.route.product} / ${result.route.badge}`,
      `- 권장 결정 단계: ${result.decision.label}`,
      `- 대상 축종: ${SPECIES_LABELS[result.answers.species] || '미정'}`,
      `- 우선 과제: ${GOAL_LABELS[result.answers.goal] || '미정'}`,
      `- 현재 준비도: ${STAGE_LABELS[result.answers.stage] || '미정'}`,
      `- 최우선 확인사항: ${criterionLabel(result.answers.criterion)}`,
      `- 권장 KPI: ${result.kpis.join(', ')}`,
      '- 요청사항: 위 조건에 맞는 제품 규격, 샘플·파일럿 방식, MOQ·견적·납기와 필요한 기술자료를 안내해 주세요.'
    ].join('\n');
  }

  async function copyResult(section) {
    if (!lastResult) return;
    const text = resultText(lastResult);
    try {
      await navigator.clipboard.writeText(text);
      setStatus(section, '결과를 복사했습니다. 내부 검토 문서나 이메일에 붙여 넣을 수 있습니다.');
    } catch (_error) {
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.append(textarea);
      textarea.select();
      document.execCommand('copy');
      textarea.remove();
      setStatus(section, '결과를 복사했습니다.');
    }
  }

  function setStatus(section, text) {
    const status = section.querySelector('#visitorResultStatus');
    if (status) status.textContent = text;
  }

  function ensureHidden(form, name, value) {
    let input = form.querySelector(`input[type="hidden"][name="${name}"]`);
    if (!input) {
      input = document.createElement('input');
      input.type = 'hidden';
      input.name = name;
      form.append(input);
    }
    input.value = value;
  }

  function setSelect(field, value) {
    if (!field || !value || field.tagName !== 'SELECT') return;
    const option = [...field.options].find((item) => item.value === value || item.textContent.trim() === value);
    if (option) {
      field.value = option.value;
      field.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }

  function checkValues(form, name, values) {
    values.forEach((value) => {
      const checkbox = [...form.querySelectorAll(`input[name="${name}"]`)].find((item) => item.value === value);
      if (checkbox) checkbox.checked = true;
    });
  }

  function checkGoal(form, goal) {
    const map = { heat: '열스트레스', intake: '섭취량', performance: '생산성', quality: '육질', reproduction: '번식', brand: '브랜드' };
    checkValues(form, '현재_과제', [map[goal]].filter(Boolean));
  }

  function checkKpis(form, kpis) {
    const map = {
      '사료섭취량': 'KPI섭취', '일일 사료섭취량': 'KPI섭취', 'ADG': 'KPI성장', 'FCR': 'KPI성장',
      '출하일': 'KPI성장', 'cortisol': 'KPI스트레스', 'cortisol 또는 스트레스 지표': 'KPI스트레스',
      '정액량·운동성·이상정자율': 'KPI번식', '육색': 'KPI육질', 'TBARS': 'KPI육질',
      '보수력·가열감량': 'KPI육질', '등급·감가율': 'KPI육질', '폐사·생산성': 'KPI건강'
    };
    checkValues(form, '핵심_평가지표', [...new Set(kpis.map((item) => map[item]).filter(Boolean))]);
  }

  function stageForOrder(key) {
    return key === 'commercial' ? 'commercial' : key === 'pilot' ? 'pilot' : 'sample';
  }

  function stageForInquiry(key) {
    return { commercial: '상업 발주·유통 협의 단계', pilot: '파일럿 설계 단계', sample: '샘플·규격서 검토 단계', review: '정보 수집 단계' }[key] || '정보 수집 단계';
  }

  function speciesForOrder(key) {
    return { pig: '비육돈', breederPig: '씨돼지(종모돈·종빈돈)', poultry: '육계', beef: '한우·육우·와규', dairyCalf: '송아지', other: '복수 축종' }[key] || '';
  }

  function speciesForInquiry(key) {
    return speciesForOrder(key);
  }

  function criterionLabel(key) {
    return { evidence: '논문·축종별 근거', quality: '규격·CoA·품질관리', economics: '단가·MOQ·경제성', regulatory: '국가별 규제·표시', supply: 'CAPA·납기·공급안정성' }[key] || '미정';
  }

  function escapeHtml(value) {
    return String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#039;');
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
