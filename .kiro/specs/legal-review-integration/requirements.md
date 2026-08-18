# Legal Review Integration — 智优 × Amazon Q Legal Chatbot

## 概述

在 Smart Suite 内容生产流水线中，智优（内容优化）完成后，增加一个自动化 Legal 审核环节。内容提交到 QuickSight Space 中的 Amazon Q Legal Chatbot 进行合规审核，审核通过后才标记为 final 版本。

## 流程定位

```
智库 → 智造 → 智优 → 【Legal Review (NEW)】→ 智布
                         ↑                    ↓
                         └── 修改建议回传 ←──┘
```

---

## 需求列表

### REQ-1: 智优输出自动触发 Legal 审核
- **描述**: 智优完成内容优化后，系统自动将优化后的内容提交给 Legal Chatbot 审核
- **输入**: 智优输出的文章全文（Markdown/文本格式）
- **触发条件**: 智优标记内容为 `optimized` 状态时

### REQ-2: 与 Amazon Q Legal Chatbot 对接
- **描述**: 通过 Amazon Q 的 Q&A 界面（或 API）将内容提交审核
- **对接方式**: QuickSight Space (https://us-east-1.quicksight.aws.amazon.com/sn/account/amazonbi/spaces/125b87c5-60e2-477a-b5ff-bdac0e609c55)
- **输入格式**: 文章全文或文件链接均可
- **备注**: 当前确认是通过 Q&A 界面提问，API 能力待确认

### REQ-3: 解析 Legal 审核结果
- **描述**: 接收并解析 Legal Chatbot 返回的审核结果
- **结果类型**:
  - ✅ **PASS** — 无合规问题，内容可发布
  - ⚠️ **REVISE** — 有具体修改建议，需修改后重审
  - ❌ **REJECT** — 严重合规问题，需人工介入
- **返回内容**: 具体修改建议（文本）

### REQ-4: 审核通过 → 标记为 Final
- **描述**: Legal 审核通过后，内容状态从 `optimized` 变为 `legal_approved`（final）
- **输出**: 内容可进入智布发布流程

### REQ-5: 审核未通过 → 自动/手动修改循环
- **描述**: 审核返回修改建议时，需要回传给智优进行修改
- **选项 A（自动）**: 智优根据修改建议自动修正，再次提交审核（最多 N 轮）
- **选项 B（人工）**: 将修改建议展示给用户，用户确认修改后重新提交
- **最大重试次数**: 3 轮自动修改，超过后转人工

### REQ-6: 审核状态可视化
- **描述**: 在前端（智优页面或独立 Legal Review 页面）展示审核状态
- **展示内容**:
  - 当前审核状态（待审核/审核中/通过/需修改/拒绝）
  - Legal 反馈的具体修改建议
  - 审核历史（每轮提交和反馈）

---

## 技术约束

| 项目 | 说明 |
|------|------|
| Legal Chatbot 位置 | QuickSight Space (Amazon Q) |
| 当前对接方式 | Q&A 界面（手动），API 待确认 |
| 输入格式 | 文本/链接均可 |
| 输出格式 | 文本修改建议 |
| 认证 | AWS IAM (amazonbi account) |

---

## 待确认项

- [ ] Amazon Q 在 QuickSight Space 是否有可调用的 API（如 `amazon-q:chat` 或 Bedrock Agent）？
- [ ] Legal Chatbot 的审核标准/知识库是什么？（法律条款、品牌指南、平台规则？）
- [ ] 审核延迟预期（实时返回 vs 需要排队等待）？
- [ ] 是否需要区分不同站点/语言的 Legal 审核规则？
- [ ] 自动修正循环的容忍度（允许几轮自动修改？）

---

## 优先级

| 阶段 | 内容 | 优先级 |
|------|------|--------|
| P0 | 确认 Amazon Q API 可调用性 | 🔴 Blocker |
| P1 | 智优 → Legal 提交流程 | 高 |
| P1 | Legal 结果解析 + 状态流转 | 高 |
| P2 | 自动修改循环 | 中 |
| P3 | 前端审核状态可视化 | 低 |
