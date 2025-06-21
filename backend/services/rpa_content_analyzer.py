#!/usr/bin/env python3
"""
RPA内容分析引擎
整合RPA爬虫和内容分析功能，提供完整的多平台内容洞察
"""

import asyncio
import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import logging
import numpy as np

from .rpa_multi_platform_crawler import RPAMultiPlatformCrawler, RPAContentItem
from .rpa_anti_detection import RPAAntiDetection
from .content_analyzer import ContentAnalyzer

@dataclass
class RPATrendingTopic:
    """RPA发现的趋势话题"""
    topic: str
    platforms: List[str]
    total_engagement: int
    growth_indicators: Dict[str, float]
    sentiment_score: float
    content_samples: List[RPAContentItem]
    confidence_score: float
    category: str
    related_keywords: List[str]
    market_opportunity: str
    scraped_at: str

@dataclass
class ContentGap:
    """内容空白机会"""
    gap_type: str
    description: str
    opportunity_score: float
    target_platforms: List[str]
    suggested_content_types: List[str]
    competitive_analysis: Dict[str, Any]

@dataclass
class InfluencerInsight:
    """影响者洞察"""
    name: str
    platform: str
    follower_estimate: int
    engagement_rate: float
    content_themes: List[str]
    posting_frequency: str
    collaboration_potential: float

