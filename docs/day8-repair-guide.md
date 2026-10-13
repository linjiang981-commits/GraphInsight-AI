# Day 8 修复说明与学习入口

当前代码已经修复到可以继续学习和运行实验的状态。学习时按下面的顺序阅读代码与执行命令；不需要再次照旧教程覆盖文件。本文不会把已有代码当作你已经掌握的知识。

## 修复了什么

| 文件 | 原问题 | 修复后 |
|---|---|---|
| `ai-service/app/services/bm25_service.py` | 缺少 build_index；私自读取旧 JSON | 接收统一字典列表；保留 ID 和元数据；统一分词 |
| `ai-service/app/services/retrieval_service.py` | 调用不存在的方法；把字典当二元组读取 | 旧内存 Demo 使用新接口；仍只检索旧 JSON |
| `ai-service/app/services/vector_store.py` | BM25 没有读取数据库语料的入口 | 新增 list_chunks；向量分数相同时按 ID 排序 |
| `ai-service/app/services/database_retrieval_service.py` | JSON ID 与数据库 ID 混用 | 两路都使用 document_chunks；每次 Hybrid 请求刷新小型 BM25 索引 |
| `ai-service/app/services/hybrid_retriever.py` | 原始分数尺度不同却直接加权 | 使用 RRF；同 ID 对应不同内容时立即报错 |
| `ai-service/app/services/rag_service.py` | 正式 RAG 只有 Vector | 支持 vector/hybrid；共用 Prompt 和生成流程；返回 Chunk ID |
| `ai-service/app/schemas/rag.py`、`ai-service/app/main.py` | 请求无法选择检索方式 | 新增 retrieval_mode；非法模式、空白问题被拒绝 |
| `ai-service/app/services/evaluation_service.py` | 三个脚本评分规则不一致 | 共用规则；处理空格和 Markdown；根据 answerable 评分 |
| `ai-service/scripts/evaluation_runner.py` | 对照脚本另写 Prompt、丢失证据、覆盖历史 | 复用 RagService；保存完整证据、配置与失败数；输出带时间戳 |
| `ai-service/scripts/rescore_evaluation.py` | 无法单独修正旧答案评分 | 离线重新评分，不调用数据库或 LLM，不覆盖旧文件 |

`/api/retrieval/search` 仍是旧 JSON 内存检索教学接口；数据库 RAG 使用 `/api/rag/query`。两套数据不再混在一个检索结果中。

## 第 1 步：恢复环境

打开 Docker Desktop，然后执行：

```powershell
cd D:\projects\GraphInsight-AI
docker compose -f .\docker\docker-compose.yml up -d
docker ps
git status
```

这次修复尚未替你执行 Git commit，因此看到修改文件是正常的。不要为了让状态干净执行 reset。

激活 Python：

```powershell
cd D:\projects\GraphInsight-AI\ai-service
.\.venv\Scripts\Activate.ps1
python -c "import sys; print(sys.executable)"
python -m scripts.db_test
```

预期看到项目虚拟环境路径、PostgreSQL 版本、vector 扩展。若 PowerShell 无法激活，后续直接用 `.\.venv\Scripts\python.exe` 替代 `python`。

## 第 2 步：先理解 BM25 的输入输出

打开 `D:\projects\GraphInsight-AI\ai-service\app\services\bm25_service.py`。

按顺序阅读 tokenize、build_index、search。输入是带 id/content 的字典，输出保留所有字段并增加 score。英文编号和缩写保留为完整 token，中文暂按字切分。

```powershell
python -m scripts.bm25_test
```

预期 GI-NET-023 命中样例 ID 2，最后显示 `BM25 CHECKS PASSED`。这一步不访问 LLM，也不连接数据库。

不要把 BM25 分数理解成概率。小型语料下分数可能为零或负数；当前实现按词项交集排除完全无匹配候选，不简单删除所有非正分。

## 第 3 步：理解数据库 Chunk 身份

打开 `D:\projects\GraphInsight-AI\ai-service\app\services\vector_store.py` 的 list_chunks，然后阅读 `database_retrieval_service.py`。

