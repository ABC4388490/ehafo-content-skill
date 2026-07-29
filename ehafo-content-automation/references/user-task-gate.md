# 用户任务与价值验证门禁

## 1. 用户任务卡

生产前记录：

```json
{
  "user_task": {
    "current_state": "用户此刻已经完成什么、卡在哪里",
    "core_question": "用户真正需要回答的一个核心问题",
    "desired_outcome": "看完后可验证的结果",
    "must_answer": ["完成任务不可缺少的问题"],
    "next_action": "用户看完立刻执行的动作",
    "success_without_other_guide": true
  }
}
```

不得用“了解政策”“知道相关信息”作为结果。结果应是能完成判断、准备材料、进入正确入口、纠正错误或形成明确复习安排。

## 2. 独立用户测试

成品完成后，仅向测试视角提供成品，不提供制作过程、设计意图或预期答案。让测试视角回答：

1. 这篇内容是给谁的？
2. 我看完后下一步具体做什么？
3. `must_answer` 中每个问题的答案在哪里？
4. 是否仍要另找一篇攻略才能完成核心任务？
5. 哪一句会引起新的关键疑问、误解或不信任？

记录：

```json
{
  "user_test": {
    "audience_identified": true,
    "next_action_understood": true,
    "must_answer_coverage": [
      {"question": "问题", "answered": true, "location": "模块名"}
    ],
    "requires_other_guide": false,
    "critical_new_questions": [],
    "verdict": "pass"
  }
}
```

测试失败但可改稿时使用 `DRAFT_PASS`；因官方信息缺失而无法回答时使用 `BLOCKED`。

## 3. 价值证据

结构测试不能证明用户愿意点击、读完、收藏或转化。记录真实证据：

```json
{
  "value_evidence": {
    "status": "unproven",
    "comparable_content": [],
    "success_criteria": [],
    "observation_window": ""
  }
}
```

只有同时满足以下条件才能使用 `AUTO_RELEASE`：

- 存在主题、受众和形式均可比的已发布内容；
- 发布前已写明评价指标、基准和观察窗口；
- 实际数据达到标准，且样本不存在明显异常；
- 没有以单一点击率替代阅读完成、收藏/转发或后续行动；
- 本次内容未引入新的高风险事实或未经验证的新结构。

否则，即使事实和独立用户测试均通过，也只能使用 `VALUE_UNPROVEN`。

## 4. 状态判定

| 状态 | 判定 |
|---|---|
| `BLOCKED` | 关键事实或官方依据缺失，核心任务无法安全回答 |
| `DRAFT_PASS` | 事实和格式合格，但独立用户测试未通过 |
| `VALUE_UNPROVEN` | 独立用户测试通过，真实效果尚未验证 |
| `AUTO_RELEASE` | 独立用户测试通过，且同类历史表现达到预设标准 |
