// ═══════════════════════════════════════════════════════
// TrustWise — Premium Frontend JavaScript
// ═══════════════════════════════════════════════════════

document.addEventListener("DOMContentLoaded", () => {
  loadSystemStatus();
  loadPlans();
  setupFormHandler();
  setupChipHandler();
  setupModalHandler();
  setupClearHandler();
  setupRefreshHandler();
});

// ─── Toast Notification System ─────────────────────────

function showToast(message, type = "info") {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;

  const icons = { error: "✖", success: "✔", info: "ℹ" };
  toast.innerHTML = `<span>${icons[type] || icons.info}</span> <span>${escapeHtml(message)}</span>`;

  container.appendChild(toast);

  // Auto-dismiss
  setTimeout(() => {
    toast.classList.add("toast-exit");
    toast.addEventListener("animationend", () => toast.remove());
  }, 4500);
}

// ─── System Status ─────────────────────────────────────

async function loadSystemStatus() {
  const indicator = document.getElementById("statusIndicator");
  const statusText = indicator.querySelector(".status-text");
  const statusDot = indicator.querySelector(".status-dot");

  try {
    const response = await fetch("/api/status");
    const data = await response.json();

    if (data.success) {
      const s = data.status;
      if (s.has_api_key) {
        statusText.textContent = `${s.llm_provider} · ${s.llm_model}`;
        statusDot.style.background = "var(--emerald)";
        statusDot.style.boxShadow = "0 0 8px var(--emerald-glow)";
      } else {
        statusText.textContent = "Mock Mode";
        statusDot.style.background = "var(--amber)";
        statusDot.style.boxShadow = "0 0 8px var(--amber-glow)";
      }
    }
  } catch (error) {
    console.error("Failed to load status:", error);
    statusText.textContent = "Offline";
    statusDot.style.background = "var(--rose)";
    statusDot.style.boxShadow = "0 0 8px var(--rose-glow)";
  }
}

// ─── Form Handler ──────────────────────────────────────

function setupFormHandler() {
  const form = document.getElementById("queryForm");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    await submitQuery();
  });
}

// ─── Chip (Example Query) Handler ──────────────────────

function setupChipHandler() {
  document.querySelectorAll(".chip[data-query]").forEach((chip) => {
    chip.addEventListener("click", () => {
      const q = chip.getAttribute("data-query");
      const input = document.getElementById("queryInput");
      input.value = q;
      input.focus();

      // Visual feedback
      chip.style.transform = "scale(.95)";
      setTimeout(() => (chip.style.transform = ""), 150);
    });
  });
}

// ─── Modal Handler ─────────────────────────────────────

function setupModalHandler() {
  const overlay = document.getElementById("planModal");
  const closeBtn = document.getElementById("modalCloseBtn");

  closeBtn.addEventListener("click", closeModal);
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeModal();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
  });
}

function openModal(title, bodyHtml) {
  document.getElementById("modalTitle").textContent = title;
  document.getElementById("modalBody").innerHTML = bodyHtml;
  document.getElementById("planModal").style.display = "flex";
  document.body.style.overflow = "hidden";
}

function closeModal() {
  const modal = document.getElementById("planModal");
  modal.style.display = "none";
  document.body.style.overflow = "";
}

// ─── Clear & Refresh Handlers ──────────────────────────

function setupClearHandler() {
  document.getElementById("clearResultsBtn").addEventListener("click", () => {
    document.getElementById("resultsSection").style.display = "none";
    document.getElementById("queryInput").value = "";
  });
}

function setupRefreshHandler() {
  document.getElementById("refreshPlansBtn").addEventListener("click", () => {
    loadPlans();
    showToast("Plans refreshed", "success");
  });
}

// ─── Submit Query ──────────────────────────────────────

async function submitQuery() {
  const queryInput = document.getElementById("queryInput");
  const query = queryInput.value.trim();

  if (!query) {
    showToast("Please enter a research query.", "error");
    return;
  }

  showLoading();

  const submitBtn = document.getElementById("submitBtn");
  submitBtn.disabled = true;
  submitBtn.querySelector(".btn-text").textContent = "Processing…";

  try {
    const response = await fetch("/api/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });

    const data = await response.json();

    if (data.success) {
      displayResults(data);
      loadPlans();
      showToast("Query executed successfully!", "success");
    } else {
      showToast(data.error || "Failed to process query", "error");
    }
  } catch (error) {
    console.error("Query submission failed:", error);
    showToast("Network error: " + error.message, "error");
  } finally {
    hideLoading();
    submitBtn.disabled = false;
    submitBtn.querySelector(".btn-text").textContent = "Generate Plan & Execute";
  }
}

// ─── Display Results ───────────────────────────────────

function displayResults(data) {
  const resultsSection = document.getElementById("resultsSection");
  resultsSection.style.display = "block";
  resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });

  displayPlanSummary(data.plan);
  displayExecutionSummary(data.execution);
  displayTaskResults(data.results);
}

