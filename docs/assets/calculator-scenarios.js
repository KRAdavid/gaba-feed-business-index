(() => {
  'use strict';

  const DEFAULT_GROWTH_PCT = 3;
  const DEFAULT_FCR_PCT = 2;
  const MAX_SCENARIO_PCT = 20;

  function clampPercent(value, fallback) {
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) return fallback;
    return Math.min(MAX_SCENARIO_PCT, Math.max(0, parsed));
  }

  function percentText(value) {
    const rounded = Math.round(Number(value) * 10) / 10;
    return Number.isInteger(rounded) ? String(rounded) : rounded.toFixed(1);
  }

  function buildControls(inputs) {
    if (document.getElementById('growthImprovementPct')) return;

    inputs.insertAdjacentHTML('beforeend', `
      <div class="calc-field calc-scenario-field">
        <label for="growthImprovementPct">성장 개선 가정 (%)</label>
        <input id="growthImprovementPct" type="number" min="0" max="20" step="0.5" value="${DEFAULT_GROWTH_PCT}" list="growthScenarioPresets" inputmode="decimal" aria-describedby="growthScenarioHelp">
        <datalist id="growthScenarioPresets">
          <option value="0"></option><option value="1"></option><option value="2"></option><option value="3"></option><option value="5"></option><option value="7"></option><option value="10"></option>
        </datalist>
        <small id="growthScenarioHelp" class="scenario-helper">0~20% 범위에서 직접 선택·입력</small>
      </div>
      <div class="calc-field calc-scenario-field">
        <label for="fcrImprovementPct">사료효율 개선 가정 (%)</label>
        <input id="fcrImprovementPct" type="number" min="0" max="20" step="0.5" value="${DEFAULT_FCR_PCT}" list="fcrScenarioPresets" inputmode="decimal" aria-describedby="fcrScenarioHelp">
        <datalist id="fcrScenarioPresets">
          <option value="0"></option><option value="1"></option><option value="2"></option><option value="3"></option><option value="5"></option><option value="7"></option><option value="10"></option>
        </datalist>
        <small id="fcrScenarioHelp" class="scenario-helper">선택값만 사료비 절감 계산에 반영</small>
      </div>`);

    const note = document.createElement('div');
    note.className = 'scenario-assumption-note';
    note.innerHTML = '<strong>사용자 선택 시나리오</strong><span>성장과 사료효율 개선률은 확정 효능이 아니라 비교용 가정입니다. 성장 개선은 판매가·기초 증체량이 없으므로 금액 환산에서 제외하고, 사료효율 선택값만 절감액에 반영합니다.</span>';
    inputs.insertAdjacentElement('afterend', note);
  }

  function calculateSelectableScenario() {
    if (
      typeof speciesModel === 'undefined' ||
      typeof speciesCalc === 'undefined' ||
      typeof headCount === 'undefined' ||
      typeof fmt === 'undefined' ||
      typeof won === 'undefined'
    ) return;

    const growthInput = document.getElementById('growthImprovementPct');
    const fcrInput = document.getElementById('fcrImprovementPct');
    if (!growthInput || !fcrInput) return;

    const d = speciesModel[speciesCalc.value];
    if (!d) return;

    const growthPct = clampPercent(growthInput.value, DEFAULT_GROWTH_PCT);
    const fcrPct = clampPercent(fcrInput.value, DEFAULT_FCR_PCT);
    const heads = Math.max(1, Math.floor(Number(headCount.value) || 1));
    const totalFeedKg = d.dailyFeed * d.days * heads;
    const totalFeedTon = totalFeedKg / 1000;
    const crudeKg = (d.ppm / 0.20) * totalFeedTon / 1000;
    const rawCost = crudeKg * 18000;
    const savedFeedKg = totalFeedKg * (fcrPct / 100);
    const feedSaving = savedFeedKg * d.feedPrice;
    const net = feedSaving - rawCost;
    const growthLabel = growthPct > 0 ? `성장 +${percentText(growthPct)}%` : '성장 개선 미반영';
    const fcrLabel = fcrPct > 0 ? `FCR ${percentText(fcrPct)}% 개선` : 'FCR 개선 미반영';

    growthInput.value = percentText(growthPct);
    fcrInput.value = percentText(fcrPct);

    const summary = document.getElementById('autoSummary');
    if (summary) {
      summary.innerHTML = `<strong>${d.name} ${fmt(heads, 0)}마리</strong> · GABA ${fmt(d.ppm, 0)} mg/kg 사료 · 적용기간 ${fmt(d.days, 0)}일 · 사용자가 선택한 ${growthLabel}, ${fcrLabel} 시나리오입니다.`;
    }

    document.getElementById('autoPpm').textContent = `${fmt(d.ppm, 0)} mg/kg`;
    document.getElementById('doseBasis').textContent = d.evidence;
    document.getElementById('totalFeed').textContent = `${fmt(totalFeedTon, 2)}톤`;
    document.getElementById('feedBasis').textContent = `${fmt(d.dailyFeed, 2)} kg/마리·일 × ${fmt(d.days, 0)}일`;
    document.getElementById('neededCrude').textContent = `${fmt(crudeKg, 2)} kg`;
    document.getElementById('rawCost').textContent = won(rawCost);
    document.getElementById('costPerHead').textContent = `마리당 ${won(rawCost / heads)}`;
    document.getElementById('feedSaving').textContent = won(feedSaving);

    const feedSavingNote = document.getElementById('feedSaving')?.nextElementSibling;
    if (feedSavingNote) feedSavingNote.textContent = `${fcrLabel} 선택값 반영`;

    const netEl = document.getElementById('netBenefit');
    netEl.textContent = `${net >= 0 ? '' : '-'}${won(Math.abs(net))}`;
    netEl.style.color = net >= 0 ? 'var(--green)' : '#a4423b';
    const netCard = netEl.closest('div');
    if (netCard) {
      const label = netCard.querySelector('small');
      const note = netCard.querySelector('span');
      if (label) label.textContent = 'FCR 절감 기준 예상 이익';
      if (note) note.textContent = '사료비 절감 - 도입비 · 성장가치 미포함';
    }

    document.getElementById('effectTitle').textContent = `${d.focus} · 선택 시나리오`;
    document.getElementById('effectText').textContent = `${growthLabel}, ${fcrLabel}`;
    document.getElementById('kpiText').textContent = d.kpi;

    if (typeof lastCalc !== 'undefined') {
      lastCalc = {
        축종: d.name,
        사육마릿수: heads,
        자동_GABA_농도_mg_per_kg: d.ppm,
        성장_개선_가정_pct: growthPct,
        사료효율_FCR_개선_가정_pct: fcrPct,
        일일_사료섭취량_kg_per_head: d.dailyFeed,
        적용기간_일: d.days,
        총_사료량_kg: totalFeedKg,
        필요_가바크루드_kg: crudeKg,
        가바크루드_도입비_원: rawCost,
        예상_사료절감량_kg: savedFeedKg,
        예상_사료비절감_원: feedSaving,
        도입후_예상이익_FCR기준_원: net,
        성장가치_금액반영: '미반영',
        시뮬레이션_가정: `${growthLabel}, ${fcrLabel}`,
        주의사항: '사용자 선택 가정이며 실제 효능과 경제성은 축종별 대조시험으로 확인'
      };
    }
  }

  function init() {
    const calculator = document.getElementById('calculator');
    const panel = calculator?.querySelector('.calc-panel');
    const inputs = panel?.querySelector('.calc-inputs');
    if (!calculator || !panel || !inputs || panel.dataset.selectableScenario === 'true') return;

    panel.dataset.selectableScenario = 'true';
    buildControls(inputs);

    const copy = calculator.querySelector('.calc-copy > p');
    const flow = calculator.querySelector('.calc-flow');
    const disclaimer = panel.querySelector('.calc-disclaimer');
    if (copy) copy.textContent = '축종과 사육규모를 입력한 뒤 성장과 사료효율 개선률을 직접 선택하면, 가바크루드 필요량·도입비·FCR 기준 사료비 절감 시나리오를 비교할 수 있습니다.';
    if (flow) flow.textContent = '축종·규모 선택 → 성장 개선률 선택 → 사료효율 개선률 선택 → GABA 설계량 → 필요 원료·도입비 → FCR 기준 절감액 자동 계산';
    if (disclaimer) disclaimer.textContent = '본 결과는 사용자가 직접 선택한 성장·사료효율 개선률을 적용한 사업성 시뮬레이션입니다. 성장 개선 가치는 판매단가와 기초 증체량이 없어 금액에 포함하지 않으며, 실제 효능·최적 급여량·경제적 결과는 축종별 대조시험으로 확인해야 합니다.';

    const growthInput = document.getElementById('growthImprovementPct');
    const fcrInput = document.getElementById('fcrImprovementPct');
    [growthInput, fcrInput].forEach((input) => {
      input.addEventListener('input', calculateSelectableScenario);
      input.addEventListener('change', calculateSelectableScenario);
      input.addEventListener('blur', calculateSelectableScenario);
    });

    speciesCalc.addEventListener('change', () => window.setTimeout(calculateSelectableScenario, 0));
    headCount.addEventListener('input', () => window.setTimeout(calculateSelectableScenario, 0));

    try { calculateSpeciesEffect = calculateSelectableScenario; } catch (_error) { /* global binding may be protected */ }
    try { window.calculateSpeciesEffect = calculateSelectableScenario; } catch (_error) { /* no-op */ }

    calculateSelectableScenario();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
