// LlamaIndex Demo 前端逻辑：所有功能面板的请求与渲染。

const $ = (id) => document.getElementById(id);

// ---------------------------------------------------------------------------
// 通用工具
// ---------------------------------------------------------------------------

function toast(message, type = "") {
  const el = $("toast");
  el.textContent = message;
  el.className = "toast show " + type;
  setTimeout(() => { el.className = "toast"; }, 3000);
}

function setLoading(el, text = "加载中…") {
  el.classList.add("loading");
  el.classList.remove("error");
  el.textContent = text;
}

function setError(el, message) {
  el.classList.remove("loading");
  el.classList.add("error");
  el.textContent = "❌ " + message;
}

function setHtml(el, html) {
  el.classList.remove("loading", "error");
  el.innerHTML = html;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

function renderAnswer(answer) {
  return `<div class="answer-text">${escapeHtml(answer)}</div>`;
}

function renderSources(sources) {
  if (!sources || sources.length === 0) return "";
  const items = sources.map((s) => `
    <div class="source-item">
      <div class="source-meta">
        <span class="source-file">${escapeHtml(s.file_name)}</span>
        <span class="source-score">score: ${s.score ?? "N/A"}</span>
        <span class="muted">#${s.position}</span>
      </div>
      <div class="source-preview">${escapeHtml(s.preview)}…</div>
    </div>`).join("");
  return `<div class="sources">
    <div class="sources-title">来源节点 (${sources.length})</div>
    ${items}
  </div>`;
}

async function postJSON(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const err = await res.json();
      detail = err.detail || JSON.stringify(err);
    } catch (_) { /* ignore */ }
    throw new Error(detail);
  }
  return res.json();
}

// ---------------------------------------------------------------------------
// 标签页切换
// ---------------------------------------------------------------------------

