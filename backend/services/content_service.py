import asyncio
from typing import List
from models.schemas import Topic, ArticleFramework, GeneratedContent, ContentGenerationRequest

class ContentService:
    def __init__(self):
        pass
    
    async def generate_content(self, request: ContentGenerationRequest) -> GeneratedContent:
        """生成文章内容"""
        # 模拟AI生成过程
        await asyncio.sleep(2)
        
        # 根据不同框架生成不同结构的内容
        if request.framework == ArticleFramework.PROBLEM_SOLUTION:
            return await self._generate_problem_solution_content(request.topic)
        elif request.framework == ArticleFramework.STORY_TIPS:
            return await self._generate_story_tips_content(request.topic)
        elif request.framework == ArticleFramework.TUTORIAL_STEPS:
            return await self._generate_tutorial_content(request.topic)
        else:  # COMPARISON_REVIEW
            return await self._generate_comparison_content(request.topic)
    
    async def _generate_problem_solution_content(self, topic: Topic) -> GeneratedContent:
        """生成痛点+解决方案型内容"""
        title = f"解决副业难题：{topic.title}的完整攻略"
        
        outline = [
            "当前副业市场痛点分析",
            f"{topic.category.value}领域机会解读",
            "具体操作方法和步骤",
            "常见问题及解决方案",
            "收益预期和注意事项"
        ]
        
        content = f"""## 前言

在当今经济环境下，越来越多人开始关注副业赚钱。{topic.reason}，这为我们提供了新的机会。

## 痛点分析

很多人想要开始副业，但面临以下问题：
- 不知道从何开始
- 缺乏专业技能
- 担心投入产出比
- 时间管理困难

## {topic.title}的优势

{topic.reason}，具体优势包括：
- 门槛相对较低
- 市场需求旺盛
- 时间安排灵活
- 收益潜力可观

## 具体操作步骤

### 第一步：技能准备
- 学习相关基础知识
- 掌握必要工具使用
- 了解行业标准和规范

### 第二步：市场调研
- 分析目标客户群体
- 研究竞争对手定价
- 确定自己的服务定位

### 第三步：建立作品集
- 制作高质量样品
- 展示专业能力
- 积累初期案例

### 第四步：获客推广
- 选择合适的平台
- 制定营销策略
- 建立客户关系

## 收益预期

根据市场调研，{topic.category.value}领域的收益情况：
- 新手期：月收入500-2000元
- 成长期：月收入2000-8000元
- 成熟期：月收入8000-20000元

## 注意事项

1. 保持学习和提升
2. 建立良好的服务意识
3. 合理安排时间精力
4. 注意法律和税务问题

## 总结

{topic.title}确实是一个值得尝试的副业方向。成功的关键在于持续学习、专业服务和用心经营。

---

关注我，获取更多副业赚钱干货！"""

        return GeneratedContent(
            title=title,
            content=content,
            outline=outline,
            keywords=topic.keywords,
            estimated_read_time=8
        )
    
    async def _generate_story_tips_content(self, topic: Topic) -> GeneratedContent:
        """生成故事+干货型内容"""
        title = f"真实案例：我是如何通过{topic.title.split('，')[0]}实现财务自由的"
        
        outline = [
            "我的副业起步故事",
            "遇到的挑战和困难",
            "关键转折点和突破",
            "总结的实用干货",
            "给新手的建议"
        ]
        
        content = f"""## 我的副业故事

大家好，我是小张。今天想和大家分享我通过{topic.title.split('，')[0]}实现月入过万的真实经历。

## 初期探索

两年前，我还是一个普通的上班族，每月工资勉强够用。{topic.reason}，让我看到了机会。

起初，我也是什么都不懂：
- 不知道怎么开始
- 担心没有客户
- 害怕做不好被骂

## 第一次接单

记得第一次接单，我紧张得手心出汗。客户要求很简单，但我花了整整一个周末才完成。虽然只赚了50元，但那种成就感至今难忘。

## 能力提升阶段

为了提高技能，我：
- 每天花2小时学习相关知识
- 研究优秀作品的特点
- 主动寻求客户反馈
- 不断优化工作流程

## 突破瓶颈

第三个月时，我遇到了瓶颈。收入停滞在2000元左右，客户也不太满意。这时我意识到需要：
- 提升专业技能
- 改善服务态度
- 扩大营销渠道

## 关键转折点

真正的转折发生在第六个月。我接到一个大客户的长期合作项目，月收入一下子突破了8000元。这让我明白了几个道理：

### 干货分享

1. **专业技能是根本**
   - 持续学习新技术
   - 关注行业发展趋势
   - 投资优质学习资源

2. **服务意识很重要**
   - 及时回复客户消息
   - 主动汇报项目进度
   - 超出客户期望

3. **营销推广不可少**
   - 建立个人品牌
   - 维护客户关系
   - 利用口碑传播

4. **时间管理要到位**
   - 制定详细计划
   - 提高工作效率
   - 平衡工作生活

## 现在的状态

经过两年的努力，我现在：
- 月收入稳定在1.5万以上
- 拥有20多个长期合作客户
- 建立了小型工作团队

## 给新手的建议

如果你也想开始{topic.category.value}副业，我建议：

1. **从小做起，不要贪大**
2. **专注提升专业能力**
3. **建立良好的工作习惯**
4. **保持耐心和坚持**

## 结语

副业之路并不容易，但只要用心去做，就一定能有所收获。希望我的经历能给大家一些启发！

有问题欢迎在评论区交流～"""

        return GeneratedContent(
            title=title,
            content=content,
            outline=outline,
            keywords=topic.keywords + ["真实案例", "经验分享"],
            estimated_read_time=10
        )
    
    async def _generate_tutorial_content(self, topic: Topic) -> GeneratedContent:
        """生成教程+步骤型内容"""
        title = f"{topic.title}完全教程：从零基础到月入5000+"
        
        outline = [
            "准备工作和工具",
            "基础技能学习",
            "实操演练步骤",
            "进阶技巧分享",
            "常见问题解答"
        ]
        
        content = f"""## 教程说明

本教程将手把手教你如何从零开始{topic.title.split('，')[0]}。{topic.reason}，现在正是入场的好时机。

## 准备阶段

### 硬件要求
- 电脑配置：中等配置即可
- 网络环境：稳定的宽带连接
- 辅助设备：根据具体需求准备

### 软件工具
1. 必备软件清单
2. 推荐插件和扩展
3. 学习资源整理

### 技能基础
- 基础知识掌握程度：60%
- 学习时间投入：每天2小时
- 预期学习周期：1-2个月

## 详细操作步骤

### 第一步：基础学习（第1-2周）

**学习内容：**
- 行业基础知识
- 工具使用方法
- 基本操作技巧

**具体任务：**
1. 观看入门教程视频
2. 跟着教程做练习
3. 加入相关学习群组

**验收标准：**
- 能够独立完成基础操作
- 了解行业基本规范
- 掌握主要工具使用

### 第二步：实操练习（第3-4周）

**练习项目：**
- 项目A：基础案例制作
- 项目B：进阶效果实现
- 项目C：综合应用练习

**注意要点：**
1. 严格按照标准流程操作
2. 注重细节和质量
3. 记录遇到的问题

### 第三步：作品集建设（第5-6周）

**作品要求：**
- 数量：不少于5个完整作品
- 质量：展示不同技能点
- 风格：体现个人特色

**展示平台：**
- 个人网站/博客
- 专业社交平台
- 作品集网站

### 第四步：客户获取（第7-8周）

**渠道选择：**
1. 线上平台
   - 威客网站
   - 自由职业平台
   - 社交媒体

2. 线下渠道
   - 朋友介绍
   - 本地商家
   - 行业活动

**接单技巧：**
- 合理定价策略
- 专业沟通方式
- 服务流程标准化

## 进阶技巧

### 提升效率
- 建立标准化流程
- 使用自动化工具
- 优化工作环境

### 扩大规模
- 建立客户管理系统
- 发展长期合作关系
- 考虑团队化运作

### 品牌建设
- 打造个人IP
- 内容营销策略
- 口碑维护方法

## 常见问题解答

### Q1：没有相关经验可以做吗？
A1：完全可以。这个教程就是为零基础学员设计的。

### Q2：需要投入多少资金？
A2：初期投入很少，主要是学习成本和基础工具费用。

### Q3：多久能开始赚钱？
A3：认真学习的话，1-2个月就能接到第一单。

### Q4：收入能达到多少？
A4：因人而异，但月入3000-8000是比较常见的。

## 成功案例

**案例1：小王的逆袭之路**
- 学习时间：2个月
- 第一单收入：300元
- 现在月收入：8000+元

**案例2：宝妈的副业选择**
- 利用碎片时间学习
- 兼顾家庭和工作
- 月收入稳定在5000元

## 总结

{topic.title}确实是一个不错的副业选择。关键在于：
1. 系统性学习
2. 持续性练习
3. 专业化服务
4. 耐心和坚持

希望这个教程对你有帮助！有问题随时交流～"""

        return GeneratedContent(
            title=title,
            content=content,
            outline=outline,
            keywords=topic.keywords + ["教程", "步骤", "新手"],
            estimated_read_time=12
        )
    
    async def _generate_comparison_content(self, topic: Topic) -> GeneratedContent:
        """生成盘点+评测型内容"""
        title = f"2024年{topic.category.value}副业大盘点：哪个最赚钱？"
        
        outline = [
            "副业选择标准",
            "热门项目对比",
            "收益分析评测",
            "难度和门槛评估",
            "推荐排行榜"
        ]
        
        content = f"""## 前言

2024年{topic.category.value}领域出现了很多新机会。{topic.reason}，今天就来系统盘点一下这个领域的热门副业项目。

## 评测标准

在开始盘点之前，先明确一下我们的评测维度：

### 收益潜力 ⭐⭐⭐⭐⭐
- 月收入预期
- 成长空间
- 被动收入可能性

### 入门门槛 ⭐⭐⭐⭐⭐
- 技能要求
- 资金投入
- 时间成本

### 市场前景 ⭐⭐⭐⭐⭐
- 需求稳定性
- 竞争激烈程度
- 发展趋势

### 风险控制 ⭐⭐⭐⭐⭐
- 政策风险
- 市场风险
- 技术风险

## 热门项目深度评测

### 项目一：{topic.title.split('，')[0]}

**收益潜力：⭐⭐⭐⭐⭐**
- 新手月收入：1000-3000元
- 熟手月收入：5000-15000元
- 顶级玩家：月入20000+

**入门门槛：⭐⭐⭐⭐☆**
- 技能要求：中等
- 初期投资：500-2000元
- 学习周期：1-3个月

**市场前景：⭐⭐⭐⭐⭐**
- 需求量：持续增长
- 竞争度：中等偏高
- 发展前景：非常看好

**优势：**
- {topic.reason}
- 市场需求量大
- 技能可持续积累

**劣势：**
- 需要一定学习成本
- 竞争逐渐激烈
- 对创意要求较高

### 项目二：内容创作类副业

**收益潜力：⭐⭐⭐⭐☆**
- 新手月收入：500-2000元
- 熟手月收入：3000-10000元
- 头部创作者：月入50000+

**入门门槛：⭐⭐⭐☆☆**
- 技能要求：写作/拍摄能力
- 初期投资：几乎为零
- 学习周期：持续学习

**市场前景：⭐⭐⭐⭐⭐**
- 内容消费需求旺盛
- 平台支持力度大
- 变现方式多样

### 项目三：技能服务类副业

**收益潜力：⭐⭐⭐⭐☆**
- 按时计费：50-200元/小时
- 项目制：1000-10000元/项目
- 顾问费：月费3000-15000元

**入门门槛：⭐⭐⭐⭐⭐**
- 需要专业技能
- 客户积累周期长
- 服务标准化难度大

## 综合对比分析

| 项目类型 | 收益潜力 | 入门门槛 | 市场前景 | 推荐指数 |
|---------|---------|---------|---------|---------|
| {topic.category.value} | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐☆ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 内容创作 | ⭐⭐⭐⭐☆ | ⭐⭐⭐☆☆ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐☆ |
| 技能服务 | ⭐⭐⭐⭐☆ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐☆ | ⭐⭐⭐⭐☆ |

## 选择建议

### 适合新手的项目
1. **{topic.title.split('，')[0]}**
   - 原因：门槛适中，收益可观
   - 建议：先从简单项目开始

2. **内容创作**
   - 原因：投入成本低
   - 建议：选择自己擅长的领域

### 适合有经验者的项目
1. **高端技能服务**
   - 利用现有专业技能
   - 单价高，时间成本低

2. **项目整合运营**
   - 结合多种技能
   - 建立完整业务闭环

## 2024年趋势预测

### 看涨项目
- AI相关技能服务
- 短视频制作
- 在线教育

### 需要谨慎的项目
- 过度依赖平台的项目
- 技术更新快的领域
- 政策敏感行业

## 实操建议

### 如何开始
1. **能力评估**
   - 盘点现有技能
   - 评估学习能力
   - 确定投入预算

2. **项目选择**
   - 结合个人情况
   - 考虑市场需求
   - 评估风险收益

3. **执行计划**
   - 制定学习计划
   - 设定阶段目标
   - 建立反馈机制

## 总结

{topic.category.value}领域机会很多，关键是找到适合自己的方向。建议：
- 从自己的兴趣和能力出发
- 选择有长期发展前景的项目
- 做好持续学习的准备

最后，成功的副业不是一蹴而就的，需要持续投入和优化。希望这个盘点对你有帮助！

---

关注我，持续分享副业干货！"""

        return GeneratedContent(
            title=title,
            content=content,
            outline=outline,
            keywords=topic.keywords + ["对比", "盘点", "评测"],
            estimated_read_time=15
        )
    
    async def optimize_title(self, original_title: str) -> List[str]:
        """优化标题，生成多个选项"""
        await asyncio.sleep(1)
        
        # 模拟生成多个标题选项
        optimized_titles = [
            f"干货！{original_title}",
            f"2024年最新：{original_title}",  
            f"月入过万！{original_title}的秘密",
            f"实测有效：{original_title}完整攻略",
            f"零基础也能做：{original_title}"
        ]
        
        return optimized_titles
    
    async def polish_content(self, content: str) -> str:
        """内容润色"""
        await asyncio.sleep(1.5)
        
        # 模拟内容润色（实际应该调用AI接口）
        return content + "\n\n---\n*内容已经过AI润色优化*"