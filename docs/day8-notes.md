# Day 8 登录与 JWT

## 今日目标
用户持久化、BCrypt 校验、JWT 登录、AI 入口保护。

## 我理解的链路
账号密码 → Controller → AuthService → Repository → BCrypt
→ JWT → Bearer Header → SecurityFilterChain → 业务接口。

## Authentication 与 Authorization
Authentication：待填。
Authorization：待填。
401：待填。
403：待填。

## JWT
sub：待填。
iss：待填。
aud：待填。
iat：待填。
exp：待填。
scope：待填。

Payload 为什么不能存秘密：待填。
为什么解码不等于验签：待填。
为什么 token 过期需要重新登录：待填。

## BCrypt
为什么不存明文：待填。
为什么相同密码的哈希可能不同：待填。
matches 的两个参数：待填。

## 真实运行结果
编译：待填。
用户表：待填。
正确登录：待填。
错误密码：待填。
无 token：待填。
篡改与过期 token：待填。
有效 token 获取 /me：待填。
AI 无 token：待填。
AI 有 token：待填。
自动化测试：待填。

## 问题与排查
现象：
根因：
如何定位：
如何修复：

## 当前边界
本地 dev 账号；没有注册、刷新、主动撤销 token。
FastAPI 仍为内部服务，部署需网络隔离或服务认证。
账号删除不会自动使所有已签发 token 失效。
ddl-auto=update 仅用于本地，后续使用数据库迁移。
Day 7 保留原评测版本，关键词评分仍有局限。

## 五个复盘问题
1. 为什么 login 不要求已有 token？
2. 为什么 /me 不接受用户传来的 userId？
3. 为什么密码用 matches 而不是重新 encode 比较？
4. 为什么无权限请求不会调用 LLM？
5. 为什么 Java .env 要显式加载？

## 下一天
按原始计划学习 knowledge_base、document、conversation 业务模型，
把知识库与当前用户关联，今天不提前实现。