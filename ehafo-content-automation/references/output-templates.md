# 成品模板

## 目录

1. 考讯
2. 文章
3. 贴图
4. 统一输出包

## 1. 考讯

标题优先使用 12—26 个汉字，直接包含考试与核心事项，并保持在平台 64 字上限内。

先写一句话结论，再只选择完成当前事件任务必需的信息。考试、地区、时间、受影响人群、入口、材料、风险、行动和 CTA 都是候选项，不是固定清单；缺少其中某项不会影响用户判断或行动时不写。官方来源和适用范围保留在成品或内部事实卡的对应位置，核验日期不写入用户可见正文。

没有官方通知时不得写成“已经公布”。

## 2. 文章

标题优先使用 12—26 个汉字并保持在平台 64 字上限内。摘要直接给出核心结论、适用边界和读者能解决的问题。制作正文和 HTML 时同时遵守 [article-mobile-layout.md](article-mobile-layout.md)。

写作前先建立结构卡：记录唯一核心问题、明确不属于本篇范围的相关内容，并列出完成核心任务所需的模块。模块数量不设下限；一个模块足以完成任务时不得扩写成三个。每个模块只标记一个任务类型：结论、边界、判断、行动、必要证据或异常处理。

正文先回答核心问题，再只选择确有必要的后续模块。适用人群、地区差异、入口、材料、错误、行动、CTA 和官方来源都是候选内容，不要求全部出现：缺少后会改变判断或阻止行动的列为必须信息；只在特定情形下使用的放入补充信息；不能服务核心问题的即使正确也删除或拆成另一篇。

标题优先复现用户会直接搜索或询问的问题，不把更模糊的编辑观点当作标题。避免为了篇幅重复事实；同一结论在开头讲清后，后文转入判断或行动。普通正文、重点句、引用规则、图片和留白必须交替形成阅读节奏，不得连续堆放同一种文本模块。

交付前逐段执行独立价值检查：每段只能以新结论、适用边界、判断标准、执行动作或必要证据为主要作用；无法标记，或与前文作用和事实相同的段落直接删除。用户可见正文、HTML 与微信草稿不得出现“选题来源”“核验日期”“内容参考”，不得说明参考了其他文章，也不得展示竞品公众号、问题中心或医学指南链接。这些素材只留在内部事实卡、验证包和交接记录中。只有确需支撑专业事实且存在正式通知时才展示“官方依据”；否则不生成来源区。

本地预览在标题和摘要之后、正文首段之前原样放置 `assets/ehafo-article-header.png`；正式写入微信时标题和摘要使用独立字段，因此顶部图仍是正文第一项。正文结束后原样放置 `assets/ehafo-article-footer.png`。两张固定品牌图不计入正文信息图数量，也不得替代内容模块。

当前固定顶部图的原图内部已有留白，本地预览中摘要与顶部图、顶部图与首段之间的外部间距默认各约 `10px`；正式微信正文中顶部图与首段的外部间距默认约 `10px`。不得裁剪、放大、重绘或压缩固定图来填空。其他固定资产或正文图片不机械套用该数值。

正文需要绿色扫描锚点时，使用独立行内元素包裹 3—6 个可见字符，设置 `color:#3D8063;font-weight:500;white-space:nowrap;`，每段最多一处。不要包裹标点、整句或整段，不用于标题、摘要、小标题、官方依据或已有浅绿底的重点句。

居中重点句需要浅绿高亮时，使用逐行复制的下半部硬分界色带，不使用整块背景：`background-image:linear-gradient(to bottom,transparent 50%,#DCEFE7 50%);box-decoration-break:clone;-webkit-box-decoration-break:clone;`。该渐变只是实现半高色带的硬分界，不得改成装饰性渐变。

正文信息图限定为 0—2 张。固定顶部图、固定底部图、Logo、二维码和品牌宣传图不计入数量。为每张图写出一条“图片独有信息”；写不出、或删除后不影响理解与操作时直接删除。不得为了避免 0 张而制造关系、步骤或装饰图。

