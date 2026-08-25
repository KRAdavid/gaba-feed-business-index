(() => {
  'use strict';

  const DATA_URL = 'data/reproduction_evidence.json';

  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;').replaceAll("'", '&#039;');
  }

  function ensureStyle() {
    if (document.querySelector('link[data-reproduction-session]')) return;
    const link = document.createElement('link');
    link.rel = 'stylesheet'; link.href = 'assets/reproduction-session.css';
    link.dataset.reproductionSession = 'v1'; document.head.append(link);
  }

  function list(items) {
    return (items || []).map((item) => `<li>${escapeHtml(item)}</li>`).join('');
  }

  function build(data) {
    const evidence = data.evidence || [];
    const primary = evidence.find((item) => item.id === 'gaba-sow-pubmed-36230278');
    const manual = evidence.find((item) => item.id === 'msd-pig-abortion');
    const gilt = evidence.find((item) => item.id === 'gaba-gilt-pmc10781436');
    return `
      <section class="reproduction-session" id="reproduction-session">
        <div class="container">
          <div class="section-title left">
            <span class="product-label">REPRODUCTION &amp; PREGNANCY-LOSS SESSION</span>
            <h2>유사산 비율 개선은<br>원인 분해부터 시작합니다.</h2>
            <p class="reproduction-session-lead"><strong>GABA를 넣으면 유사산이 줄어든다</strong>고 단정하지 않습니다. 번식실패의 원인을 감염·고온·사료·영양·관리로 나누고, GABA는 스트레스·항산화·태반 관련 지표를 포함한 대조시험으로 검증하는 세션입니다.</p>
            <div class="repro-alert"><strong>근거 수준 안내:</strong> 현재 공개된 GABA 임신돈 연구는 유사산율 직접 개선을 입증하지 않았습니다. 아래 내용은 진단·관리 기준과 제한적인 생리·번식 탐색근거를 연결한 파일럿 설계안입니다.</div>
          </div>
          <div class="repro-grid">
            <article class="repro-card"><span class="eyebrow">01 · DEFINE THE LOSS</span><h3>유사산을 한 숫자로 묶지 않기</h3><p>발생 시점과 결과를 구분해야 원인과 개선효과를 분리할 수 있습니다.</p><ul>${list(['유사산·임신손실·재발정', '사산·미라·허약자돈', '분만율·총산자수·생존산자수'])}</ul></article>
            <article class="repro-card"><span class="eyebrow">02 · CONTROL THE CAUSES</span><h3>감염·고온·사료를 먼저 통제</h3><p>번식실패는 다원인성입니다. 원인검사와 농장관리 기록 없이 제품효과를 해석하지 않습니다.</p><ul>${list(['PRRSV·PPV·Leptospira 등 진단', '곰팡이독소·음수·사료 점검', '고온·환기·밀사·백신·산차 기록'])}</ul></article>
            <article class="repro-card"><span class="eyebrow">03 · TEST THE PATHWAY</span><h3>GABA는 파일럿 지표로 확인</h3><p>번식성적뿐 아니라 사료섭취·산화스트레스·태반·자돈 건강을 함께 측정합니다.</p><ul>${list(['대조군·군집 단위 비교', 'SOD·GSH-Px·MDA·cortisol', 'IUGR·초유·허약자돈 지표'])}</ul></article>
          </div>
          <div class="repro-panel"><div class="repro-panel-head"><h3>파일럿에서 반드시 남길 KPI</h3><p>권장량이 아닌 시험설계용 측정 프레임</p></div><div class="repro-kpis"><div class="repro-kpi"><strong>Primary</strong><span>임신 확인 대비 유사산·임신손실률 · 분만율 · 재발정률</span></div><div class="repro-kpi"><strong>Litter outcome</strong><span>총산자수 · 생존산자수 · 사산 · 미라 · 허약자돈 · IUGR</span></div><div class="repro-kpi"><strong>Mechanism &amp; safety</strong><span>섭취량 · 체온·호흡수 · BCS · cortisol · SOD/GSH-Px/MDA</span></div></div></div>
          <div class="repro-evidence"><article class="repro-evidence-card"><span class="repro-status">수의학 원인·진단 기준</span><h3>왜 원인 분해가 먼저인가</h3><ul><li>${escapeHtml(manual?.finding || '')}</li><li><a href="${escapeHtml(manual?.url || '#')}" target="_blank" rel="noreferrer">MSD Veterinary Manual 원문 확인 ↗</a></li></ul></article><article class="repro-evidence-card"><span class="repro-status">GABA 직접근거 · 제한적</span><h3>현재 GABA 연구가 말하는 범위</h3><ul><li>${escapeHtml(primary?.finding || '')}</li><li>${escapeHtml(gilt?.finding || '')}</li><li><a href="${escapeHtml(primary?.url || '#')}" target="_blank" rel="noreferrer">PubMed 원문 ↗</a> · <a href="${escapeHtml(gilt?.url || '#')}" target="_blank" rel="noreferrer">PMC 원문 ↗</a></li></ul></article></div>
          <p class="repro-session-note">이 세션은 제품 효능·유사산 감소를 보장하지 않습니다. 수의사·영양전문가와 질병진단, 사료·음수·환경 점검, 대조군·중단기준·통계계획을 확정한 뒤 파일럿을 진행하세요. 근거 데이터 기준일: ${escapeHtml(data.updated_at || '')}</p>
        </div>
      </section>`;
  }

  function addNavShortcut() {
    const nav = document.getElementById('nav');
    if (!nav || nav.querySelector('[data-reproduction-session-nav]')) return;
    const button = document.createElement('button');
    button.type = 'button'; button.textContent = '유사산 세션';
    button.dataset.reproductionSessionNav = 'true';
    const calculatorButton = nav.querySelector('[data-scroll="calculator"]');
    if (calculatorButton) calculatorButton.before(button);
    else nav.append(button);
    button.addEventListener('click', () => document.getElementById('reproduction-session')?.scrollIntoView({ behavior: 'smooth' }));
  }

  async function init() {
    if (document.getElementById('reproduction-session')) return;
    ensureStyle();
    try {
      const response = await fetch(DATA_URL, { cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      const anchor = document.getElementById('evidence') || document.querySelector('.evidence-section');
      if (!anchor) return;
      anchor.insertAdjacentHTML('afterend', build(data));
      addNavShortcut();
    } catch (error) {
      console.warn('Reproduction evidence session unavailable', error);
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
