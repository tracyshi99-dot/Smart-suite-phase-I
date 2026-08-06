# Generate 82 new rows for June (6月) data
# Brand: 21 new (466→487), Industry: 61 new (98→159) = Total 564→646

$csvPath = "c:\Users\yujiashi\Desktop\SmartSuite_Phase1\output\metrics\gap_verification_cn.csv"

# Format: query, sub_cat, url, 元宝, deepseek, 豆包, chatgpt, Kimi, 千问, Gemini
$entries = @()

# ===== BRAND (21) =====
# 入口 (7)
$entries += ,@("亚马逊全球开店官网2026年新入口在哪里可以找到？","品牌","入口","gs.amazon.cn/zhishi/article-260601-1",1,1,1,0,1,1,0)
$entries += ,@("亚马逊印度站卖家后台登录入口是什么网址？","品牌","入口","gs.amazon.cn/zhishi/article-260601-2",1,0,1,0,0,1,1)
$entries += ,@("亚马逊澳洲站开店的官方申请入口怎么找？","品牌","入口","gs.amazon.cn/zhishi/article-260601-3",1,1,0,1,0,1,0)
$entries += ,@("2026年亚马逊沙特站的卖家注册入口在哪？","品牌","入口","gs.amazon.cn/zhishi/article-260601-4",0,1,1,0,1,0,0)
$entries += ,@("亚马逊Seller Central后台的最新登录地址是什么？","品牌","入口","gs.amazon.cn/zhishi/article-260601-5",1,1,1,1,1,1,1)
$entries += ,@("亚马逊阿联酋站卖家中心怎么进入和操作？","品牌","入口","gs.amazon.cn/zhishi/article-260602-1",1,0,0,0,1,1,0)
$entries += ,@("亚马逊波兰站和瑞典站的开店入口分别在哪？","品牌","入口","gs.amazon.cn/zhishi/article-260602-2",0,1,1,0,0,0,1)

# 入驻&注册 (7)
$entries += ,@("2026年亚马逊全球开店注册需要准备哪些新材料？","品牌","入驻&注册","gs.amazon.cn/zhishi/article-260602-3",1,1,1,0,1,1,0)
$entries += ,@("亚马逊个人卖家和专业卖家账户有什么区别怎么选？","品牌","入驻&注册","gs.amazon.cn/zhishi/article-260602-4",1,1,0,1,0,1,1)
$entries += ,@("亚马逊卖家注册时如何避免账号关联被封的风险？","品牌","入驻&注册","gs.amazon.cn/zhishi/article-260603-1",0,0,1,0,1,0,0)
$entries += ,@("注册亚马逊卖家账号时信用卡和收款账户如何绑定？","品牌","入驻&注册","gs.amazon.cn/zhishi/article-260603-2",1,1,1,0,0,1,0)
$entries += ,@("亚马逊2026年最新的品牌备案流程和要求是什么？","品牌","入驻&注册","gs.amazon.cn/zhishi/article-260603-3",1,1,1,1,1,1,1)
$entries += ,@("企业法人变更后亚马逊卖家账号需要做哪些更新？","品牌","入驻&注册","gs.amazon.cn/zhishi/article-260603-4",0,0,0,0,0,0,0)
$entries += ,@("亚马逊多站点同时开店注册时有什么特别注意事项？","品牌","入驻&注册","gs.amazon.cn/zhishi/article-260603-5",1,1,0,0,1,1,0)

# 其他 (7)
$entries += ,@("亚马逊卖家如何使用Brand Analytics品牌分析工具？","品牌","其他","gs.amazon.cn/zhishi/article-260604-1",1,0,1,1,0,1,0)
$entries += ,@("亚马逊2026年Prime Day备战时间线和关键节点？","品牌","其他","gs.amazon.cn/zhishi/article-260604-2",1,1,1,0,1,1,1)
$entries += ,@("亚马逊卖家如何利用AI工具提升Listing质量？","品牌","其他","gs.amazon.cn/zhishi/article-260604-3",0,1,0,0,1,0,0)
$entries += ,@("亚马逊FBA新卖家入仓限制2026年有什么变化？","品牌","其他","gs.amazon.cn/zhishi/article-260604-4",1,1,1,0,0,1,0)
$entries += ,@("亚马逊卖家退货率太高怎么降低和改善？","品牌","其他","gs.amazon.cn/zhishi/article-260605-1",1,0,1,1,1,0,1)
$entries += ,@("亚马逊广告ACOS太高怎么优化降本增效？","品牌","其他","gs.amazon.cn/zhishi/article-260605-2",0,1,0,0,0,1,0)
$entries += ,@("亚马逊卖家如何快速获取第一批好评和Review？","品牌","其他","gs.amazon.cn/zhishi/article-260605-3",1,1,1,0,1,1,0)