document.querySelectorAll(".nav-item").forEach((nav) => {
  nav.addEventListener("click", (e) => {
    e.preventDefault();
    document.querySelectorAll(".nav-item").forEach((n) => n.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    nav.classList.add("active");
    $(`tab-${nav.dataset.tab}`).classList.add("active");
  });
});

// ---------------------------------------------------------------------------
// 状态：健康检查、重建索引
// ---------------------------------------------------------------------------

async function refreshHealth() {
  const badge = $("provider-badge");
  const modelInfo = $("model-info");
  badge.className = "badge badge-loading";
  badge.textContent = "检查中…";
  try {
    const data = await fetch("/api/health").then((r) => r.json());
    badge.className = "badge " + (data.uses_openai ? "badge-openai" : "badge-local");
    badge.textContent = `provider: ${data.provider}`;
    modelInfo.textContent = `model: ${data.llm_model} | embed: ${data.embed_model} | 会话: ${data.active_chat_sessions}`;
    return data;
  } catch (e) {
    badge.className = "badge badge-loading";
    badge.textContent = "服务未就绪";
    modelInfo.textContent = "请确认服务已启动";
    return null;
  }
}

$("btn-refresh").addEventListener("click", refreshHealth);

$("btn-rebuild").addEventListener("click", async () => {
  if (!confirm("将删除现有 storage 并重新切块、嵌入，可能耗时数秒。继续？")) return;
  const btn = $("btn-rebuild");
  btn.disabled = true;
  btn.textContent = "重建中…";
  toast("正在重建索引…");
  try {
    const data = await postJSON("/api/rebuild", {});
    toast(data.message || "索引已重建", "success");
    await refreshHealth();
  } catch (e) {
    toast("重建失败：" + e.message, "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "重建索引";
  }
});

// ---------------------------------------------------------------------------
// Quickstart
// ---------------------------------------------------------------------------

$("qs-run").addEventListener("click", async () => {
  const el = $("qs-result");
  setLoading(el);
  try {
    const data = await postJSON("/api/quickstart", {
      question: $("qs-question").value,
      top_k: parseInt($("qs-topk").value, 10) || 3,
    });
    setHtml(el, renderAnswer(data.answer) + renderSources(data.sources));
  } catch (e) { setError(el, e.message); }
});

// ---------------------------------------------------------------------------
// Retrieve
// ---------------------------------------------------------------------------

$("rt-run").addEventListener("click", async () => {
  const el = $("rt-result");
  setLoading(el);
  try {
    const data = await postJSON("/api/retrieve", {
      question: $("rt-question").value,
      top_k: parseInt($("rt-topk").value, 10) || 3,
      file_name: $("rt-file").value.trim() || null,
    });
    setHtml(el, renderSources(data.sources));
  } catch (e) { setError(el, e.message); }
});

// ---------------------------------------------------------------------------
// Summary
// ---------------------------------------------------------------------------

$("sm-run").addEventListener("click", async () => {
  const el = $("sm-result");
  setLoading(el);
  try {
    const data = await postJSON("/api/summary", { question: $("sm-question").value });
    setHtml(el, renderAnswer(data.answer));
  } catch (e) { setError(el, e.message); }
});

// ---------------------------------------------------------------------------
// Router
// ---------------------------------------------------------------------------

$("rr-run").addEventListener("click", async () => {
  const el = $("rr-result");
  setLoading(el);
  try {
    const data = await postJSON("/api/router", { question: $("rr-question").value });
    setHtml(el,
      `<div class="answer-text"><span class="muted">路由选择：</span>
        <span class="badge badge-local">${escapeHtml(data.route)}</span></div>`
      + renderAnswer(data.answer));
  } catch (e) { setError(el, e.message); }
});

// ---------------------------------------------------------------------------
// Structured
// ---------------------------------------------------------------------------

$("st-run").addEventListener("click", async () => {
  const el = $("st-result");
  setLoading(el);
  try {
    const data = await postJSON("/api/structured", { material: $("st-material").value });
    const card = data.card;
    setHtml(el, `
      <div class="answer-text">
        <div><b>标题：</b>${escapeHtml(card.title)}</div>
        <div><b>难度：</b><span class="badge badge-local">${escapeHtml(card.difficulty)}</span></div>
        <div><b>摘要：</b>${escapeHtml(card.summary)}</div>
        <div><b>关键词：</b>${(card.keywords || []).map((k) =>
          `<span class="badge badge-openai">${escapeHtml(k)}</span>`).join(" ")}</div>
      </div>
      <pre><code>${escapeHtml(JSON.stringify(card, null, 2))}</code></pre>`);
  } catch (e) { setError(el, e.message); }
});

// ---------------------------------------------------------------------------
// Stream (SSE)
// ---------------------------------------------------------------------------

let streamController = null;

$("sr-run").addEventListener("click", () => {
  const el = $("sr-result");
  el.classList.remove("loading", "error");
  el.innerHTML = '<span class="stream-cursor" id="sr-cursor"></span>';
  $("sr-run").disabled = true;
  $("sr-stop").disabled = false;

  streamController = new AbortController();
  let buffer = "";
  let lineBuffer = "";

  fetch("/api/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: $("sr-question").value, top_k: 3 }),
    signal: streamController.signal,
  }).then(async (res) => {
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      // SSE 按行分割；一次 read 可能只包含半行，需要自行拼接。
      lineBuffer += decoder.decode(value, { stream: true });
      const lines = lineBuffer.split("\n");
      lineBuffer = lines.pop(); // 最后一段可能不完整，留到下次
      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const payload = line.slice(6).trim();
        if (payload === "[DONE]") continue;
        try {
          const obj = JSON.parse(payload);
          if (obj.token) {
            buffer += obj.token;
            el.innerHTML = escapeHtml(buffer) + '<span class="stream-cursor"></span>';
          }
        } catch (_) { /* ignore partial */ }
      }
    }
    el.innerHTML = escapeHtml(buffer);
  }).catch((e) => {
    if (e.name === "AbortError") {
      el.innerHTML = escapeHtml(buffer) + "\n\n[已停止]";
    } else {
      setError(el, e.message);
    }
  }).finally(() => {
    $("sr-run").disabled = false;
    $("sr-stop").disabled = true;
    streamController = null;
  });
});

$("sr-stop").addEventListener("click", () => {
  if (streamController) streamController.abort();
});

// ---------------------------------------------------------------------------
// Async
// ---------------------------------------------------------------------------

$("as-run").addEventListener("click", async () => {
  const el = $("as-result");
  setLoading(el);
  try {
    const data = await postJSON("/api/async", {
      question: $("as-question").value,
      top_k: parseInt($("as-topk").value, 10) || 3,
    });
    setHtml(el, renderAnswer(data.answer) + renderSources(data.sources));
  } catch (e) { setError(el, e.message); }
});

// ---------------------------------------------------------------------------
// Workflow
// ---------------------------------------------------------------------------

