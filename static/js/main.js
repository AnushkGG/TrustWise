"use strict";
(() => {
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __commonJS = (cb, mod) => function __require() {
    return mod || (0, cb[__getOwnPropNames(cb)[0]])((mod = { exports: {} }).exports, mod), mod.exports;
  };

  // src/client/main.ts
  var require_main = __commonJS({
    "src/client/main.ts"() {
      var pipelineTimer = null;
      var PIPELINE_STEPS = [
        { id: "plan", label: "Planning", detail: "LLM produces JSON execution plan" },
        { id: "agents", label: "Agents", detail: "Web + research tasks (DDG, arXiv, OpenAlex, Semantic Scholar)" },
        { id: "citations", label: "Citations", detail: "Scraping curated trusted sources for query-relevant data" },
        { id: "structure", label: "Structure", detail: "Cleaner normalizes records" },
        { id: "trust", label: "Trust", detail: "Validation and scoring" },
        { id: "store", label: "Storage", detail: "SQLite deduplication / cache" },
        { id: "insights", label: "Insights", detail: "Summary and highlights" }
      ];
      document.addEventListener("DOMContentLoaded", () => {
        loadSystemStatus();
        loadPlans();
        setupFormHandler();
        setupChipHandler();
        setupModalHandler();
        setupClearHandler();
        setupRefreshHandler();
        setupExportHandlers();
      });
      var currentResults = null;
      function showToast(message, type = "info") {
        const container = document.getElementById("toastContainer");
        if (!container) return;
        const toast = document.createElement("div");
        toast.className = `toast ${type}`;
        toast.innerHTML = `<span>${type === "error" ? "!" : type === "success" ? "OK" : "i"}</span> <span>${escapeHtml(message)}</span>`;
        container.appendChild(toast);
        setTimeout(() => {
          toast.classList.add("toast-exit");
          toast.addEventListener("animationend", () => toast.remove());
        }, 4500);
      }
      async function loadSystemStatus() {
        const indicator = document.getElementById("statusIndicator");
        if (!indicator) return;
        const statusText = indicator.querySelector(".status-text");
        const statusDot = indicator.querySelector(".status-dot");
        if (!statusText || !statusDot) return;
        try {
          const response = await fetch("/api/status");
          const data = await response.json();
          if (!data.success) throw new Error("bad status");
          const s = data.status;
          const provider = (s.llm_provider || "").toLowerCase();
          const model = s.llm_model || "";
          if (provider === "ollama") {
            const ok = s.ollama_reachable === true || s.has_api_key === true;
            if (ok) {
              statusText.textContent = `Local \xB7 Ollama \xB7 ${model}`;
              statusDot.className = "status-dot status-dot--ok";
            } else {
              statusText.textContent = "Ollama unreachable \u2014 start Ollama or check OLLAMA_BASE_URL";
              statusDot.className = "status-dot status-dot--warn";
            }
            return;
          }
          if (provider === "gemini") {
            const ok = s.gemini_configured === true || s.has_api_key === true && !!s.llm_model;
            if (ok) {
              statusText.textContent = `Gemini \xB7 ${model}`;
              statusDot.className = "status-dot status-dot--ok";
            } else {
              statusText.textContent = "Gemini API key not set \u2014 using mock plan";
              statusDot.className = "status-dot status-dot--warn";
            }
            return;
          }
          statusText.textContent = `${provider || "LLM"} \xB7 ${model}`;
          statusDot.className = "status-dot status-dot--ok";
        } catch (error) {
          console.error("Failed to load status:", error);
          statusText.textContent = "API offline";
          statusDot.className = "status-dot status-dot--err";
        }
      }
      function setupFormHandler() {
        document.getElementById("queryForm").addEventListener("submit", async (e) => {
          e.preventDefault();
          await submitQuery();
        });
      }
      function setupChipHandler() {
        document.querySelectorAll(".chip[data-query]").forEach((chip) => {
          chip.addEventListener("click", () => {
            const q = chip.getAttribute("data-query");
            const input = document.getElementById("queryInput");
            input.value = q;
            input.focus();
          });
        });
      }
      function setupModalHandler() {
        const overlay = document.getElementById("planModal");
        document.getElementById("modalCloseBtn").addEventListener("click", closeModal);
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
        document.getElementById("planModal").style.display = "none";
        document.body.style.overflow = "";
      }
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
      function setupExportHandlers() {
        document.getElementById("exportCsvBtn").addEventListener("click", () => {
          if (!currentResults || !currentResults.trusted_data) return;
          exportToCsv(currentResults.trusted_data, "trustwise-results.csv");
        });
        document.getElementById("exportPdfBtn").addEventListener("click", () => {
          window.print();
        });
      }
      function exportToCsv(data, filename) {
        if (!data.length) return;
        const headers = Object.keys(data[0]).join(",");
        const rows = data.map(
          (obj) => Object.values(obj).map((val) => `"${String(val).replace(/"/g, '""')}"`).join(",")
        );
        const csvContent = [headers, ...rows].join("\n");
        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
        const link = document.createElement("a");
        const url = URL.createObjectURL(blob);
        link.setAttribute("href", url);
        link.setAttribute("download", filename);
        link.style.visibility = "hidden";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        showToast("CSV exported", "success");
      }
      async function submitQuery() {
        const queryInput = document.getElementById("queryInput");
        const query = queryInput.value.trim();
        if (!query) {
          showToast("Enter a research query.", "error");
          return;
        }
        showLoading();
        const submitBtn = document.getElementById("submitBtn");
        submitBtn.disabled = true;
        submitBtn.querySelector(".btn-text").textContent = "Running\u2026";
        try {
          const response = await fetch("/api/submit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query })
          });
          const data = await response.json();
          if (data.success) {
            currentResults = data;
            displayResults(data);
            loadPlans();
            showToast("Pipeline completed.", "success");
          } else {
            showToast(data.error || "Request failed", "error");
          }
        } catch (error) {
          console.error(error);
          showToast("Network error: " + (error instanceof Error ? error.message : String(error)), "error");
        } finally {
          hideLoading();
          submitBtn.disabled = false;
          submitBtn.querySelector(".btn-text").textContent = "Run pipeline";
        }
      }
      function displayResults(data) {
        const resultsSection = document.getElementById("resultsSection");
        resultsSection.style.display = "block";
        resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
        displayPlanSummary(data.plan);
        displayExecutionSummary(data.execution);
        document.getElementById("insightsMount").innerHTML = data.insights ? renderInsightsPanelHtml(data.insights) : '<p class="text-muted">No insights object returned.</p>';
        document.getElementById("trustMount").innerHTML = data.trust_report ? renderTrustPanelHtml(data.trust_report, data.execution) : '<p class="text-muted">No trust report.</p>';
        displayItemCards(
          data.trusted_data || [],
          document.getElementById("taskResultsTrusted"),
          { empty: "No trusted items (threshold not met or cache-only)." }
        );
        displayItemCards(
          data.structured_data || [],
          document.getElementById("taskResultsStructured"),
          { empty: "No structured records." }
        );
        displayRawTaskResults(data.results || [], document.getElementById("taskResultsRaw"));
      }
      function displayPlanSummary(plan) {
        const el = document.getElementById("planSummary");
        const renderList = (items) => {
          if (!items) return "\u2014";
          if (Array.isArray(items)) {
            return items.map((d) => `<span class="chip">${escapeHtml(d)}</span>`).join(" ");
          }
          return escapeHtml(String(items));
        };
        el.innerHTML = `
    <h3>Execution plan</h3>
    <div class="plan-detail">
      <div class="plan-item">
        <div class="plan-item-label">Goal</div>
        <div class="plan-item-value">${escapeHtml(String(plan.goal ?? ""))}</div>
      </div>
      <div class="plan-item">
        <div class="plan-item-label">Domains</div>
        <div class="plan-item-value">${renderList(plan.domains)}</div>
      </div>
      <div class="plan-item">
        <div class="plan-item-label">Time range</div>
        <div class="plan-item-value">${escapeHtml(String(plan.time_range ?? ""))}</div>
      </div>
      <div class="plan-item">
        <div class="plan-item-label">Sources</div>
        <div class="plan-item-value">${renderList(plan.sources)}</div>
      </div>
      <div class="plan-item">
        <div class="plan-item-label">Tasks</div>
        <div class="plan-item-value plan-item-value--num">${plan.total_tasks}</div>
      </div>
    </div>
  `;
      }
      function displayExecutionSummary(execution) {
        const cacheCard = execution.cache_hit ? `<div class="stat-card stat-card--highlight"><div class="stat-value">Yes</div><div class="stat-label">Cache hit</div></div>` : `<div class="stat-card"><div class="stat-value">No</div><div class="stat-label">Cache hit</div></div>`;
        document.getElementById("executionSummary").innerHTML = `
    <h3>Execution metrics</h3>
    <div class="stat-grid">
      <div class="stat-card"><div class="stat-value">${execution.web_tasks}</div><div class="stat-label">Web tasks</div></div>
      <div class="stat-card"><div class="stat-value">${execution.paper_tasks}</div><div class="stat-label">Research tasks</div></div>
      <div class="stat-card"><div class="stat-value">${execution.citation_sources ?? 0}</div><div class="stat-label">Citation sources</div></div>
      <div class="stat-card"><div class="stat-value">${execution.total_results}</div><div class="stat-label">Agent results</div></div>
      <div class="stat-card"><div class="stat-value">${execution.successful}</div><div class="stat-label">Successful</div></div>
      <div class="stat-card"><div class="stat-value">${execution.structured_items ?? 0}</div><div class="stat-label">Structured</div></div>
      <div class="stat-card"><div class="stat-value">${execution.trusted_items ?? 0}</div><div class="stat-label">Trusted</div></div>
      <div class="stat-card"><div class="stat-value">${execution.db_inserted ?? 0}</div><div class="stat-label">DB inserted</div></div>
      <div class="stat-card"><div class="stat-value">${execution.db_skipped ?? 0}</div><div class="stat-label">DB skipped</div></div>
      ${cacheCard}
    </div>
  `;
      }
      function renderTrustPanelHtml(trustReport, execution) {
        const v = trustReport.validated_count ?? 0;
        const t = trustReport.trusted_count ?? 0;
        const d = trustReport.dropped_count ?? 0;
        const cache = execution && execution.cache_hit ? " (served from SQLite cache)" : "";
        return `
    <h3>Trust validation</h3>
    <p class="trust-line"><strong>${t}</strong> trusted / <strong>${v}</strong> validated \xB7 <strong>${d}</strong> dropped${cache}</p>
  `;
      }
      function renderInsightsPanelHtml(insights) {
        const summary = escapeHtml(insights.concise_answer || insights.summary || "\u2014");
        const keyPoints = Array.isArray(insights.key_points) ? insights.key_points : Array.isArray(insights.key_highlights) ? insights.key_highlights : [];
        const keyHtml = keyPoints.length ? `<ul class="insights-list">${keyPoints.map((p) => `<li>${escapeHtml(p)}</li>`).join("")}</ul>` : '<p class="text-muted">No key points.</p>';
        const top = Array.isArray(insights.top_sources_detailed) ? insights.top_sources_detailed : [];
        const topHtml = top.length ? `<div class="chip-row">${top.map((x) => `<span class="chip">${escapeHtml(x.source ?? "")} (${escapeHtml(String(x.count ?? ""))})</span>`).join("")}</div>` : "";
        const conf = insights.confidence !== void 0 && insights.confidence !== null ? `<p class="insights-meta">Confidence: ${escapeHtml(String(insights.confidence))}</p>` : "";
        const citationLinks = Array.isArray(insights.citation_links) ? insights.citation_links : [];
        let citationHtml = "";
        if (citationLinks.length > 0) {
          const byCategory = {};
          for (const link of citationLinks) {
            const cat = link.category || "Other";
            if (!byCategory[cat]) byCategory[cat] = [];
            byCategory[cat].push(link);
          }
          let linksInner = "";
          for (const [cat, links] of Object.entries(byCategory)) {
            linksInner += `<div class="citation-category"><div class="citation-category-label">${escapeHtml(cat)}</div>`;
            for (const link of links) {
              const displayUrl = link.page_url || link.url || "";
              const displayName = link.name || "Source";
              const title = link.page_title ? ` \u2014 ${escapeHtml(link.page_title)}` : "";
              linksInner += `<div class="citation-link"><a href="${escapeHtml(displayUrl)}" target="_blank" rel="noopener">\u{1F517} ${escapeHtml(displayName)}${title}</a></div>`;
            }
            linksInner += `</div>`;
          }
          citationHtml = `<div class="insights-block"><strong>Source Citations (${citationLinks.length} sources)</strong><div class="citation-links-grid">${linksInner}</div></div>`;
        }
        return `
    <h3>Insights</h3>
    ${conf}
    <p class="insights-summary">${summary}</p>
    <div class="insights-block"><strong>Key points</strong>${keyHtml}</div>
    ${topHtml ? `<div class="insights-block"><strong>Sources</strong>${topHtml}</div>` : ""}
    ${citationHtml}
  `;
      }
      function displayItemCards(items, container, opts) {
        if (!container) return;
        const emptyMsg = opts && opts.empty || "No items.";
        if (!items || items.length === 0) {
          container.innerHTML = `<p class="text-muted">${emptyMsg}</p>`;
          return;
        }
        container.innerHTML = items.slice(0, 24).map(
          (item, i) => {
            const trust = item.trust;
            const content = String(item.content ?? "");
            return `
      <div class="task-card" style="animation-delay:${i * 40}ms">
        <div class="task-header">
          <div class="task-title">${item.content_type === "research_paper" ? "Research" : "Web"} \xB7 ${escapeHtml(String(item.title || "Untitled"))}</div>
          <span class="task-badge">${escapeHtml(String(item.content_type || "item"))}</span>
        </div>
        <div class="task-body">
          <div class="task-meta"><strong>Source</strong> ${escapeHtml(String(item.source || "\u2014"))}</div>
          <div class="task-meta">${item.url ? `<a href="${escapeHtml(String(item.url))}" target="_blank" rel="noopener">Open link</a>` : "No URL"}</div>
          ${trust ? `<div class="task-meta"><strong>Trust score</strong> ${escapeHtml(String(trust.score))}</div>` : ""}
          ${item.published_at ? `<div class="task-meta"><strong>Published</strong> ${escapeHtml(String(item.published_at))}</div>` : ""}
          <div class="task-snippet">${escapeHtml(content.substring(0, 500))}${content.length > 500 ? "\u2026" : ""}</div>
        </div>
      </div>`;
          }
        ).join("");
      }
      function displayRawTaskResults(results, el) {
        if (!el) return;
        if (!results || results.length === 0) {
          el.innerHTML = '<p class="text-muted">No raw task results.</p>';
          return;
        }
        el.innerHTML = results.map((result, i) => {
          const statusClass = result.status || "unknown";
          const agent = result.agent || "";
          let inner = "";
          if (result.data && result.data.length > 0) {
            inner = `<pre class="raw-pre">${escapeHtml(JSON.stringify(result.data.slice(0, 3), null, 2))}</pre>`;
          } else if (result.error) {
            inner = `<p class="task-error">${escapeHtml(result.error)}</p>`;
          }
          return `
        <div class="task-card">
          <div class="task-header">
            <div class="task-title">${escapeHtml(result.task_id || "task")}</div>
            <span class="task-badge task-badge--${statusClass}">${escapeHtml(statusClass)}</span>
          </div>
          <div class="task-body">
            <div class="task-meta"><strong>Agent</strong> ${escapeHtml(agent)}</div>
            <div class="task-meta"><strong>Prompt</strong> ${escapeHtml(result.prompt || "")}</div>
            ${inner}
          </div>
        </div>`;
        }).join("");
      }
      async function loadPlans() {
        const plansList = document.getElementById("plansList");
        plansList.innerHTML = '<p class="loading-text">Loading\u2026</p>';
        try {
          const response = await fetch("/api/plans");
          const data = await response.json();
          if (data.success && data.plans.length > 0) {
            plansList.innerHTML = data.plans.map(
              (plan, i) => `
          <div class="plan-card" data-filename="${escapeHtml(plan.filename)}" style="animation-delay:${i * 40}ms">
            <div class="plan-card-title">${escapeHtml(plan.goal)}</div>
            <div class="plan-card-meta">
              <span>${formatTimestamp(plan.created_at)}</span>
              <span>${plan.tasks} tasks</span>
            </div>
            <div class="plan-card-query">${escapeHtml(plan.query)}</div>
          </div>`
            ).join("");
            plansList.querySelectorAll(".plan-card[data-filename]").forEach((card) => {
              card.addEventListener("click", () => viewPlan(card.getAttribute("data-filename")));
            });
          } else {
            plansList.innerHTML = '<p class="text-muted text-center" style="padding:2rem">No saved plans yet.</p>';
          }
        } catch (error) {
          plansList.innerHTML = '<p class="text-muted text-center">Failed to load plans</p>';
        }
      }
      async function viewPlan(filename) {
        try {
          const response = await fetch(`/api/plan/${filename}`);
          const data = await response.json();
          if (data.success) {
            const plan = data.plan;
            const domains = Array.isArray(plan.domains) ? plan.domains.join(", ") : plan.domains || "\u2014";
            const sources = Array.isArray(plan.sources) ? plan.sources.join(", ") : plan.sources || "\u2014";
            const body = `
        <div class="detail-row"><span class="detail-label">Goal</span><span class="detail-value">${escapeHtml(plan.goal)}</span></div>
        <div class="detail-row"><span class="detail-label">Domains</span><span class="detail-value">${escapeHtml(domains)}</span></div>
        <div class="detail-row"><span class="detail-label">Time range</span><span class="detail-value">${escapeHtml(plan.time_range)}</span></div>
        <div class="detail-row"><span class="detail-label">Sources</span><span class="detail-value">${escapeHtml(sources)}</span></div>
        <div class="detail-row"><span class="detail-label">Tasks</span><span class="detail-value">${plan.tasks ? plan.tasks.length : 0}</span></div>
        <div class="detail-row"><span class="detail-label">Query</span><span class="detail-value">${escapeHtml(plan._metadata?.query || "N/A")}</span></div>
        <div class="detail-row"><span class="detail-label">Created</span><span class="detail-value">${formatTimestamp(plan._metadata?.created_at)}</span></div>`;
            openModal("Plan details", body);
          }
        } catch (error) {
          showToast("Failed to load plan", "error");
        }
      }
      function showLoading() {
        const loading = document.getElementById("loadingIndicator");
        loading.style.display = "block";
        const ol = document.getElementById("pipelineSteps");
        ol.innerHTML = PIPELINE_STEPS.map(
          (s, idx) => `<li class="pipeline-step" data-idx="${idx}"><span class="pipeline-step-num">${idx + 1}</span><div><strong>${escapeHtml(s.label)}</strong><span class="pipeline-step-detail">${escapeHtml(s.detail)}</span></div></li>`
        ).join("");
        let active = 0;
        const steps = ol.querySelectorAll(".pipeline-step");
        const tick = () => {
          steps.forEach((n, i) => {
            n.classList.toggle("pipeline-step--active", i === active);
            n.classList.toggle("pipeline-step--done", i < active);
          });
          active = (active + 1) % steps.length;
        };
        tick();
        pipelineTimer = setInterval(tick, 900);
        loading.scrollIntoView({ behavior: "smooth", block: "center" });
      }
      function hideLoading() {
        document.getElementById("loadingIndicator").style.display = "none";
        if (pipelineTimer) {
          clearInterval(pipelineTimer);
          pipelineTimer = null;
        }
      }
      function formatTimestamp(timestamp) {
        if (!timestamp) return "N/A";
        try {
          return new Date(timestamp).toLocaleString(void 0, {
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit"
          });
        } catch {
          return timestamp;
        }
      }
      function escapeHtml(text) {
        if (text === void 0 || text === null) return "";
        const div = document.createElement("div");
        div.textContent = String(text);
        return div.innerHTML;
      }
      window.setQuery = function(query) {
        document.getElementById("queryInput").value = query;
        document.getElementById("queryInput").focus();
      };
      window.clearResults = function() {
        document.getElementById("resultsSection").style.display = "none";
        document.getElementById("queryInput").value = "";
      };
      window.loadPlans = loadPlans;
    }
  });
  require_main();
})();