class RPAContentAnalyzer:
    """RPA内容分析引擎"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rpa_crawler = RPAMultiPlatformCrawler(use_playwright=True)
        self.anti_detection = RPAAntiDetection()
        self.content_analyzer = ContentAnalyzer()
        
        # 分析配置
        self.config = {
            'min_content_quality_score': 0.6,
            'min_cross_platform_mentions': 2,
            'trend_detection_threshold': 0.7,
            'sentiment_analysis_enabled': True,
            'competitive_analysis_enabled': True,
            'cache_duration_hours': 6
        }
        
        # 话题分类词典
        self.topic_categories = {
            'AI_AUTOMATION': {
                'keywords': ['ai', 'artificial intelligence', 'automation', 'chatgpt', 'machine learning', 'bot'],
                'weight': 1.5
            },
            'CONTENT_CREATION': {
                'keywords': ['youtube', 'tiktok', 'instagram', 'content', 'creator', 'influencer', 'video'],
                'weight': 1.3
            },
            'ECOMMERCE': {
                'keywords': ['ecommerce', 'dropshipping', 'amazon', 'shopify', 'online store', 'selling'],
                'weight': 1.2
            },
            'FREELANCING': {
                'keywords': ['freelance', 'upwork', 'fiverr', 'remote work', 'consulting', 'services'],
                'weight': 1.1
            },
            'INVESTMENT': {
                'keywords': ['stocks', 'crypto', 'investment', 'trading', 'dividends', 'portfolio'],
                'weight': 1.0
            },
            'DIGITAL_PRODUCTS': {
                'keywords': ['course', 'ebook', 'software', 'app', 'saas', 'template'],
                'weight': 1.1
            }
        }
    
    async def analyze_market_trends_rpa(self, search_queries: List[str], time_range: str = "7d") -> List[RPATrendingTopic]:
        """
        使用RPA分析市场趋势
        
        Args:
            search_queries: 搜索关键词列表
            time_range: 时间范围
            
        Returns:
            趋势话题列表
        """
        self.logger.info(f"开始RPA市场趋势分析: {search_queries}")
        
        all_content = []
        
        # 使用RPA爬取多平台内容
        async with self.rpa_crawler:
            for query in search_queries:
                try:
                    content_items = await self.rpa_crawler.search_all_platforms_rpa(query, time_range)
                    all_content.extend(content_items)
                    
                    # 防止被检测，添加延迟
                    await asyncio.sleep(np.random.uniform(3, 7))
                    
                except Exception as e:
                    self.logger.error(f"RPA爬取失败 {query}: {e}")
                    continue
        
        self.logger.info(f"RPA爬取完成，共获取 {len(all_content)} 条内容")
        
        # 过滤低质量内容
        high_quality_content = [
            item for item in all_content 
            if item.confidence_score >= self.config['min_content_quality_score']
        ]
        
        self.logger.info(f"高质量内容: {len(high_quality_content)} 条")
        
        # 提取和分析话题
        trending_topics = await self._extract_trending_topics_rpa(high_quality_content)
        
        # 跨平台验证
        validated_topics = self._cross_platform_validation_rpa(trending_topics)
        
        # 计算趋势分数和洞察
        final_topics = []
        for topic in validated_topics:
            enhanced_topic = await self._enhance_topic_analysis(topic, high_quality_content)
            if enhanced_topic:
                final_topics.append(enhanced_topic)
        
        # 按置信度排序
        final_topics.sort(key=lambda x: x.confidence_score, reverse=True)
        
        self.logger.info(f"最终识别出 {len(final_topics)} 个趋势话题")
        return final_topics
    
    async def _extract_trending_topics_rpa(self, content_items: List[RPAContentItem]) -> List[RPATrendingTopic]:
        """从RPA内容中提取趋势话题"""
        topic_data = defaultdict(list)
        
        # 按平台分组分析
        platform_content = defaultdict(list)
        for item in content_items:
            platform_content[item.platform].append(item)
        
        # 提取每个平台的热门关键词
        all_keywords = []
        for platform, items in platform_content.items():
            platform_text = " ".join([f"{item.title} {item.content}" for item in items])
            
            # 使用现有的内容分析器提取关键词
            keywords = self._extract_keywords_advanced(platform_text)
            
            for keyword in keywords:
                topic_data[keyword].extend(items)
                all_keywords.append(keyword)
        
        # 统计关键词频率
        keyword_frequency = Counter(all_keywords)
        
        # 创建趋势话题
        trending_topics = []
        for keyword, freq in keyword_frequency.most_common(50):
            if freq >= 2:  # 至少出现2次
                related_items = topic_data[keyword]
                
                # 计算平台覆盖
                platforms = list(set([item.platform for item in related_items]))
                
                if len(platforms) >= self.config['min_cross_platform_mentions']:
                    topic = RPATrendingTopic(
                        topic=keyword,
                        platforms=platforms,
                        total_engagement=sum([
                            sum(item.engagement_metrics.values()) 
                            for item in related_items
                        ]),
                        growth_indicators=self._calculate_growth_indicators(related_items),
                        sentiment_score=self._analyze_sentiment_rpa(related_items),
                        content_samples=related_items[:5],
                        confidence_score=self._calculate_topic_confidence(keyword, related_items, platforms),
                        category=self._categorize_topic_rpa(keyword),
                        related_keywords=self._find_related_keywords(keyword, all_keywords),
                        market_opportunity="",  # 后续填充
                        scraped_at=datetime.now().isoformat()
                    )
                    
                    trending_topics.append(topic)
        
        return trending_topics
    
    def _cross_platform_validation_rpa(self, topics: List[RPATrendingTopic]) -> List[RPATrendingTopic]:
        """跨平台验证话题"""
        validated_topics = []
        
        for topic in topics:
            # 检查平台覆盖度
            if len(topic.platforms) >= self.config['min_cross_platform_mentions']:
                # 检查内容质量
                avg_quality = np.mean([item.confidence_score for item in topic.content_samples])
                
                if avg_quality >= self.config['min_content_quality_score']:
                    validated_topics.append(topic)
        
        return validated_topics
    
    async def _enhance_topic_analysis(self, topic: RPATrendingTopic, all_content: List[RPAContentItem]) -> Optional[RPATrendingTopic]:
        """增强话题分析"""
        try:
            # 市场机会分析
            market_opportunity = self._analyze_market_opportunity(topic)
            topic.market_opportunity = market_opportunity
            
            # 重新计算置信度（考虑更多因素）
            enhanced_confidence = self._calculate_enhanced_confidence(topic, all_content)
            topic.confidence_score = enhanced_confidence
            
            return topic
            
        except Exception as e:
            self.logger.error(f"增强话题分析失败 {topic.topic}: {e}")
            return None
    
    def _extract_keywords_advanced(self, text: str) -> List[str]:
        """高级关键词提取"""
        # 清理文本
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 提取1-3词的短语
        words = text.split()
        keywords = []
        
        # 单词
        word_freq = Counter(words)
        for word, freq in word_freq.most_common(50):
            if len(word) > 3 and freq > 2:
                keywords.append(word)
        
        # 二元组
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        bigram_freq = Counter(bigrams)
        for bigram, freq in bigram_freq.most_common(30):
            if freq > 1:
                keywords.append(bigram)
        
        # 三元组
        trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words)-2)]
        trigram_freq = Counter(trigrams)
        for trigram, freq in trigram_freq.most_common(20):
            if freq > 1:
                keywords.append(trigram)
        
        # 过滤停用词
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'man', 'men', 'put', 'say', 'she', 'too', 'use'}
        
        filtered_keywords = [kw for kw in keywords if not any(sw in kw.split() for sw in stop_words)]
        
        return filtered_keywords[:20]
    
    def _calculate_growth_indicators(self, content_items: List[RPAContentItem]) -> Dict[str, float]:
        """计算增长指标"""
        if not content_items:
            return {'growth_rate': 0.0, 'momentum': 0.0}
        
        # 按时间排序
        sorted_items = sorted(content_items, key=lambda x: x.scraped_at)
        
        # 计算时间段内的参与度变化
        if len(sorted_items) < 2:
            return {'growth_rate': 0.0, 'momentum': 0.5}
        
        # 简化的增长率计算
        early_engagement = np.mean([
            sum(item.engagement_metrics.values()) 
            for item in sorted_items[:len(sorted_items)//2]
        ])
        
        late_engagement = np.mean([
            sum(item.engagement_metrics.values()) 
            for item in sorted_items[len(sorted_items)//2:]
        ])
        
        growth_rate = (late_engagement - early_engagement) / max(early_engagement, 1)
        momentum = min(len(sorted_items) / 10.0, 1.0)  # 内容数量动量
        
        return {
            'growth_rate': round(growth_rate, 3),
            'momentum': round(momentum, 3)
        }
    
    def _analyze_sentiment_rpa(self, content_items: List[RPAContentItem]) -> float:
        """分析内容情感"""
        if not self.config['sentiment_analysis_enabled'] or not content_items:
            return 0.0
        
        # 简化的情感分析
        positive_indicators = ['great', 'amazing', 'excellent', 'fantastic', 'awesome', 'love', 'best', 'perfect', 'wonderful']
        negative_indicators = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disappointing', 'failed']
        
        total_score = 0
        total_items = 0
        
        for item in content_items:
            text = f"{item.title} {item.content}".lower()
            
            positive_count = sum(text.count(word) for word in positive_indicators)
            negative_count = sum(text.count(word) for word in negative_indicators)
            
            if positive_count + negative_count > 0:
                sentiment = (positive_count - negative_count) / (positive_count + negative_count)
                total_score += sentiment
                total_items += 1
        
        return round(total_score / max(total_items, 1), 3)
    
    def _calculate_topic_confidence(self, topic: str, content_items: List[RPAContentItem], platforms: List[str]) -> float:
        """计算话题置信度"""
        # 基础分数
        base_score = 0.5
        
        # 平台覆盖度奖励
        platform_bonus = min(len(platforms) * 0.1, 0.3)
        base_score += platform_bonus
        
        # 内容数量奖励
        content_bonus = min(len(content_items) * 0.02, 0.2)
        base_score += content_bonus
        
        # 内容质量奖励
        avg_quality = np.mean([item.confidence_score for item in content_items])
        quality_bonus = (avg_quality - 0.5) * 0.4
        base_score += quality_bonus
        
        # 参与度奖励
        total_engagement = sum([sum(item.engagement_metrics.values()) for item in content_items])
        engagement_bonus = min(total_engagement / 1000.0, 0.2)
        base_score += engagement_bonus
        
        return round(min(base_score, 1.0), 3)
    
    def _categorize_topic_rpa(self, topic: str) -> str:
        """对话题进行分类"""
        topic_lower = topic.lower()
        
        for category, config in self.topic_categories.items():
            for keyword in config['keywords']:
                if keyword in topic_lower:
                    return category
        
        return 'OTHER'
    
    def _find_related_keywords(self, main_keyword: str, all_keywords: List[str]) -> List[str]:
        """寻找相关关键词"""
        related = []
        main_words = set(main_keyword.lower().split())
        
        for keyword in all_keywords:
            if keyword != main_keyword:
                keyword_words = set(keyword.lower().split())
                # 计算词汇重叠
                overlap = len(main_words & keyword_words)
                if overlap > 0 and overlap / len(main_words) > 0.3:
                    related.append(keyword)
        
        return related[:5]
    
    def _analyze_market_opportunity(self, topic: RPATrendingTopic) -> str:
        """分析市场机会"""
        category_opportunities = {
            'AI_AUTOMATION': "AI工具和自动化服务需求增长，适合开发相关产品或提供咨询服务",
            'CONTENT_CREATION': "内容创作市场活跃，可开发创作工具或提供培训服务",
            'ECOMMERCE': "电商领域竞争激烈但机会多，适合产品销售或服务提供",
            'FREELANCING': "自由职业需求增长，适合技能型服务或平台开发",
            'INVESTMENT': "投资教育和工具需求稳定，适合知识付费或工具开发",
            'DIGITAL_PRODUCTS': "数字产品市场持续增长，适合课程、软件或模板销售"
        }
        
        base_opportunity = category_opportunities.get(topic.category, "新兴市场机会，需要进一步研究")
        
        # 根据话题数据增强分析
        if topic.total_engagement > 1000:
            base_opportunity += "，市场参与度高"
        
        if len(topic.platforms) >= 3:
            base_opportunity += "，跨平台热度高"
        
        if topic.growth_indicators.get('growth_rate', 0) > 0.5:
            base_opportunity += "，增长趋势明显"
        
        return base_opportunity
    
    def _calculate_enhanced_confidence(self, topic: RPATrendingTopic, all_content: List[RPAContentItem]) -> float:
        """计算增强的置信度"""
        # 原始置信度
        base_confidence = topic.confidence_score
        
        # 增长趋势奖励
        growth_bonus = topic.growth_indicators.get('growth_rate', 0) * 0.1
        
        # 情感分析奖励
        sentiment_bonus = max(topic.sentiment_score * 0.05, 0)
        
        # 相关内容丰富度
        related_content_count = len([
            item for item in all_content 
            if any(keyword in item.content.lower() for keyword in topic.related_keywords)
        ])
        richness_bonus = min(related_content_count * 0.01, 0.1)
        
        final_confidence = base_confidence + growth_bonus + sentiment_bonus + richness_bonus
        
        return round(min(final_confidence, 1.0), 3)
    
    async def identify_content_gaps(self, trending_topics: List[RPATrendingTopic]) -> List[ContentGap]:
        """识别内容空白机会"""
        gaps = []
        
        # 平台覆盖空白
        all_platforms = {'google', 'youtube', 'reddit', 'twitter'}
        
        for topic in trending_topics[:10]:  # 分析前10个话题
            missing_platforms = all_platforms - set(topic.platforms)
            
            if missing_platforms:
                gap = ContentGap(
                    gap_type="platform_coverage",
                    description=f"话题'{topic.topic}'在{missing_platforms}平台缺少内容",
                    opportunity_score=topic.confidence_score * 0.8,
                    target_platforms=list(missing_platforms),
                    suggested_content_types=self._suggest_content_types_for_platforms(missing_platforms),
                    competitive_analysis={}
                )
                gaps.append(gap)
        
        # 内容类型空白
        content_type_distribution = defaultdict(int)
        for topic in trending_topics:
            for item in topic.content_samples:
                if 'video' in item.engagement_metrics:
                    content_type_distribution['video'] += 1
                else:
                    content_type_distribution['text'] += 1
        
        if content_type_distribution['video'] < content_type_distribution['text'] * 0.3:
            gaps.append(ContentGap(
                gap_type="content_type",
                description="视频内容相对不足，有机会创作更多视频内容",
                opportunity_score=0.7,
                target_platforms=['youtube'],
                suggested_content_types=['tutorial_video', 'case_study_video', 'review_video'],
                competitive_analysis={}
            ))
        
        return gaps[:5]  # 返回前5个机会
    
    def _suggest_content_types_for_platforms(self, platforms: set) -> List[str]:
        """为平台建议内容类型"""
        suggestions = []
        
        if 'youtube' in platforms:
            suggestions.extend(['tutorial_video', 'review_video', 'case_study'])
        
        if 'reddit' in platforms:
            suggestions.extend(['discussion_post', 'ama', 'guide'])
        
        if 'twitter' in platforms:
            suggestions.extend(['thread', 'quick_tip', 'news_update'])
        
        if 'google' in platforms:
            suggestions.extend(['blog_post', 'how_to_guide', 'resource_list'])
        
        return list(set(suggestions))
    
    async def analyze_influencers(self, trending_topics: List[RPATrendingTopic]) -> List[InfluencerInsight]:
        """分析影响者"""
        influencers = []
        author_stats = defaultdict(lambda: {
            'platforms': set(),
            'total_engagement': 0,
            'content_count': 0,
            'topics': set()
        })
        
        # 统计作者数据
        for topic in trending_topics:
            for item in topic.content_samples:
                if item.author and item.author != 'Unknown':
                    stats = author_stats[item.author]
                    stats['platforms'].add(item.platform)
                    stats['total_engagement'] += sum(item.engagement_metrics.values())
                    stats['content_count'] += 1
                    stats['topics'].add(topic.topic)
        
        # 生成影响者洞察
        for author, stats in author_stats.items():
            if stats['content_count'] >= 2:  # 至少有2个内容
                avg_engagement = stats['total_engagement'] / stats['content_count']
                
                influencer = InfluencerInsight(
                    name=author,
                    platform=list(stats['platforms'])[0],  # 主要平台
                    follower_estimate=self._estimate_follower_count(avg_engagement),
                    engagement_rate=min(avg_engagement / 1000.0, 1.0),
                    content_themes=list(stats['topics'])[:5],
                    posting_frequency=self._estimate_posting_frequency(stats['content_count']),
                    collaboration_potential=self._calculate_collaboration_potential(stats)
                )
                
                influencers.append(influencer)
        
        # 按合作潜力排序
        influencers.sort(key=lambda x: x.collaboration_potential, reverse=True)
        
        return influencers[:10]
    
    def _estimate_follower_count(self, avg_engagement: float) -> int:
        """估算粉丝数量"""
        # 简化的估算公式
        if avg_engagement < 10:
            return int(avg_engagement * 100)
        elif avg_engagement < 100:
            return int(avg_engagement * 50)
        elif avg_engagement < 1000:
            return int(avg_engagement * 20)
        else:
            return int(avg_engagement * 10)
    
    def _estimate_posting_frequency(self, content_count: int) -> str:
        """估算发布频率"""
        if content_count >= 10:
            return "high"
        elif content_count >= 5:
            return "medium"
        else:
            return "low"
    
    def _calculate_collaboration_potential(self, stats: Dict) -> float:
        """计算合作潜力"""
        base_score = 0.5
        
        # 平台多样性
        platform_bonus = len(stats['platforms']) * 0.1
        
        # 参与度
        engagement_bonus = min(stats['total_engagement'] / 1000.0, 0.3)
        
        # 内容丰富度
        content_bonus = min(stats['content_count'] * 0.05, 0.2)
        
        return round(min(base_score + platform_bonus + engagement_bonus + content_bonus, 1.0), 3)


# 使用示例
async def main():
    """测试RPA内容分析器"""
    analyzer = RPAContentAnalyzer()
    
    # 分析市场趋势
    queries = ["ai automation", "passive income", "side hustle"]
    trending_topics = await analyzer.analyze_market_trends_rpa(queries, "7d")
    
    print(f"发现 {len(trending_topics)} 个趋势话题:")
    for topic in trending_topics[:5]:
        print(f"\n话题: {topic.topic}")
        print(f"平台: {', '.join(topic.platforms)}")
        print(f"置信度: {topic.confidence_score}")
        print(f"参与度: {topic.total_engagement}")
        print(f"市场机会: {topic.market_opportunity}")
    
    # 识别内容空白
    gaps = await analyzer.identify_content_gaps(trending_topics)
    print(f"\n内容空白机会 ({len(gaps)}个):")
    for gap in gaps:
        print(f"- {gap.description} (评分: {gap.opportunity_score})")
    
    # 分析影响者
    influencers = await analyzer.analyze_influencers(trending_topics)
    print(f"\n关键影响者 ({len(influencers)}个):")
    for inf in influencers[:3]:
        print(f"- {inf.name} ({inf.platform}): 合作潜力 {inf.collaboration_potential}")

if __name__ == "__main__":
    asyncio.run(main())