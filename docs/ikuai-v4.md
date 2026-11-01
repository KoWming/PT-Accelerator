# 爱快 4.0 DNS 联动

远程同步管理新增 `4.0（HTTPS / API Token）` 模式，原有用户名 / 密码模式保持可用。

## 配置

1. 在爱快后台生成具有 DNS 代理规则读取和写入权限的 API Token。
2. 在 PT-Accelerator 的远程同步管理中选择 4.0，填写路由器的 HTTPS 管理地址和 Token。
3. 默认验证 HTTPS 证书。如果设备使用尚未受信任的自签名证书，可关闭“验证 HTTPS 证书”；也可在容器中配置受信任 CA（HTTPX 支持 `SSL_CERT_FILE`）。
4. 点击测试连接，保存配置，再执行一次立即同步。

规则同步与实际 DNS 应答是两项验收。请在爱快后台启用相应 DNS 代理服务，并确保客户端实际使用爱快提供的解析服务。API 测试成功不代表 DNS 服务已经启用；程序不会自动修改路由器的全局 DNS 开关。

Token 通过已有的凭据加密机制保存，查询配置只返回掩码。它不应写入源码、Dockerfile 或镜像。

## 同步行为

- 手动同步与 Hosts 更新管线共用同一个服务工厂。
- 使用 `/api/v4.0/network/dns/proxy/rules`，通过 Bearer Token 认证。
- 分页读取规则，读取失败时停止同步。
- 兼容只识别数值 `limit`、忽略 `page/page_size` 的固件；检测到重复页时改为完整快照读取，并验证记录 ID 与总数，避免把重复页误判为重复规则。
- 使用精确域名，备注为 `PT-Accelerator`；不自动转换为通配符。
- 缺失时新增，地址变化时原位更新，地址和启用状态一致时跳过写入。
- 目标精确域名已有非本程序管理的规则或重复规则时，本轮同步停止，由用户处理冲突。
- 不删除其他规则，也不自动清理不再出现在优选结果中的旧规则。
- 写入后回读确认所有目标记录。多条写入不具备事务性，中途失败会报告失败，已完成的写入可在重试时复用。
- 支持 IPv4 / IPv6 数据处理；旧版 TXT 导入导出在 4.0 模式下不可用。

## 本地验证与镜像

```bash
python -m pip install -r requirements.txt pytest
python -m pytest -q
cd frontend
npm ci
npm run build
cd ..
docker build -t pt-accelerator:ikuai-v4-local .
docker save -o pt-accelerator-ikuai-v4-local.tar pt-accelerator:ikuai-v4-local
```

将镜像归档复制到 NAS 后执行：

```bash
docker load -i pt-accelerator-ikuai-v4-local.tar
```

在现有 Compose 配置中将 `image` 改为 `pt-accelerator:ikuai-v4-local`，保留原有卷挂载、网络和环境变量，并设置 `pull_policy: never`。重建容器前备份配置；新增字段兼容旧配置，但降级前仍建议保留备份。

验收可使用临时 `.invalid` 域名和文档保留 IP，依次验证规则新增、查询、更新、启停和删除，再查询实际 DNS 应答，最后清理测试规则。IPv6 和各固件版本应分别验证。
