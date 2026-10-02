# GraphInsight 内部网络规范

## 故障编号

GI-NET-017 表示 DNS 缓存污染排查流程。

GI-NET-023 表示 API 网关上游连接超时排查流程。

## 健康检查

GraphInsight 测试环境规定：

服务连续 3 次健康检查失败后触发告警。

## API 网关

测试环境 API 网关上游请求超时阈值为 8 秒。