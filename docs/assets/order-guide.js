(() => {
  'use strict';

  const PRODUCTS = {
    crude20: {
      name: '가바크루드 20% 기준품',
      shortName: '가바크루드 20%',
      badge: '규격 원료',
      description: '사료회사·프리믹스 업체가 자체 배합에 사용할 수 있도록 GABA 20% 기준으로 공급하는 원료형 제품입니다.',
      bestFor: '표준 규격과 로트별 품질자료를 먼저 확인하고 싶은 고객',
      collaboration: ['원료'],
      defaultStage: 'sample',
      optionLabel: '희망 규격',
      options: ['GABA 20% 기준품', '포장·규격 협의 필요'],
      steps: [
        ['적용 조건 확인', '축종, 목표 사료농도, 예상 물량과 적용 시기를 확인합니다.'],
        ['규격서·품질자료 확인', '제품 규격서, 로트별 CoA, 포장·보관조건과 샘플 필요 여부를 안내합니다.'],
        ['견적·공급조건 확정', 'MOQ, 단가, 포장단위, 납기, 운송과 결제조건을 담당자가 확인합니다.'],
        ['발주서·계약 확인', '구매발주서(PO) 또는 공급계약을 접수하고 생산·출고 일정을 확정합니다.'],
        ['로트 검사·출고', '확정 로트의 품질자료와 출고정보를 전달한 뒤 지정 장소로 공급합니다.']
      ],
      checklist: ['축종·사용목적', '목표 GABA 농도', '샘플 또는 초도 물량', '납품 지역', '희망 납기']
    },
    customCrude: {
      name: '주문형 가바크루드 5–20%',
      shortName: '주문형 가바크루드',
      badge: '맞춤농도 OEM',
      description: '고객의 제품 콘셉트와 배합 조건에 맞춰 GABA 농도와 담체·포장 조건을 협의하는 주문형 원료입니다.',
      bestFor: '자체 제품 규격에 맞는 농도와 포장형태가 필요한 고객',
      collaboration: ['원료', 'OEM'],
      defaultStage: 'sample',
      optionLabel: '희망 GABA 농도',
      options: ['5%', '10%', '15%', '20%', '아직 미정·상담 필요'],
      steps: [
        ['목표 규격 정의', '희망 GABA 농도, 담체, 수분·미생물 기준, 포장단위와 적용 공정을 확인합니다.'],
        ['배합·공정 적합성 검토', '혼합균일도, 펠릿·열공정, 보관조건과 고객의 기존 공정 적용 가능성을 검토합니다.'],
        ['샘플 제작·승인', '필요 시 소량 샘플을 제작하고 함량·외관·혼합성을 확인해 기준 규격을 승인합니다.'],
        ['MOQ·견적·일정 확정', '승인 규격을 기준으로 최소주문량, 단가, 생산 리드타임과 납품조건을 확정합니다.'],
        ['OEM 생산·품질확인·출고', '승인된 규격으로 생산하고 로트 시험성적서와 함께 공급합니다.']
      ],
      checklist: ['희망 GABA 농도', '담체·원료 제한사항', '공정 온도·형태', '초도·연간 예상량', '포장단위']
    },
    caremix: {
      name: 'GABA Care Mix OEM·ODM',
      shortName: '가바케어믹스',
      badge: '축종별 제품개발',
      description: 'GABA와 미네랄 매트릭스를 축종·목표성과에 맞춰 설계해 고객 브랜드로 개발하는 OEM·ODM 솔루션입니다.',
      bestFor: '기능성 브랜드 사료 또는 프리믹스를 출시하려는 사료회사',
      collaboration: ['OEM', '공동개발'],
      defaultStage: 'pilot',
      optionLabel: '희망 제품 형태',
      options: ['프리믹스', '완전배합사료 적용형', '농장 프로그램형', '아직 미정·상담 필요'],
      steps: [
        ['축종·과제·KPI 정의', '대상 축종과 스트레스, 사료효율, 장 건강, 육질 등 해결과제와 검증지표를 정합니다.'],
        ['배합 콘셉트 설계', 'GABA 적용 수준, 미네랄·보조성분, 사료형태와 제조공정을 반영해 1차 배합안을 만듭니다.'],
        ['샘플·파일럿 검증', '시험용 제품을 공급하고 대조군, 적용기간, 급여량과 측정항목을 합의합니다.'],
        ['제품 규격·표시·견적 확정', '시험결과와 국가별 분류·표시 검토를 반영해 규격, MOQ, 단가와 출시 일정을 확정합니다.'],
        ['OEM 생산·출시·재주문', '승인 규격으로 생산하고 판매·농장 데이터를 축적해 반복발주 기준을 관리합니다.']
      ],
      checklist: ['대상 축종', '브랜드 콘셉트', '핵심 KPI', '제조 공정·사료형태', '목표 출시일']
    },
    pilot: {
      name: '농장 파일럿·공동실증',
      shortName: '농장 파일럿',
      badge: '시험부터 시작',
      description: '효능을 미리 단정하지 않고 농장 조건에서 급여량, 생산성, 품질과 경제성을 확인하는 실증형 프로그램입니다.',
      bestFor: '상업 도입 전에 실제 농장 데이터와 ROI를 확인하려는 고객',
      collaboration: ['파일럿'],
      defaultStage: 'pilot',
      optionLabel: '희망 실증 형태',
      options: ['농장 파일럿', '연구기관 시험', '사료회사 공동실증', '아직 미정·상담 필요'],
      steps: [
        ['기초조건 수집', '사육규모, 기초사료, 환경, 과거 생산성, 문제구간과 현재 사용 첨가제를 확인합니다.'],
        ['시험계획 합의', '대조군, 급여수준, 적용기간, 개체·군 식별, KPI와 중단기준을 문서로 확정합니다.'],
        ['샘플 공급·시험 시작', '시험용 제품, 급여 가이드와 기록양식을 제공하고 현장 적용을 시작합니다.'],
        ['성과 모니터링', '씨돼지는 고온기 4–8주를 예시로 하고, 다른 축종은 생산주기에 맞춰 기간과 측정시점을 확정합니다.'],
        ['결과 검토·상업 전환', '대조군 대비 효과, 안전성, 경제성과 재현성을 검토해 규격화·발주 또는 추가시험을 결정합니다.']
      ],
      checklist: ['농장 규모·위치', '기초사료·급여량', '대조군 설정 가능 여부', '측정 가능한 KPI', '시험 희망기간']
    }
  };

  const SPECIES = [
    '비육돈', '씨돼지(종모돈·종빈돈)', '이유자돈·육성돈', '육계', '산란계·종계',
    '한우·육우·와규', '젖소', '송아지', '양·염소', '양식어류·새우', '복수 축종', '해당 없음·기타'
  ];

  const STAGES = [
    { value: 'sample', label: '샘플·규격 확인부터' },
    { value: 'pilot', label: '파일럿·배합시험부터' },
    { value: 'commercial', label: '상업 발주 협의부터' }
  ];

  const STARTS = ['가능한 한 빠르게', '1개월 이내', '1~3개월 이내', '3~6개월 이내', '6개월 이후', '일정 미정'];

  let selectedProduct = 'crude20';

  function init() {
    const productSection = document.getElementById('products') || document.querySelector('.product-section');
    if (!productSection || document.getElementById('order-guide')) return;

    const section = document.createElement('section');
    section.id = 'order-guide';
    section.className = 'order-guide-section';
    section.innerHTML = buildMarkup();
    productSection.insertAdjacentElement('afterend', section);

    bindGuide(section);
    addProductShortcut(productSection, section);
    selectProduct(section, selectedProduct, false);
  }

  function buildMarkup() {
    return `
      <div class="container order-guide-container">
        <div class="order-guide-heading">
          <span class="order-guide-eyebrow">GUIDED B2B ORDER</span>
          <h2>원하는 제품을 고르면<br>주문 준비 순서를 안내합니다.</h2>
          <p>직접 결제 화면이 아니라, 제품 규격·샘플·파일럿·견적·발주까지 담당자와 정확하게 협의하기 위한 주문 가이드입니다.</p>
        </div>

        <div class="order-product-grid" role="list" aria-label="주문 제품 선택">
          ${Object.entries(PRODUCTS).map(([key, product]) => productCard(key, product)).join('')}
        </div>

        <div class="order-guide-panel" aria-live="polite">
          <div class="order-guide-config">
            <div class="order-guide-selected">
              <span id="orderProductBadge"></span>
              <h3 id="orderProductName"></h3>
              <p id="orderProductDescription"></p>
              <div class="order-guide-fit"><strong>이런 고객에게 적합</strong><span id="orderProductFit"></span></div>
            </div>

            <div class="order-guide-fields">
              <label class="order-guide-field">
                <span>주요 축종</span>
                <select id="orderSpecies">
                  <option value="">아직 미정</option>
                  ${SPECIES.map((item) => `<option>${item}</option>`).join('')}
                </select>
              </label>
              <label class="order-guide-field">
                <span>현재 주문 단계</span>
                <select id="orderStage">
                  ${STAGES.map((item) => `<option value="${item.value}">${item.label}</option>`).join('')}
                </select>
              </label>
              <label class="order-guide-field">
                <span id="orderOptionLabel">희망 규격</span>
                <select id="orderOption"></select>
              </label>
              <label class="order-guide-field">
                <span>예상 샘플·초도 물량</span>
                <input id="orderQuantity" type="text" maxlength="100" placeholder="예: 샘플 5 kg / 초도 500 kg">
              </label>
              <label class="order-guide-field">
                <span>적용 국가·지역</span>
                <input id="orderCountry" type="text" maxlength="80" placeholder="예: 대한민국 충남 / Australia QLD">
              </label>
              <label class="order-guide-field">
                <span>희망 시작 시기</span>
                <select id="orderStart">
                  ${STARTS.map((item) => `<option>${item}</option>`).join('')}
                </select>
              </label>
            </div>

            <div class="order-guide-checklist">
              <strong>미리 준비하면 상담이 빨라지는 정보</strong>
              <div id="orderChecklist"></div>
            </div>

            <div class="order-guide-actions">
              <button type="button" id="orderToInquiry" class="order-guide-primary">이 선택으로 주문·견적 문의 시작</button>
              <button type="button" id="orderCopySummary" class="order-guide-secondary">선택 내용 복사</button>
            </div>
            <p id="orderGuideStatus" class="order-guide-status" role="status" aria-live="polite"></p>
          </div>

          <div class="order-guide-timeline">
            <div class="order-guide-timeline-head">
              <span>추천 주문 경로</span>
              <strong id="orderRouteTitle"></strong>
            </div>
            <ol id="orderTimeline"></ol>
            <div class="order-guide-note">
              <strong>주문 확정 전 확인사항</strong>
              <p>최종 규격, MOQ, 단가, 납기, 결제조건, 국가별 등록·표시는 담당자 확인 후 확정됩니다. 급여량과 효능 표현은 축종별 시험조건과 관계기관 검토를 따릅니다.</p>
            </div>
          </div>
        </div>
      </div>`;
  }

  function productCard(key, product) {
    return `
      <button type="button" class="order-product-card" data-order-product="${key}" role="listitem" aria-pressed="false">
        <span>${product.badge}</span>
        <strong>${product.name}</strong>
        <small>${product.description}</small>
        <b>선택하기 →</b>
      </button>`;
  }

  function bindGuide(section) {
    section.querySelectorAll('[data-order-product]').forEach((button) => {
      button.addEventListener('click', () => selectProduct(section, button.dataset.orderProduct, true));
    });

    section.querySelector('#orderToInquiry').addEventListener('click', () => transferToInquiry(section));
    section.querySelector('#orderCopySummary').addEventListener('click', () => copySummary(section));
  }

  function selectProduct(section, key, focusPanel) {
    const product = PRODUCTS[key] || PRODUCTS.crude20;
    selectedProduct = key in PRODUCTS ? key : 'crude20';

    section.querySelectorAll('[data-order-product]').forEach((button) => {
      const active = button.dataset.orderProduct === selectedProduct;
      button.classList.toggle('is-selected', active);
      button.setAttribute('aria-pressed', String(active));
    });

    section.querySelector('#orderProductBadge').textContent = product.badge;
    section.querySelector('#orderProductName').textContent = product.name;
    section.querySelector('#orderProductDescription').textContent = product.description;
    section.querySelector('#orderProductFit').textContent = product.bestFor;
    section.querySelector('#orderOptionLabel').textContent = product.optionLabel;
    section.querySelector('#orderStage').value = product.defaultStage;

    const option = section.querySelector('#orderOption');
    option.innerHTML = product.options.map((item) => `<option>${escapeHtml(item)}</option>`).join('');

    section.querySelector('#orderChecklist').innerHTML = product.checklist
      .map((item) => `<span>${escapeHtml(item)}</span>`).join('');

    section.querySelector('#orderRouteTitle').textContent = `${product.shortName} 주문 절차`;
    section.querySelector('#orderTimeline').innerHTML = product.steps
      .map(([title, body], index) => `<li><i>${String(index + 1).padStart(2, '0')}</i><div><strong>${escapeHtml(title)}</strong><p>${escapeHtml(body)}</p></div></li>`)
      .join('');

    section.querySelector('#orderGuideStatus').textContent = `${product.name}을 선택했습니다. 아래 조건을 입력하면 문의 내용에 자동 반영됩니다.`;
    if (focusPanel) section.querySelector('.order-guide-panel').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function addProductShortcut(productSection, guideSection) {
    const productCopy = productSection.querySelector('.product-copy');
    if (!productCopy || productCopy.querySelector('.order-guide-shortcut')) return;

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'order-guide-shortcut';
    productCopy.append(button);

    function sync() {
      const active = productSection.querySelector('[data-product].active');
      const key = active && active.dataset.product === 'caremix' ? 'caremix' : 'crude20';
      button.dataset.orderProduct = key;
      button.textContent = key === 'caremix' ? '가바케어믹스 주문방법 보기 →' : '가바크루드 주문방법 보기 →';
    }

    productSection.querySelectorAll('[data-product]').forEach((tab) => {
      tab.addEventListener('click', () => setTimeout(sync, 0));
    });

    button.addEventListener('click', () => {
      selectProduct(guideSection, button.dataset.orderProduct || 'crude20', false);
      guideSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    sync();
  }

  function collectSelection(section) {
    const product = PRODUCTS[selectedProduct];
    const stage = STAGES.find((item) => item.value === section.querySelector('#orderStage').value);
    return {
      product,
      species: section.querySelector('#orderSpecies').value.trim(),
      stageValue: stage ? stage.value : 'sample',
      stageLabel: stage ? stage.label : '샘플·규격 확인부터',
      option: section.querySelector('#orderOption').value.trim(),
      quantity: section.querySelector('#orderQuantity').value.trim(),
      country: section.querySelector('#orderCountry').value.trim(),
      start: section.querySelector('#orderStart').value.trim()
    };
  }

  function selectionSummary(selection) {
    return [
      '[제품 주문 가이드에서 선택]',
      `- 선택 제품: ${selection.product.name}`,
      `- 주문 단계: ${selection.stageLabel}`,
      `- 주요 축종: ${selection.species || '미정'}`,
      `- ${selection.product.optionLabel}: ${selection.option || '미정'}`,
      `- 예상 샘플·초도 물량: ${selection.quantity || '미정'}`,
      `- 적용 국가·지역: ${selection.country || '미정'}`,
      `- 희망 시작 시기: ${selection.start || '미정'}`,
      '- 요청사항: 위 조건을 기준으로 제품 규격서, 샘플 가능 여부, MOQ, 견적, 리드타임과 발주 절차 안내를 요청합니다.'
    ].join('\n');
  }

  function transferToInquiry(section) {
    const selection = collectSelection(section);
    const form = document.getElementById('businessInquiryForm');
    const contact = document.getElementById('contact') || document.querySelector('.contact-section');
    const status = section.querySelector('#orderGuideStatus');

    if (!form || !contact) {
      status.textContent = '문의 폼을 불러오는 중입니다. 잠시 후 다시 눌러 주세요.';
      return;
    }

    ensureHidden(form, '선택제품', selection.product.name);
    ensureHidden(form, '선택규격_형태', selection.option || '미정');
    ensureHidden(form, '주문가이드_경로', selection.stageLabel);

    setSelect(form, '주요_축종', selection.species);
    setSelect(form, '현재_준비단계', stageToInquiry(selection.stageValue));
    setSelect(form, '희망_시작시기', selection.start);
    setValueIfBlank(form, '예상_샘플_초도물량', selection.quantity);
    setValueIfBlank(form, '국가_지역', selection.country);
    checkValues(form, '협업_유형', selection.product.collaboration);

    const message = form.elements.namedItem('상세_요청사항');
    const summary = selectionSummary(selection);
    if (message && typeof message.value === 'string') {
      const marker = '[제품 주문 가이드에서 선택]';
      if (!message.value.includes(marker)) {
        message.value = message.value.trim() ? `${summary}\n\n${message.value.trim()}` : summary;
      }
      message.dispatchEvent(new Event('input', { bubbles: true }));
    }

    showPrefillBanner(form, selection);
    status.textContent = '선택 내용이 사업협업 문의 폼에 입력되었습니다. 기본 정보를 작성한 뒤 전송해 주세요.';
    contact.scrollIntoView({ behavior: 'smooth', block: 'start' });
    setTimeout(() => form.querySelector('#inquiryCompany')?.focus({ preventScroll: true }), 500);
  }

  function stageToInquiry(stage) {
    return {
      sample: '샘플·규격서 검토 단계',
      pilot: '파일럿 설계 단계',
      commercial: '상업 발주·유통 협의 단계'
    }[stage] || '샘플·규격서 검토 단계';
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

  function setSelect(form, name, value) {
    if (!value) return;
    const field = form.elements.namedItem(name);
    if (!field || field.tagName !== 'SELECT') return;
    const option = [...field.options].find((item) => item.value === value || item.textContent.trim() === value);
    if (option) {
      field.value = option.value;
      field.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }

  function setValueIfBlank(form, name, value) {
    if (!value) return;
    const field = form.elements.namedItem(name);
    if (!field || typeof field.value !== 'string' || field.value.trim()) return;
    field.value = value;
    field.dispatchEvent(new Event('input', { bubbles: true }));
  }

  function checkValues(form, name, values) {
    values.forEach((value) => {
      const field = [...form.querySelectorAll(`input[name="${name}"]`)].find((item) => item.value === value);
      if (field) field.checked = true;
    });
  }

  function showPrefillBanner(form, selection) {
    let banner = form.querySelector('.order-prefill-banner');
    if (!banner) {
      banner = document.createElement('div');
      banner.className = 'order-prefill-banner';
      const progress = form.querySelector('.inquiry-progress');
      if (progress) progress.before(banner);
      else form.prepend(banner);
    }
    banner.innerHTML = `<strong>선택 제품: ${escapeHtml(selection.product.name)}</strong><span>${escapeHtml(selection.stageLabel)} · ${escapeHtml(selection.species || '축종 미정')} · ${escapeHtml(selection.quantity || '물량 미정')}</span>`;
  }

  async function copySummary(section) {
    const text = selectionSummary(collectSelection(section));
    const status = section.querySelector('#orderGuideStatus');
    try {
      await navigator.clipboard.writeText(text);
      status.textContent = '선택 내용을 복사했습니다. 이메일이나 내부 검토 문서에 붙여 넣을 수 있습니다.';
    } catch (_error) {
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.setAttribute('readonly', '');
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.append(textarea);
      textarea.select();
      document.execCommand('copy');
      textarea.remove();
      status.textContent = '선택 내용을 복사했습니다.';
    }
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
