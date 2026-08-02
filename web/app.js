(() => {
  "use strict";

  const state = {
    scenario: null,
    items: [],
    visibleItems: [],
    selectedIds: new Set(),
    filters: { query: "", department: "", sensitivity: "" },
    providerMode: "ready",
    connected: false,
    lastRun: null,
    activeResultId: null,
  };

  const SAMPLE_IDS = ["CNT-1001", "CNT-1002", "CNT-1005", "CNT-1006"];
  const $ = (selector) => document.querySelector(selector);

  document.addEventListener("DOMContentLoaded", init);

  async function init() {
    bindStaticEvents();
    setLoading(true);
    try {
      const [scenario, content] = await Promise.all([apiGet("/api/scenario"), apiGet("/api/content")]);
      state.scenario = scenario;
      state.items = content.items || [];
      state.connected = true;
      setHealth("ready", "Mock provider ready", "The customer contract and sample catalog are available.", "DETERMINISTIC · NO CREDENTIALS · SAFE TO INSPECT");
    } catch (_error) {
      state.scenario = window.CONTENT_AI_FALLBACK;
      state.items = window.CONTENT_AI_FALLBACK_ITEMS || [];
      state.connected = false;
      setHealth("fallback", "Browser fallback active", "The Python API is unavailable; the same seeded sample remains inspectable in this browser.", "BROWSER FALLBACK · NO CREDENTIALS · SAFE TO INSPECT");
    }
    setLoading(false);
    renderScenario();
    populateFilters();
    selectSample();
    renderCatalog();
    renderHandoff();
  }

  function bindStaticEvents() {
    document.querySelectorAll("[data-scroll-to]").forEach((button) => {
      button.addEventListener("click", () => {
        const target = document.getElementById(button.dataset.scrollTo);
        if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });
    $("#catalog-search").addEventListener("input", (event) => {
      state.filters.query = event.target.value.trim().toLowerCase();
      renderCatalog();
    });
    $("#department-filter").addEventListener("change", (event) => {
      state.filters.department = event.target.value;
      renderCatalog();
    });
    $("#sensitivity-filter").addEventListener("change", (event) => {
      state.filters.sensitivity = event.target.value;
      renderCatalog();
    });
    $("#reset-filters").addEventListener("click", resetFilters);
    document.querySelectorAll("[data-reset-filters]").forEach((button) => button.addEventListener("click", resetFilters));
    $("#select-sample").addEventListener("click", selectSample);
    $("#select-all").addEventListener("click", selectVisible);
    $("#clear-selection").addEventListener("click", clearSelection);
    $("#run-workflow").addEventListener("click", runWorkflow);
    $("#provider-toggle").addEventListener("click", toggleProvider);
  }

  async function apiGet(path) {
    const response = await fetch(path, { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error(`GET ${path} failed with ${response.status}`);
    return response.json();
  }

  async function apiPost(path, payload) {
    const response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.error || `POST ${path} failed with ${response.status}`);
    return body;
  }

  function setLoading(isLoading) {
    if (isLoading) {
      $("#requirements-list").innerHTML = '<div class="table-loading"><span class="loading-bar"></span><span class="loading-bar short"></span><span class="loading-bar"></span></div>';
      $("#discovery-grid").innerHTML = '<div class="table-loading"><span class="loading-bar"></span><span class="loading-bar short"></span></div>';
    }
  }

  function setHealth(mode, title, copy, footer) {
    const status = $("#health-status");
    const iconClass = mode === "ready" ? "signal-icon-ready" : mode === "degraded" ? "signal-icon-degraded" : "";
    const icon = mode === "ready" ? "✓" : mode === "degraded" ? "!" : "↺";
    status.innerHTML = `<span class="signal-icon ${iconClass}" aria-hidden="true">${icon}</span><div><strong>${escapeHTML(title)}</strong><p>${escapeHTML(copy)}</p></div>`;
    $(".signal-footer").textContent = footer;
    $("#provider-toggle").textContent = mode === "degraded" ? "Restore provider" : "Simulate issue";
    $("#provider-toggle").setAttribute("aria-pressed", String(mode === "degraded"));
  }

  function toggleProvider() {
    if (state.providerMode === "degraded") {
      state.providerMode = "ready";
      setHealth(state.connected ? "ready" : "fallback", state.connected ? "Mock provider ready" : "Browser fallback active", state.connected ? "The customer contract and sample catalog are available." : "The Python API is unavailable; the same seeded sample remains inspectable in this browser.", state.connected ? "DETERMINISTIC · NO CREDENTIALS · SAFE TO INSPECT" : "BROWSER FALLBACK · NO CREDENTIALS · SAFE TO INSPECT");
    } else {
      state.providerMode = "degraded";
      setHealth("degraded", "Provider degraded", "The simulation is paused so an operator can see how an unavailable dependency is surfaced.", "DEGRADED · ACTIONS PAUSED · RECOVERABLE");
      showCalloutError("Provider degraded", "Restore the mock provider before running a workflow. No content action was attempted.");
    }
  }

  function renderScenario() {
    const scenario = state.scenario;
    $("#customer-name").textContent = scenario.customer;
    $("#customer-industry").textContent = scenario.industry;
    const requirements = scenario.requirements || [];
    $("#requirements-count").textContent = requirements.length;
    $("#requirements-list").innerHTML = requirements.map((requirement, index) => `
      <div class="requirement-row">
        <span class="requirement-mark" aria-hidden="true">${String(index + 1).padStart(2, "0")}</span>
        <div><strong>${escapeHTML(requirement.label)}</strong><small>${escapeHTML(requirement.evidence)}</small><span class="requirement-status">${escapeHTML(requirement.status)}</span></div>
      </div>`).join("");

    $("#discovery-grid").innerHTML = (scenario.discovery_signals || []).map((signal, index) => `
      <article class="discovery-card">
        <p class="card-label">SIGNAL 0${index + 1}</p>
        <h3>${escapeHTML(signal.stakeholder)}</h3>
        <p>${escapeHTML(signal.business_problem)}</p>
        <p class="discovery-desired">${escapeHTML(signal.desired_outcome)}</p>
        <div class="chip-row">${(signal.systems || []).map((system) => `<span class="chip">${escapeHTML(system)}</span>`).join("")}</div>
        <div class="chip-row">${(signal.compliance_needs || []).map((need) => `<span class="chip chip-compliance">${escapeHTML(need)}</span>`).join("")}</div>
      </article>`).join("");

    const themes = Object.entries(scenario.themes || {});
    const maxTheme = Math.max(...themes.map(([, count]) => Number(count)), 1);
    $("#theme-bars").innerHTML = themes.map(([theme, count]) => `
      <div class="theme-row"><span>${escapeHTML(theme)}</span><div class="theme-track"><div class="theme-fill" style="width:${Math.max(8, (Number(count) / maxTheme) * 100)}%"></div></div><strong>${escapeHTML(count)}</strong></div>`).join("");
  }

  function populateFilters() {
    const departments = [...new Set(state.items.map((item) => item.department))].sort();
    const sensitivities = [...new Set(state.items.map((item) => item.sensitivity))].sort();
    $("#department-filter").innerHTML = '<option value="">All departments</option>' + departments.map((value) => `<option value="${escapeAttribute(value)}">${escapeHTML(value)}</option>`).join("");
    $("#sensitivity-filter").innerHTML = '<option value="">All levels</option>' + sensitivities.map((value) => `<option value="${escapeAttribute(value)}">${escapeHTML(value)}</option>`).join("");
  }

  function getVisibleItems() {
    return state.items.filter((item) => {
      const haystack = `${item.title} ${item.text} ${item.owner} ${item.department}`.toLowerCase();
      return (!state.filters.query || haystack.includes(state.filters.query))
        && (!state.filters.department || item.department === state.filters.department)
        && (!state.filters.sensitivity || item.sensitivity === state.filters.sensitivity);
    });
  }

  function renderCatalog() {
    state.visibleItems = getVisibleItems();
    $("#catalog-total").textContent = `${state.visibleItems.length} of ${state.items.length} assets visible`;
    $("#selected-count").textContent = `${state.selectedIds.size} selected`;
    const body = $("#catalog-body");
    const empty = $("#catalog-empty");
    if (!state.visibleItems.length) {
      body.innerHTML = "";
      empty.hidden = false;
      return;
    }
    empty.hidden = true;
    body.innerHTML = state.visibleItems.map((item) => {
      const decision = previewDecision(item);
      const selected = state.selectedIds.has(item.item_id);
      return `<tr class="catalog-row ${selected ? "is-selected" : ""}">
        <td class="check-col"><input class="row-check" type="checkbox" data-item-id="${escapeAttribute(item.item_id)}" ${selected ? "checked" : ""} aria-label="Select ${escapeAttribute(item.title)}"></td>
        <td class="item-cell"><strong>${escapeHTML(item.title)}</strong><small>${escapeHTML(item.item_id)} · ${escapeHTML(item.content_type)}</small></td>
        <td class="owner-cell">${escapeHTML(item.owner)}<small>${escapeHTML(item.department)}</small></td>
        <td><span class="sensitivity-pill sensitivity-${escapeAttribute(item.sensitivity)}">${escapeHTML(item.sensitivity)}</span></td>
        <td><span class="lifecycle-pill">${escapeHTML(item.lifecycle_stage.replaceAll("_", " "))}</span></td>
        <td><span class="policy-preview ${decision.disposition === "needs_review" ? "is-review" : decision.disposition === "blocked" ? "is-blocked" : ""}">${escapeHTML(prettyDisposition(decision.disposition))}</span></td>
      </tr>`;
    }).join("");
    body.querySelectorAll("input[data-item-id]").forEach((checkbox) => checkbox.addEventListener("change", (event) => {
      const id = event.target.dataset.itemId;
      if (event.target.checked) state.selectedIds.add(id); else state.selectedIds.delete(id);
      renderCatalog();
    }));
  }

  function selectSample() {
    state.selectedIds = new Set(SAMPLE_IDS.filter((id) => state.items.some((item) => item.item_id === id)));
    renderCatalog();
  }

  function selectVisible() {
    state.visibleItems.forEach((item) => state.selectedIds.add(item.item_id));
    renderCatalog();
  }

  function clearSelection() {
    state.selectedIds.clear();
    renderCatalog();
  }

  function resetFilters() {
    state.filters = { query: "", department: "", sensitivity: "" };
    $("#catalog-search").value = "";
    $("#department-filter").value = "";
    $("#sensitivity-filter").value = "";
    renderCatalog();
  }

  async function runWorkflow() {
    if (!state.selectedIds.size) {
      showCalloutError("Selection required", "Select at least one content item before running the policy workflow.");
      $("#catalog-search").focus();
      return;
    }
    if (state.providerMode === "degraded") {
      showCalloutError("Provider degraded", "Restore the mock provider before running a workflow. No content action was attempted.");
      return;
    }
    const button = $("#run-workflow");
    button.disabled = true;
    button.textContent = "Running decision path…";
    setRunStatus("running", "Processing sample");
    try {
      state.lastRun = state.connected
        ? await apiPost("/api/run", { item_ids: [...state.selectedIds], mode: "simulation" })
        : fallbackRun([...state.selectedIds]);
      renderRun(state.lastRun);
      document.getElementById("stage-ops").scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (error) {
      showCalloutError("Run failed", error.message || "The workflow could not be completed.");
      setRunStatus("error", "Run failed");
    } finally {
      button.disabled = false;
      button.innerHTML = 'Run policy workflow <span aria-hidden="true">↗</span>';
    }
  }

  function renderRun(run) {
    const summary = run.summary || {};
    const status = run.status === "partial" ? "partial" : run.status === "complete" ? "complete" : "error";
    setRunStatus(status, status === "complete" ? `${run.run_id} · complete` : status === "partial" ? `${run.run_id} · partial` : `${run.run_id} · failed`);
    $("#run-summary").innerHTML = `<div class="summary-metrics">
      <div class="summary-metric metric-run"><strong>${escapeHTML(run.run_id || "—")}</strong><span>sample run</span></div>
      <div class="summary-metric metric-auto"><strong>${escapeHTML(summary.auto_process || 0)}</strong><span>proceed automatically</span></div>
      <div class="summary-metric metric-review"><strong>${escapeHTML(summary.needs_review || 0)}</strong><span>needs review</span></div>
      <div class="summary-metric metric-blocked"><strong>${escapeHTML(summary.blocked || 0)}</strong><span>blocked / conflict</span></div>
      <div class="summary-metric"><strong>${escapeHTML(summary.failed || 0)}</strong><span>item failures</span></div>
    </div>`;
    const results = (run.results || []).filter((result) => result.status === "processed");
    const columns = {
      auto_process: { title: "Proceed automatically", subtitle: "Known signals · internal-only action", className: "auto" },
      needs_review: { title: "Needs human review", subtitle: "Sensitive or incomplete context", className: "review" },
      blocked: { title: "Blocked / policy conflict", subtitle: "No link · security escalation", className: "blocked" },
    };
    $("#queue-grid").innerHTML = Object.entries(columns).map(([key, column]) => {
      const matches = results.filter((result) => result.decision && result.decision.disposition === key);
      return `<section class="queue-column queue-column-${column.className}"><div class="queue-header"><div><h3>${column.title}</h3><p>${column.subtitle}</p></div><span class="queue-count">${matches.length}</span></div><div class="queue-cards">${matches.length ? matches.map(decisionCard).join("") : '<div class="queue-empty">No items in this queue.</div>'}</div></section>`;
    }).join("");
    $("#queue-grid").querySelectorAll("[data-result-id]").forEach((card) => card.addEventListener("click", () => {
      state.activeResultId = card.dataset.resultId;
      $("#queue-grid").querySelectorAll(".decision-card").forEach((candidate) => candidate.classList.toggle("is-active", candidate.dataset.resultId === state.activeResultId));
      renderDetail(results.find((result) => result.item_id === state.activeResultId));
    }));
    renderAudit(run.audit_log || []);
    renderEvaluation(run.evaluation);
    if (run.status === "partial") showCalloutError("Partial run recorded", `${summary.processed || 0} item(s) completed; ${summary.failed || 0} item(s) failed without hiding the successful decisions.`);
    else clearCalloutError();
    if (results.length) {
      const first = results.find((result) => result.item_id === state.activeResultId) || results[0];
      state.activeResultId = first.item_id;
      renderDetail(first);
      const activeCard = $("#queue-grid").querySelector(`[data-result-id="${CSS.escape(first.item_id)}"]`);
      if (activeCard) activeCard.classList.add("is-active");
    } else {
      renderDetail(null);
    }
  }

  function decisionCard(result) {
    const decision = result.decision;
    const flags = decision.policy_flags || [];
    return `<button class="decision-card" type="button" data-result-id="${escapeAttribute(result.item_id)}">
      <span class="decision-card-top"><span><strong>${escapeHTML(result.title)}</strong><small>${escapeHTML(result.item_id)} · ${escapeHTML(decision.classification)}</small></span><span class="confidence-dot ${escapeAttribute(decision.confidence)}" title="${escapeAttribute(decision.confidence)} confidence"></span></span>
      <span class="decision-card-meta"><span class="mini-pill">${escapeHTML(decision.confidence)} confidence</span>${flags.slice(0, 2).map((flag) => `<span class="mini-pill flag">${escapeHTML(flag)}</span>`).join("")}</span>
    </button>`;
  }

  function renderDetail(result) {
    const content = $("#detail-content");
    const empty = $("#detail-empty");
    if (!result) {
      $("#detail-id").textContent = "SELECT AN ITEM";
      empty.hidden = false;
      content.hidden = true;
      return;
    }
    const decision = result.decision;
    $("#detail-id").textContent = result.item_id;
    empty.hidden = true;
    content.hidden = false;
    content.innerHTML = `<h3 class="detail-heading">${escapeHTML(result.title)}</h3>
      <p class="detail-subline">${escapeHTML(result.item.department)} / ${escapeHTML(result.item.content_type)} / ${escapeHTML(result.item.sensitivity)} · owned by ${escapeHTML(result.item.owner)}</p>
      <div class="detail-decision-grid"><div class="detail-stat"><span>Route</span><strong>${escapeHTML(decision.classification)}</strong></div><div class="detail-stat"><span>Confidence</span><strong>${escapeHTML(decision.confidence)}</strong></div><div class="detail-stat"><span>Retention</span><strong>${escapeHTML(decision.retention_policy)}</strong></div></div>
      <div class="detail-block"><p class="detail-label">Why this route</p><p>${escapeHTML(decision.rationale)}</p></div>
      <div class="detail-block"><p class="detail-label">Next action</p><p>${escapeHTML(decision.next_action)}</p></div>
      <div class="detail-block"><p class="detail-label">Policy flags</p><div class="detail-flags">${(decision.policy_flags || []).length ? decision.policy_flags.map((flag) => `<span class="detail-flag">${escapeHTML(flag)}</span>`).join("") : '<span class="mini-pill">none detected</span>'}</div></div>`;
  }

  function renderAudit(events) {
    $("#audit-count").textContent = `${events.length} EVENTS`;
    $("#audit-list").innerHTML = events.length ? events.map((event) => `<li class="audit-entry"><span class="audit-marker" aria-hidden="true"></span><div><strong>${escapeHTML(event.action)}</strong><p><b>${escapeHTML(event.item_id)}</b> · ${escapeHTML(event.detail)}</p></div></li>`).join("") : '<li class="audit-empty">No actions recorded yet.</li>';
  }

  function renderEvaluation(evaluation) {
    if (!evaluation) return;
    $("#evaluation-score").textContent = `${evaluation.passed} / ${evaluation.total}`;
    $("#evaluation-score").classList.toggle("is-review", evaluation.status !== "pass");
    $("#evaluation-controls").innerHTML = (evaluation.controls || []).map((control) => `<div class="evaluation-control ${control.passed ? "is-pass" : "is-fail"}"><div class="evaluation-control-top"><strong>${escapeHTML(control.label)}</strong><span class="control-icon" aria-hidden="true">${control.passed ? "✓" : "!"}</span></div><p>${escapeHTML(control.detail)}</p></div>`).join("");
  }

  function renderHandoff() {
    const handoff = state.scenario.handoff || {};
    $("#handoff-grid").innerHTML = (handoff.phases || []).map((phase) => `<article class="handoff-card"><span class="handoff-label">${escapeHTML(phase.label)}</span><h3>${escapeHTML(phase.title)}</h3><p>${escapeHTML(phase.detail)}</p></article>`).join("");
    $("#api-mapping").innerHTML = (handoff.api_mapping || []).map((row) => `<div class="mapping-row"><span class="sample">${escapeHTML(row.sample)}</span><span class="mapped">→ ${escapeHTML(row.real_integration_shape)}</span><span class="owner">${escapeHTML(row.owner)}</span></div>`).join("");
    $("#boundaries").innerHTML = (handoff.boundaries || []).map((boundary) => `<li>${escapeHTML(boundary)}</li>`).join("");
  }

  function setRunStatus(mode, message) {
    const status = $("#run-status");
    status.className = `run-status ${mode === "complete" ? "is-complete" : mode === "partial" ? "is-partial" : mode === "error" ? "is-error" : ""}`;
    status.innerHTML = `<span class="status-dot"></span><span>${escapeHTML(message)}</span>`;
  }

  function showCalloutError(title, message) {
    const callout = $("#run-callout");
    callout.classList.add("is-error");
    callout.querySelector("strong").textContent = title;
    callout.querySelector("p").textContent = message;
  }

  function clearCalloutError() {
    const callout = $("#run-callout");
    callout.classList.remove("is-error");
    callout.querySelector("strong").textContent = "Ready to test the decision path?";
    callout.querySelector("p").textContent = "Select at least one item. The run will apply mock metadata, create an internal link for safe items, and route sensitive or unsafe items to a visible human gate.";
  }

  function previewDecision(item) {
    const text = `${item.title} ${item.text}`.toLowerCase();
    if (["password", "credential", "bypass approval", "production access", "public link", "external contractor"].some((term) => text.includes(term))) return { disposition: "blocked" };
    if (["restricted", "confidential"].includes(item.sensitivity)) return { disposition: "needs_review" };
    return { disposition: "auto_process" };
  }

  function fallbackRun(itemIds) {
    const results = [];
    const audit = [];
    for (const itemId of [...new Set(itemIds)]) {
      const item = state.items.find((candidate) => candidate.item_id === itemId);
      if (!item) {
        results.push({ item_id: itemId, title: "Unknown content item", status: "failed", error: `Unknown content item: ${itemId}`, decision: null, actions: {} });
        continue;
      }
      const decision = fallbackDecision(item);
      audit.push({ action: "metadata.updated", item_id: itemId, detail: `Updated [classification, confidence, disposition, retention_policy, risk_level]` });
      const actions = { metadata_updated: true };
      if (decision.disposition === "auto_process") {
        actions.shared_link = `https://content.example/shared/${hashToken(`${itemId}:internal-workflow`)}`;
        audit.push({ action: "shared_link.created", item_id: itemId, detail: "Audience=internal-workflow" });
      } else {
        actions.approval = { item_id: itemId, title: item.title, approver: decision.approver, status: decision.disposition === "blocked" ? "blocked_pending_review" : "pending_review", reason: decision.rationale };
        audit.push({ action: "approval.routed", item_id: itemId, detail: `Approver=${decision.approver}; Status=${actions.approval.status}; Reason=${decision.rationale}` });
      }
      results.push({ item_id: itemId, title: item.title, status: "processed", item: { department: item.department, content_type: item.content_type, sensitivity: item.sensitivity, lifecycle_stage: item.lifecycle_stage, owner: item.owner }, decision, actions, summary: `${item.title}: ${item.text.split(/\s+/).slice(0, 24).join(" ")}${item.text.split(/\s+/).length > 24 ? "…" : ""}` });
    }
    const processed = results.filter((result) => result.status === "processed");
    const count = (value) => processed.filter((result) => result.decision.disposition === value).length;
    const controls = [
      {id:"sensitive-review",label:"Sensitive content requires review",passed:processed.every((result) => !["restricted","confidential"].includes(result.item.sensitivity) || result.decision.disposition !== "auto_process"),detail:"Confidential and restricted items never receive an automatic link."},
      {id:"unsafe-blocked",label:"Unsafe requests are blocked",passed:processed.filter((result) => result.decision.classification === "security-escalation").every((result) => result.decision.disposition === "blocked"),detail:"Credential, access, and approval-bypass signals stop automatic processing."},
      {id:"explainable-routing",label:"Every route has a reason",passed:processed.every((result) => result.decision.rationale && result.decision.next_action),detail:"Each processed item includes confidence, policy flags, rationale, and next action."},
      {id:"failure-isolation",label:"Item failures stay isolated",passed:results.filter((result) => result.status === "failed").length === 0 || processed.length > 0,detail:"A missing item is reported without hiding successful decisions for the rest of the run."}
    ];
    return { run_id: `RUN-${hashToken([...new Set(itemIds)].join(",")).slice(0, 8).toUpperCase()}`, mode: "simulation", status: results.some((result) => result.status === "failed") ? (processed.length ? "partial" : "failed") : "complete", summary: {selected:itemIds.length,processed:processed.length,failed:results.length-processed.length,auto_process:count("auto_process"),needs_review:count("needs_review"),blocked:count("blocked")},results,evaluation:{status:controls.every((control) => control.passed) ? "pass" : "review",passed:controls.filter((control) => control.passed).length,total:controls.length,controls},audit_log:audit};
  }

  function fallbackDecision(item) {
    const text = `${item.title} ${item.text}`.toLowerCase();
    const flags = [];
    const signals = [];
    const critical = {"credential-exposure":["password","credential","secret","api key"],"approval-bypass":["bypass approval","skip approval","without approval","bypass review"],"unsafe-access-request":["production access","admin access","temporary admin","elevated access"],"external-sharing-risk":["external contractor","external sharing","public link","share broadly"]};
    Object.entries(critical).forEach(([flag, terms]) => { const matches = terms.filter((term) => text.includes(term)); if (matches.length) { flags.push(flag); signals.push(...matches); } });
    if (["unclear","unknown","maybe","tbd","missing context","urgent exception"].some((term) => text.includes(term))) flags.push("ambiguous-request");
    let classification = "business-owner-review";
    if (flags.some((flag) => Object.keys(critical).includes(flag))) classification = "security-escalation";
    else if (text.includes("security") || text.includes("access control") || text.includes("encryption")) classification = "security-review";
    else if (text.includes("invoice") || text.includes("payment")) classification = "finance-automation";
    else if (text.includes("contract") || text.includes("msa")) classification = "legal-review";
    else if (text.includes("employee") || text.includes("compensation")) classification = "hr-confidential";
    const blocked = classification === "security-escalation";
    const review = !blocked && (flags.includes("ambiguous-request") || ["restricted","confidential"].includes(item.sensitivity));
    const disposition = blocked ? "blocked" : review ? "needs_review" : "auto_process";
    const approvers = {Legal:"legal-ops@example.com",Finance:"ap-controller@example.com",People:"people-ops@example.com",Security:"security-ops@example.com"};
    return {classification,retention_policy:{"legal-review":"contract-lifecycle","finance-automation":"7-year-finance","hr-confidential":"employee-record","security-review":"security-questionnaire","security-escalation":"security-exception","business-owner-review":"standard-business"}[classification],confidence:blocked ? "high" : review ? "medium" : "high",disposition,risk_level:blocked ? "high" : review ? "medium" : "low",approver:classification === "security-escalation" ? "security-ops@example.com" : (approvers[item.department] || `${item.owner.toLowerCase().replaceAll(" ", ".")}@example.com`),rationale:blocked ? "Policy engine detected a potentially unsafe access or sharing request; no link or automatic action is allowed." : review ? "The workflow can classify this item, but sensitivity or incomplete context requires a human checkpoint before handoff." : "Known content signals and an internal sensitivity level meet the demo policy for automatic metadata enrichment.",next_action:blocked ? "Security owner must validate the exception and remove any credential or access-risk language." : review ? "Route the approval packet to the mapped owner, then apply the retention policy after review." : "Apply metadata and create an internal-only link for the configured workflow audience.",link_policy:blocked ? "no_link" : review ? "restricted_link_after_approval" : "internal_only",policy_flags:[...new Set([...flags,...(item.sensitivity === "restricted" ? ["restricted-content"] : item.sensitivity === "confidential" ? ["confidential-content"] : [])])],detected_signals:[...new Set(signals)]};
  }

  function hashToken(value) {
    let hash = 0;
    for (let index = 0; index < value.length; index += 1) hash = ((hash << 5) - hash + value.charCodeAt(index)) | 0;
    return Math.abs(hash).toString(16).padStart(12, "0");
  }

  function prettyDisposition(value) {
    return {auto_process: "automatic", needs_review: "human review", blocked: "blocked"}[value] || value;
  }

  function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, (character) => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[character]));
  }

  function escapeAttribute(value) {
    return escapeHTML(value).replace(/`/g, "&#96;");
  }
})();
