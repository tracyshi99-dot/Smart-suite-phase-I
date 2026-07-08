---
inclusion: manual
---

# 智库重构 — 待办事项 (2026-07-02 更新)

## 今日已完成 ✅ (7/2)

1. ✅ 页面索引重排（智测插入后所有页面 +1）
2. ✅ 智测独立页面（_page_idx == 2）完整实现
3. ✅ 导航条 PIPELINE_STEPS 加入智测
4. ✅ 智测→智造 只传选中的 gap 短语（reset 其他）
5. ✅ 智预 lifecycle 改为 AI 动态生成（不再固定列表）
6. ✅ 智预 lifecycle 加 AI 平台选择（全部9个平台）+ 阶段下拉 + "全部"选项
7. ✅ 智析去掉智测 tab（已独立）
8. ✅ 智析去掉智预的竞争壁垒价值矩阵
9. ✅ 智析 Gap tab 加入智测数据展示
10. ✅ Tab 改名：引用追踪总表 + 检索短语引用详情
11. ✅ 检索短语引用详情 tab 加品牌提及率列 + 类别筛选

## 待完成 ❌

### 高优先级

1. ❌ **检索短语引用详情 tab 完善**：
   - 加类别筛选的 filter 逻辑（已有下拉，需连接到 df_gap_show）
   - summary 表加 35 大类各自对应的检索短语数量和比例

2. ❌ **智析里的智测 tab 内容已删，确认无残留引用**

3. ❌ **P2 Tab 非 SEO 来源的上传 merge 逻辑完善**

### 中优先级

4. ❌ 智预从智析 tab 是否需要也独立？（当前保留在智析里）
5. ❌ 校准算法实现（B1 跨平台共识、B2 类别匹配自动化、B3 时效性检测）
6. ❌ 去重算法优化（语义相似度 > 85% 合并）
7. ❌ 总览 wiki 英文版加智测 section

### 低优先级

8. ❌ Harmony 前端同步更新
9. ❌ 全面英文翻译（内部内容）
10. ❌ TODO 文件自身清理

## 已完成 ✅

1. ✅ 导航顺序调整：智库 → 智测 → 智造 → 智优 → 智布 → 智传 → 智析 → 智中枢
2. ✅ 导航列表更新（中英文）
3. ✅ tool_map_idx 更新
4. ✅ 智库① 短语产出改为按优先级分 Tab（P1/P2/P3）
5. ✅ P1: A1 下拉联想上传 + A2 逆向召回(单条+批量) + A3 社区提问上传
6. ✅ P2: 下拉选来源类型 + SEO/SEM裂变（带数量选择）
7. ✅ P3: AI扩写 + 词根扩展（带数量选择）+ 手动输入
8. ✅ 智库② 校准+去重面板（基础框架）
9. ✅ 智库③ 人工选取/修改（可编辑表格）
10. ✅ Steering 文件：pipeline-flow-rules.md、phrase-accuracy-validation.md、reverse-recall-rules.md、zhiku-source-c.md、zhiyu-forecaster.md、zhiku-ui-spec.md

## 待完成 ❌

### 高优先级（当前）

1. ❌ **智析 tab_zhice_gap：加类别筛选到 detail 表**（已加下拉，还需应用 filter 逻辑）
2. ❌ **智析 tab_zhice_gap summary：加 35 大类每类检索短语比例**
3. ❌ **智优 POC 审核流程**：
   - Critical 5 文章自动流入 POC 审核界面
   - 审批合格后回到智优显示"已审批合格"
   - 加手动 edit 选项让用户可以选择任何文章进入人工审核（走和 Critical 5 一样的流程）
4. ❌ 智析里的智测 tab 已去掉但需确认无残留引用错误
5. ❌ P2 Tab 非 SEO 来源上传后的 category filter 应用到 detail 表

### 中优先级

5. ❌ P2 Tab 非 SEO 来源的上传逻辑完善（当前缺 merge 到 zhiku 的代码末尾）
6. ❌ 智预从智析 tab 移到哪里？（保持在智析？还是也独立？）
7. ❌ 校准算法实现（B1 跨平台共识、B2 类别匹配自动化、B3 时效性检测）
8. ❌ 去重算法优化（语义相似度 > 85% 合并）

### 低优先级

9. ❌ Harmony 前端同步更新（把新的流程反映到 Harmony prototype）
10. ❌ 全面英文翻译（内部内容）
11. ❌ EC2 已清理确认（两台实例是否终止）

## 当前 app.py 状态

- 语法检查：通过 ✅
- 导航已更新但页面索引还没全部调整 → 切换到智造/智优等页面可能会白屏
- 智库页面可正常使用（① ② ③ ④ 骨架完整）
- 智测暂时还在智析 tab 里（还没搬出来）

## 文件清单

| 文件 | 状态 |
|------|------|
| `ui/app.py` | 已修改，导航+智库重构 |
| `.kiro/steering/pipeline-flow-rules.md` | 新建 |
| `.kiro/steering/phrase-accuracy-validation.md` | 新建 |
| `.kiro/steering/reverse-recall-rules.md` | 新建 |
| `.kiro/steering/zhiku-source-c.md` | 新建 |
| `.kiro/steering/zhiyu-forecaster.md` | 新建/修改 |
| `.kiro/steering/zhiku-ui-spec.md` | 新建 |
| `.kiro/steering/content-rules.md` | 修改（加 Critical=5 规则） |
| `harmony_prompt.md` | 修改（加智预+Critical） |
