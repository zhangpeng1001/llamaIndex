// 质检规范知识库前端逻辑(src 版 · 端口 8082)。
//
// 主要新增内容:
//   - 流程面板:Loading / Indexing / Storing 分阶段按钮事件 + 阶段卡片状态展示
//   - 顶部状态栏:三阶段进度 badge(done / pending)
//   - 一键重建:顺序执行三阶段,完成后刷新健康检查
//   - 原所有功能面板(RAG问答/向量检索/按部分检索/全文总结/流式回答/异步查询/方案编排)逻辑保留
//
// 与原 qualityScheme/static/app.js 的差异:
//   - 健康检查返回的字段不含 indexed_files,改为 collection_has_data + 阶段状态
//   - 向量检索端点由 /api/retrieve 改为 /api/querying(支持 part_number 过滤)
//   - 新增 /api/loading, /api/indexing, /api/storing, /api/state 端点

const $ = (id) => document.getElementById(id);

// ---------------------------------------------------------------------------
// 通用工具
// ---------------------------------------------------------------------------

/** 弹出右下角 toast 提示。type 可为 "" / "success" / "error"。 */
function toast(message, type = "") {
  const el = $("toast");
  el.textContent = message;
  el.className = "toast show " + type;
  setTimeout(() => { el.className = "toast"; }, 3000);
}

/** 把目标元素置为 loading 状态。 */
function setLoading(el, text = "加载中…") {
  el.classList.add("loading");
  el.classList.remove("error");
  el.textContent = text;
}

/** 把目标元素置为 error 状态。 */
function setError(el, message) {
  el.classList.remove("loading");
  el.classList.add("error");
  el.textContent = "❌ " + message;
}

/** 安全地设置 innerHTML(配合 escapeHtml 使用)。 */
function setHtml(el, html) {
  el.classList.remove("loading", "error");
  el.innerHTML = html;
}

/** HTML 转义,避免注入。 */
function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

/** 渲染回答文本。 */
function renderAnswer(answer) {
  return `<div class="answer-text">${escapeHtml(answer)}</div>`;
}

/** 渲染来源节点列表(sources 数组)。 */
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

/** 统一的 POST JSON 请求,失败时抛出带 detail 的 Error。 */
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
// 健康检查 + 阶段状态同步
// ---------------------------------------------------------------------------

/**
 * 刷新顶部状态栏:provider badge、模型信息、三阶段进度 badge。
 *
 * 数据来源 /api/health,返回字段包括:
 *   - provider / llm_model / embed_model / uses_openai
 *   - collection_has_data: Milvus 是否已有数据
 *   - loading_done / indexing_done / storing_done: 三阶段完成标志
 */
async function refreshHealth() {
  const badge = $("provider-badge");
  const modelInfo = $("model-info");
  badge.className = "badge badge-loading";
  badge.textContent = "检查中…";
  try {
    const data = await fetch("/api/health").then((r) => r.json());
    badge.className = "badge " + (data.uses_openai ? "badge-openai" : "badge-local");
    badge.textContent = `provider: ${data.provider}`;
    const milvusStatus = data.collection_has_data ? "Milvus: 有数据" : "Milvus: 空";
    modelInfo.textContent =
      `model: ${data.llm_model} | embed: ${data.embed_model} | ${milvusStatus}`;
    // 同步阶段进度 badge
    updateStageBadges(data);
    // 同步流程面板的卡片状态
    updateStageCards(data);
    return data;
  } catch (e) {
    badge.className = "badge badge-loading";
    badge.textContent = "服务未就绪";
    modelInfo.textContent = "请确认服务已启动 (python -m src.server)";
    return null;
  }
}

/**
 * 更新顶部三阶段 badge 的样式。
 * done → 绿色;pending → 灰色。
 */
function updateStageBadges(state) {
  const stages = [
    { id: "stage-loading", done: state.loading_done },
    { id: "stage-indexing", done: state.indexing_done },
    { id: "stage-storing", done: state.storing_done },
  ];
  stages.forEach((s) => {
    const el = $(s.id);
    if (!el) return;
    el.classList.remove("done", "pending");
    el.classList.add(s.done ? "done" : "pending");
  });
}

/**
 * 根据阶段状态为流程面板的卡片添加 done 样式。
 * 让用户一眼看出哪个阶段已完成。
 */
function updateStageCards(state) {
  const cards = [
    { id: "card-loading", done: state.loading_done },
    { id: "card-indexing", done: state.indexing_done },
    { id: "card-storing", done: state.storing_done },
  ];
  cards.forEach((c) => {
    const el = $(c.id);
    if (!el) return;
    el.classList.toggle("done", !!c.done);
  });
}

