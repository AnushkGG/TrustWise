/* ═══════════════════════════════════════════════════════════
   TrustWise Premium Frontend v2 — app.js
   ═══════════════════════════════════════════════════════════ */

const API_BASE = 'http://localhost:5000'; // Target the existing backend port

// ── Background Video Logic ──
function initBackgroundVideo() {
  const video = document.getElementById('heroBgVideo');
  if (!video) return;

  // Fade loop: 0.5s fade-in at start, 0.5s fade-out at end
  // The video element has transition: opacity 0.5s ease in CSS.
  
  video.addEventListener('loadeddata', () => {
    video.style.opacity = '1';
  });

  video.addEventListener('timeupdate', () => {
    const timeRemaining = video.duration - video.currentTime;
    if (timeRemaining <= 0.5 && video.style.opacity !== '0') {
      video.style.opacity = '0';
    }
  });

  video.addEventListener('ended', () => {
    video.style.opacity = '0';
    setTimeout(() => {
      video.currentTime = 0;
      video.play();
      setTimeout(() => {
        video.style.opacity = '1';
      }, 50); // slight delay to ensure it's playing before fade in
    }, 100);
  });
}

// ── Toast Notifications ──
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  const icon = type === 'error' ? '✕' : type === 'success' ? '✓' : 'ℹ';
  toast.innerHTML = `<span>${icon}</span> <span>${escapeHtml(message)}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('toast-exit');
    toast.addEventListener('animationend', () => toast.remove());
  }, 4500);
}

function escapeHtml(unsafe) {
  if (!unsafe) return '';
  return String(unsafe)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// ── Chat Box Logic ──
function initChatWidget() {
  const toggleBtn = document.getElementById('chatToggleBtn');
  const chatPanel = document.getElementById('chatPanel');
  const closeBtn = document.getElementById('chatCloseBtn');
  const chatForm = document.getElementById('chatForm');
  const chatInput = document.getElementById('chatInput');
  const chatMessages = document.getElementById('chatMessages');

  if (!toggleBtn || !chatPanel) return;

  function toggleChat() {
    const isHidden = chatPanel.style.display === 'none';
    chatPanel.style.display = isHidden ? 'flex' : 'none';
    if (isHidden) {
      chatInput.focus();
    }
  }

  toggleBtn.addEventListener('click', toggleChat);
  closeBtn.addEventListener('click', toggleChat);

  // Suggestion chips
  document.querySelectorAll('.chat-suggestion-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const msg = chip.getAttribute('data-msg');
      if (msg) {
        addMessage(msg, 'user');
        simulateBotResponse(msg);
      }
    });
  });

  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if (!msg) return;
    
    addMessage(msg, 'user');
    chatInput.value = '';
    simulateBotResponse(msg);
  });

  function addMessage(text, role) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-msg chat-msg--${role}`;
    msgDiv.innerHTML = `<div class="chat-bubble">${escapeHtml(text)}</div>`;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function simulateBotResponse(userMsg) {
    // Show typing indicator
    const typingId = 'typing-' + Date.now();
    const typingDiv = document.createElement('div');
    typingDiv.id = typingId;
    typingDiv.className = `chat-msg chat-msg--assistant chat-typing`;
    typingDiv.innerHTML = `<div class="chat-bubble"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>`;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    setTimeout(() => {
      const tDiv = document.getElementById(typingId);
      if (tDiv) tDiv.remove();

      let reply = "I'm a local demo of the chat. To connect me to the LLM backend, implement the API endpoint!";
      if (userMsg.toLowerCase().includes('status')) {
        reply = "I can fetch the system status for you. Looking at the indicator, it seems we are connected.";
      } else if (userMsg.toLowerCase().includes('trustwise')) {
        reply = "TrustWise is an AI research pipeline. We collect from arXiv, PubMed, and more, then validate findings with trust scores.";
      }

      addMessage(reply, 'assistant');
    }, 1500);
  }
}

