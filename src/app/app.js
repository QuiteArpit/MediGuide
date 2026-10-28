/* MediGuide frontend: dependency-free API client and DOM renderer. */
(function () {
  "use strict";

  const params = new URLSearchParams(window.location.search);
  const API_BASE = (params.get("api") || localStorage.getItem("mediguide_api") || "http://127.0.0.1:8000").replace(/\/$/, "");
  const state = { questions: [], answers: {} };
  const $ = (selector) => document.querySelector(selector);
  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" })[char]);

  function showStatus(message) { $("#global-status").textContent = message || ""; }
  function setBusy(button, busy, label) { button.disabled = busy; if (busy) { button.dataset.label = button.textContent; button.textContent = label || "Working…"; } else if (button.dataset.label) button.textContent = button.dataset.label; }

  async function api(path, options = {}) {
    let response;
    try {
      response = await fetch(`${API_BASE}${path}`, { headers: { "Content-Type": "application/json", ...(options.headers || {}) }, ...options });
    } catch (error) {
      throw new Error("The MediGuide API is offline. Start the backend at http://127.0.0.1:8000 and try again.");
    }
    let body;
    try { body = await response.json(); } catch (_) { body = {}; }
    if (!response.ok) {
      const message = body.error?.message || body.error?.details?.[0]?.msg || body.detail || `Request failed (${response.status})`;
      throw new Error(message);
    }
    return body;
  }

  function renderQuestions() {
    const container = $("#questions-container");
    container.innerHTML = state.questions.map((question, index) => {
      const type = (question.answer_type || "").toLowerCase();
      const isNumber = type.includes("number");
      const isMultiple = type.includes("multiple");
      let input;
      if (isNumber && question.question_id !== "Q25") {
        input = `<input class="numeric-input answer-input" type="number" id="${escapeHtml(question.question_id)}" data-question="${escapeHtml(question.question_id)}" ${question.required ? "required" : ""}>`;
      } else if (question.question_id === "Q25") {
        input = `<div class="two-number-grid"><input class="numeric-input answer-input" type="number" min="1" placeholder="Height (cm)" data-question="Q25-height" required><input class="numeric-input answer-input" type="number" min="1" placeholder="Weight (kg)" data-question="Q25-weight" required></div>`;
      } else {
        input = `<div class="options">${(question.options || []).map((option, optionIndex) => `<label class="option"><input type="${isMultiple ? "checkbox" : "radio"}" name="${escapeHtml(question.question_id)}" value="${escapeHtml(option)}" data-question="${escapeHtml(question.question_id)}" ${optionIndex === 0 && !isMultiple && question.required ? "required" : ""}><span>${escapeHtml(option)}</span></label>`).join("")}</div>`;
      }
      return `<article class="question-card ${question.question_id === "Q25" ? "full-width" : ""}"><span class="question-number">Question ${index + 1}</span><p class="question-text">${escapeHtml(question.text)}</p>${question.help_text ? `<p class="help-text">${escapeHtml(question.help_text)}</p>` : ""}${input}</article>`;
    }).join("");
    updateProgress();
  }

  function collectAnswers() {
    const answers = {};
    state.questions.forEach((question) => {
      const inputs = [...document.querySelectorAll(`[data-question="${CSS.escape(question.question_id)}"]`)];
      if (question.question_id === "Q25") {
        const height = document.querySelector('[data-question="Q25-height"]')?.value;
        const weight = document.querySelector('[data-question="Q25-weight"]')?.value;
        if (height && weight) answers.Q25 = [Number(height), Number(weight)];
      } else if ((question.answer_type || "").toLowerCase().includes("multiple")) {
        const values = inputs.filter((input) => input.checked).map((input) => input.value);
        if (values.length) answers[question.question_id] = values;
      } else {
        const input = inputs.find((candidate) => candidate.checked) || inputs[0];
        if (input?.value) answers[question.question_id] = input.type === "number" ? Number(input.value) : input.value;
      }
    });
    return answers;
  }

  function updateProgress() {
    const answered = state.questions.filter((question) => {
      if (question.question_id === "Q25") return Boolean(document.querySelector('[data-question="Q25-height"]')?.value && document.querySelector('[data-question="Q25-weight"]')?.value);
      return [...document.querySelectorAll(`[data-question="${CSS.escape(question.question_id)}"]`)].some((input) => input.checked || input.value);
    }).length;
    const percent = state.questions.length ? Math.round(answered / state.questions.length * 100) : 0;
    $("#screening-progress").textContent = `${answered} of ${state.questions.length} answered`;
    $("#progress-bar").style.width = `${percent}%`;
  }

  function profilePayload() {
    const sodium = $("#sodium-limit").value;
    return {
      heart_condition: $("#profile-heart").checked,
      hypertension: $("#profile-hypertension").checked,
      diabetes: $("#profile-diabetes").checked,
      diet_preference: $("#diet-preference").value,
      ...(sodium ? { custom_sodium_limit_mg: Number(sodium) } : {})
    };
  }

  function renderScreening(result) {
    const emergency = result.care_level === "emergency";
    const ml = result.ml_assessment;
    const score = result.concern_score;
    $("#screening-result").hidden = false;
    $("#screening-result").innerHTML = `<div class="result-card ${emergency ? "emergency-card" : ""}">
      <div class="result-header"><div><p class="eyebrow">${emergency ? "Immediate action" : "Your screening result"}</p><h3>${escapeHtml(result.recommendation)}</h3></div><span class="badge badge-${escapeHtml(result.care_level)}">${escapeHtml(result.care_level.replaceAll("_", " "))}</span></div>
      ${emergency ? `<div class="emergency-copy"><h3>Emergency care is recommended now</h3><p>Call your local emergency number (112/108 in India) or go to the nearest hospital. Do not drive yourself.</p></div>` : ""}
      <div class="result-columns">
        <div class="subcard"><h4>Why this recommendation?</h4><p>${escapeHtml(result.explanation)}</p></div>
        ${score ? `<div class="subcard"><h4>Concern score</h4><div class="risk-number">${escapeHtml(score.score)}</div><p class="muted">${escapeHtml((score.triggered_factors || []).join(" · ") || "Based on the answers provided.")}</p></div>` : ""}
        ${ml ? `<div class="subcard"><h4>Comparative model estimate</h4><div class="risk-number">${Math.round(ml.probability * 100)}%</div><p>${escapeHtml(ml.risk_label)} supplementary estimate</p><ul class="feature-list">${(ml.feature_importances || []).slice(0, 4).map((item) => `<li class="chip">${escapeHtml(item.feature)} · ${Math.round(item.importance * 100)}%</li>`).join("")}</ul><p class="muted">${escapeHtml(ml.safety_note || "")}</p></div>` : ""}
      </div><p class="disclaimer">${escapeHtml(result.disclaimer)}</p>
    </div>`;
    $("#screening-result").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderFood(result) {
    const nutrients = Object.entries(result.nutrient_impact || {});
    $("#food-result").hidden = false;
    $("#food-result").innerHTML = `<div class="subcard">
      <div class="suitability-row"><h4>${escapeHtml(result.food_name)} · ${escapeHtml(result.portion_str)}</h4><span class="badge badge-${escapeHtml(result.suitability)}">${escapeHtml(result.suitability)}</span></div>
      <p>${escapeHtml(result.advice)}</p>
      ${nutrients.map(([name, item]) => `<div class="nutrient-row"><div class="nutrient-label"><span>${escapeHtml(name.replaceAll("_", " "))}</span><strong>${item.value} · ${item.percent_of_daily_limit}%</strong></div><div class="nutrient-bar"><span style="width:${Math.min(item.percent_of_daily_limit, 100)}%"></span></div></div>`).join("")}
      <h4>Healthier alternatives</h4><ul class="chip-list">${(result.healthier_alternatives || []).map((name) => `<li class="chip">${escapeHtml(name)}</li>`).join("") || "<li class=\"muted\">No alternatives listed.</li>"}</ul>
      <p class="disclaimer">${escapeHtml(result.disclaimer)}</p>
    </div>`;
  }

  function renderPlan(result) {
    const totals = result.total_nutrients || {};
    $("#plan-result").hidden = false;
    $("#plan-result").innerHTML = `<div class="meal-grid">${Object.entries(result.meals || {}).map(([meal, entries]) => `<div class="meal-card"><h4>${escapeHtml(meal)}</h4><ul>${entries.map((entry) => `<li><strong>${escapeHtml(entry.food)}</strong> · ${escapeHtml(entry.portion)}</li>`).join("")}</ul></div>`).join("")}</div>
      <div class="totals">${["calories_kcal", "sodium_mg", "saturated_fat_g", "dietary_fiber_g"].map((key) => `<div class="total"><strong>${totals[key] ?? "—"}</strong><small>${escapeHtml(key.replaceAll("_", " "))}</small></div>`).join("")}</div>
      <p class="notice ${result.meets_targets ? "notice-info" : ""}">${result.meets_targets ? "This sample plan is within the configured daily targets." : "This sample plan needs review against the configured daily targets."}</p>
      <ul class="muted">${(result.summary_notes || []).map((note) => `<li>${escapeHtml(note)}</li>`).join("")}</ul><p class="disclaimer">${escapeHtml(result.disclaimer)}</p>`;
  }

  async function loadQuestions() {
    try { const response = await api("/questions"); state.questions = response.questions || []; renderQuestions(); } catch (error) { $("#questions-container").innerHTML = `<div class="loading-card">${escapeHtml(error.message)}</div>`; showStatus(error.message); }
  }

  $("#screening-form").addEventListener("input", updateProgress);
  $("#screening-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = $("#screening-submit");
    const answers = collectAnswers();
    if (!Object.keys(answers).length) { showStatus("Please answer at least one questionnaire item."); return; }
    setBusy(button, true, "Reviewing safely…"); showStatus("");
    try { renderScreening(await api("/screening", { method: "POST", body: JSON.stringify({ answers }) })); } catch (error) { showStatus(error.message); } finally { setBusy(button, false); }
  });
  $("#screening-reset").addEventListener("click", () => { $("#screening-form").reset(); $("#screening-result").hidden = true; updateProgress(); });
  $("#food-query-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = event.submitter; setBusy(button, true, "Checking…");
    try { renderFood(await api("/food-query", { method: "POST", body: JSON.stringify({ query: $("#food-query").value.trim(), portion: $("#food-portion").value.trim(), ...profilePayload() }) })); } catch (error) { showStatus(error.message); } finally { setBusy(button, false); }
  });
  $("#plan-button").addEventListener("click", async () => {
    const button = $("#plan-button"); setBusy(button, true, "Planning…");
    try { renderPlan(await api("/diet-plan", { method: "POST", body: JSON.stringify(profilePayload()) })); } catch (error) { showStatus(error.message); } finally { setBusy(button, false); }
  });
  loadQuestions();
}());