`document_id` 是文档 ID，`id` 是数据库 Chunk ID，`chunk_index` 是文档内片段序号。两路中的同一个 id 必须对应同一份内容。旧 network_documents.json 的 ID 不进入数据库 RAG。

运行已有的向量基线检查：

```powershell
python -m scripts.database_retrieval_test
```

检索结果应包含真实 document_name 和 chunk_index。这一步加载本地 Embedding 模型、读取数据库，不调用生成模型。

## 第 4 步：读懂 RRF，再看混合结果

打开 `D:\projects\GraphInsight-AI\ai-service\app\services\hybrid_retriever.py`。

每一路贡献为 `1 / (60 + rank)`，rank 从 1 开始。未出现在某一路时，那一路贡献为零。最终按贡献总和排序；相同 ID 只保留一份证据。

参数区别：每路候选数 candidate_k 当前为 max(6, top_k × 2)，最终给 LLM 的数量是 top_k，公式中的 60 是 rrf_k。它们不是同一个参数。

```powershell
python -m scripts.hybrid_test
```

逐题观察 Vector Top-6、BM25 Top-6、RRF Top-3。脚本会检查结果 ID 对应的内容及元数据，最后显示 `IDENTITY CHECKS PASSED`。这个检查不等于答案正确性评测，还要亲眼看正确事实是否进入 Top-3。

修复时实际数据库有 13 个 Chunk，来自三份样例文档。四个检查问题的正确证据都进入了 RRF Top-3。后续修改语料可能改变结果。

## 第 5 步：运行离线回归检查

```powershell
python -m unittest discover -s tests -v
```

17 个测试覆盖编号检索、空语料、数据身份、融合去重、索引刷新、模式切换、评分误判、失败计数及 API 结构。模型、数据库与生成调用在测试中使用替身，不消耗 LLM API。

## 第 6 步：启动 FastAPI

```powershell
python -m uvicorn app.main:app --reload
```

保持此终端运行。在第二个 PowerShell 终端执行：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

应返回 status=ok。代码修复已验证真实应用初始化和真实 Embedding 检索；没有执行真实 LLM 回答验证。

## 第 7 步：用一个问题体验两种 RAG

下面每次正常请求会调用一次 LLM，按你的 API 配置产生消耗。先在第二个 PowerShell 终端请求 Vector：

```powershell
$payload = @{
    question = 'GI-NET-023对应什么故障排查流程？'
    top_k = 3
    temperature = 0.1
    retrieval_mode = 'vector'
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri 'http://127.0.0.1:8000/api/rag/query' `
    -Method Post `
    -ContentType 'application/json; charset=utf-8' `
    -Body ([System.Text.Encoding]::UTF8.GetBytes($payload))
