(() => {
  'use strict';

  const RECIPIENT = 'dubaissday@cellpinda.com';
  const FORM_ENDPOINT = `https://formsubmit.co/${RECIPIENT}`;
  const STEP_TITLES = ['기본 정보', '협업 목표', '도입 조건', '검토·전송'];

  function init() {
    const section = ensureContactSection();
    section.id = 'contact';
    section.classList.add('inquiry-section');
    section.innerHTML = buildMarkup();

    updateContactLinks();
    bindForm(section);
    showSuccessState(section);
  }

  function ensureContactSection() {
    let section = document.querySelector('.contact-section');
    if (section) return section;

    section = document.createElement('section');
    section.className = 'contact-section';
    const footer = document.querySelector('footer');
    if (footer) footer.before(section);
    else document.body.append(section);
    return section;
  }

  function updateContactLinks() {
    document.querySelectorAll('a[href^="mailto:"]').forEach((link) => {
      const href = (link.getAttribute('href') || '').toLowerCase();
      if (!href.includes('cellpinda.com')) return;
      link.setAttribute('href', '#contact');
      link.removeAttribute('target');
      if (link.classList.contains('nav-cta')) link.textContent = '사업협업 문의';
    });
  }

  function buildMarkup() {
    return `
      <div class="container inquiry-container">
        <div class="inquiry-shell">
          <aside class="inquiry-intro" aria-labelledby="inquiryTitle">
            <span class="inquiry-eyebrow">BUSINESS COLLABORATION</span>
            <h2 id="inquiryTitle">협업 목적에 맞춰<br>필요한 정보를 먼저 확인합니다.</h2>
            <p>원료 공급, OEM·ODM, 농장 파일럿, 공동연구 또는 해외 유통을 검토할 수 있도록 핵심 조건을 순서대로 질문합니다.</p>
            <div class="inquiry-promise">
              <div><span>01</span><strong>요청 목적 확인</strong><small>제품·시험·유통 중 필요한 협업 유형을 구분합니다.</small></div>
              <div><span>02</span><strong>적용 조건 확인</strong><small>축종, 규모, 해결 과제와 목표 지표를 확인합니다.</small></div>
              <div><span>03</span><strong>담당자 검토</strong><small>입력 내용은 ${RECIPIENT}으로 전달됩니다.</small></div>
            </div>
            <p class="inquiry-security">민감정보, 주민등록번호, 계좌번호 또는 영업비밀 원문은 입력하지 마세요.</p>
          </aside>

          <div class="inquiry-card">
            <div id="inquirySuccess" class="inquiry-success" role="status" aria-live="polite" hidden>
              <strong>문의가 접수되었습니다.</strong>
              <span>입력하신 이메일로 접수 안내가 발송되며, 담당자가 내용을 확인한 후 회신드립니다.</span>
            </div>

            <form id="businessInquiryForm" class="inquiry-form" action="${FORM_ENDPOINT}" method="POST" novalidate>
              <input type="hidden" name="_subject" id="inquirySubject" value="[GABA Feed 협업문의] 신규 문의">
              <input type="hidden" name="_template" value="table">
              <input type="hidden" name="_next" id="inquiryNext" value="">
              <input type="hidden" name="_autoresponse" value="셀핀다 GABA Feed Solutions에 문의해 주셔서 감사합니다. 전달해 주신 내용을 확인한 후 담당자가 회신드리겠습니다.">
              <input type="hidden" name="접수시각" id="inquiryTimestamp" value="">
              <input type="hidden" name="접수페이지" id="inquiryPage" value="">
              <input type="text" name="_honey" class="inquiry-honeypot" tabindex="-1" autocomplete="off" aria-hidden="true">

              <div class="inquiry-progress" aria-label="문의 작성 단계">
                <div class="inquiry-progress-bar"><i id="inquiryProgressBar"></i></div>
                <div class="inquiry-progress-meta">
                  <span id="inquiryStepNumber">1 / 4</span>
                  <strong id="inquiryStepTitle">${STEP_TITLES[0]}</strong>
                </div>
              </div>

              <div id="inquiryError" class="inquiry-error" role="alert" aria-live="assertive" hidden></div>

              <fieldset class="inquiry-step is-active" data-step="0">
                <legend>기본 정보</legend>
                <p class="inquiry-step-copy">회신과 협업 가능성 검토에 필요한 최소 정보를 입력해 주세요.</p>
                <div class="inquiry-grid two">
                  <label class="inquiry-field">
                    <span>회사·기관명 <em>필수</em></span>
                    <input id="inquiryCompany" name="회사_기관명" type="text" autocomplete="organization" maxlength="100" required placeholder="예: ○○사료 / ○○농장">
                  </label>
                  <label class="inquiry-field">
                    <span>담당자명 <em>필수</em></span>
                    <input id="inquiryName" name="담당자명" type="text" autocomplete="name" maxlength="60" required placeholder="성명">
                  </label>
                  <label class="inquiry-field">
                    <span>직책·부서</span>
                    <input name="직책_부서" type="text" autocomplete="organization-title" maxlength="80" placeholder="예: R&D 팀장">
                  </label>
                  <label class="inquiry-field">
                    <span>이메일 <em>필수</em></span>
                    <input id="inquiryEmail" name="email" type="email" autocomplete="email" maxlength="120" required placeholder="name@company.com">
                  </label>
                  <label class="inquiry-field">
                    <span>연락처</span>
                    <input name="연락처" type="tel" autocomplete="tel" maxlength="40" placeholder="전화 / WhatsApp">
                  </label>
                  <label class="inquiry-field">
                    <span>국가·지역 <em>필수</em></span>
                    <input name="국가_지역" type="text" autocomplete="country-name" maxlength="80" required placeholder="예: 대한민국 충남 / Australia QLD">
                  </label>
                </div>
              </fieldset>

              <fieldset class="inquiry-step" data-step="1" hidden>
                <legend>협업 목표</legend>
                <p class="inquiry-step-copy">가장 가까운 협업 유형과 적용 대상을 선택해 주세요.</p>

                <div class="inquiry-fieldset" data-required-group="협업_유형">
                  <span class="inquiry-label">협업 유형 <em>필수 · 복수 선택 가능</em></span>
                  <div class="inquiry-choice-grid">
                    ${checkbox('협업_유형', 'GABA 원료 도입·공급', '원료')}
                    ${checkbox('협업_유형', 'GABA Care Mix OEM·ODM', 'OEM')}
                    ${checkbox('협업_유형', '농장 파일럿·실증', '파일럿')}
                    ${checkbox('협업_유형', '사료회사 공동개발', '공동개발')}
                    ${checkbox('협업_유형', '연구기관 공동연구', '공동연구')}
                    ${checkbox('협업_유형', '해외 수입·유통 파트너십', '수출입')}
                  </div>
                </div>

                <div class="inquiry-grid two inquiry-gap-top">
                  <label class="inquiry-field">
                    <span>주요 축종 <em>필수</em></span>
                    <select id="inquirySpecies" name="주요_축종" required>
                      <option value="">선택해 주세요</option>
                      <option>비육돈</option>
                      <option>씨돼지(종모돈·종빈돈)</option>
                      <option>이유자돈·육성돈</option>
                      <option>육계</option>
                      <option>산란계·종계</option>
                      <option>한우·육우·와규</option>
                      <option>젖소</option>
                      <option>송아지</option>
                      <option>양·염소</option>
                      <option>양식어류·새우</option>
                      <option>복수 축종</option>
                      <option>해당 없음·기타</option>
                    </select>
                  </label>
                  <label class="inquiry-field">
                    <span>사육규모 또는 사료물량</span>
                    <input name="사육규모_사료물량" type="text" maxlength="120" placeholder="예: 종모돈 300두 / 월 2,000톤">
                  </label>
                </div>

                <div class="inquiry-fieldset inquiry-gap-top" data-required-group="현재_과제">
                  <span class="inquiry-label">현재 해결하려는 과제 <em>필수 · 복수 선택 가능</em></span>
                  <div class="inquiry-chip-grid">
                    ${checkbox('현재_과제', '고온·열 스트레스', '열스트레스', true)}
                    ${checkbox('현재_과제', '사료섭취량 저하', '섭취량', true)}
                    ${checkbox('현재_과제', 'ADG·FCR·생산성', '생산성', true)}
                    ${checkbox('현재_과제', '행동·이동·혼군 스트레스', '행동', true)}
                    ${checkbox('현재_과제', '장 건강·소화율', '장건강', true)}
                    ${checkbox('현재_과제', '육질·육색·항산화', '육질', true)}
                    ${checkbox('현재_과제', '번식·정액 품질 관련 지표', '번식', true)}
                    ${checkbox('현재_과제', '신제품·브랜드 차별화', '브랜드', true)}
                    ${checkbox('현재_과제', '수입·등록·표시 검토', '규제', true)}
                  </div>
                </div>
              </fieldset>

              <fieldset class="inquiry-step" data-step="2" hidden>
                <legend>도입 조건</legend>
                <p class="inquiry-step-copy">시험 또는 상업 도입을 검토하는 데 필요한 범위를 알려 주세요.</p>

                <div class="inquiry-grid two">
                  <label class="inquiry-field">
                    <span>현재 준비 단계 <em>필수</em></span>
                    <select name="현재_준비단계" required>
                      <option value="">선택해 주세요</option>
                      <option>정보 수집 단계</option>
                      <option>샘플·규격서 검토 단계</option>
                      <option>배합·원가 검토 단계</option>
                      <option>파일럿 설계 단계</option>
                      <option>즉시 파일럿 가능</option>
                      <option>상업 발주·유통 협의 단계</option>
                    </select>
                  </label>
                  <label class="inquiry-field">
                    <span>희망 시작 시기 <em>필수</em></span>
                    <select name="희망_시작시기" required>
                      <option value="">선택해 주세요</option>
                      <option>가능한 한 빠르게</option>
                      <option>1개월 이내</option>
                      <option>1~3개월 이내</option>
                      <option>3~6개월 이내</option>
                      <option>6개월 이후</option>
                      <option>일정 미정</option>
                    </select>
                  </label>
                  <label class="inquiry-field">
                    <span>예상 샘플·초도 물량</span>
                    <input name="예상_샘플_초도물량" type="text" maxlength="100" placeholder="예: 샘플 5 kg / 초도 500 kg">
                  </label>
                  <label class="inquiry-field">
                    <span>예상 연간 물량</span>
                    <input name="예상_연간물량" type="text" maxlength="100" placeholder="예: 연 10톤 / 미정">
                  </label>
                </div>

                <div class="inquiry-fieldset inquiry-gap-top">
                  <span class="inquiry-label">확인하고 싶은 핵심 지표 <small>선택</small></span>
                  <div class="inquiry-chip-grid">
                    ${checkbox('핵심_평가지표', '사료섭취량·기호성', 'KPI섭취', true)}
                    ${checkbox('핵심_평가지표', 'ADG·FCR·출하일', 'KPI성장', true)}
                    ${checkbox('핵심_평가지표', '폐사·질병·설사', 'KPI건강', true)}
                    ${checkbox('핵심_평가지표', 'cortisol·행동', 'KPI스트레스', true)}
                    ${checkbox('핵심_평가지표', '정액량·운동성·이상정자율', 'KPI번식', true)}
                    ${checkbox('핵심_평가지표', '육색·TBARS·등급', 'KPI육질', true)}
                    ${checkbox('핵심_평가지표', 'ROI·사료비 절감', 'KPI경제성', true)}
                    ${checkbox('핵심_평가지표', '혼합균일도·열안정성', 'KPI품질', true)}
                  </div>
                </div>

                <label class="inquiry-field inquiry-gap-top">
                  <span>상세 요청사항 <em>필수</em></span>
                  <textarea id="inquiryMessage" name="상세_요청사항" rows="6" maxlength="2000" required placeholder="현재 상황, 희망 제품 형태, 시험 조건, 목표 일정, 필요한 자료를 구체적으로 작성해 주세요."></textarea>
                  <small class="inquiry-count"><b id="inquiryCount">0</b> / 2,000</small>
                </label>
              </fieldset>

              <fieldset class="inquiry-step" data-step="3" hidden>
                <legend>검토·전송</legend>
                <p class="inquiry-step-copy">아래 요약을 확인한 후 문의를 전송해 주세요.</p>
                <div id="inquiryReview" class="inquiry-review"></div>

                <label class="inquiry-consent">
                  <input id="inquiryConsent" name="개인정보_전송동의" type="checkbox" value="동의" required>
                  <span>입력한 정보가 문의 대응을 위해 외부 폼 전송 서비스(FormSubmit)를 거쳐 <strong>${RECIPIENT}</strong>으로 전달되는 것에 동의합니다. <em>필수</em></span>
                </label>

                <div class="inquiry-submit-note">
                  <strong>전송 후 처리</strong>
                  <p>문의 내용은 표 형식의 이메일로 전달됩니다. 스팸 방지를 위해 전송 과정에서 보안 확인 화면이 표시될 수 있습니다.</p>
                </div>
              </fieldset>

              <div class="inquiry-actions">
                <button type="button" id="inquiryPrev" class="inquiry-button secondary" hidden>이전</button>
                <button type="button" id="inquiryMailFallback" class="inquiry-button ghost" hidden>메일 앱으로 보내기</button>
                <button type="button" id="inquiryNextButton" class="inquiry-button primary">다음</button>
                <button type="submit" id="inquirySubmit" class="inquiry-button primary" hidden>협업문의 전송</button>
              </div>
            </form>
          </div>
        </div>
      </div>`;
  }

  function checkbox(name, label, value, chip = false) {
    return `<label class="${chip ? 'inquiry-chip' : 'inquiry-choice'}"><input type="checkbox" name="${name}" value="${value}"><span>${label}</span></label>`;
  }

  function bindForm(section) {
    const form = section.querySelector('#businessInquiryForm');
    const steps = [...form.querySelectorAll('.inquiry-step')];
    const nextButton = form.querySelector('#inquiryNextButton');
    const prevButton = form.querySelector('#inquiryPrev');
    const submitButton = form.querySelector('#inquirySubmit');
    const fallbackButton = form.querySelector('#inquiryMailFallback');
    const errorBox = form.querySelector('#inquiryError');
    const message = form.querySelector('#inquiryMessage');
    let stepIndex = 0;

    function renderStep(nextIndex) {
      stepIndex = Math.max(0, Math.min(nextIndex, steps.length - 1));
      steps.forEach((step, index) => {
        const active = index === stepIndex;
        step.classList.toggle('is-active', active);
        step.hidden = !active;
      });
      form.querySelector('#inquiryStepNumber').textContent = `${stepIndex + 1} / ${steps.length}`;
      form.querySelector('#inquiryStepTitle').textContent = STEP_TITLES[stepIndex];
      form.querySelector('#inquiryProgressBar').style.width = `${((stepIndex + 1) / steps.length) * 100}%`;
      prevButton.hidden = stepIndex === 0;
      nextButton.hidden = stepIndex === steps.length - 1;
      submitButton.hidden = stepIndex !== steps.length - 1;
      fallbackButton.hidden = stepIndex !== steps.length - 1;
      errorBox.hidden = true;
      if (stepIndex === steps.length - 1) renderReview(form);
      const firstField = steps[stepIndex].querySelector('input:not([type="hidden"]), select, textarea');
      if (firstField && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        setTimeout(() => firstField.focus({ preventScroll: true }), 60);
      }
    }

    nextButton.addEventListener('click', () => {
      if (!validateStep(form, steps[stepIndex], errorBox)) return;
      renderStep(stepIndex + 1);
      section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    prevButton.addEventListener('click', () => {
      renderStep(stepIndex - 1);
      section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    message.addEventListener('input', () => {
      form.querySelector('#inquiryCount').textContent = String(message.value.length);
    });

    fallbackButton.addEventListener('click', () => {
      if (!validateAll(form, steps, errorBox, renderStep)) return;
      prepareSubmission(form);
      const subject = form.querySelector('#inquirySubject').value;
      const body = buildMailBody(form);
      window.location.href = `mailto:${RECIPIENT}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    });

    form.addEventListener('submit', (event) => {
      if (!validateAll(form, steps, errorBox, renderStep)) {
        event.preventDefault();
        return;
      }
      prepareSubmission(form);
      submitButton.disabled = true;
      submitButton.textContent = '전송 중…';
    });

    renderStep(0);
  }

  function validateStep(form, step, errorBox) {
    const fields = [...step.querySelectorAll('input, select, textarea')];
    const invalid = fields.find((field) => !field.checkValidity());
    if (invalid) {
      showError(errorBox, '필수 항목을 확인해 주세요.');
      invalid.reportValidity();
      invalid.focus();
      return false;
    }

    const requiredGroups = [...step.querySelectorAll('[data-required-group]')];
    const emptyGroup = requiredGroups.find((group) => !group.querySelector('input[type="checkbox"]:checked'));
    if (emptyGroup) {
      showError(errorBox, '필수 선택 항목에서 한 가지 이상 선택해 주세요.');
      emptyGroup.scrollIntoView({ behavior: 'smooth', block: 'center' });
      emptyGroup.querySelector('input').focus();
      return false;
    }

    errorBox.hidden = true;
    return true;
  }

  function validateAll(form, steps, errorBox, renderStep) {
    for (let index = 0; index < steps.length; index += 1) {
      if (!validateStep(form, steps[index], errorBox)) {
        renderStep(index);
        return false;
      }
    }
    return true;
  }

  function showError(errorBox, message) {
    errorBox.textContent = message;
    errorBox.hidden = false;
  }

  function prepareSubmission(form) {
    const company = form.querySelector('#inquiryCompany').value.trim();
    const species = form.querySelector('#inquirySpecies').value;
    const types = checkedValues(form, '협업_유형').join('·');
    form.querySelector('#inquirySubject').value = `[GABA Feed 협업문의] ${company} · ${types || '협업'} · ${species || '축종 미정'}`;
    form.querySelector('#inquiryTimestamp').value = new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });
    form.querySelector('#inquiryPage').value = window.location.href.split('#')[0];

    const next = new URL(window.location.href);
    next.searchParams.set('inquiry', 'success');
    next.hash = 'contact';
    form.querySelector('#inquiryNext').value = next.toString();
  }

  function checkedValues(form, name) {
    return [...form.querySelectorAll(`input[name="${name}"]:checked`)].map((field) => field.value);
  }

  function renderReview(form) {
    const rows = [
      ['회사·담당자', `${value(form, '회사_기관명')} · ${value(form, '담당자명')}`],
      ['이메일', value(form, 'email')],
      ['국가·지역', value(form, '국가_지역')],
      ['협업 유형', checkedValues(form, '협업_유형').join(', ')],
      ['주요 축종', value(form, '주요_축종')],
      ['현재 과제', checkedValues(form, '현재_과제').join(', ')],
      ['준비 단계', value(form, '현재_준비단계')],
      ['희망 시작', value(form, '희망_시작시기')],
      ['상세 요청', value(form, '상세_요청사항')]
    ];
    form.querySelector('#inquiryReview').innerHTML = rows.map(([label, text]) => `
      <div><span>${escapeHtml(label)}</span><strong>${escapeHtml(text || '미입력')}</strong></div>`).join('');
  }

  function value(form, name) {
    const field = form.elements.namedItem(name);
    return field && typeof field.value === 'string' ? field.value.trim() : '';
  }

  function buildMailBody(form) {
    const data = new FormData(form);
    const grouped = new Map();
    for (const [key, raw] of data.entries()) {
      if (key.startsWith('_')) continue;
      const value = String(raw).trim();
      if (!value) continue;
      if (!grouped.has(key)) grouped.set(key, []);
      grouped.get(key).push(value);
    }
    return [...grouped.entries()]
      .map(([key, values]) => `${key.replaceAll('_', ' ')}: ${values.join(', ')}`)
      .join('\n\n');
  }

  function showSuccessState(section) {
    const params = new URLSearchParams(window.location.search);
    if (params.get('inquiry') !== 'success') return;
    const success = section.querySelector('#inquirySuccess');
    success.hidden = false;
    success.scrollIntoView({ behavior: 'smooth', block: 'center' });
    params.delete('inquiry');
    const clean = `${window.location.pathname}${params.toString() ? `?${params}` : ''}${window.location.hash}`;
    window.history.replaceState({}, '', clean);
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