// ── System Status ──
async function loadSystemStatus() {
  const indicator = document.getElementById("statusIndicator");
  if (!indicator) return;
  const statusText = indicator.querySelector(".status-text");
  const statusDot = indicator.querySelector(".status-dot");
  if (!statusText || !statusDot) return;

  try {
    const response = await fetch(`${API_BASE}/api/status`);
    const data = await response.json();
    if (!data.success) throw new Error("bad status");

    const s = data.status || {};
    const provider = (s.llm_provider || "Unknown").toLowerCase();
    const model = s.llm_model || "";

    statusText.textContent = `${provider} · ${model}`;
    statusDot.className = "status-dot status-dot--ok";
  } catch (error) {
    console.error("Failed to load status:", error);
    statusText.textContent = "Backend offline";
    statusDot.className = "status-dot status-dot--err";
  }
}

// ── Pipeline Form Handling ──
function setupQueryForm() {
  const queryForm = document.getElementById('queryForm');
  const heroCtaBtn = document.getElementById('heroCtaBtn');
  const openResearchBtn = document.getElementById('openResearchBtn');
  
  if (heroCtaBtn) {
    heroCtaBtn.addEventListener('click', () => {
      document.getElementById('mainApp').scrollIntoView({ behavior: 'smooth' });
      document.getElementById('queryInput').focus();
    });
  }

  if (openResearchBtn) {
    openResearchBtn.addEventListener('click', () => {
      document.getElementById('mainApp').scrollIntoView({ behavior: 'smooth' });
      document.getElementById('queryInput').focus();
    });
  }

  // Suggestion chips
  document.querySelectorAll('#queryBarSection .chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const q = chip.getAttribute('data-query');
      const input = document.getElementById('queryInput');
      input.value = q;
      input.focus();
    });
  });

  if (queryForm) {
    queryForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      await submitQuery();
    });
  }

  document.getElementById('clearResultsBtn')?.addEventListener('click', () => {
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('queryInput').value = '';
    window.scrollTo({ top: document.getElementById('mainApp').offsetTop, behavior: 'smooth' });
  });

  document.getElementById('refreshPlansBtn')?.addEventListener('click', () => {
    loadPlans();
    showToast('Plans refreshed', 'success');
  });
}

// ── Submission Logic ──
let currentResults = null;