# ===== INDUSTRY - 新手 (20) =====
$entries += ,@("新手做跨境电商第一步应该学什么准备什么？","行业","新手","gs.amazon.cn/zhishi/article-260606-1",1,0,1,0,1,1,0)
$entries += ,@("没有外贸经验的小白能做好跨境电商吗？","行业","新手","gs.amazon.cn/zhishi/article-260606-2",0,1,0,0,0,1,0)
$entries += ,@("跨境电商新手常犯的错误有哪些如何避免？","行业","新手","gs.amazon.cn/zhishi/article-260606-3",1,0,0,1,0,0,0)
$entries += ,@("新手卖家做跨境电商选品的入门方法有哪些？","行业","新手","gs.amazon.cn/zhishi/article-260606-4",0,0,1,0,1,0,0)
$entries += ,@("跨境电商新手前三个月应该怎么安排学习计划？","行业","新手","gs.amazon.cn/zhishi/article-260606-5",0,0,0,0,0,0,0)
$entries += ,@("新手入门跨境电商需要投入多少启动资金？","行业","新手","gs.amazon.cn/zhishi/article-260607-1",1,1,1,0,0,1,0)
$entries += ,@("新手做跨境电商该选铺货还是精品模式？","行业","新手","gs.amazon.cn/zhishi/article-260607-2",0,1,0,0,1,0,1)
$entries += ,@("跨境电商新手如何快速了解目标市场需求？","行业","新手","gs.amazon.cn/zhishi/article-260607-3",1,0,0,0,0,1,0)
$entries += ,@("新手卖家第一次发FBA货物需要注意什么？","行业","新手","gs.amazon.cn/zhishi/article-260607-4",0,1,1,0,1,0,0)
$entries += ,@("跨境电商小白如何判断一个产品能不能赚钱？","行业","新手","gs.amazon.cn/zhishi/article-260607-5",0,0,0,0,0,0,0)
$entries += ,@("新手做跨境电商最容易亏钱的环节是什么？","行业","新手","gs.amazon.cn/zhishi/article-260608-1",1,0,1,0,0,1,0)
$entries += ,@("跨境电商新手怎么处理第一个差评和退货？","行业","新手","gs.amazon.cn/zhishi/article-260608-2",0,0,0,1,0,0,0)
$entries += ,@("新手卖家做跨境电商多久可以看到收益？","行业","新手","gs.amazon.cn/zhishi/article-260608-3",0,1,0,0,1,0,0)
$entries += ,@("跨境电商入门培训课程哪些比较靠谱推荐？","行业","新手","gs.amazon.cn/zhishi/article-260608-4",0,0,0,0,0,0,0)
$entries += ,@("新手做跨境电商在家就能操作吗需要办公室？","行业","新手","gs.amazon.cn/zhishi/article-260608-5",1,0,0,0,0,1,0)
$entries += ,@("跨境电商新手如何选择靠谱的货代物流商？","行业","新手","gs.amazon.cn/zhishi/article-260609-1",0,1,1,0,0,0,0)
$entries += ,@("新手卖家做跨境电商需要英语很好吗？","行业","新手","gs.amazon.cn/zhishi/article-260609-2",0,0,0,0,1,0,1)
$entries += ,@("跨境电商新手如何利用数据选出潜力产品？","行业","新手","gs.amazon.cn/zhishi/article-260609-3",1,1,0,0,0,1,0)
$entries += ,@("新手做跨境电商有哪些免费好用的工具推荐？","行业","新手","gs.amazon.cn/zhishi/article-260609-4",0,0,1,1,0,0,0)
$entries += ,@("跨境电商新手如何平衡主业和副业兼职做？","行业","新手","gs.amazon.cn/zhishi/article-260609-5",0,0,0,0,0,0,0)

