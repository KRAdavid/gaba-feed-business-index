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
        <small id="fcrScenarioHelp" class="scenario-helper">선택값을 최종 사료량 절감에 반영</small>
      </div>`);

    const note = document.createElement('div');
    note.className = 'scenario-assumption-note';
    note.innerHTML = '<strong>사용자 선택 시나리오</strong><span>ADG 개선은 같은 목표 증체량을 더 짧은 기간에 달성하는 효과로, FCR 개선은 그 후 필요한 사료량을 줄이는 효과로 계산합니다. 두 값은 확정 효능이 아닌 비교용 가정입니다.</span>';
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
    const baselineFeedKg = d.dailyFeed * d.days * heads;
    const adgFeedKg = baselineFeedKg / (1 + growthPct / 100);
    const adgSavedFeedKg = baselineFeedKg - adgFeedKg;
    const fcrSavedFeedKg = adgFeedKg * (fcrPct / 100);
    const improvedFeedKg = adgFeedKg - fcrSavedFeedKg;
    const totalSavedFeedKg = baselineFeedKg - improvedFeedKg;
    const totalFeedTon = baselineFeedKg / 1000;
    const crudeKg = (d.ppm / 0.20) * totalFeedTon / 1000;
    const rawCost = crudeKg * 18000;
    const feedSaving = totalSavedFeedKg * d.feedPrice;
    const net = feedSaving - rawCost;
    const growthLabel = growthPct > 0 ? `성장 +${percentText(growthPct)}%` : '성장 개선 미반영';
    const fcrLabel = fcrPct > 0 ? `FCR ${percentText(fcrPct)}% 개선` : 'FCR 개선 미반영';

    growthInput.value = percentText(growthPct);
    fcrInput.value = percentText(fcrPct);

    const summary = document.getElementById('autoSummary');
    if (summary) {
      summary.innerHTML = `<strong>${d.name} ${fmt(heads, 0)}마리</strong> · GABA ${fmt(d.ppm, 0)} mg/kg 사료 · 적용기간 ${fmt(d.days, 0)}일 · 사용자가 선택한 ${growthLabel}, ${fcrLabel} 시나리오입니다.`;
    }

    document.getElementById('feedUnitPrice').textContent = `${won(d.feedPrice)}/kg`;
    document.getElementById('feedUnitPriceBasis').textContent = `${d.evidence} · 실제 견적 대체`;
    document.getElementById('autoPpm').textContent = `${fmt(d.ppm, 0)} mg/kg`;
    document.getElementById('doseBasis').textContent = d.evidence;
    document.getElementById('neededCrude').textContent = `${fmt(crudeKg, 2)} kg`;
    document.getElementById('rawCost').textContent = won(rawCost);
    document.getElementById('costPerHead').textContent = `18,000원/kg · 마리당 ${won(rawCost / heads)}`;

    const adgDaysSaved = d.days - d.days / (1 + growthPct / 100);
    const improvedDays = d.days - adgDaysSaved;
    const feedSavedPct = baselineFeedKg > 0 ? (totalSavedFeedKg / baselineFeedKg) * 100 : 0;
    const setText = (id, value) => {
      const element = document.getElementById(id);
      if (element) element.textContent = value;
    };
    const baselineFeedCost = baselineFeedKg * d.feedPrice;
    const improvedFeedCost = improvedFeedKg * d.feedPrice;
    const afterTotalCost = improvedFeedCost + rawCost;
    setText('beforeShipDays', `${fmt(d.days, 0)}일`);
    setText('afterShipDays', `${fmt(improvedDays, 1)}일`);
    setText('beforeFeedAmount', `${fmt(baselineFeedKg, 1)} kg`);
    setText('afterFeedAmount', `${fmt(improvedFeedKg, 1)} kg`);
    setText('beforeCrudeCost', '없음');
    setText('afterCrudeCost', `+${won(rawCost)}`);
    setText('beforeTotalCost', won(baselineFeedCost));
    setText('afterTotalCost', won(afterTotalCost));
    setText('compareBenefit', `${net >= 0 ? '절감 ' : '증가 '}${won(Math.abs(net))}`);
    setText('compareBenefitBasis', `출하 -${fmt(adgDaysSaved, 1)}일 · 사료 -${fmt(totalSavedFeedKg, 1)}kg`);
    setText('impactKeySummary', `${growthLabel}로 출하 ${fmt(adgDaysSaved, 1)}일 단축, ${fcrLabel}로 사료 ${fmt(totalSavedFeedKg, 1)}kg 절감. 사료비 절감 ${won(feedSaving)}에서 가바크루드 추가비용 ${won(rawCost)}을 차감한 ${net >= 0 ? '예상 이익' : '예상 손실'}은 ${won(Math.abs(net))}입니다.`);
    const compareDelta = document.getElementById('compareBenefit');
    if (compareDelta) compareDelta.parentElement.classList.toggle('is-negative', net < 0);

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
        예상_출하일수_일: improvedDays,
        예상_출하시기_단축일: adgDaysSaved,
        총_사료량_kg: baselineFeedKg,
        ADG적용_사료량_kg: adgFeedKg,
        ADG로_절감된_사료량_kg: adgSavedFeedKg,
        FCR로_추가절감된_사료량_kg: fcrSavedFeedKg,
        최종_예상사료량_kg: improvedFeedKg,
        총_예상사료절감량_kg: totalSavedFeedKg,
        필요_가바크루드_kg: crudeKg,
        가바크루드_도입비_원: rawCost,
        적용전_사료비_원: baselineFeedCost,
        적용후_사료비_원: improvedFeedCost,
        적용후_총비용_원: afterTotalCost,
        예상_사료절감량_kg: totalSavedFeedKg,
        예상_사료비절감_원: feedSaving,
        도입후_예상이익_총사료절감기준_원: net,
        성장가치_금액반영: '동일 목표 증체량 기준 사료량으로 환산',
        시뮬레이션_가정: `${growthLabel}, ${fcrLabel}`,
        계산가정: 'ADG 적용 후 FCR 절감률을 순차 반영',
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
    if (copy) copy.textContent = '축종과 사육규모를 입력한 뒤 성장과 사료효율 개선률을 직접 선택하면, ADG로 줄어드는 사육기간과 FCR로 추가 절감되는 사료량을 한눈에 비교할 수 있습니다.';
    if (flow) flow.textContent = '축종·규모 선택 → 성장 개선률 선택 → 사료효율 개선률 선택 → 기본 사료량 → ADG 적용 → FCR 적용 → 총 절감량 자동 계산';
    if (disclaimer) disclaimer.textContent = '본 결과는 동일 목표 증체량·동일 일일사료섭취량을 가정해 ADG와 FCR 개선률을 순차 적용한 사업성 시뮬레이션입니다. 개선률은 확정 효능이 아니며, 실제 급여량·효능·경제성은 축종별 대조시험으로 확인해야 합니다.';

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
