# 📱 微信公众号文章智能分析功能指南

## 🎯 功能概述

基于您提供的微信公众号文章链接 `https://mp.weixin.qq.com/s/LZgG-5uE8fGaJAiqb0FGYQ`，我们实现了一个智能的内容分析和选题生成系统。

## ✨ 核心功能

### 1. 🕷️ 智能爬虫系统
- **文章信息提取**: 自动提取标题、作者、发布时间、正文内容
- **反爬策略**: 使用合理的请求间隔和User-Agent
- **错误处理**: 完善的异常处理和备用方案

### 2. 🧠 智能内容分析
- **中文分词**: 使用jieba进行精确的中文分词
- **关键词提取**: 基于TF-IDF和TextRank算法
- **主题分类**: 6大分类系统（AI工具、电商变现、内容创作等）
- **热度评分**: 多维度热度计算算法

### 3. 🎯 智能选题生成
- **模板化生成**: 5种不同风格的选题模板
- **个性化推荐**: 基于内容特征的个性化建议
- **去重优化**: 智能去重和排序算法

## 🚀 使用方法

### 前端界面使用

1. **启动应用**
   ```bash
   cd sidehustle-engine
   ./start.sh
   ```

2. **访问界面**: http://localhost:3000

3. **使用微信分析功能**:
   - 点击"微信分析"按钮
   - 输入微信文章链接（支持多个）
   - 选择生成选题数量
   - 点击"开始分析"

### API直接调用

#### 1. 分析单篇文章
```bash
curl -X POST "http://localhost:8000/api/topics/analyze/article" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://mp.weixin.qq.com/s/LZgG-5uE8fGaJAiqb0FGYQ"
  }'
```

#### 2. 批量生成选题
```bash
curl -X POST "http://localhost:8000/api/topics/trending/wechat" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://mp.weixin.qq.com/s/LZgG-5uE8fGaJAiqb0FGYQ"],
    "limit": 5
  }'
```

#### 3. 演示功能
```bash
curl "http://localhost:8000/api/topics/demo/wechat"
```

## 📊 实测结果

基于您提供的文章，系统成功分析出：

### 📰 文章信息
- **标题**: "一天两小时，收入500+，这3个正规赚钱平台，真的太香了！"
- **作者**: 收入增长
- **分类**: 内容创作
- **热度**: 90分

### 🔍 关键词提取
- 抄书 (高频词)
- 剪辑 (技能相关)
- 平台 (渠道相关)

### 🎯 生成选题示例
1. **内容创作新趋势：抄书变现指南**
   - 分类: 内容创作
   - 热度: 90分
   - 推荐理由: 时效性指标得分25、收益性指标得分30、实用性指标得分15

2. **2024年抄书副业机会深度解析**
   - 针对新手的详细分析
   - 市场前景和可行性评估

3. **从零开始做内容创作：抄书实战经验**
   - 操作步骤和注意事项
   - 收益预期和风险控制

## 🛠️ 技术架构

### 后端服务
```
backend/
├── services/
│   ├── wechat_crawler.py      # 微信爬虫
│   ├── content_analyzer.py    # 内容分析器
│   └── intelligent_topic_service.py  # 智能选题服务
├── api/routes/
│   └── topics.py              # API路由
└── data/
    └── topics_cache.json      # 缓存文件
```

### 前端界面
```
frontend/src/components/
└── TopicFinder.vue            # 选题发现组件（已集成微信分析）
```

## ⚙️ 配置说明

### 缓存设置
- **缓存时长**: 6小时
- **缓存文件**: `backend/data/topics_cache.json`
- **自动清理**: 过期自动重新分析

### 请求限制
- **单次分析**: 最多10篇文章
- **请求间隔**: 2秒（避免被封）
- **超时设置**: 10秒

## 🔧 扩展功能

### 1. 多公众号支持
可以添加多个公众号的文章进行批量分析：
```python
urls = [
    "https://mp.weixin.qq.com/s/article1",
    "https://mp.weixin.qq.com/s/article2",
    "https://mp.weixin.qq.com/s/article3"
]
```

### 2. 自定义分类
在 `content_analyzer.py` 中可以自定义分类词典：
```python
self.side_hustle_dict = {
    '新分类': ['关键词1', '关键词2', '关键词3']
}
```

### 3. 热度算法调优
在 `_calculate_heat_score` 方法中调整评分权重。

## 🚨 注意事项

### 法律合规
- 仅用于学习和研究目的
- 遵守网站robots.txt规则
- 尊重版权和知识产权

### 技术限制
- 微信可能有反爬限制
- 网络连接稳定性影响
- 内容解析准确性依赖页面结构

### 使用建议
- 建议分批次分析，避免频繁请求
- 定期清理缓存文件
- 关注微信政策变化

## 📈 性能优化

- ✅ 智能缓存机制
- ✅ 异步处理支持
- ✅ 错误重试机制
- ✅ 内存优化
- ✅ 并发控制

## 🔮 未来规划

1. **AI增强**: 集成GPT模型进行更智能的内容理解
2. **多平台支持**: 扩展到知乎、小红书等平台
3. **实时监控**: 定时抓取热门文章
4. **数据可视化**: 趋势分析和数据图表
5. **用户个性化**: 基于用户偏好的选题推荐

---

🎉 **恭喜！您的智能选题生成系统已经成功集成微信公众号分析功能！**

项目地址: https://github.com/chinajavaAgent/sidehustle-engine