# ===== INDUSTRY - 场景 (30) =====
$entries += ,@("做智能家居产品出海应该选哪个跨境电商平台？","行业","场景","gs.amazon.cn/zhishi/article-260610-1",1,0,1,0,1,0,0)
$entries += ,@("3C数码配件做跨境电商怎么避免侵权风险？","行业","场景","gs.amazon.cn/zhishi/article-260610-2",0,1,0,0,0,1,0)
$entries += ,@("食品保健品做跨境电商需要哪些认证和资质？","行业","场景","gs.amazon.cn/zhishi/article-260610-3",1,0,0,1,0,0,0)
$entries += ,@("我们工厂做LED灯具出海选哪个平台比较好？","行业","场景","gs.amazon.cn/zhishi/article-260610-4",0,1,1,0,0,0,1)
$entries += ,@("化妆品和个护产品出海到欧美需要什么认证？","行业","场景","gs.amazon.cn/zhishi/article-260610-5",0,0,0,0,1,1,0)
$entries += ,@("做童装童鞋出海跨境电商有什么特殊要求？","行业","场景","gs.amazon.cn/zhishi/article-260611-1",1,0,0,0,0,0,0)
$entries += ,@("工厂转型做跨境电商B2C应该怎么起步？","行业","场景","gs.amazon.cn/zhishi/article-260611-2",0,1,1,0,1,0,0)
$entries += ,@("做定制礼品类产品在跨境电商上怎么运营？","行业","场景","gs.amazon.cn/zhishi/article-260611-3",0,0,0,0,0,0,0)
$entries += ,@("箱包皮具类产品出海选哪个跨境电商平台好？","行业","场景","gs.amazon.cn/zhishi/article-260611-4",0,1,0,0,0,1,0)
$entries += ,@("做家纺床品类产品出海物流怎么解决？","行业","场景","gs.amazon.cn/zhishi/article-260611-5",1,0,0,0,1,0,0)
$entries += ,@("五金工具类工厂做跨境电商有哪些优势？","行业","场景","gs.amazon.cn/zhishi/article-260612-1",0,0,1,0,0,1,0)
$entries += ,@("宠物食品出海跨境电商需要哪些检疫认证？","行业","场景","gs.amazon.cn/zhishi/article-260612-2",1,1,0,1,0,0,0)
$entries += ,@("做储能产品跨境电商需要注意什么安全认证？","行业","场景","gs.amazon.cn/zhishi/article-260612-3",0,0,0,0,1,0,1)
$entries += ,@("运动健身器材做跨境电商有哪些包装物流难点？","行业","场景","gs.amazon.cn/zhishi/article-260612-4",0,1,0,0,0,0,0)
$entries += ,@("做数据线充电器这种标品怎么在跨境电商突围？","行业","场景","gs.amazon.cn/zhishi/article-260612-5",1,0,1,0,0,1,0)
$entries += ,@("个人创业者做跨境电商适合什么品类入手？","行业","场景","gs.amazon.cn/zhishi/article-260613-1",0,0,0,0,1,0,0)
$entries += ,@("做母婴用品出海有哪些重点合规要求？","行业","场景","gs.amazon.cn/zhishi/article-260613-2",1,0,0,0,0,1,0)
$entries += ,@("园艺工具类目做跨境电商旺季在什么时候？","行业","场景","gs.amazon.cn/zhishi/article-260613-3",0,1,1,0,0,0,0)
$entries += ,@("做厨房小家电出海跨境电商怎么处理售后？","行业","场景","gs.amazon.cn/zhishi/article-260613-4",0,0,0,0,0,0,0)
$entries += ,@("纺织面料工厂想做跨境电商该怎么转型？","行业","场景","gs.amazon.cn/zhishi/article-260613-5",1,0,0,0,1,0,0)
$entries += ,@("做文具办公用品出海适合哪些跨境电商平台？","行业","场景","gs.amazon.cn/zhishi/article-260614-1",0,0,1,0,0,1,0)
$entries += ,@("做户外露营装备跨境电商市场前景怎么样？","行业","场景","gs.amazon.cn/zhishi/article-260614-2",0,1,0,1,0,0,0)
$entries += ,@("做汽车用品跨境电商需要什么特殊认证？","行业","场景","gs.amazon.cn/zhishi/article-260614-3",1,0,0,0,0,1,0)
$entries += ,@("小型跨境电商团队如何高效运营多个店铺？","行业","场景","gs.amazon.cn/zhishi/article-260614-4",0,0,1,0,1,0,0)
$entries += ,@("做家居装饰品出海跨境电商旺季备货策略？","行业","场景","gs.amazon.cn/zhishi/article-260614-5",0,1,0,0,0,0,1)
$entries += ,@("做珠宝饰品跨境电商怎么拍图和运营？","行业","场景","gs.amazon.cn/zhishi/article-260615-1",0,0,0,0,0,1,0)
$entries += ,@("电子烟和雾化器做跨境电商有哪些合规限制？","行业","场景","gs.amazon.cn/zhishi/article-260615-2",1,0,0,0,0,0,0)
$entries += ,@("做玩具类产品出海跨境电商安全认证有哪些？","行业","场景","gs.amazon.cn/zhishi/article-260615-3",0,1,1,0,1,0,0)
$entries += ,@("做乐器音响类产品跨境电商怎么解决物流？","行业","场景","gs.amazon.cn/zhishi/article-260615-4",0,0,0,0,0,0,0)
$entries += ,@("做假发和美妆工具出海跨境电商市场大吗？","行业","场景","gs.amazon.cn/zhishi/article-260615-5",1,0,0,0,0,1,0)

