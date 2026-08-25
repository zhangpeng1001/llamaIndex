# 旧版 `/api/scheme/generate` 方案生成实现详解

> 历史说明：本文描述的是精简改造前的复杂方案生成链路，仅用于理解旧设计与排查历史问题。
> 当前运行实现见 [05_scheme_simple_implementation.md](05_scheme_simple_implementation.md)，实际链路为
> `src/server.py` → `src/scheme.py` → `src/scheme_simple.py`，不再调用本文所述的
> `qualityScheme` 方案生成、查询分解和检查项检索模块。

## 1. 结论先说

当前这条链路的**真实执行路径**是：

`src/server.py` 的 `/api/scheme/generate` → `src/scheme.py` 的 `run_scheme_generate()` → `qualityScheme/scheme_generator.py` 的 `generate_scheme()` → `query_decomposer.py` / `metadata_filter.py` / `check_items_indexer.py` → 结构化结果。

需要特别注意：代码里虽然保留了 `scheme_intent.recognize_scheme_intent()`，但 `src/scheme.py` 里这一步已经被注释掉了，所以**当前实际不会先做“是否为质检需求”的拒绝判断**。这一点和项目里的架构说明存在轻微偏差。

## 2. 源码定位

- `E:\project\agent\llamaIndex\src\server.py:496-515`
- `E:\project\agent\llamaIndex\src\scheme.py:45-138`
- `E:\project\agent\llamaIndex\qualityScheme\scheme_generator.py:205-499`
- `E:\project\agent\llamaIndex\qualityScheme\query_decomposer.py:352-478`
- `E:\project\agent\llamaIndex\qualityScheme\metadata_filter.py:142-314`
- `E:\project\agent\llamaIndex\qualityScheme\check_items.py:31-376`
- `E:\project\agent\llamaIndex\qualityScheme\check_items_indexer.py:56-274`

## 3. 路由层做了什么

`/api/scheme/generate` 的请求体是 `SchemeRequest`，只有两个字段：`requirement` 和 `context_top_k`。

路由层先做两次前置校验：

1. `require_runtime()`：确认 `config / llm / embed_model` 已经在 startup 阶段装配完成。
2. `require_index()`：确认 `index` 已经可用，也就是 `Storing` 阶段已经完成。

如果 `requirement` 为空，会直接返回 400，而不是交给模型猜。

真正的方案生成放在 `asyncio.to_thread(...)` 里执行，原因很直接：`generate_scheme()` 里有检索、LLM 调用和结构化解析，都是同步重活，不能卡住 FastAPI 事件循环。

## 4. `run_scheme_generate()` 只是薄封装

`src/scheme.py` 里的 `run_scheme_generate()` 做的事很少：

1. 收到 `index / llm / requirement / context_top_k`。
2. 直接调用 `generate_scheme(...)`。
3. 再用 `scheme_to_dict(...)` 转成前端更容易消费的字典。

这里保留了意图识别的设计说明，但当前代码把那段逻辑注释掉了，所以现在它不是“先识别、再生成”，而是“直接生成”。

## 5. 核心生成器在做什么

`qualityScheme/scheme_generator.py` 是真正的业务中枢，核心分成四步：

### 5.1 先把输出结构固定住

它定义了两个 Pydantic 模型：

- `CheckItem`：单个检查项，包含 `checkCode / checkName / dataName / params`
- `QualityScheme`：最终方案，包含 `schemeName / description / checkItem[]`

这一步的作用不是“写样子”，而是把 LLM 的自由输出约束成结构化数据，后面才能做白名单校验和参数归一化。

### 5.2 再把 Prompt 约束死

`PROMPT_TEMPLATE` 明确要求：

- `checkCode` 只能从候选项里选，不能自造
- `dataName` 必须放顶层
- `params` 只能放规则参数，不含 `dataName`
- 参数值不确定时填 `null`

这套约束是“提示词约束 + 代码后处理”双保险，不把希望只压在模型上。

### 5.3 先检索，再生成

`_retrieve_for_scheme()` 是生成前的关键准备：它会对每个子意图分别做两类检索：

- 规范条款上下文：用来推断字段名、阈值、坐标系等
- 检查项候选项：只给 LLM 看少量最相关的检查项

每个子意图都单独检索，然后把结果去重合并。这样做的目的很明确：复合需求不会因为整句检索而漏项。