$("btn-refresh").addEventListener("click", refreshHealth);

// ---------------------------------------------------------------------------
// 流程面板:分阶段操作
// ---------------------------------------------------------------------------

/**
 * 把阶段结果区显示出来并填充内容。
 *
 * 参数:
 *   - el: stage-result 元素
 *   - lines: 字符串数组,每项作为一行(支持简单的 key:value 对齐)
 *   - isError: 是否为错误信息
 */
function showStageResult(el, lines, isError = false) {
  el.classList.remove("error");
  el.classList.add("show");
  if (isError) el.classList.add("error");
  el.textContent = Array.isArray(lines) ? lines.join("\n") : String(lines);
}

/** 切换阶段按钮的可用状态并更新文字。 */
function setStageButton(btn, disabled, text) {
  btn.disabled = disabled;
  if (text !== undefined) btn.textContent = text;
}

// Loading 阶段按钮事件
$("pl-loading-run").addEventListener("click", async () => {
  const btn = $("pl-loading-run");
  const el = $("pl-loading-result");
  const reExtract = $("pl-re-extract").checked;
  setStageButton(btn, true, "加载中…");
  showStageResult(el, [
    "⏳ Loading 开始",
    `  re_extract_pdf = ${reExtract}`,
    "  从 standard/ 提取或读取已有 MD ...",
  ]);
  try {
    const data = await postJSON("/api/loading", { re_extract_pdf: reExtract });
    const ktype = JSON.stringify(data.knowledge_type_distribution || {}, null, 2);
    const parts = JSON.stringify(data.part_distribution || {}, null, 2);
    showStageResult(el, [
      "✅ Loading 完成",
      `  documents_count = ${data.documents_count}`,
      `  knowledge_type 分布:\n${ktype}`,
      `  part 分布:\n${parts}`,
    ]);
    toast(`Loading 完成: ${data.documents_count} 篇文档`, "success");
    await refreshHealth();
  } catch (e) {
    showStageResult(el, ["❌ Loading 失败", `  ${e.message}`], true);
    toast("Loading 失败: " + e.message, "error");
  } finally {
    setStageButton(btn, false, "加载文档");
  }
});

// Indexing 阶段按钮事件
$("pl-indexing-run").addEventListener("click", async () => {
  const btn = $("pl-indexing-run");
  const el = $("pl-indexing-result");
  setStageButton(btn, true, "索引中…");
  showStageResult(el, [
    "⏳ Indexing 开始",
    "  章节感知切块(384/64) + 嵌入 + Node JSON 导出 ...",
  ]);
  try {
    const data = await postJSON("/api/indexing", {});
    showStageResult(el, [
      "✅ Indexing 完成",
      `  spec_nodes_count      = ${data.spec_nodes_count}`,
      `  total_nodes_count    = ${data.total_nodes_count}`,
      `  avg_chunk_length      = ${data.avg_chunk_length}`,
      `  chunk_length 范围     = [${data.min_chunk_length}, ${data.max_chunk_length}]`,
    ]);
    toast(`Indexing 完成: ${data.total_nodes_count} 节点`, "success");
    await refreshHealth();
  } catch (e) {
    showStageResult(el, ["❌ Indexing 失败", `  ${e.message}`], true);
    toast("Indexing 失败: " + e.message, "error");
  } finally {
    setStageButton(btn, false, "切块索引");
  }
});

// Storing 阶段按钮事件
$("pl-storing-run").addEventListener("click", async () => {
  const btn = $("pl-storing-run");
  const el = $("pl-storing-result");
  const rebuild = $("pl-rebuild-store").checked;
  setStageButton(btn, true, "写入中…");
  showStageResult(el, [
    "⏳ Storing 开始",
    `  rebuild = ${rebuild}`,
    "  创建 MilvusVectorStore + 写入规范 Nodes + manifest ...",
  ]);
  try {
    const data = await postJSON("/api/storing", { rebuild });
    showStageResult(el, [
      "✅ Storing 完成",
      `  total_nodes_written  = ${data.total_nodes_written}`,
      `  collection_has_data   = ${data.collection_has_data}`,
    ]);
    toast("Storing 完成,Milvus 写入成功", "success");
    await refreshHealth();
  } catch (e) {
    showStageResult(el, ["❌ Storing 失败", `  ${e.message}`], true);
    toast("Storing 失败: " + e.message, "error");
  } finally {
    setStageButton(btn, false, "写入 Milvus");
  }
});