```

再请求 Hybrid：

```powershell
$payload = @{
    question = 'GI-NET-023对应什么故障排查流程？'
    top_k = 3
    temperature = 0.1
    retrieval_mode = 'hybrid'
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri 'http://127.0.0.1:8000/api/rag/query' `
    -Method Post `
    -ContentType 'application/json; charset=utf-8' `
    -Body ([System.Text.Encoding]::UTF8.GetBytes($payload))
```

检查 answer 和 sources。每条 source 有 id、rank、document_name、chunk_index、score、content。两种模式的 score 含义不同，不能拿 Vector score 与 RRF score 直接比较大小。省略 retrieval_mode 时仍使用 Vector 基线。

## 第 8 步：先读旧结果重新评分

已生成 `D:\projects\GraphInsight-AI\ai-service\data\evaluation\vector_vs_hybrid_rescored.json`。原始 vector_vs_hybrid.json、rag_eval_results.json、llm_only_results.json 保持不变。

本次对旧答案的规则重评分：Vector 12/12，Hybrid 10/12。旧的四道正确拒答不再被全部判错，`API 网关` 与 `8 秒` 的格式误判得到纠正。

这些数字不是修复后重新调用模型的结果，也不证明新系统达到了对应准确率。旧 Hybrid 的两道私有知识题仍然是真的拒答。

想自己再执行一次离线重评分，在 ai-service 目录运行：

```powershell
python -m scripts.rescore_evaluation .\data\evaluation\vector_vs_hybrid.json
```

默认另存带时间戳的文件，不调用 LLM。不要把输出参数指回原始文件，脚本会拒绝覆盖已有文件。

## 第 9 步：理解评分边界

打开 `D:\projects\GraphInsight-AI\ai-service\app\services\evaluation_service.py`。

answerable=true 时执行规范化后的关键词匹配；false 时判断拒答短语。按 answerable 字段区分，而不是依赖题目 ID 前缀。

这些仍是简单规则：包含“8秒”不保证整句话事实正确；包含“无法确定”后继续编造也可能误判。指标字段 answer_accuracy 为兼容原有命名保留，实际含义是规则评分通过率。报告必须配合人工核查。

Document Hit@3 只是命中文件名，不代表返回的那个 Chunk 一定包含答案。未知题没有可标注证据，不纳入检索命中率。密码题还混合了安全拒绝因素，本轮保留原数据集便于比较，未来单独改版再更换题目。

## 第 10 步：正式重新运行对照实验

保持数据库和模型配置不变，实验期间不要重新入库。在 ai-service 的已激活终端执行：

```powershell
python -m scripts.evaluate_retrieval_compare
```

12 道题 × 2 个模式，正常需要 24 次 LLM 调用。两个方法共用同一个 RagService 和评分规则，top_k=3、temperature=0.1。

输出文件名为 `vector_vs_hybrid_<UTC时间戳>.json`，不会覆盖原来的结果。文件使用统一的 config/metrics/results 结构；metrics 按模式分组。每个问题完成后保存一次，异常请求计入失败数和总体分母，不会被悄悄丢弃。

LLM Only 或单独 Vector 评测仍使用原来的命令，各需要 12 次正常调用：

```powershell
python -m scripts.evaluate_llm_only
python -m scripts.evaluate_rag
```

新结果同样带时间戳。若只检查参数而不运行模型，可以执行：

```powershell
python -m scripts.evaluate_retrieval_compare --help
```

## 第 11 步：解读报告

- answer_accuracy：所有已尝试问题上的规则通过率，失败请求算未通过。
- failed：请求失败数；大于零时先处理服务错误，再解释回答效果。
- category_accuracy：按 private_fact、semantic_paraphrase、unanswerable 切片。
- refusal_accuracy：未知问题规则通过率。
- retrieval_hit_at_3_successful：成功请求中有答案问题的文件级命中率，分母另记为 retrieval_evaluated_count。
- average_latency_successful：成功请求的检索与生成耗时，不含初始化与预热。
- config.corpus_unchanged：实验前后语料指纹是否相同；false 时本轮比较无效。
- completed：所有题目是否尝试完成；中途停止的结果仍可排查，但不是完整报告。

保存完整 sources 用于回看当时证据。只有 ID 的旧结果不能凭空恢复当时的 Chunk，因此离线重评分报告不会编造旧检索命中率。

## 第 12 步：记录你的理解并提交

至少写三个案例：格式误判、旧 Hybrid 私有知识失败、修复后实际检索到正确证据。再用自己的话说明为何两路 ID 必须一致，以及为何 RRF 不直接相加原始分数。

```powershell
cd D:\projects\GraphInsight-AI
git diff --stat
git diff
git check-ignore ai-service/.env
git status
```

检查完成后按你自己的提交节奏暂存和 commit。本次修复没有自动替你提交或推送。

## 当前实现范围

BM25 每次 Hybrid 请求从数据库重建内存索引，适合当前 13 个 Chunk 的 Demo；大语料需要版本化索引和刷新机制。实验期间保持语料静止，前后指纹检查并不等于数据库事务级快照。

保留了已有文档解析、入库和 Embedding 模型，没有添加 Reranker、LangChain、GraphRAG 或 Agent。后续按学习计划展开时，先读懂现有 Hybrid 检索，再决定是否增加优化。
