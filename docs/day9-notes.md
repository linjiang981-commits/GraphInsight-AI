# Day 9 知识库业务模型与用户隔离

## 今日目标
设计 knowledge_base、kb_document、conversation；
实现知识库 CRUD、状态、分页，以及按用户隔离。

## 与 Day 8 的连接
Day 8 判断请求身份与 AI scope。
Day 9 进一步判断当前用户能否访问某条知识库记录。
JWT 有效不等于可以操作所有人的数据。

## 数据模型
app_users 1 → N knowledge_base。
knowledge_base 1 → N kb_document。
knowledge_base 1 → N conversation。
会话归属由知识库 owner 推导，当前不支持共享知识库。
旧 documents / document_chunks 仍服务原 Python 检索，不自动迁入新模型。

## 新知识
主键：一条记录的唯一身份，名称不替代主键。
外键：确保引用存在，保护关联完整性，不替代用户授权。
索引：帮助按 owner_id / knowledge_base_id 查询，有存储和写入维护成本。
Entity：映射表；Repository：数据库访问；Service：业务规则；
DTO：接口传输字段，避免直接暴露实体关联和内部属性。
枚举用 STRING 保存，重排顺序不会改变旧值的意义；重命名仍需迁移。
LAZY：请求延迟加载关联，不保证绝对没有额外查询。
事务：把数据库操作组织成提交或回滚的整体。
readOnly：读取优化提示，不是权限控制。
脏检查：受管实体发生变化后，JPA 在 flush 时生成更新。
flush：执行待发送 SQL；commit：提交事务，二者不同。
分页：page 从 0 开始；size 为 1～50；固定按 id 倒序。
归档：保留记录；空库删除：物理删除；非空删除：409。

## 接口
POST /api/knowledge-bases → 201
GET /api/knowledge-bases?page=0&size=10 → 200
GET /api/knowledge-bases/{id} → 200
PUT /api/knowledge-bases/{id} → 200
DELETE /api/knowledge-bases/{id} → 204

错误：400 输入错误；401 无有效身份；
404 不存在或不属于当前用户；409 有关联数据或约束冲突。

## 实际验收
- PostgreSQL 建表、索引、外键：待填写。
- 创建、查询、修改、归档、恢复：待填写。
- Alice / Bob 跨用户读改删：待填写。
- 非空删除 409、空库删除 204：待填写。
- Day 8 测试：待填写。
- Day 9 测试：待填写。
- 总测试数、失败数：待填写。
- Git 提交号和 GitHub 同步结果：待填写。
不记录完整 token、真实密码或 .env 内容。

## 我遇到的问题
现象：待填写。
出错层：待填写。
原因：待填写。
修改及验证：待填写。

## 五个复盘问题与参考答案

### 1. JWT 已经验证通过，为什么还要检查 owner_id？
JWT 验证说明请求携带有效身份，不说明这个人拥有所有记录。
例如 Bob 有合法 token，但 Alice 的知识库不属于他。
列表用 findByOwner_Id，详情、修改、删除用
findByIdAndOwner_Id，把记录 ID 与当前用户 ID 同时作为条件。
当前用户 ID 来自已验证 JWT 的 sub，再确认用户存在，
不能使用请求正文里用户自填的 ownerId。
对应：KnowledgeBaseController.ownerId、
KnowledgeBaseRepository、KnowledgeBaseService.ownedBase。

### 2. 外键和 Service 里的“不能删除非空知识库”为什么都要保留？
Service 检查能返回清楚的业务提示，并表达产品删除策略。
但其他代码可能绕过 Service，并发请求也可能在检查后插入子记录。
数据库外键负责最终阻止产生孤儿记录。
外键保证关联完整性，不会判断请求人是否是 owner。
所以业务检查、数据库约束、用户授权解决不同的问题。
对应：实体 JoinColumn、KnowledgeBaseService.delete、
ApiExceptionHandler.dataConflict。

### 3. 为什么更新时没有再次 save？flush 与提交有什么区别？
update 在事务中通过 Repository 取到受管实体，再修改其字段。
JPA 脏检查在 flush 时发现变化，执行 UPDATE，不必重复 save。
flush 只是把 SQL 发给数据库，事务仍可以回滚；
方法正常返回、事务提交后才完成本次提交。
这里 flush 也让 PreUpdate 更新时间在构造响应前生效。
不能把这个规律推广到脱离持久化上下文的任意 Java 对象。
对应：KnowledgeBaseService.update、
KnowledgeBase.onUpdate。

### 4. 为什么不直接返回 KnowledgeBase Entity，还要 Response DTO？
Entity 表达数据库结构，可能包含 User 关联、内部字段与懒加载对象。
直接序列化可能暴露密码哈希等属性，或触发额外查询和关联循环。
DTO 明确允许返回的字段，使 API 不必跟数据库内部结构同步变化。
请求 DTO 同样限制用户可以填写什么，创建时不包含 ownerId。
对应：KnowledgeBaseCreateRequest、KnowledgeBaseResponse.from。

### 5. ARCHIVED 和删除有什么区别？文档为什么默认 PENDING？
ARCHIVED 保留知识库及关联数据，当前仍可查看和重新启用。
DELETE 对空知识库执行物理删除，非空返回 409。
PENDING 只表示文档元数据登记，不能宣称解析、embedding 已完成。
后续真实处理链才推动 PROCESSING → READY / FAILED。
今天只建立状态字段，没有实现异步任务、重试或上传。
对应：三个状态枚举、实体初始值、Service.delete。

## 当前边界
知识库管理 API 做了用户隔离。
旧 RAG 尚未按 knowledgeBaseId 隔离，不能宣称完成多租户 RAG。
没有上传接口、异步处理、message 持久化、共享权限。
没有自动级联删除文件、向量、文档和会话。
本地仍用 ddl-auto=update，未来引入显式数据库迁移。
H2 测试不能代替真实 PostgreSQL 验收。

## 下一天
按原计划进入文件上传与处理状态：
将文件与 knowledgeBaseId 关联，检查归属与归档状态，
明确业务文档 ID 和索引文档 ID 的映射，再接解析、向量化与状态回写。