$("wf-run").addEventListener("click", async () => {
  const el = $("wf-result");
  setLoading(el);
  try {
    const data = await postJSON("/api/workflow", {
      question: $("wf-question").value,
      top_k: parseInt($("wf-topk").value, 10) || 3,
    });
    setHtml(el,
      renderAnswer(data.answer)
      + `<div class="sources"><div class="sources-title">来源文件</div>
        <div>${(data.sources || []).map((s) =>
          `<span class="badge badge-local">${escapeHtml(s)}</span>`).join(" ")}</div></div>`
      + `<pre><code>${escapeHtml(JSON.stringify(data, null, 2))}</code></pre>`);
  } catch (e) { setError(el, e.message); }
});

// ---------------------------------------------------------------------------
// Agent
// ---------------------------------------------------------------------------

$("ag-run").addEventListener("click", async () => {
  const el = $("ag-result");
  setLoading(el);
  try {
    const data = await postJSON("/api/agent", { question: $("ag-question").value });
    setHtml(el, renderAnswer(data.answer));
  } catch (e) { setError(el, e.message); }
});

// ---------------------------------------------------------------------------
// Evaluate
// ---------------------------------------------------------------------------

$("ev-run").addEventListener("click", async () => {
  const el = $("ev-result");
  setLoading(el);
  try {
    const topK = parseInt($("ev-topk").value, 10) || 3;
    const data = await fetch(`/api/evaluate?top_k=${topK}`).then((r) => r.json());
    const rows = (data.details || []).map((d) => `
      <tr>
        <td>${escapeHtml(d.question)}</td>
        <td>${escapeHtml(d.expected)}</td>
        <td>${(d.retrieved || []).map((f) => escapeHtml(f)).join("<br>")}</td>
        <td class="${d.rank ? "hit" : "miss"}">${d.rank ?? "未命中"}</td>
      </tr>`).join("");
    setHtml(el, `
      <div class="metric-grid">
        <div class="metric-card"><div class="metric-value">${(data.hit_rate * 100).toFixed(1)}%</div><div class="metric-label">Hit Rate</div></div>
        <div class="metric-card"><div class="metric-value">${data.mrr.toFixed(3)}</div><div class="metric-label">MRR</div></div>
        <div class="metric-card"><div class="metric-value">${data.top_k}</div><div class="metric-label">Top-K</div></div>
      </div>
      <table class="eval-table">
        <thead><tr><th>问题</th><th>期望文件</th><th>检索结果</th><th>排名</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>`);
  } catch (e) { setError(el, e.message); }
});

// ---------------------------------------------------------------------------
// Chat：多轮对话
// ---------------------------------------------------------------------------

let chatSessionId = null;

async function ensureChatSession() {
  if (chatSessionId) return chatSessionId;
  const data = await postJSON("/api/chat/sessions", {});
  chatSessionId = data.session_id;
  $("chat-session").textContent = chatSessionId;
  return chatSessionId;
}

function appendChat(role, text) {
  const log = $("chat-log");
  const div = document.createElement("div");
  div.className = "chat-msg chat-msg-" + role;
  div.innerHTML = `<div class="chat-role">${role === "user" ? "你" : "助教"}</div>
    <div class="chat-text">${escapeHtml(text)}</div>`;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

$("chat-new").addEventListener("click", async () => {
  $("chat-log").innerHTML = "";
  chatSessionId = null;
  await ensureChatSession();
  toast("已创建新会话：" + chatSessionId, "success");
});

$("chat-reset").addEventListener("click", async () => {
  if (chatSessionId) {
    try { await fetch(`/api/chat/${chatSessionId}`, { method: "DELETE" }); } catch (_) {}
  }
  $("chat-log").innerHTML = "";
  chatSessionId = null;
  $("chat-session").textContent = "（未创建）";
  toast("会话已重置");
});

async function sendChat() {
  const input = $("chat-input");
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  try {
    await ensureChatSession();
    appendChat("user", text);
    const data = await postJSON(`/api/chat/${chatSessionId}/message`, { message: text });
    appendChat("bot", data.reply);
  } catch (e) {
    appendChat("bot", "❌ " + e.message);
  }
}

$("chat-send").addEventListener("click", sendChat);
$("chat-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendChat();
  }
});

// ---------------------------------------------------------------------------
// 初始化
// ---------------------------------------------------------------------------

refreshHealth();
