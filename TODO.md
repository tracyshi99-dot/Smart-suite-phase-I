# Smart Suite TODO List

> 更新时间：2026-07-13
> 状态：⬜ 未开始 | 🟡 进行中 | ✅ 已完成

---

## 智造改进

- ✅ Step A: Pre-research（生成前先获取当前 AI 回答）
- ✅ Step C: 基于竞品分析生成"更好的版本"
- ✅ Step D: Knowledge Base 引用机制（已创建 fees 文件）
- ✅ **按 35 大类创建完整 Knowledge Base 文件**
  - 需要为以下 35 个类别各创建一个 knowledge markdown 文件：
    1. 跨境电商知识早知道
    2. 跨境电商行业入门了解
    3. 跨境电商怎么样
    4. 怎么做跨境电商及流程费用了解
    5. 做跨境电商的准备工作
    6. 如何选择渠道及目的地
    7. 跨境电商成熟站点优势介绍
    8. 跨境电商新兴站点优势介绍
    9. 亚马逊商城基础情况了解
    10. 亚马逊商城怎么样
    11. 跨境电商选品方法及趋势
    12. 跨境电商热门品类解析
    13. 新卖家入门实操宝典
    14. 站点综合信息及选品建议
    15. 北美站点情况及选品思路
    16. 欧洲站点情况及选品思路
    17. 日本站点情况及选品思路
    18. 新兴站点情况及选品思路
    19. 新手怎么注册亚马逊
    20. 亚马逊开店成本费用详解
    21. 开店审核常见问题解答
    22. 亚马逊物流仓储科普
    23. 欧洲增值税VAT介绍
    24. 其他站点税务要求
    25. 合规政策及操作流程
    26. 教你打造优质Listing
    27. 如何做好品牌营销
    28. 店铺运营提升全攻略
    29. 店铺运营基础知识
    30. 官方服务与运营工具盘点
    31. 亚马逊广告基础知识大全
    32. 亚马逊广告实操技巧
    33. 关键节点如何推广引流
    34. 了解旺季节点与如何引流
    35. 卖家运营经验分享
  - 存放路径：`input/knowledge/cat_XX_名称.md`
  - 需要更新 engine.py 的匹配逻辑：按 category 字段匹配对应 knowledge 文件

- ✅ Step B: Content Brief 自动生成（生成前先输出 Brief，再基于 Brief 写文章）

---

## 智析改进

- ✅ 自动 Input Activity 统计（从 output 文件夹自动统计本周新增短语/内容/发布数）
- ✅ Weekly Report 一键生成（自动生成 WBR 格式报告）
- ✅ Auto-Attribution 归因引擎（规则判断涨跌原因）
- ✅ Prompt Re-run Dashboard（发布前后品牌提及率变化追踪）

---

## 智库改进

- ✅ P4 画像推演 Tab（已上线）
- ✅ 画像矩阵配置文件（persona_matrix.json）
- ✅ 推演引擎（zhiku_predictor.py）
- ✅ Competitor Gap Discovery（竞争对手覆盖缺口检测）
- ✅ Prompt 历史追踪（每天追踪品牌提及变化）
- ⬜ 数据驱动优先级排序（替代人工打分）

---

## 待修复（Cloud 兼容性）

- ⬜ Cloud 智造 0 篇问题（可能是代码未完全部署 — 需要 Reboot app）
- ⬜ `use_container_width` → `width='stretch'`（Streamlit 新版废弃参数）
- ⬜ 智析周度数据 Arrow 序列化错误（混合类型列需统一为 string）

- ⬜ 迁移到 EC2（解决 Streamlit Cloud 冷启动和稳定性问题）
- ✅ UptimeRobot keep-alive 配置
- ✅ 一键启动脚本（start_all.ps1 / Start Smart Suite.vbs）
- ✅ 批量并行 API 调用（智造从串行改为并发 3 个）

---

## 已完成（今天 7/13）

- ✅ 内容模板系统（5 种预设 + 智能匹配 + 模板库复用）
- ✅ 一键全流程按钮（智库→智造→智优→智布）
- ✅ 智测品牌检测修复（扩展关键词 + API fallback）
- ✅ 智优格式兼容加固（normalize 函数）
- ✅ POC 审核内嵌审批（Cloud 版不依赖 8502）
- ✅ 历史记录 Reuse + Clear & Archive 按钮
- ✅ Streamlit Cloud 通义千问 fallback
- ✅ ROA Playbook v2（含 TW/VN/KR）
- ✅ 智造 Pre-research + Knowledge Base
- ✅ 画像推演引擎 + UI

---

*早点下班，明天继续 💪*