function displayPlanSummary(plan) {
  const el = document.getElementById("planSummary");

  const renderList = (items) => {
    if (!items) return "—";
    if (Array.isArray(items)) {
      return items
        .map((d) => `<span class="chip" style="cursor:default;">${escapeHtml(d)}</span>`)
        .join(" ");
    }
    return escapeHtml(String(items));
  };

  el.innerHTML = `
    <h3>📋 Execution Plan</h3>
    <div class="plan-detail">
      <div class="plan-item">
        <div class="plan-item-label">Goal</div>
        <div class="plan-item-value">${escapeHtml(plan.goal)}</div>
      </div>
      <div class="plan-item">
        <div class="plan-item-label">Domains</div>
        <div class="plan-item-value">${renderList(plan.domains)}</div>
      </div>
      <div class="plan-item">
        <div class="plan-item-label">Time Range</div>
        <div class="plan-item-value">${escapeHtml(plan.time_range)}</div>
      </div>
      <div class="plan-item">
        <div class="plan-item-label">Sources</div>
        <div class="plan-item-value">${renderList(plan.sources)}</div>
      </div>
      <div class="plan-item">
        <div class="plan-item-label">Total Tasks</div>
        <div class="plan-item-value" style="font-size:1.3rem; font-weight:700; color:var(--accent);">
          ${plan.total_tasks}
        </div>
      </div>
    </div>
  `;
}

function displayExecutionSummary(execution) {
  document.getElementById("executionSummary").innerHTML = `
    <div class="stat-card web">
      <div class="stat-value">${execution.web_tasks}</div>
      <div class="stat-label">Web Tasks</div>
    </div>
    <div class="stat-card paper">
      <div class="stat-value">${execution.paper_tasks}</div>
      <div class="stat-label">Research Tasks</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">${execution.total_results}</div>
      <div class="stat-label">Total Results</div>
    </div>
    <div class="stat-card success">
      <div class="stat-value">${execution.successful}</div>
      <div class="stat-label">Successful</div>
    </div>
  `;
}

function displayTaskResults(results) {
  const el = document.getElementById("taskResults");

  if (!results || results.length === 0) {
    el.innerHTML = '<p class="text-muted text-center">No results available</p>';
    return;
  }

  el.innerHTML = results
    .map((result, i) => {
      const statusClass = result.status || "unknown";
      const statusText = result.status || "Unknown";
      const agentIcon = result.agent === "web_agent" ? "🌐" : "📚";
      let dataHtml = "";

      if (result.data && result.data.length > 0) {
        if (result.agent === "web_agent") {
          dataHtml = `
            <div class="task-data">
              <strong>🌐 Sources collected:</strong> ${result.data.length}<br>
              ${result.data
                .slice(0, 2)
                .map(
                  (d) => `
                  <div class="mt-10">
                    <strong>Source:</strong> ${escapeHtml(d.source)}<br>
                    <strong>Content:</strong> ${escapeHtml(d.content.substring(0, 200))}…
                  </div>`
                )
                .join("")}
            </div>`;
        } else if (result.agent === "research_agent") {
          dataHtml = `
            <div class="task-data">
              <strong>📚 Papers found:</strong> ${result.data.length}<br>
              ${result.data
                .slice(0, 3)
                .map(
                  (paper) => `
                  <div class="mt-10">
                    <strong>Title:</strong> ${escapeHtml(paper.title)}<br>
                    <strong>Authors:</strong> ${escapeHtml(paper.authors.join(", "))}<br>
                    <strong>Published:</strong> ${escapeHtml(paper.published)}<br>
                    <a href="${paper.pdf_url}" target="_blank" rel="noopener">View PDF ↗</a>
                  </div>`
                )
                .join("")}
            </div>`;
        }
      } else if (result.error) {
        dataHtml = `
          <div class="task-data" style="border-left: 3px solid var(--rose);">
            <strong style="color:var(--rose);">Error:</strong> ${escapeHtml(result.error)}
          </div>`;
      }

      return `
        <div class="task-card" style="animation-delay:${i * 60}ms; animation: fadeSlideUp var(--dur-slow) var(--ease-out) both ${i * 60}ms;">
          <div class="task-header">
            <div class="task-title">${agentIcon} ${escapeHtml(result.task_id)}</div>
            <span class="task-status ${statusClass}">${statusText}</span>
          </div>
          <div class="task-body">
            <strong>Prompt:</strong> ${escapeHtml(result.prompt || "N/A")}<br>
            <strong>Agent:</strong> ${escapeHtml(result.agent || "N/A")}<br>
            <strong>Timestamp:</strong> ${formatTimestamp(result.timestamp)}
          </div>
          ${dataHtml}
        </div>`;
    })
    .join("");
}

