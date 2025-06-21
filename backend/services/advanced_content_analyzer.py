#!/usr/bin/env python3
"""
高级内容分析引擎
整合多平台数据源，进行深度内容分析和趋势识别
"""

import asyncio
import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import logging
import numpy as np
from textblob import TextBlob
import networkx as nx

from .multi_platform_crawler import RPAMultiPlatformCrawler, ContentItem
from .video_content_extractor import VideoContentExtractor

@dataclass
class TrendingTopic:
    """趋势话题数据结构"""
    topic: str
    platforms: List[str]
    total_engagement: int
    growth_rate: float
    sentiment_score: float
    key_influencers: List[str]
    content_samples: List[ContentItem]
    prediction_score: float
    topic_category: str
    related_topics: List[str]

@dataclass
class ContentInsight:
    """内容洞察数据结构"""
    theme: str
    confidence: float
    supporting_evidence: List[str]
    cross_platform_validation: bool
    trend_direction: str  # "rising", "stable", "declining"
    market_opportunity: str
    content_gaps: List[str]
    recommended_angles: List[str]

class AdvancedContentAnalyzer:
    """高级内容分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.crawler = RPAMultiPlatformCrawler()
        self.video_extractor = VideoContentExtractor()
        
        # 分析配置
        self.min_cross_platform_mentions = 2  # 至少在2个平台出现才算趋势
        self.sentiment_threshold = 0.3  # 情感分析阈值
        self.engagement_weights = {
            'google': 1.2,    # Google结果权重稍高
            'youtube': 1.5,   # 视频内容权重最高
            'twitter': 1.0,   # Twitter基准权重
            'reddit': 1.3     # Reddit社区讨论权重较高
        }
        
        # 话题分类词典
        self.topic_categories = {
            'AI_AUTOMATION': ['ai', 'artificial intelligence', 'automation', 'machine learning', 'chatgpt', 'openai'],
            'ECOMMERCE': ['ecommerce', 'dropshipping', 'amazon', 'shopify', 'online store', 'marketplace'],
            'CONTENT_CREATION': ['youtube', 'tiktok', 'instagram', 'content creator', 'influencer', 'social media'],
            'FREELANCING': ['freelance', 'upwork', 'fiverr', 'remote work', 'consulting', 'services'],
            'INVESTMENT': ['stocks', 'crypto', 'investment', 'trading', 'dividends', 'portfolio'],
            'DIGITAL_PRODUCTS': ['course', 'ebook', 'software', 'app', 'saas', 'digital product'],
            'AFFILIATE_MARKETING': ['affiliate', 'commission', 'referral', 'marketing', 'promotion'],
            'REAL_ESTATE': ['real estate', 'property', 'rental', 'airbnb', 'landlord']
        }
    
    async def analyze_market_trends(self, 
                                  search_queries: List[str], 
                                  time_range: str = "7d") -> List[TrendingTopic]:
        """
        分析市场趋势
        
        Args:
            search_queries: 搜索关键词列表
            time_range: 时间范围
            
        Returns:
            趋势话题列表，按预测分数排序
        """
        self.logger.info(f"开始分析市场趋势，关键词: {search_queries}")
        
        all_content = []
        
        # 收集多平台数据
        async with self.crawler:
            for query in search_queries:
                content_items = await self.crawler.search_all_platforms(query, time_range)
                all_content.extend(content_items)
        
        self.logger.info(f"收集到 {len(all_content)} 条内容")
        
        # 提取和分析话题
        topics_data = await self._extract_topics_from_content(all_content)
        
        # 跨平台验证
        validated_topics = self._cross_platform_validation(topics_data)
        
        # 计算趋势分数
        trending_topics = []
        for topic_name, topic_data in validated_topics.items():
            trend_topic = await self._analyze_single_topic(topic_name, topic_data, all_content)
            if trend_topic:
                trending_topics.append(trend_topic)
        
        # 按预测分数排序
        trending_topics.sort(key=lambda x: x.prediction_score, reverse=True)
        
        self.logger.info(f"识别出 {len(trending_topics)} 个趋势话题")
        return trending_topics
    
    async def generate_content_insights(self, trending_topics: List[TrendingTopic]) -> List[ContentInsight]:
        """
        基于趋势话题生成内容洞察
        
        Args:
            trending_topics: 趋势话题列表
            
        Returns:
            内容洞察列表
        """
        insights = []
        
        for topic in trending_topics[:10]:  # 分析前10个话题
            insight = await self._generate_topic_insight(topic)
            if insight:
                insights.append(insight)
        
        return insights
    
    async def _extract_topics_from_content(self, content_items: List[ContentItem]) -> Dict[str, List[ContentItem]]:
        """从内容中提取话题"""
        topics_data = defaultdict(list)
        
        for item in content_items:
            # 提取关键词和短语
            text = f"{item.title} {item.content}"
            keywords = self._extract_keywords_advanced(text)
            
            for keyword in keywords:
                topics_data[keyword].append(item)
        
        return dict(topics_data)
    
    def _extract_keywords_advanced(self, text: str) -> List[str]:
        """高级关键词提取"""
        # 清理文本
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 使用TextBlob进行关键词提取
        blob = TextBlob(text)
        
        # 提取名词短语
        noun_phrases = []
        for phrase in blob.noun_phrases:
            if len(phrase.split()) <= 3 and len(phrase) > 3:  # 1-3个词的短语
                noun_phrases.append(phrase)
        
        # 提取高频词
        words = [word for word in blob.words if len(word) > 3]
        word_freq = Counter(words)
        high_freq_words = [word for word, freq in word_freq.most_common(20) if freq > 1]
        
        # 合并结果
        keywords = list(set(noun_phrases + high_freq_words))
        
        # 过滤常见词
        stop_words = {'this', 'that', 'with', 'have', 'will', 'from', 'they', 'been', 'were', 'said', 'each', 'which', 'their'}
        keywords = [kw for kw in keywords if kw not in stop_words]
        
        return keywords[:15]  # 返回前15个关键词
    
    def _cross_platform_validation(self, topics_data: Dict[str, List[ContentItem]]) -> Dict[str, List[ContentItem]]:
        """跨平台验证话题"""
        validated = {}
        
        for topic, items in topics_data.items():
            # 检查是否在多个平台出现
            platforms = set(item.platform for item in items)
            
            if len(platforms) >= self.min_cross_platform_mentions and len(items) >= 3:
                validated[topic] = items
        
        return validated
    
    async def _analyze_single_topic(self, topic_name: str, content_items: List[ContentItem], all_content: List[ContentItem]) -> Optional[TrendingTopic]:
        """分析单个话题"""
        try:
            # 基础统计
            platforms = list(set(item.platform for item in content_items))
            total_engagement = sum(item.engagement_score * self.engagement_weights.get(item.platform, 1.0) 
                                 for item in content_items)
            
            # 计算增长率
            growth_rate = await self._calculate_growth_rate(topic_name, content_items)
            
            # 情感分析
            sentiment_score = self._analyze_topic_sentiment(content_items)
            
            # 识别关键影响者
            key_influencers = self._identify_key_influencers(content_items)
            
            # 预测分数计算
            prediction_score = self._calculate_prediction_score(
                total_engagement, growth_rate, sentiment_score, len(platforms), len(content_items)
            )
            
            # 话题分类
            topic_category = self._categorize_topic(topic_name)
            
            # 相关话题
            related_topics = self._find_related_topics(topic_name, all_content)
            
            return TrendingTopic(
                topic=topic_name,
                platforms=platforms,
                total_engagement=int(total_engagement),
                growth_rate=growth_rate,
                sentiment_score=sentiment_score,
                key_influencers=key_influencers,
                content_samples=content_items[:5],  # 前5个样本
                prediction_score=prediction_score,
                topic_category=topic_category,
                related_topics=related_topics
            )
            
        except Exception as e:
            self.logger.error(f"分析话题失败 {topic_name}: {e}")
            return None
    
    async def _calculate_growth_rate(self, topic: str, content_items: List[ContentItem]) -> float:
        """计算话题增长率"""
        try:
            # 按时间分组
            now = datetime.now()
            recent_items = [item for item in content_items 
                          if self._parse_time(item.publish_time) > now - timedelta(days=3)]
            older_items = [item for item in content_items 
                         if self._parse_time(item.publish_time) <= now - timedelta(days=3)]
            
            if not older_items:
                return 1.0  # 新话题
            
            recent_engagement = sum(item.engagement_score for item in recent_items)
            older_engagement = sum(item.engagement_score for item in older_items)
            
            if older_engagement == 0:
                return 1.0
            
            growth_rate = (recent_engagement - older_engagement) / older_engagement
            return min(max(growth_rate, -1.0), 5.0)  # 限制在-100%到500%之间
            
        except Exception:
            return 0.0
    
    def _analyze_topic_sentiment(self, content_items: List[ContentItem]) -> float:
        """分析话题情感"""
        sentiments = []
        
        for item in content_items:
            text = f"{item.title} {item.content}"
            blob = TextBlob(text)
            sentiments.append(blob.sentiment.polarity)
        
        return np.mean(sentiments) if sentiments else 0.0
    
    def _identify_key_influencers(self, content_items: List[ContentItem]) -> List[str]:
        """识别关键影响者"""
        author_scores = defaultdict(float)
        
        for item in content_items:
            if item.author:
                # 基于参与度和内容质量计算影响力
                score = item.engagement_score * 0.7 + item.quality_score * 0.3
                author_scores[item.author] += score
        
        # 返回前5个影响者
        top_influencers = sorted(author_scores.items(), key=lambda x: x[1], reverse=True)
        return [author for author, _ in top_influencers[:5]]
    
    def _calculate_prediction_score(self, engagement: float, growth_rate: float, 
                                  sentiment: float, platform_count: int, content_count: int) -> float:
        """计算预测分数"""
        # 归一化各项指标
        normalized_engagement = min(engagement / 1000, 1.0)
        normalized_growth = min(max(growth_rate + 1, 0), 2.0) / 2.0
        normalized_sentiment = (sentiment + 1) / 2.0
        normalized_platforms = min(platform_count / 4.0, 1.0)
        normalized_content = min(content_count / 20.0, 1.0)
        
        # 加权计算
        weights = {
            'engagement': 0.3,
            'growth': 0.25,
            'sentiment': 0.15,
            'platforms': 0.2,
            'content': 0.1
        }
        
        score = (
            normalized_engagement * weights['engagement'] +
            normalized_growth * weights['growth'] +
            normalized_sentiment * weights['sentiment'] +
            normalized_platforms * weights['platforms'] +
            normalized_content * weights['content']
        )
        
        return round(score * 100, 2)
    
    def _categorize_topic(self, topic: str) -> str:
        """对话题进行分类"""
        topic_lower = topic.lower()
        
        for category, keywords in self.topic_categories.items():
            if any(keyword in topic_lower for keyword in keywords):
                return category
        
        return 'OTHER'
    
    def _find_related_topics(self, topic: str, all_content: List[ContentItem]) -> List[str]:
        """找到相关话题"""
        # 简化版本：基于共现分析
        related = []
        topic_words = set(topic.lower().split())
        
        word_cooccurrence = defaultdict(int)
        
        for item in all_content:
            text = f"{item.title} {item.content}".lower()
            words = set(re.findall(r'\b\w+\b', text))
            
            if topic_words.intersection(words):
                for word in words:
                    if word not in topic_words and len(word) > 3:
                        word_cooccurrence[word] += 1
        
        # 返回前5个相关词
        top_related = sorted(word_cooccurrence.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in top_related[:5]]
    
    async def _generate_topic_insight(self, topic: TrendingTopic) -> Optional[ContentInsight]:
        """为话题生成内容洞察"""
        try:
            # 分析主题
            theme = self._extract_main_theme(topic)
            
            # 置信度评估
            confidence = self._calculate_insight_confidence(topic)
            
            # 支持证据
            evidence = self._gather_supporting_evidence(topic)
            
            # 跨平台验证
            cross_platform = len(topic.platforms) >= 2
            
            # 趋势方向
            trend_direction = self._determine_trend_direction(topic)
            
            # 市场机会
            market_opportunity = self._identify_market_opportunity(topic)
            
            # 内容空白
            content_gaps = self._identify_content_gaps(topic)
            
            # 推荐角度
            recommended_angles = self._suggest_content_angles(topic)
            
            return ContentInsight(
                theme=theme,
                confidence=confidence,
                supporting_evidence=evidence,
                cross_platform_validation=cross_platform,
                trend_direction=trend_direction,
                market_opportunity=market_opportunity,
                content_gaps=content_gaps,
                recommended_angles=recommended_angles
            )
            
        except Exception as e:
            self.logger.error(f"生成洞察失败 {topic.topic}: {e}")
            return None
    
    def _extract_main_theme(self, topic: TrendingTopic) -> str:
        """提取主要主题"""
        # 基于内容样本提取共同主题
        all_text = " ".join([f"{item.title} {item.content}" for item in topic.content_samples])
        
        # 简化版主题提取
        common_phrases = self._extract_keywords_advanced(all_text)
        
        if common_phrases:
            return f"围绕'{topic.topic}'的{topic.topic_category.lower()}趋势"
        
        return f"{topic.topic}相关内容趋势"
    
    def _calculate_insight_confidence(self, topic: TrendingTopic) -> float:
        """计算洞察置信度"""
        factors = [
            len(topic.platforms) / 4.0,  # 平台覆盖度
            min(len(topic.content_samples) / 10.0, 1.0),  # 内容数量
            (topic.sentiment_score + 1) / 2.0,  # 情感积极度
            min(topic.prediction_score / 100.0, 1.0)  # 预测分数
        ]
        
        return round(np.mean(factors), 2)
    
    def _gather_supporting_evidence(self, topic: TrendingTopic) -> List[str]:
        """收集支持证据"""
        evidence = []
        
        # 平台分布证据
        evidence.append(f"在{len(topic.platforms)}个平台出现: {', '.join(topic.platforms)}")
        
        # 参与度证据
        evidence.append(f"总参与度达到{topic.total_engagement}分")
        
        # 增长证据
        if topic.growth_rate > 0.2:
            evidence.append(f"显示{topic.growth_rate:.1%}的增长趋势")
        
        # 情感证据
        if topic.sentiment_score > 0.3:
            evidence.append("社区反响积极")
        elif topic.sentiment_score < -0.3:
            evidence.append("存在争议性讨论")
        
        return evidence
    
    def _determine_trend_direction(self, topic: TrendingTopic) -> str:
        """确定趋势方向"""
        if topic.growth_rate > 0.3:
            return "rising"
        elif topic.growth_rate < -0.2:
            return "declining"
        else:
            return "stable"
    
    def _identify_market_opportunity(self, topic: TrendingTopic) -> str:
        """识别市场机会"""
        category_opportunities = {
            'AI_AUTOMATION': "AI工具开发和自动化服务需求增长",
            'ECOMMERCE': "电商平台和工具市场扩张机会",
            'CONTENT_CREATION': "内容创作工具和培训服务需求",
            'FREELANCING': "自由职业者服务平台发展",
            'INVESTMENT': "投资教育和工具市场潜力",
            'DIGITAL_PRODUCTS': "数字产品创作和销售机会",
            'AFFILIATE_MARKETING': "联盟营销平台和资源需求",
            'REAL_ESTATE': "房地产科技和服务创新"
        }
        
        return category_opportunities.get(topic.topic_category, "新兴市场机会值得关注")
    
    def _identify_content_gaps(self, topic: TrendingTopic) -> List[str]:
        """识别内容空白"""
        gaps = []
        
        # 基于平台分布识别空白
        all_platforms = {'google', 'twitter', 'reddit', 'youtube'}
        missing_platforms = all_platforms - set(topic.platforms)
        
        if 'youtube' in missing_platforms:
            gaps.append("缺少视频教程内容")
        
        if 'reddit' in missing_platforms:
            gaps.append("社区讨论和深度分析不足")
        
        # 基于内容类型识别空白
        content_types = [item.media_type for item in topic.content_samples]
        if 'video' not in content_types:
            gaps.append("视觉化内容缺乏")
        
        return gaps[:3]  # 最多3个空白
    
    def _suggest_content_angles(self, topic: TrendingTopic) -> List[str]:
        """建议内容角度"""
        angles = []
        
        # 基于话题类别建议角度
        category_angles = {
            'AI_AUTOMATION': [
                f"如何用AI工具实现{topic.topic}自动化",
                f"{topic.topic}的AI解决方案对比",
                f"零基础学会{topic.topic}AI应用"
            ],
            'ECOMMERCE': [
                f"{topic.topic}电商实战指南",
                f"从0到1搭建{topic.topic}业务",
                f"{topic.topic}盈利模式深度解析"
            ],
            'CONTENT_CREATION': [
                f"{topic.topic}内容创作技巧",
                f"如何通过{topic.topic}实现变现",
                f"{topic.topic}创作者成功案例分析"
            ]
        }
        
        default_angles = [
            f"{topic.topic}初学者完整指南",
            f"{topic.topic}进阶策略和技巧",
            f"{topic.topic}成功案例分析",
            f"{topic.topic}常见误区避坑指南"
        ]
        
        angles = category_angles.get(topic.topic_category, default_angles)
        
        return angles[:4]  # 最多4个角度
    
    def _parse_time(self, time_str: str) -> datetime:
        """解析时间字符串"""
        try:
            # 尝试ISO格式
            return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        except:
            try:
                # 尝试其他格式
                return datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            except:
                # 默认当前时间
                return datetime.now()


# 使用示例
async def main():
    """测试高级内容分析"""
    analyzer = AdvancedContentAnalyzer()
    
    # 分析市场趋势
    queries = ["passive income", "side hustle", "ai automation"]
    trending_topics = await analyzer.analyze_market_trends(queries, "7d")
    
    print(f"发现 {len(trending_topics)} 个趋势话题:")
    for topic in trending_topics[:5]:
        print(f"\n话题: {topic.topic}")
        print(f"预测分数: {topic.prediction_score}")
        print(f"平台: {', '.join(topic.platforms)}")
        print(f"参与度: {topic.total_engagement}")
        print(f"增长率: {topic.growth_rate:.2%}")
    
    # 生成内容洞察
    insights = await analyzer.generate_content_insights(trending_topics)
    
    print(f"\n生成 {len(insights)} 个内容洞察:")
    for insight in insights[:3]:
        print(f"\n主题: {insight.theme}")
        print(f"置信度: {insight.confidence}")
        print(f"趋势方向: {insight.trend_direction}")
        print(f"市场机会: {insight.market_opportunity}")

if __name__ == "__main__":
    asyncio.run(main())