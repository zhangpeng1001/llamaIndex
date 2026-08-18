// 质检规范知识库前端逻辑：所有功能面板的请求与渲染。

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
    const fileList = (data.indexed_files || []).join(", ");
    modelInfo.textContent = `model: ${data.llm_model} | embed: ${data.embed_model} | 文件: ${fileList}`;
    return data;
  } catch (e) {
    badge.className = "badge badge-loading";
    badge.textContent = "服务未就绪";
    modelInfo.textContent = "请确认服务已启动 (python -m qualityScheme.web)";
    return null;
  }
}

$("btn-refresh").addEventListener("click", refreshHealth);

$("btn-rebuild").addEventListener("click", async () => {
  if (!confirm("将删除现有 storage 并重新切块、嵌入质检规范，可能耗时数秒。继续？")) return;
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
// RAG 问答
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
// 向量检索
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
// 按部分检索
// ---------------------------------------------------------------------------

$("rp-run").addEventListener("click", async () => {
  const el = $("rp-result");
  setLoading(el);
  try {
    const data = await postJSON("/api/retrieve/part", {
      question: $("rp-question").value,
      part_number: parseInt($("rp-part").value, 10),
      top_k: parseInt($("rp-topk").value, 10) || 3,
    });
    const partBadge = `<div class="answer-text">
      <span class="muted">检索范围：</span>
      <span class="badge badge-local">第${data.part_number}部分</span>
    </div>`;
    setHtml(el, partBadge + renderSources(data.sources));
  } catch (e) { setError(el, e.message); }
});

// ---------------------------------------------------------------------------
// 全文总结
// ---------------------------------------------------------------------------

$("sm-run").addEventListener("click", async () => {
  const el = $("sm-result");
  setLoading(el, "正在遍历全部规范做总结，请稍候…");
  try {
    const data = await postJSON("/api/summary", { question: $("sm-question").value });
    setHtml(el, renderAnswer(data.answer));
  } catch (e) { setError(el, e.message); }
});

// ---------------------------------------------------------------------------
// 流式回答 (SSE)
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
    body: JSON.stringify({
      question: $("sr-question").value,
      top_k: parseInt($("sr-topk").value, 10) || 3,
    }),
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
// 异步查询
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
// 方案编排：自然语言生成质检方案
// ---------------------------------------------------------------------------

$("sc-run").addEventListener("click", async () => {
  const el = $("sc-result");
  const requirement = $("sc-requirement").value.trim();
  if (!requirement) {
    setError(el, "请输入质检需求描述");
    return;
  }
  setLoading(el, "正在检索规范并生成方案，请稍候…");
  try {
    const data = await postJSON("/api/scheme/generate", {
      requirement: requirement,
      context_top_k: parseInt($("sc-topk").value, 10) || 5,
    });
    renderScheme(el, data);
  } catch (e) { setError(el, e.message); }
});

$("sc-show-items").addEventListener("click", async () => {
  const el = $("sc-result");
  setLoading(el, "加载检查项清单…");
  try {
    const data = await fetch("/api/scheme/check-items").then((r) => r.json());
    const rows = (data.data || []).map((item) => `
      <tr>
        <td><code>${escapeHtml(item.checkCode)}</code></td>
        <td>${escapeHtml(item.checkName)}</td>
        <td>${escapeHtml(item.checkDesc)}</td>
        <td><code>${escapeHtml(item.checkParam)}</code></td>
      </tr>`).join("");
    setHtml(el, `
      <div class="sources">
        <div class="sources-title">预定义检查项清单 (${data.data.length} 项)</div>
        <table class="eval-table">
          <thead><tr><th>checkCode</th><th>名称</th><th>说明</th><th>参数</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>`);
  } catch (e) { setError(el, e.message); }
});

function renderScheme(el, scheme) {
  const items = (scheme.checkItem || []).map((item) => `
    <div class="source-item">
      <div class="source-meta">
        <span class="source-file">${escapeHtml(item.checkName)}</span>
        <span class="source-score"><code>${escapeHtml(item.checkCode)}</code></span>
      </div>
      <div class="source-preview"><code>${escapeHtml(JSON.stringify(item.params, null, 2))}</code></div>
    </div>`).join("");
  setHtml(el, `
    <div class="answer-text">
      <div><b>方案名称：</b>${escapeHtml(scheme.schemeName)}</div>
      <div><b>方案描述：</b>${escapeHtml(scheme.description)}</div>
    </div>
    <div class="sources">
      <div class="sources-title">检查项 (${scheme.checkItem.length})</div>
      ${items}
    </div>
    <details>
      <summary class="muted">查看完整 JSON</summary>
      <pre><code>${escapeHtml(JSON.stringify(scheme, null, 2))}</code></pre>
    </details>`);
}

// ---------------------------------------------------------------------------
// 初始化
// ---------------------------------------------------------------------------

refreshHealth();