将正文内容转成信息图后，删除正文中同义的清单、步骤和事实复述；只保留图片未承载的来源、边界、风险解释和行动。文章已有固定顶部图时，正文信息图不再重复放 Logo。

## 3. 贴图

不要固定张数。按完成用户任务所需的独立信息模块决定。

多张贴图可从以下信息任务中选取，不要求全部使用：

- 核心结论与适用人群；
- 时间线或关键节点；
- 常见情形的判断方法；
- 特殊情形或例外；
- 材料或操作步骤；
- 易错点与后果；
- 行动清单。

每张只承担一个信息任务，但必须同时包含结论与足够的有用细节。标题短，正文用短句，保证手机端可读。封面不得单独占用一张而没有实用信息。内容不足时不生成多张贴图。

多张贴图第 1 张采用“封面＋信息”结构：

1. 主标题：从用户关心的结果、风险、遗漏或行动切入，避免“材料关系”“内容总览”等说明书式标题；
2. 副标题：明确看完能解决什么；
3. 实用信息：至少给出一个立即可用的结论或行动；
4. 系列提示：简短标明页码或后续内容，不堆砌目录。

例如可写“2026护考合格后，这4件事别漏掉”，不可写“护考材料关系”。标题吸引力必须来自具体价值，不得制造焦虑或虚假稀缺。

生成前先建立内容兑现表：

1. 列出首图承诺解决的 1–4 个核心问题；
2. 为每个问题指定一张后续贴图；
3. 每张贴图写明“用户问题—明确答案—下一步动作”；
4. 选择符合任务的用户路径：时间顺序、判断路径、对照关系或自查顺序；
5. 若存在地区差异，补充具体官方入口名称和需要核对的事项，不能只写“以当地为准”。

对于“考试合格后怎么办”类办理指南，优先采用：

- 第 1 张：封面＋立即行动；
- 第 2 张：容易混淆的材料或证书对照；
- 第 3 张：从当前状态到完成办理的时间顺序；
- 第 4 张：材料清单、办理入口和关键例外。

这只是结构范式，不得把示例事实直接套用于其他考试。

完整图片要求：

- 同组背景、字号、边距和层级一致；
- 黑、灰、白为主，绿色只作少量强调；
- 使用纯白或单一浅色底，不生成背景图片；
- 禁止渐变、纹理、照片、人物、场景、插画和装饰图案；
- 只用文字层级、留白、细线及少量纯色色块组织信息；
- 标题清晰但不过黑、不过粗；
- 次要信息用浅灰；
- 不放大单个数字制造虚假重点；
- Logo 只可用原始文件程序化叠加。

验证包中的 `cards` 必须记录：

```json
{
  "visual_spec": {
    "background_type": "solid",
    "background_image": false,
    "people_or_illustration": false,
    "logo_mode": "programmatic_overlay"
  },
  "brand_promo": {
    "required": true,
    "placement": "append_after_content",
    "asset_path": "assets/ehafo-brand-promo.png",
    "transform": "none",
    "sha256": "56f998e0802d34b23077036160f380e4fd14bda1fbf5e192fae8222f69f1343c"
  },
  "journey_type": "chronological",
  "journey_reason": "用户需要知道考试合格后的先后办理顺序",
  "cover_promises": [
    {
      "id": "P01",
      "text": "分清考试材料与执业证书",
      "fulfilled_by": ["M02"]
    }
  ],
  "items": [
    {
      "module_id": "M01",
      "role": "cover_and_content",
      "hook": "用户关心的具体结果、风险、遗漏或行动",
      "payoff": "看完能解决的核心问题",
      "question": "合格后现在先做什么？",
      "answer": "先在开放期内保存考试材料，再按顺序准备注册。",
      "next_action": "立即检查成绩单和合格证明是否已下载",
      "official_entry": ""
    }
  ]
}
```

后续图片的 `role` 使用 `content`。没有原始 Logo 时，`logo_mode` 使用 `asset_blocked`。

