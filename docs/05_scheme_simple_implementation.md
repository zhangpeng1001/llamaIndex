# 精简版方案生成实现说明

## 目标

`/api/scheme/generate` 现在使用一条独立、可追踪的方案生成链路：

`src/server.py` → `src/scheme.py` → `src/scheme_simple.py`

其中 `server.py` 的路由、请求参数和返回结构都没有变化。`scheme.py` 只保留兼容入口，全部业务实现集中在 `scheme_simple.py`；这条链路不导入 `qualityScheme` 中的方案生成、查询分解、检查项检索或元数据过滤代码。

## 执行流程

1. 接收 `requirement` 和 `context_top_k`；空需求仍由 API 路由返回 400，`context_top_k` 小于 1 时按 1 检索。
2. 调用一次 `llm.complete()` 改写需求，得到更适合检索规范条款的一句话查询。改写失败、为空或超过 500 字时，直接使用原始需求继续执行。
3. 用改写词对当前 Milvus 索引调用 `index.as_retriever()`。优先使用 `hybrid`；如果旧 collection 没有稀疏向量字段，则自动改用普通向量检索。
4. 将命中的规范条款、原始需求、改写词和全部检查项字典组装为一个 Prompt，再调用一次 `llm.complete()` 生成方案 JSON。
5. 解析 JSON 后按本地检查项字典做最终校验：非法 `checkCode` 会删除，名称会改成标准名称，`dataName` 会提升到顶层，额外参数会删除，缺失参数补为 `null`，列表参数转为英文逗号字符串。所有检查项都非法时抛出清晰异常，避免返回不可执行方案。

## 检查项配置

检查项不再进入 Milvus。唯一来源是 [scheme_check_items.json](../src/scheme_check_items.json)，目前包含 27 项，结构为：

```json
{
  "checkCode": "QualityCheckUniqueValue",
  "checkName": "字段唯一值检查",
  "checkDesc": "检查字段值是否唯一不重复",
  "paramNames": ["fieldNames"]
}
```

`paramNames` 是该检查项允许写进 `params` 的参数名。修改 JSON 后重启服务即可加载新配置；文件缺失、JSON 损坏、必要字段缺失、重复编码或重复参数名都会给出明确的 `ValueError`。

`GET /api/scheme/check-items` 仍然返回 `checkCode`、`checkName`、`checkDesc`、`checkParam` 等原有前端字段，其中 `checkParam` 由 `paramNames` 动态转换为 JSON 字符串。

## 排查方式

INFO 日志记录需求改写结果、检索模式、命中条款的文件/章节/分数/摘要，以及非法编码和删除参数。将 `src.scheme_simple` 的日志级别调到 DEBUG 后，还能看到完整改写 Prompt、规范上下文、生成 Prompt 和模型原始输出。

旧链路的阅读分析保留在 [04_scheme_generate_implementation_analysis.md](04_scheme_generate_implementation_analysis.md)，它描述的是替换前实现，可用于对照。