// 一键重建索引按钮事件
$("btn-rebuild").addEventListener("click", async () => {
  if (!confirm("将顺序执行 Loading(从 PDF 重新提取)→ Indexing → Storing(rebuild collection),可能耗时较久。继续?")) {
    return;
  }
  const btn = $("btn-rebuild");
  setStageButton(btn, true, "重建中…");
  toast("正在一键重建索引(全流程)…");
  try {
    const data = await postJSON("/api/rebuild", {});
    toast(data.message || "索引已重建", "success");
    await refreshHealth();
  } catch (e) {
    toast("重建失败: " + e.message, "error");
  } finally {
    setStageButton(btn, false, "一键重建索引");
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
      top_k: parseInt($("qs-topk").value, 10) || 5,
    });
    setHtml(el, renderAnswer(data.answer) + renderSources(data.sources));
  } catch (e) { setError(el, e.message); }
});

// ---------------------------------------------------------------------------
// 向量检索(纯检索,不调 LLM)
// ---------------------------------------------------------------------------

$("rt-run").addEventListener("click", async () => {
  const el = $("rt-result");
  setLoading(el);
  try {
    const partNum = $("rt-part").value.trim();
    const data = await postJSON("/api/querying", {
      question: $("rt-question").value,
      top_k: parseInt($("rt-topk").value, 10) || 5,
      file_name: $("rt-file").value.trim() || null,
      part_number: partNum ? parseInt(partNum, 10) : null,
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
      top_k: parseInt($("rp-topk").value, 10) || 5,
    });
    const partBadge = `<div class="answer-text">
      <span class="muted">检索范围:</span>
      <span class="badge badge-local">第${data.part_number}部分</span>
    </div>`;
    setHtml(el, partBadge + renderSources(data.sources));
  } catch (e) { setError(el, e.message); }
});

// ---------------------------------------------------------------------------
// 全文总结(SummaryIndex + 两级缓存)
// ---------------------------------------------------------------------------

$("sm-run").addEventListener("click", async () => {
  const el = $("sm-result");
  setLoading(el, "正在遍历全部规范做总结,请稍候…");
  try {
    const data = await postJSON("/api/summary", { question: $("sm-question").value });
    const cacheTag = data.from_cache ? '<span class="badge badge-local">命中缓存</span>' : "";
    setHtml(el, renderAnswer(data.answer) + `<div class="muted">${cacheTag}</div>`);
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
      top_k: parseInt($("sr-topk").value, 10) || 5,
    }),
    signal: streamController.signal,
  }).then(async (res) => {
    if (!res.ok) {
      let detail = `${res.status} ${res.statusText}`;
      try {
        const err = await res.json();
        detail = err.detail || JSON.stringify(err);
      } catch (_) { /* ignore */ }
      throw new Error(detail);
    }
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      // SSE 按行分割;一次 read 可能只包含半行,需要自行拼接。
      lineBuffer += decoder.decode(value, { stream: true });
      const lines = lineBuffer.split("\n");
      lineBuffer = lines.pop(); // 最后一段可能不完整,留到下次
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
      top_k: parseInt($("as-topk").value, 10) || 5,
    });
    setHtml(el, renderAnswer(data.answer) + renderSources(data.sources));
  } catch (e) { setError(el, e.message); }
});

// ---------------------------------------------------------------------------
// 方案编排:自然语言生成质检方案
// ---------------------------------------------------------------------------

$("sc-run").addEventListener("click", async () => {
  const el = $("sc-result");
  const requirement = $("sc-requirement").value.trim();
  if (!requirement) {
    setError(el, "请输入质检需求描述");
    return;
  }
  setLoading(el, "正在检索规范并生成方案,请稍候…");
  try {
    const data = await postJSON("/api/scheme/generate", {
      requirement: requirement,
      context_top_k: parseInt($("sc-topk").value, 10) || 5,
    });
    // 意图识别未命中质检要求时,后端返回 status=rejected + 引导提示,
    // 这里作为友好提示展示,而非当作错误。
    if (data && data.status === "rejected") {
      renderSchemeRejected(el, data);
      return;
    }
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

/** 渲染质检方案结果。 */
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
      <div><b>方案名称:</b>${escapeHtml(scheme.schemeName)}</div>
      <div><b>方案描述:</b>${escapeHtml(scheme.description)}</div>
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

// 意图识别未命中质检要求时,展示友好引导提示(而非红色错误)。
function renderSchemeRejected(el, data) {
  setHtml(el, `
    <div class="answer-text">
      <div>⚠️ ${escapeHtml(data.message || "未识别到质检方案要求")}</div>
      <div class="muted">${escapeHtml(data.suggestion || "请输入具体的质检需求,例如:检测点坐标精度不超过0.5米,编号唯一。")}</div>
    </div>`);
}

// ---------------------------------------------------------------------------
// 初始化
// ---------------------------------------------------------------------------

refreshHealth();
