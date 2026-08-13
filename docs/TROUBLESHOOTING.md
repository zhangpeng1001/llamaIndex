# 常见问题与排查

## 找不到 `llama-demo` 命令

确认已经激活虚拟环境并执行过可编辑安装：

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

也可始终使用 `python -m llamaindex_demo.cli ...`。

## PowerShell 不允许运行 Activate.ps1

不必修改全局策略，直接使用虚拟环境内的解释器：

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m llamaindex_demo.cli quickstart
```

## OpenAI 模式提示缺少密钥

复制 `.env.example` 为 `.env`，填写 `OPENAI_API_KEY`。`.env` 已被 `.gitignore` 忽略。也可在当前 PowerShell 会话临时设置 `$env:OPENAI_API_KEY="..."`。

## 修改文档后回答还是旧内容

已有 `storage/` 会被直接加载。使用 `--rebuild` 重新摄取：

```powershell
llama-demo --rebuild quickstart
```

## 切换模型后出现向量维度或检索异常

Embedding 模型变更后必须 `--rebuild`。不要用一个模型建立的 storage 配合另一个模型查询。

## 中文检索结果不够好

默认 local 哈希模型只依据字面字符重合，不能理解同义词，这是预期行为。切换真实语义 Embedding，或自行接入本地 HuggingFace/BGE 模型。随后调整切块、Top-K，并用 `evaluate` 比较结果。

## 回答看起来像原文拼接

local 模式的 `LocalExtractiveLLM` 本来就是抽取式教学替身。它证明查询链路可运行，但没有真正生成与推理能力。切换 `openai` 模式即可观察差异。

## Windows 安装时报文件正在使用

关闭正在使用同一虚拟环境的 Python、Jupyter 或编辑器测试进程，然后重试。始终优先在项目 `.venv` 中安装，避免与全局 Anaconda 环境互相影响。

## Windows 终端中文乱码

源码和文档均为 UTF-8。若旧版 PowerShell 或重定向工具显示乱码，可在当前会话执行：

```powershell
chcp 65001
$env:PYTHONUTF8="1"
```

也可以改用 Windows Terminal 或 PowerShell 7。

