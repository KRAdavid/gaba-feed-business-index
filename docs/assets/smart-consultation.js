(() => {
  'use strict';

  const DATA_URL = 'data/b2b_operations.json';
  const STORE_KEY = 'cellpindaSmartConsultationV1';
  const START = '[스마트 상담 자동설정]';
  const END = '[자동설정 끝]';

  const SPECIES = {
    pig: '비육돈', breederPig: '씨돼지(종모돈·종빈돈)', breeder_pig: '씨돼지(종모돈·종빈돈)',
    poultry: '육계', broiler: '육계', beef: '한우·육우·와규', dairyCalf: '송아지', other: '복수 축종'
  };
  const STAGE = {
    sample: '샘플·규격서 검토 단계', pilot: '파일럿 설계 단계', commercial: '상업 발주·유통 협의 단계',
    learn: '정보 수집 단계', spec: '샘플·규격서 검토 단계', review: '정보 수집 단계'
  };
  const TASK_KPI = {
    열스트레스: ['KPI섭취', 'KPI스트레스', 'KPI건강'], 섭취량: ['KPI섭취', 'KPI건강'],
    생산성: ['KPI성장', 'KPI경제성'], 행동: ['KPI스트레스', 'KPI섭취'], 장건강: ['KPI건강', 'KPI섭취'],
    육질: ['KPI육질', 'KPI경제성'], 번식: ['KPI번식', 'KPI스트레스', 'KPI섭취'], 브랜드: ['KPI경제성'], 규제: []
  };
  let packMap = new Map();

  const esc = (v) => String(v ?? '').replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#039;');
  const norm = (v) => String(v ?? '').replace(/\s+/g, ' ').trim().toLowerCase();
  const reduced = () => window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  const css = (v) => window.CSS?.escape ? window.CSS.escape(String(v)) : String(v).replace(/["\\]/g, '\\$&');
  const byName = (form, name) => form?.elements?.namedItem(name);
  const value = (selector) => {
    const el = document.querySelector(selector);
    if (!el) return '';
    return el.tagName === 'SELECT' ? (el.options[el.selectedIndex]?.textContent?.trim() || el.value) : String(el.value || el.textContent || '').trim();
  };
  const checked = (form, name) => [...form.querySelectorAll(`input[name="${css(name)}"]:checked`)].map((el) => el.value);

  function addStyles() {
    if (document.querySelector('link[data-smart-consultation-style]')) return;
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'assets/smart-consultation.css';
    link.dataset.smartConsultationStyle = 'v1';
    document.head.append(link);
  }

  function speciesOf(v) {
    const raw = String(v || '').trim();
    if (!raw) return '';
    if (SPECIES[raw]) return SPECIES[raw];
    if (/씨돼지|종모돈|종빈돈|번식돈/.test(raw)) return '씨돼지(종모돈·종빈돈)';
    if (/이유|육성돈|자돈/.test(raw)) return '이유자돈·육성돈';
    if (/비육돈|돼지/.test(raw)) return '비육돈';
    if (/산란|종계/.test(raw)) return '산란계·종계';
    if (/육계|브로일러/.test(raw)) return '육계';
    if (/와규|한우|육우|비육우/.test(raw)) return '한우·육우·와규';
    if (/젖소|낙농/.test(raw)) return '젖소';
    if (/송아지|calf/i.test(raw)) return '송아지';
    if (/양|염소/.test(raw)) return '양·염소';
    if (/어류|새우|양식/.test(raw)) return '양식어류·새우';
    if (/복수|기타/.test(raw)) return '복수 축종';
    return raw;
  }

  function setSelect(form, name, wanted) {
    const el = byName(form, name);
    if (!el || el.tagName !== 'SELECT' || !wanted || el.value) return false;
    const target = norm(STAGE[wanted] || SPECIES[wanted] || wanted);
    const option = [...el.options].find((opt) => norm(opt.value) === target || norm(opt.textContent) === target);
    if (!option) return false;
    el.value = option.value;
    el.dispatchEvent(new Event('change', { bubbles: true }));
    return true;
  }

  function setInput(form, name, wanted) {
    const el = byName(form, name);
    if (!el || !wanted || String(el.value || '').trim()) return false;
    el.value = String(wanted).trim();
    el.dispatchEvent(new Event('input', { bubbles: true }));
    return true;
  }

  function setChecks(form, name, values) {
    let count = 0;
    const wanted = new Set(values || []);
    form.querySelectorAll(`input[name="${css(name)}"]`).forEach((el) => {
      if (wanted.has(el.value) && !el.checked) { el.checked = true; el.dispatchEvent(new Event('change', { bubbles: true })); count += 1; }
    });
    return count;
  }

  function hidden(form, name, wanted) {
    let el = form.querySelector(`input[type="hidden"][name="${css(name)}"]`);
    if (!el) { el = document.createElement('input'); el.type = 'hidden'; el.name = name; form.append(el); }
    el.value = String(wanted || '');
    el.dataset.smartConsultation = 'true';
  }

  function currentContext(source, pack) {
    const form = document.getElementById('businessInquiryForm');
    const active = document.querySelector('.product-switch [data-product].active')?.dataset.product;
    const product = pack?.product || form?.querySelector('input[name="선택제품"]')?.value || (active === 'caremix' ? 'GABA Care Mix OEM·ODM' : '가바크루드 20% 기준품');
    const orderSpecies = value('#orderSpecies');
    const calcSpecies = value('#speciesCalc, #calculator select');
    const stage = pack?.stage || byName(form, '현재_준비단계')?.value || value('#orderStage');
    return {
      source, pack,
      role: pack?.role || form?.querySelector('input[name="B2B_바이어역할"]')?.value || '',
      product,
      species: speciesOf(byName(form, '주요_축종')?.value || orderSpecies || calcSpecies),
      stage: STAGE[stage] || stage || '',
      start: byName(form, '희망_시작시기')?.value || value('#orderStart'),
      option: value('#orderOption'), quantity: value('#orderQuantity'), country: value('#orderCountry'),
      collaboration: form ? checked(form, '협업_유형') : [], tasks: form ? checked(form, '현재_과제') : [], kpis: form ? checked(form, '핵심_평가지표') : [],
      calculator: {
        heads: value('#headCount'), growth: value('#growthImprovementPct'), fcr: value('#fcrImprovementPct'),
        ppm: document.getElementById('autoPpm')?.textContent?.trim() || '', crude: document.getElementById('neededCrude')?.textContent?.trim() || ''
      }
    };
  }

  function settingsOf(c) {
    const collaboration = [...c.collaboration];
    const add = (arr, v) => { if (v && !arr.includes(v)) arr.push(v); };
    const text = `${c.role} ${c.product} ${c.stage} ${c.pack?.title || ''}`;
    if (/Care Mix|OEM|ODM/i.test(text)) { add(collaboration, 'OEM'); add(collaboration, '공동개발'); }
    else add(collaboration, '원료');
    if (/파일럿|실증|농장/.test(text)) add(collaboration, '파일럿');
    if (/연구기관|공동연구/.test(text)) add(collaboration, '공동연구');
    if (/해외|수입|유통/.test(text)) add(collaboration, '수출입');

    const tasks = [...c.tasks];
    if (/Care Mix|OEM|ODM|브랜드/i.test(text)) add(tasks, '브랜드');
    if (/해외|수입|유통/.test(text)) add(tasks, '규제');
    if (/씨돼지|종모돈|종빈돈/.test(c.species)) add(tasks, '번식');
    const kpis = [...c.kpis];
    tasks.forEach((task) => (TASK_KPI[task] || []).forEach((kpi) => add(kpis, kpi)));
    if (collaboration.includes('파일럿') && !kpis.length) ['KPI섭취', 'KPI성장', 'KPI경제성'].forEach((kpi) => add(kpis, kpi));

    const stage = c.stage || (collaboration.includes('파일럿') ? '파일럿 설계 단계' : '정보 수집 단계');
    const start = c.start || (/상업 발주/.test(stage) ? '가능한 한 빠르게' : /파일럿/.test(stage) ? '1~3개월 이내' : /샘플|규격/.test(stage) ? '1개월 이내' : '일정 미정');
    const documents = c.pack?.items?.length ? c.pack.items : collaboration.includes('수출입')
      ? ['영문 규격·대표 CoA', '제조공정·원산지', '국가별 규제 포지션', 'MOQ·Incoterms']
      : collaboration.includes('파일럿') ? ['제품 규격', '급여설계', '대조군·KPI 프로토콜', '경제성 검토']
        : ['제품 규격', '대표 CoA', 'MOQ·가격·포장·납기'];
    return { collaboration, tasks, kpis, stage, start, documents };
  }

  function conditionalFields(c, s) {
    const fields = [{ name: '희망_회신범위', label: '우선 받을 내용', options: ['기술자료 우선', '기술자료·샘플', '파일럿 설계', '견적·공급조건', '종합 상담'], value: /상업 발주/.test(s.stage) ? '견적·공급조건' : /파일럿/.test(s.stage) ? '파일럿 설계' : /샘플|규격/.test(s.stage) ? '기술자료·샘플' : '기술자료 우선' }];
    if (/Care Mix|OEM|ODM/i.test(c.product)) fields.push({ name: '희망_제품형태', label: '희망 제품 형태', options: ['프리믹스', '완전배합사료 적용형', '농장 프로그램형', '아직 미정·상담 필요'], value: c.option || '아직 미정·상담 필요' });
    else fields.push({ name: '희망_GABA_규격', label: '희망 GABA 규격', options: ['GABA 20% 기준품', '5% 맞춤', '10% 맞춤', '15% 맞춤', '20% 맞춤', '아직 미정·상담 필요'], value: c.option || 'GABA 20% 기준품' });
    if (s.collaboration.includes('파일럿')) fields.push({ name: '대조군_설정가능여부', label: '대조군 설정 가능 여부', options: ['가능', '일부 가능', '검토 필요', '현재 불가'], value: '검토 필요' });
    if (/씨돼지|종모돈|종빈돈/.test(c.species)) fields.push({ name: '희망_시험기간', label: '희망 시험기간', value: '고온기 4~8주 검토' });
    else if (/한우|육우|와규/.test(c.species)) fields.push({ name: '육우_우선_KPI', label: '육우·와규 우선 KPI', value: 'DMI·ADG·FCR·건강·육질·ROI' });
    if (s.collaboration.includes('수출입')) fields.push({ name: '목표_판매국', label: '목표 판매국', value: c.country || '' });
    return fields.slice(0, 5);
  }

  function renderConditionals(form, fields) {
    const step = form.querySelector('[data-step="2"]');
    if (!step) return;
    let panel = form.querySelector('#smartConditionalFields');
    if (!panel) { panel = document.createElement('div'); panel.id = 'smartConditionalFields'; panel.className = 'inquiry-fieldset inquiry-gap-top smart-conditional-panel'; step.append(panel); }
    panel.innerHTML = `<div class="smart-conditional-head"><div><span>조건별 추가 확인</span><strong>선택 경로에 필요한 항목만 자동 구성했습니다.</strong></div><em>AUTO SET</em></div><div class="smart-conditional-grid">${fields.map((f) => `<label class="inquiry-field smart-conditional-field"><span>${esc(f.label)}</span>${f.options ? `<select name="${esc(f.name)}">${f.options.map((o) => `<option>${esc(o)}</option>`).join('')}</select>` : `<input name="${esc(f.name)}" type="text" maxlength="240">`}<small>필요한 경우 수정할 수 있습니다.</small></label>`).join('')}</div>`;
    fields.forEach((f) => {
      const el = panel.querySelector(`[name="${css(f.name)}"]`); if (!el || !f.value) return;
      if (el.tagName === 'SELECT') { const opt = [...el.options].find((o) => norm(o.textContent) === norm(f.value)); if (opt) el.value = opt.value; }
      else el.value = f.value;
    });
  }

  function summary(c, s) {
    const calc = [c.calculator.heads && `${c.calculator.heads}마리`, c.calculator.ppm && `GABA ${c.calculator.ppm}`, c.calculator.growth && `성장 가정 ${c.calculator.growth}%`, c.calculator.fcr && `FCR 가정 ${c.calculator.fcr}%`, c.calculator.crude && `필요 원료 ${c.calculator.crude}`].filter(Boolean).join(' · ');
    return [START, `- 진입경로: ${c.source}`, `- 바이어 역할: ${c.role || '직접 확인'}`, `- 제품: ${c.product}`, `- 축종: ${c.species || '직접 선택 필요'}`, `- 현재 단계: ${s.stage}`, `- 협업 유형: ${s.collaboration.join(', ')}`, `- 해결 과제: ${s.tasks.join(', ') || '상담 중 확인'}`, `- 핵심 KPI: ${s.kpis.join(', ') || '상담 중 확인'}`, `- 요청자료: ${s.documents.join(', ')}`, calc && `- 계산기 조건: ${calc}`, END].filter(Boolean).join('\n');
  }

  function putSummary(form, text) {
    const el = byName(form, '상세_요청사항'); if (!el) return;
    const old = String(el.value || '').replace(/\[스마트 상담 자동설정\][\s\S]*?\[자동설정 끝\]\s*/g, '').trim();
    el.value = old ? `${text}\n\n${old}` : text; el.dispatchEvent(new Event('input', { bubbles: true }));
  }

  function missing(form) {
    const out = [];
    form.querySelectorAll('[required]').forEach((el) => { if (el.type !== 'hidden' && !(el.type === 'checkbox' ? el.checked : String(el.value || '').trim())) out.push(el.closest('label')?.querySelector('span')?.textContent?.replace(/필수.*$/g, '').trim() || el.name); });
    form.querySelectorAll('[data-required-group]').forEach((g) => { if (!g.querySelector('input:checked')) out.push(g.querySelector('.inquiry-label')?.textContent?.replace(/필수.*$/g, '').trim() || g.dataset.requiredGroup); });
    return [...new Set(out)];
  }

  function renderReview(form, c, s, autoCount) {
    let box = form.querySelector('#smartConsultationReview');
    if (!box) { box = document.createElement('section'); box.id = 'smartConsultationReview'; box.className = 'smart-consultation-review'; (form.querySelector('.inquiry-progress') || form.firstElementChild).after(box); }
    const need = missing(form);
    box.innerHTML = `<div class="smart-review-head"><div><span>SMART CONSULTATION · AUTO SET</span><h3>검토한 조건을 문의에 자동 반영했습니다.</h3><p>남은 필수 정보만 입력한 뒤 협업문의를 보내세요.</p></div><div class="smart-review-count"><strong>${autoCount}</strong><span>자동 설정</span><small>${need.length}개 직접 확인</small></div></div><div class="smart-review-chips"><span><small>제품</small><strong>${esc(c.product)}</strong></span><span><small>역할</small><strong>${esc(c.role || '상담 중 확인')}</strong></span><span><small>축종</small><strong>${esc(c.species || '직접 선택')}</strong></span><span><small>단계</small><strong>${esc(s.stage)}</strong></span></div><div class="smart-review-grid"><div class="smart-review-auto"><strong>자동 설정된 조건</strong><ul><li>협업 유형 · ${esc(s.collaboration.join(', '))}</li><li>현재 과제 · ${esc(s.tasks.join(', ') || '상담 중 확인')}</li><li>평가 KPI · ${esc(s.kpis.join(', ') || '상담 중 확인')}</li><li>요청자료 · ${esc(s.documents.join(', '))}</li></ul></div><div class="smart-review-missing ${need.length ? '' : 'complete'}"><strong>${need.length ? '직접 확인할 필수 정보' : '필수조건 준비 완료'}</strong><p>${(need.length ? need : ['내용 검토', '개인정보 동의', '협업문의 보내기']).slice(0, 6).map((x) => `<span>${esc(x)}</span>`).join('')}</p></div></div><div class="smart-review-actions"><button type="button" class="smart-review-primary" data-smart-focus>${need.length ? '필수 정보부터 입력' : '문의내용 검토하기'} <b>→</b></button><button type="button" class="smart-review-secondary" data-smart-conditions>조건별 자동설정 보기</button></div>`;
    box.querySelector('[data-smart-focus]')?.addEventListener('click', () => { const target = [...form.querySelectorAll('[required]')].find((el) => !el.value && !el.closest('[hidden]')); (target || form).scrollIntoView({ behavior: reduced() ? 'auto' : 'smooth', block: 'center' }); target?.focus(); });
    box.querySelector('[data-smart-conditions]')?.addEventListener('click', () => form.querySelector('#smartConditionalFields')?.scrollIntoView({ behavior: reduced() ? 'auto' : 'smooth', block: 'center' }));
  }

  function apply(source, pack) {
    const form = document.getElementById('businessInquiryForm'); const contact = document.getElementById('contact');
    if (!form || !contact) return;
    const c = currentContext(source, pack); const s = settingsOf(c); const fields = conditionalFields(c, s); let count = 0;
    count += setChecks(form, '협업_유형', s.collaboration); count += setChecks(form, '현재_과제', s.tasks); count += setChecks(form, '핵심_평가지표', s.kpis);
    count += setSelect(form, '주요_축종', c.species) ? 1 : 0; count += setSelect(form, '현재_준비단계', s.stage) ? 1 : 0; count += setSelect(form, '희망_시작시기', s.start) ? 1 : 0;
    count += setInput(form, '국가_지역', c.country) ? 1 : 0; count += setInput(form, '예상_샘플_초도물량', c.quantity) ? 1 : 0; count += setInput(form, '사육규모_사료물량', c.calculator.heads && `${c.calculator.heads}마리`) ? 1 : 0;
    renderConditionals(form, fields); count += fields.length; const text = summary(c, s); putSummary(form, text);
    hidden(form, '스마트상담_버전', '1.0.0'); hidden(form, '스마트상담_진입경로', source); hidden(form, '스마트상담_요청자료', s.documents.join(', ')); hidden(form, '스마트상담_자동설정수', count); hidden(form, '선택제품', c.product); hidden(form, '주문가이드_경로', s.stage);
    try { sessionStorage.setItem(STORE_KEY, JSON.stringify({ at: Date.now(), source, packId: pack?.id || '' })); } catch (_) {}
    renderReview(form, c, s, count); contact.scrollIntoView({ behavior: reduced() ? 'auto' : 'smooth', block: 'start' });
    document.querySelector('.b2b-live-status')?.replaceChildren(document.createTextNode(`${count}개 조건을 자동 설정했습니다. 필수 정보만 확인해 주세요.`));
  }

  function injectCta() {
    const grid = document.querySelector('#b2b-operations .b2b-pack-grid'); if (!grid || grid.parentElement.querySelector('.b2b-smart-cta')) return false;
    const box = document.createElement('div'); box.className = 'b2b-smart-cta'; box.innerHTML = '<div><span>SMART CONSULTATION HANDOFF</span><h3>이미 검토한 조건은 다시 묻지 않습니다.</h3><p>제품·축종·도입단계·과제·KPI·요청자료를 자동 설정하고, 회사명·담당자·이메일 등 꼭 필요한 정보만 직접 입력하도록 정리합니다.</p></div><button type="button" data-smart-consultation>조건 검토 후 상담요청 <b>→</b></button>'; grid.after(box); return true;
  }

  function bind() {
    document.addEventListener('click', (e) => {
      const packButton = e.target.closest('[data-b2b-pack]'); if (packButton) { const pack = packMap.get(packButton.dataset.b2bPack); setTimeout(() => apply('Buyer Deal Room', pack), 120); return; }
      if (e.target.closest('[data-smart-consultation]')) { apply('Buyer Deal Room 조건검토'); return; }
      if (e.target.closest('#visitorStartInquiry')) { setTimeout(() => apply('2분 도입진단 결과'), 80); return; }
      if (e.target.closest('#orderToInquiry')) { setTimeout(() => apply('주문 가이드 결과'), 80); return; }
      if (e.target.closest('a[href="#contact"],button[data-scroll="contact"],.nav-cta')) setTimeout(() => apply('직접 상담요청'), 60);
    }, true);
  }

  async function init() {
    addStyles();
    try { const r = await fetch(DATA_URL, { cache: 'no-store' }); const data = r.ok ? await r.json() : {}; packMap = new Map((data.buyer_packs || []).map((p) => [p.id, p])); } catch (_) {}
    bind();
    if (injectCta()) return;
    const observer = new MutationObserver(() => { if (injectCta()) observer.disconnect(); }); observer.observe(document.documentElement, { childList: true, subtree: true }); setTimeout(() => observer.disconnect(), 12000);
  }

  window.CellpindaSmartConsultation = { prepare: () => apply('직접 상담요청') };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