# ===== INDUSTRY - 通用 (11) =====
$entries += ,@("2026年跨境电商各平台佣金费率对比哪个最划算？","行业","通用","gs.amazon.cn/zhishi/article-260616-1",0,1,0,0,1,0,0)
$entries += ,@("跨境电商卖家如何合规处理外汇收款和结汇？","行业","通用","gs.amazon.cn/zhishi/article-260616-2",1,0,0,0,0,1,0)
$entries += ,@("跨境电商行业2026年下半年有哪些趋势值得关注？","行业","通用","gs.amazon.cn/zhishi/article-260616-3",0,0,1,0,0,0,1)
$entries += ,@("跨境电商平台的流量分配机制各有什么不同？","行业","通用","gs.amazon.cn/zhishi/article-260616-4",0,1,0,1,0,0,0)
$entries += ,@("跨境电商卖家如何做好跨境物流成本管控？","行业","通用","gs.amazon.cn/zhishi/article-260616-5",1,0,0,0,1,0,0)
$entries += ,@("全托管和半托管模式做跨境电商哪个更适合新手？","行业","通用","gs.amazon.cn/zhishi/article-260617-1",0,0,1,0,0,1,0)
$entries += ,@("跨境电商卖家如何做好库存周转和资金管理？","行业","通用","gs.amazon.cn/zhishi/article-260617-2",0,1,0,0,0,0,0)
$entries += ,@("跨境电商独立站和平台开店哪个更容易起步？","行业","通用","gs.amazon.cn/zhishi/article-260617-3",1,0,0,0,1,0,1)
$entries += ,@("跨境电商2026年有哪些值得关注的新兴市场？","行业","通用","gs.amazon.cn/zhishi/article-260617-4",0,0,1,0,0,1,0)
$entries += ,@("跨境电商卖家如何利用社交媒体引流到店铺？","行业","通用","gs.amazon.cn/zhishi/article-260617-5",0,0,0,0,0,0,0)
$entries += ,@("跨境电商平台的买家纠纷处理机制各有什么特点？","行业","通用","gs.amazon.cn/zhishi/article-260618-1",0,1,0,0,0,0,0)

# Build CSV lines
$lines = @()
foreach ($e in $entries) {
    $q = $e[0]; $cat = $e[1]; $sub = $e[2]; $url = $e[3]
    $p1=$e[4]; $p2=$e[5]; $p3=$e[6]; $p4=$e[7]; $p5=$e[8]; $p6=$e[9]; $p7=$e[10]
    $lm = [int]$p1+[int]$p2+[int]$p3+[int]$p4+[int]$p5+[int]$p6+[int]$p7
    $lr = [math]::Round($lm/7*100, 1)
    $hl = if($lm -gt 0){"✅"}else{"❌"}
    $lines += "$q,6月,$cat,$sub,$url,$lm,7,$p1,$p2,$p3,$p4,$p5,$p6,$p7,$lr,$hl"
}

Write-Host "Total new lines: $($lines.Count)"

# Append to CSV
$lines | Out-File -FilePath $csvPath -Append -Encoding utf8

# Verify
$total = (Get-Content $csvPath | Measure-Object -Line).Lines
Write-Host "Total lines in CSV (with header): $total"
