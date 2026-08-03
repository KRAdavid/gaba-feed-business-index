(() => {
  "use strict";

  const state = { data: null, review: "all", category: "all", query: "", visible: 8 };
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const escapeHTML = (value = "") => String(value).replace(/[&<>'"]/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"})[char]);
  const safeURL = (value = "") => /^https?:\/\//i.test(value) || /^downloads\//.test(value) ? value : "#";
  const formatNumber = value => new Intl.NumberFormat("ko-KR", { maximumFractionDigits: 1 }).format(value);
  const formatDate = value => {
    if (!value) return "날짜 미상";
    const date = new Date(`${value}T00:00:00Z`);
    return Number.isNaN(date.getTime()) ? value : new Intl.DateTimeFormat("ko-KR", { year: "numeric", month: "short", day: "numeric", timeZone: "Asia/Seoul" }).format(date);
  };
  const formatTimestamp = value => {
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? value : new Intl.DateTimeFormat("ko-KR", { year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", timeZone: "Asia/Seoul" }).format(date);
  };
  const sourceLabel = source => ({ mafra_rss: "농림축산식품부", europe_pmc: "Europe PMC", world_bank_pink_sheet: "세계은행 원료 가격", "all-live-sources": "전체 공개 자료" })[source] || source;
  const stageLabel = stage => ({ EXPLORE: "탐색 단계", VALIDATE: "검증 단계", PILOT: "현장 시험 단계", SCALE: "사업 확대 단계", READY: "투자·계약 검토 단계" })[stage] || stage;

  function renderHero(data) {
    const { readiness, meta } = data;
    $("#hero-subtitle").textContent = data.subtitle;
    $("#hero-score").textContent = readiness.score;
    $("#score-ring").style.setProperty("--score", readiness.score);
    $("#hero-stage").textContent = stageLabel(readiness.stage);
    $("#hero-stage-description").textContent = readiness.stage_description;
    $("#freshness").textContent = `기준 ${formatTimestamp(meta.generated_at)} · ${meta.next_scheduled_refresh} 자동 갱신`;
  }

  function renderSummary(data) {
    const cards = [
      ["사업 준비도", `${data.summary.readiness_score}/100`, "원문 검토를 마친 근거만 반영"],
      ["남은 핵심 검증", `${data.summary.critical_open_gates}개`, "4개를 모두 확인한 뒤 사업 확대 검토"],
      ["검토를 마친 자료", `${data.summary.reviewed_signals}건`, "정책·연구·내부 자료"],
      ["검토를 기다리는 자료", `${data.summary.auto_signals_waiting_review}건`, "자동 수집 · 점수에 반영하지 않음"]
    ];
    $("#summary-grid").innerHTML = cards.map(([label, value, note]) => `<article class="summary-card"><span>${escapeHTML(label)}</span><strong>${escapeHTML(value)}</strong><p>${escapeHTML(note)}</p></article>`).join("");
  }

  function renderReadiness(data) {
    $("#readiness-rule").textContent = data.readiness.scoring_rule;
    $("#decision-title").textContent = `${stageLabel(data.readiness.stage)} · ${data.readiness.score}점`;
    $("#decision-copy").textContent = data.decision;
    $("#lowest-dimension").textContent = data.summary.lowest_dimension;
    $("#dimension-list").innerHTML = data.readiness.dimensions.map(row => {
      const percent = Math.round(row.score / row.max_score * 100);
      return `<div class="dimension-row">
        <div class="dimension-head"><strong>${escapeHTML(row.name)}</strong><span>${row.score} / ${row.max_score} · ${escapeHTML(row.status)}</span></div>
        <div class="dimension-track"><div class="dimension-fill" style="width:${percent}%"></div></div>
        <div class="dimension-detail"><span>현재: ${escapeHTML(row.evidence)}</span><span>다음: ${escapeHTML(row.next_evidence)}</span></div>
      </div>`;
    }).join("");
  }

  function renderGates(gates) {
    $("#gate-grid").innerHTML = gates.map((gate, index) => `<article class="gate-card" data-number="0${index + 1}">
      <div class="gate-top"><h3>${escapeHTML(gate.name)}</h3><span class="status-pending">${gate.status === "OPEN" ? "검증 필요" : gate.status === "DONE" ? "검증 완료" : escapeHTML(gate.status)}</span></div>
      <p class="gate-question">${escapeHTML(gate.question)}</p>
      <div class="gate-evidence"><div><small>완료 조건</small><p>${escapeHTML(gate.unlock_evidence)}</p></div><div><small>중단 기준</small><p>${escapeHTML(gate.stop_rule)}</p></div></div>
    </article>`).join("");
  }

  function signalRows() {
    const query = state.query.trim().toLocaleLowerCase("ko-KR");
    return state.data.signals.filter(row => {
      const reviewMatch = state.review === "all" || row.review_status === state.review;
      const categoryMatch = state.category === "all" || row.category === state.category;
      const queryMatch = !query || `${row.title} ${row.source_name} ${row.summary || ""}`.toLocaleLowerCase("ko-KR").includes(query);
      return reviewMatch && categoryMatch && queryMatch;
    });
  }

  function renderSignals() {
    const rows = signalRows();
    const visible = rows.slice(0, state.visible);
    $("#signal-count").textContent = `${rows.length}건`;
    $("#signal-list").innerHTML = visible.length ? visible.map(row => {
      const reviewed = row.review_status === "reviewed";
      const cls = reviewed ? "reviewed" : "auto";
      const label = reviewed ? "검토 완료" : "검토 대기";
      return `<article class="signal-item">
        <div class="signal-date">${escapeHTML(formatDate(row.date))}<b class="${cls}">${label}</b></div>
        <div class="signal-main"><h3>${escapeHTML(row.title)}</h3><p class="source">${escapeHTML(row.category)} · ${escapeHTML(row.source_name)} · ${escapeHTML(row.source_quality || "")}</p>
          <details><summary>판단 메모 보기</summary><div class="signal-detail">
            <div><small>무엇이 바뀌었나</small><p>${escapeHTML(row.summary || "원문 확인이 필요합니다.")}</p></div>
            <div><small>현재 판단</small><p>${escapeHTML(row.judgment || "검토 대기")}</p></div>
            <div><small>다음에 할 일</small><p>${escapeHTML(row.action || "담당자가 원문을 확인한 뒤 정합니다.")}</p></div>
          </div></details>
        </div>
        <a class="signal-link" href="${escapeHTML(safeURL(row.url))}" target="_blank" rel="noopener noreferrer" aria-label="${escapeHTML(row.title)} 원문 열기">↗</a>
      </article>`;
    }).join("") : `<div class="empty-state">조건에 맞는 자료가 없습니다.</div>`;
    $("#signal-more").hidden = visible.length >= rows.length;
  }

  function setupSignalFilters(data) {
    const categories = [...new Set(data.signals.map(row => row.category).filter(Boolean))].sort((a, b) => a.localeCompare(b, "ko"));
    $("#category-filter").insertAdjacentHTML("beforeend", categories.map(value => `<option value="${escapeHTML(value)}">${escapeHTML(value)}</option>`).join(""));
    $("#review-filter").addEventListener("click", event => {
      const button = event.target.closest("button[data-review]");
      if (!button) return;
      state.review = button.dataset.review;
      state.visible = 8;
      $$("button", $("#review-filter")).forEach(item => item.classList.toggle("active", item === button));
      renderSignals();
    });
    $("#category-filter").addEventListener("change", event => { state.category = event.target.value; state.visible = 8; renderSignals(); });
    $("#signal-search").addEventListener("input", event => { state.query = event.target.value; state.visible = 8; renderSignals(); });
    $("#signal-more").addEventListener("click", () => { state.visible += 8; renderSignals(); });
  }

  function sparkline(points) {
    if (!Array.isArray(points) || points.length < 2) return "";
    const values = points.map(p => Number(p.value)).filter(Number.isFinite);
    const min = Math.min(...values), max = Math.max(...values), range = max - min || 1;
    const coords = values.map((value, index) => `${(index / (values.length - 1) * 100).toFixed(2)},${(92 - (value - min) / range * 76).toFixed(2)}`).join(" ");
    return `<svg class="sparkline" viewBox="0 0 100 100" preserveAspectRatio="none" role="img" aria-label="최근 가격 추세"><defs><linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3f8069" stop-opacity=".28"/><stop offset="1" stop-color="#3f8069" stop-opacity="0"/></linearGradient></defs><polygon points="0,100 ${coords} 100,100" fill="url(#area)"/><polyline points="${coords}" fill="none" stroke="#3f8069" stroke-width="2" vector-effect="non-scaling-stroke"/></svg>`;
  }

  function renderMarket(data) {
    const rows = Object.values(data.market || {}).filter(row => row && Array.isArray(row.points) && row.points.length);
    if (!rows.length) {
      const failed = (data.automation.source_health || []).filter(row => row.source === "world_bank_pink_sheet" && row.status !== "ok");
      $("#market-grid").innerHTML = `<div class="market-unavailable"><strong>새 원료 가격을 확인하고 있습니다.</strong>국제 원료 가격 자료를 받는 데 시간이 걸리고 있습니다.${failed.length ? ` ${failed.map(row => escapeHTML(sourceLabel(row.source))).join(", ")}에서 마지막으로 받은 자료를 확인하고 있습니다.` : ""} 새 값이 확인될 때까지 기존 자료를 유지합니다.</div>`;
      return;
    }
    $("#market-grid").innerHTML = rows.map(row => `<article class="market-card">
      <div class="market-head"><div><span>${escapeHTML(row.latest_date || "")}</span><h3>${escapeHTML(row.name)}</h3></div><div class="market-value"><strong>${formatNumber(row.latest)}</strong><small>${escapeHTML(row.unit)}</small></div></div>
      ${sparkline(row.points)}
      <div class="market-foot"><span>전월 ${row.mom_pct == null ? "–" : `${row.mom_pct > 0 ? "+" : ""}${formatNumber(row.mom_pct)}%`} · 전년 ${row.yoy_pct == null ? "–" : `${row.yoy_pct > 0 ? "+" : ""}${formatNumber(row.yoy_pct)}%`}</span><a href="${escapeHTML(safeURL(row.source_url))}" target="_blank" rel="noopener noreferrer">원문 ↗</a></div>
    </article>`).join("");
  }

  function renderAssumptions(rows) {
    $("#assumption-table tbody").innerHTML = rows.map(row => `<tr><td>${escapeHTML(row.metric)}</td><td>${escapeHTML(row.value)}</td><td><span class="state-badge">${escapeHTML(row.state)}</span></td><td>${escapeHTML(row.formula)}</td><td>${escapeHTML(row.unlock)}</td></tr>`).join("");
  }

  function renderRoadmap(rows) {
    $("#roadmap-list").innerHTML = rows.map(row => `<article class="roadmap-card"><span class="window">${escapeHTML(row.window)}</span><h3>${escapeHTML(row.theme)}</h3><ul>${row.actions.map(action => `<li>${escapeHTML(action)}</li>`).join("")}</ul></article>`).join("");
  }

  function renderHealth(data) {
    const rows = data.automation.source_health || [];
    $("#source-health").innerHTML = rows.map(row => `<div class="health-row"><div><strong>${escapeHTML(sourceLabel(row.source))}</strong><small>${row.item_count}건 · ${escapeHTML(formatTimestamp(row.fetched_at))}</small></div><span class="health-status ${escapeHTML(row.status)}">${row.status === "ok" ? "정상" : row.status === "offline" ? "연결 안 됨" : "이전 자료 사용"}</span></div>`).join("");
  }

  function renderDownloads(rows) {
    const descriptions = { XLSX: "근거 목록·점수·가정·90일 실행계획", PPTX: "사료업체·투자자 미팅용 발표자료", MD: "업데이트 규칙·검토 절차·담당 업무" };
    $("#download-grid").innerHTML = rows.map(row => `<a class="download-card" href="${escapeHTML(safeURL(row.file))}" download><small>${escapeHTML(row.type)}</small><strong>${escapeHTML(row.name)}</strong><p>${escapeHTML(descriptions[row.type] || "공개 운영 자료")}</p><span>다운로드 ↓</span></a>`).join("");
  }

  function renderAppendix(data) {
    $("#glossary-list").innerHTML = data.glossary.map(row => `<details><summary>${escapeHTML(row.term)}</summary><p><strong>쉬운 뜻:</strong> ${escapeHTML(row.plain)}<br><strong>이 인덱스에서:</strong> ${escapeHTML(row.use)}</p></details>`).join("");
    $("#source-list").innerHTML = data.source_catalog.map(row => `<div class="source-item"><div><strong>${escapeHTML(row.name)}</strong><small>${escapeHTML(row.organization)} · ${escapeHTML(row.cadence)}</small></div><a href="${escapeHTML(safeURL(row.url))}" target="_blank" rel="noopener noreferrer">원문 ↗</a></div>`).join("");
    $("#disclaimer-copy").textContent = data.disclaimer;
  }

  function render(data) {
    state.data = data;
    renderHero(data);
    renderSummary(data);
    renderReadiness(data);
    renderGates(data.critical_gates);
    setupSignalFilters(data);
    renderSignals();
    renderMarket(data);
    renderAssumptions(data.assumptions);
    renderRoadmap(data.roadmap);
    renderHealth(data);
    renderDownloads(data.downloads);
    renderAppendix(data);
  }

  async function init() {
    try {
      const response = await fetch("data/index.json", { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      render(await response.json());
    } catch (error) {
      const box = $("#fatal-error");
      box.hidden = false;
      box.innerHTML = `<strong>인덱스 데이터를 불러오지 못했습니다.</strong><br>잠시 후 새로고침해 주세요. 로컬 파일이라면 docs 폴더를 웹서버로 열어야 합니다. (${escapeHTML(error.message)})`;
      $("#freshness").textContent = "데이터 연결 실패";
    }
  }

  init();
})();