`format_decision.card_count` 和 `cards.items` 只统计内容图。固定品牌尾图通过 `brand_promo` 单独登记，并在所有内容图之后原样追加。

## 4. 统一输出包

涉及图片生成或修改时，验证包必须包含四道硬门禁记录。只有一种图片时可保留单个对象；文章同时生成封面和正文插图时使用数组逐类登记：

```json
{
  "production_gates": [
    {
      "declared_before_generation": true,
      "asset_type": "article_cover",
      "template_type": "article_cover",
      "scope_verified": true,
      "locked_assets_verified": true,
      "acceptance": {
        "content_accuracy": "pass",
        "readable_size": "pass",
        "aspect_ratio": "pass",
        "asset_integrity": "pass",
        "mobile_preview": "pass"
      }
    },
    {
      "declared_before_generation": true,
      "asset_type": "article_illustration",
      "template_type": "article_illustration",
      "scope_verified": true,
      "locked_assets_verified": true,
      "acceptance": {
        "content_accuracy": "pass",
        "readable_size": "pass",
        "aspect_ratio": "pass",
        "asset_integrity": "pass",
        "mobile_preview": "pass"
      }
    }
  ]
}
```

文章封面使用 `article_cover`，文章正文插图使用 `article_illustration`，服务号贴图使用 `service_account_cards`。同类类型不得重复登记。`scope_verified` 和 `locked_assets_verified` 必须来自 `scripts/verify_edit_scope.py verify` 的成功结果，不得凭人工声明填写。

选择 `article` 时，`outputs.article` 必须登记正文插图：

```json
{
  "article": {
    "structure": {
      "core_question": "论文是不是正高申报的统一必交项？",
      "out_of_scope": [
        "不汇总全国所有地区历年材料清单",
        "不把某一地区要求套用于其他地区"
      ],
      "modules": [
        {
          "module_id": "M01",
          "necessity": "required",
          "task": "给出论文是否统一必交的明确结论",
          "task_type": "conclusion"
        }
      ]
    },
    "cover": {
      "publication_role": "article_cover",
      "cover_copy": "先查4层文件",
      "title": "申报正高，论文还必须发吗？",
      "digest": "国家政策已明确破除唯论文，但具体申报要求仍要按地区、系列、单位和年度通知逐层核对。",
      "wide": {
        "path": "output/cover-wide.png",
        "width": 900,
        "height": 383
      },
      "square": {
        "path": "output/cover-square.png",
        "width": 500,
        "height": 500
      },
      "visual_spec": {
        "background_type": "solid",
        "palette_id": "action_green",
        "background_color": "#175941",
        "primary_color": "#FFFDF6",
        "accent_color": "#F6D96B"
      },
      "thumbnail_readability": "pass"
    },
    "illustrations": [
      {
        "path": "output/rule-path.png",
        "unique_information": "展示适用规则的核对顺序"
      }
    ]
  }
}
```

`structure` 必填。`core_question` 只写一个核心问题；`out_of_scope` 必须明确列出本篇不处理的相邻问题；`modules` 不设最低数量，每项只允许一个 `task_type`，且 `required` 模块必须排在 `supplementary` 模块之前。`cover` 在声明 `article_cover` 时必填；`cover_copy` 必须为 6—10 个汉字的单行文案，不得包含换行；横版和方版必须使用不同 PNG 路径。`palette_id` 只能是 `action_green`、`notice_blue` 或 `risk_red`，对应色值不可修改，颜色对比度由验证脚本重新计算。`illustrations` 允许 0—2 项，路径不得重复，也不得填写固定顶部图或底部图。

输出内容必须服从形式门禁，不固定包含三种形式：

```text
状态：VALUE_UNPROVEN
选题：
目标用户：
解决问题：
立即行动：

【事实卡】
...

【形式判断】
...

【已选择的成品】
...

【图片制作要求】
...

【官方来源】
...
```

所有已选择的成品必须引用同一组事实卡。