async function submitQuery() {
  const queryInput = document.getElementById('queryInput');
  const query = queryInput.value.trim();
  if (!query) {
    showToast('Enter a research query.', 'error');
    return;
  }

  const submitBtn = document.getElementById('submitBtn');
  submitBtn.disabled = true;
  submitBtn.querySelector('.btn-text').textContent = 'Running…';
  
  const loading = document.getElementById('loadingIndicator');
  const resultsSec = document.getElementById('resultsSection');
  loading.style.display = 'block';
  resultsSec.style.display = 'none';

  // Mock steps for UI
  const steps = [
    { id: 'plan', label: 'Planning', detail: 'LLM producing execution plan' },
    { id: 'agents', label: 'Agents', detail: 'Executing web & academic research' },
    { id: 'trust', label: 'Trust Validation', detail: 'Scoring sources and claims' },
    { id: 'insights', label: 'Insights', detail: 'Synthesizing final report' }
  ];
  
  const stepsEl = document.getElementById('pipelineSteps');
  stepsEl.innerHTML = steps.map(s => `
    <li class="pipeline-step waiting" id="step-${s.id}">
      <div class="step-icon">${s.id.charAt(0).toUpperCase()}</div>
      <div>
        <div class="step-label">${s.label}</div>
        <div class="step-detail">${s.detail}</div>
      </div>
      <div class="step-spin" style="display:none"></div>
    </li>
  `).join('');

  // Animate steps blindly to show progress (since API is sync right now)
  let currentStepIdx = 0;
  const stepInterval = setInterval(() => {
    if (currentStepIdx < steps.length) {
      const stepEl = document.getElementById(`step-${steps[currentStepIdx].id}`);
      stepEl.className = 'pipeline-step active';
      stepEl.querySelector('.step-spin').style.display = 'block';
      
      if (currentStepIdx > 0) {
        const prevEl = document.getElementById(`step-${steps[currentStepIdx-1].id}`);
        prevEl.className = 'pipeline-step done';
        prevEl.querySelector('.step-spin').style.display = 'none';
        prevEl.querySelector('.step-icon').innerHTML = '✓';
      }
      currentStepIdx++;
    }
  }, 3000);

  try {
    const response = await fetch(`${API_BASE}/api/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    
    clearInterval(stepInterval);
    
    // Mark all done
    steps.forEach(s => {
      const el = document.getElementById(`step-${s.id}`);
      if(el) {
        el.className = 'pipeline-step done';
        el.querySelector('.step-spin').style.display = 'none';
        el.querySelector('.step-icon').innerHTML = '✓';
      }
    });

    const data = await response.json();
    if (data.success) {
      currentResults = data;
      displayResults(data);
      loadPlans();
      showToast('Pipeline completed successfully.', 'success');
    } else {
      showToast(data.error || 'Request failed', 'error');
      loading.style.display = 'none';
    }
  } catch (err) {
    clearInterval(stepInterval);
    console.error(err);
    showToast('Network error: ' + err.message, 'error');
    loading.style.display = 'none';
  } finally {
    submitBtn.disabled = false;
    submitBtn.querySelector('.btn-text').textContent = 'Run';
  }
}

function displayResults(data) {
  document.getElementById('loadingIndicator').style.display = 'none';
  const resultsSec = document.getElementById('resultsSection');
  resultsSec.style.display = 'block';

  // Plan Summary
  const plan = data.plan || {};
  document.getElementById('planSummary').innerHTML = `
    <div class="panel-title-row">
      <div class="panel-title-text">Execution Plan</div>
    </div>
    <div class="summary-grid">
      <div class="stat-card">
        <span class="stat-num">${plan.total_tasks || 0}</span>
        <span class="stat-label">Tasks Planned</span>
      </div>
      <div class="stat-card">
        <span class="stat-num">${(plan.domains || []).length}</span>
        <span class="stat-label">Target Domains</span>
      </div>
      <div class="stat-card">
        <span class="stat-num">${(plan.sources || []).length}</span>
        <span class="stat-label">Data Sources</span>
      </div>
    </div>
    <div style="margin-top: 16px;">
      <strong>Goal:</strong> ${escapeHtml(plan.goal || 'N/A')}
    </div>
  `;

  // Insights
  const ins = data.insights || {};
  let insightsHtml = '';
  if (ins.summary) {
    insightsHtml += `
      <div class="panel-inner">
        <div class="panel-title-row">
          <div class="panel-title-text">Research Synthesis</div>
        </div>
        <div class="panel-body">
          <p>${escapeHtml(ins.summary)}</p>
          ${ins.key_highlights && ins.key_highlights.length ? 
            `<ul class="insight-highlight-list">
              ${ins.key_highlights.map(h => `<li>${escapeHtml(h)}</li>`).join('')}
             </ul>` : ''}
        </div>
      </div>
    `;
  }
  document.getElementById('insightsMount').innerHTML = insightsHtml;

  // Trusted Items Render
  const trContainer = document.getElementById('taskResultsTrusted');
  trContainer.innerHTML = '';
  (data.trusted_data || []).forEach(item => {
    const card = document.createElement('div');
    card.className = 'task-card';
    card.innerHTML = `
      <div class="task-card-header">
        <div class="task-card-title">${escapeHtml(item.title || 'Untitled')}</div>
        <span class="trust-badge trust-badge--high">Score: ${item.trust_score || 'N/A'}</span>
      </div>
      <div class="task-card-snippet">${escapeHtml(item.summary || item.snippet || '')}</div>
      <div class="task-card-meta">
        ${item.source ? `<span class="meta-tag">${escapeHtml(item.source)}</span>` : ''}
        ${item.domain ? `<span class="meta-tag">${escapeHtml(item.domain)}</span>` : ''}
        ${item.url ? `<a href="${escapeHtml(item.url)}" target="_blank" class="task-card-link">View Source ↗</a>` : ''}
      </div>
    `;
    trContainer.appendChild(card);
  });
  if (!(data.trusted_data || []).length) {
    trContainer.innerHTML = `<p style="color:var(--fg-muted);font-size:14px">No trusted items found.</p>`;
  }

  // Structured Items Render
  const strContainer = document.getElementById('taskResultsStructured');
  strContainer.innerHTML = '';
  (data.structured_data || []).forEach(item => {
    const card = document.createElement('div');
    card.className = 'task-card';
    card.innerHTML = `
      <div class="task-card-header">
        <div class="task-card-title">${escapeHtml(item.title || 'Untitled')}</div>
      </div>
      <div class="task-card-snippet">${escapeHtml(item.summary || item.snippet || '')}</div>
      <div class="task-card-meta">
        ${item.source ? `<span class="meta-tag">${escapeHtml(item.source)}</span>` : ''}
        ${item.url ? `<a href="${escapeHtml(item.url)}" target="_blank" class="task-card-link">View Source ↗</a>` : ''}
      </div>
    `;
    strContainer.appendChild(card);
  });
  
  if (!(data.structured_data || []).length) {
    strContainer.innerHTML = `<p style="color:var(--fg-muted);font-size:14px">No structured items found.</p>`;
  }

  setTimeout(() => {
    resultsSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 100);
}

// ── Plans ──
async function loadPlans() {
  const plansList = document.getElementById("plansList");
  if (!plansList) return;
  try {
    const response = await fetch(`${API_BASE}/api/plans`);
    const data = await response.json();
    if (!data.success) throw new Error("bad plans");

    if (!data.plans || data.plans.length === 0) {
      plansList.innerHTML = `<p class="loading-text">No plans found.</p>`;
      return;
    }

    plansList.innerHTML = data.plans
      .map(
        (p) => `
        <div class="plan-card" onclick="viewPlan('${escapeHtml(p.filename)}')">
          <div class="plan-card-goal">${escapeHtml(p.goal)}</div>
          <div class="plan-card-meta">
            <span>Query: ${escapeHtml(p.query)}</span>
            <span>Tasks: ${p.tasks}</span>
          </div>
        </div>
      `
      )
      .join("");
  } catch (error) {
    console.error("Failed to load plans:", error);
    plansList.innerHTML = `<p class="loading-text" style="color:#f87171">Failed to load plans</p>`;
  }
}

async function viewPlan(filename) {
  try {
    const response = await fetch(`${API_BASE}/api/plan/${encodeURIComponent(filename)}`);
    const data = await response.json();
    if (!data.success) {
      showToast(data.error || "Failed to load plan details", "error");
      return;
    }

    const plan = data.plan;
    let body = `
      <div style="margin-bottom:16px"><strong>Goal:</strong> ${escapeHtml(plan.goal)}</div>
      <div style="margin-bottom:16px"><strong>Query:</strong> ${escapeHtml(plan._metadata?.query)}</div>
    `;

    if (plan.tasks && plan.tasks.length > 0) {
      body += `<h4>Tasks (${plan.tasks.length}):</h4><ul style="margin-top:8px; padding-left:20px; display:flex; flex-direction:column; gap:8px">`;
      plan.tasks.forEach((t) => {
        body += `<li>
          <strong>${escapeHtml(t.type)}:</strong> ${escapeHtml(t.description)}
        </li>`;
      });
      body += `</ul>`;
    }

    const modalTitle = document.getElementById("modalTitle");
    const modalBody = document.getElementById("modalBody");
    const modal = document.getElementById("planModal");

    modalTitle.textContent = "Plan Details";
    modalBody.innerHTML = body;
    modal.style.display = "flex";
  } catch (error) {
    console.error("Error viewing plan:", error);
    showToast("Failed to fetch plan details", "error");
  }
}

document.getElementById('modalCloseBtn')?.addEventListener('click', () => {
  document.getElementById('planModal').style.display = 'none';
});

document.getElementById('planModal')?.addEventListener('click', (e) => {
  if (e.target.id === 'planModal') {
    e.target.style.display = 'none';
  }
});


// ── Init ──
document.addEventListener('DOMContentLoaded', () => {
  initBackgroundVideo();
  initChatWidget();
  setupQueryForm();
  loadSystemStatus();
  loadPlans();
});