这里还有一个参数换算细节：`context_top_k` 并不是原样下传，而是先算成
`per_sub_k = max(context_top_k // 2 + 1, 2)`。也就是说，默认 `context_top_k=5`
时，每个子意图实际拿到 3 条规范上下文，避免上下文过短。

### 5.4 最后再做强校验

LLM 生成完后，代码不会直接信任结果，而是继续做：

- `checkCode` 是否在 27 项字典里
- `checkCode` 是否在本次候选白名单里
- 检查项数量是否超上限
- `checkName` 是否替换成标准名称
- `dataName` 是否归一化到顶层
- `params` 是否把数组转成逗号字符串
- 缺失参数是否补 `None`

这一步保证了输出能被下游系统稳定消费。

## 6. 查询分解：为什么要先拆句子

`query_decomposer.py` 解决的是“用户一句话里有多个检查要求”的问题。

它先用 `INTENT_TYPES` 做意图枚举，把“唯一、必填、坐标系、碎线、值域、时间有效性”等语义映射到对应检查项类别，再让 LLM 输出 `DecomposedQueryPydantic`。

如果 LLM 失败，代码会退回规则兜底：

- 先猜 `data_name`
- 再按关键词匹配 intent
- 最多生成 3 条，避免兜得太散

这也是为什么方案数不是“随便多”，而是受子意图数量约束的。

## 7. 检索层：不是普通向量检索

`metadata_filter.py` 做了三件很实在的事：

1. 用 `MetadataFilters` 先缩小范围。
2. 默认启用 `hybrid` 检索，也就是 Dense + BM25。
3. 再做 `post_filter`，补掉 Milvus 侧不方便表达的条件。

`retrieve_check_items()` 只查 `doc_type=check_item` 的节点，也就是 27 项检查项字典。

`retrieve_quality_context()` 只查真实规范文档，并按 `quality_rule → field_rule → 不限制` 三级渐进召回，优先拿最有用的条款。

这里还有一个细节：`retrieve()` 会把 `similarity_top_k` 乘 2 先多取一点，再过滤。这样可以减少过滤后数量不够的问题。

如果前置检索完全没拿到检查项候选，`generate_scheme()` 还会继续兜底：先根据子意图的
`intent_type` 去 `INTENT_TYPES` 里反推允许的 `checkCode`，再不行就放开到全部 27 项。
这不是理想路径，但能保证极端情况下不会输出空方案。

## 8. 检查项为什么能被单独检索

`check_items_indexer.py` 把检查项字典也做成了可检索节点：

- `doc_type = check_item`
- `part_number = 0`
- `check_code / check_name / check_desc / param_names_str` 都写进 metadata
- 语义文本里额外塞了别名词，比如“编号唯一”“必填”“不重复”

这就解释了为什么模型不用看完整 27 项表，也能先命中候选项。

`format_top_check_items_for_prompt()` 负责把这些 TopN 候选项整理成 prompt 表格，再补上每个候选项的参数说明，让 LLM 知道参数该怎么填，而不是只看到一个名字。

## 9. 检查项字典本身怎么来的

`check_items.py` 里有 `_RAW_CHECK_ITEMS`，实际就是 27 项预定义字典。

它做了两件事：

- 把 `checkParam` 解析成 `param_names`
- 用 `CHECK_ITEM_BY_CODE` 做 O(1) 查询和校验

`format_check_items_for_prompt()` 会把每项的 `checkCode / checkName / checkDesc / 参数说明` 展开成可读文本，给意图识别模块或其他 prompt 使用。

## 10. 当前实现和设计文档的差异

项目架构文档里还画着“先意图识别，再生成方案”的链路，但当前源码里这一步已经没有实际执行。

所以现在的真实行为是：

1. 只要 `requirement` 非空，就继续走方案生成。
2. 不会因为“不是质检需求”而提前拒绝。
3. 仍然保留了 `scheme_intent.py`，以后想恢复拒绝逻辑，只要把那段注释打开即可。

## 11. 一句话总结

这套实现不是“让 LLM 直接编方案”，而是“先拆需求，再检索候选，再让 LLM 在很小的候选集合里做结构化裁决，最后用代码兜底纠偏”。

这也是它比纯 prompt 方案稳得多的原因。