// ─── Load Saved Plans ──────────────────────────────────

async function loadPlans() {
  const plansList = document.getElementById("plansList");
  plansList.innerHTML = '<p class="loading-text">Loading saved plans…</p>';

  try {
    const response = await fetch("/api/plans");
    const data = await response.json();

    if (data.success && data.plans.length > 0) {
      plansList.innerHTML = data.plans
        .map(
          (plan, i) => `
          <div class="plan-card" data-filename="${escapeHtml(plan.filename)}"
               style="animation: fadeSlideUp var(--dur-slow) var(--ease-out) both ${i * 50}ms;">
            <div class="plan-card-title">${escapeHtml(plan.goal)}</div>
            <div class="plan-card-meta">
              <span>📅 ${formatTimestamp(plan.created_at)}</span>
              <span>📋 ${plan.tasks} tasks</span>
            </div>
            <div class="plan-card-meta" style="margin-top:4px;">
              <span style="font-size:0.72rem; color:var(--text-muted);">
                ${escapeHtml(plan.query)}
              </span>
            </div>
          </div>`
        )
        .join("");

      // Attach click handlers
      plansList.querySelectorAll(".plan-card[data-filename]").forEach((card) => {
        card.addEventListener("click", () => {
          viewPlan(card.getAttribute("data-filename"));
        });
      });
    } else {
      plansList.innerHTML =
        '<p class="text-muted text-center" style="padding:var(--space-xl);">No saved plans yet. Submit a query to get started!</p>';
    }
  } catch (error) {
    console.error("Failed to load plans:", error);
    plansList.innerHTML =
      '<p class="text-muted text-center">Failed to load plans</p>';
  }
}

// ─── View Plan in Modal ────────────────────────────────

async function viewPlan(filename) {
  try {
    const response = await fetch(`/api/plan/${filename}`);
    const data = await response.json();

    if (data.success) {
      const plan = data.plan;
      const domains = Array.isArray(plan.domains) ? plan.domains.join(", ") : (plan.domains || "—");
      const sources = Array.isArray(plan.sources) ? plan.sources.join(", ") : (plan.sources || "—");

      const body = `
        <div class="detail-row">
          <span class="detail-label">Goal</span>
          <span class="detail-value">${escapeHtml(plan.goal)}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Domains</span>
          <span class="detail-value">${escapeHtml(domains)}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Time Range</span>
          <span class="detail-value">${escapeHtml(plan.time_range)}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Sources</span>
          <span class="detail-value">${escapeHtml(sources)}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Tasks</span>
          <span class="detail-value">${plan.tasks ? plan.tasks.length : 0}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Query</span>
          <span class="detail-value">${escapeHtml(plan._metadata?.query || "N/A")}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Created</span>
          <span class="detail-value">${formatTimestamp(plan._metadata?.created_at)}</span>
        </div>
      `;

      openModal("📋 Plan Details", body);
    }
  } catch (error) {
    console.error("Failed to load plan:", error);
    showToast("Failed to load plan details", "error");
  }
}

// ─── Loading State ─────────────────────────────────────

function showLoading() {
  const loading = document.getElementById("loadingIndicator");
  loading.style.display = "block";

  const steps = [
    { icon: "📐", text: "Generating execution plan…" },
    { icon: "🔪", text: "Chunking tasks…" },
    { icon: "📡", text: "Scheduling to agents…" },
    { icon: "⚡", text: "Collecting data…" },
  ];

  document.getElementById("loadingSteps").innerHTML = steps
    .map((s) => `<div class="loading-step">${s.icon} ${s.text}</div>`)
    .join("");

  loading.scrollIntoView({ behavior: "smooth", block: "center" });
}

function hideLoading() {
  document.getElementById("loadingIndicator").style.display = "none";
}

// ─── Utility Functions ─────────────────────────────────

function formatTimestamp(timestamp) {
  if (!timestamp) return "N/A";
  try {
    return new Date(timestamp).toLocaleString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return timestamp;
  }
}

function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.textContent = String(text);
  return div.innerHTML;
}

// Legacy global access for backwards compat
window.setQuery = function (query) {
  document.getElementById("queryInput").value = query;
  document.getElementById("queryInput").focus();
};
window.clearResults = function () {
  document.getElementById("resultsSection").style.display = "none";
  document.getElementById("queryInput").value = "";
};
window.loadPlans = loadPlans;
