"""
智能选题服务 - 集成爬虫和内容分析
"""

import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import os
from .wechat_crawler import WeChatCrawler
from .content_analyzer import ContentAnalyzer
from models.schemas import Topic, TopicCategory
import logging

class IntelligentTopicService:
    def __init__(self):
        self.crawler = WeChatCrawler()
        self.analyzer = ContentAnalyzer()
        self.cache_file = "data/topics_cache.json"
        self.cache_duration = timedelta(hours=6)  # 缓存6小时
        
        # 确保数据目录存在
        os.makedirs("data", exist_ok=True)
        
        # 日志配置
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def get_trending_topics_from_wechat(self, wechat_urls: List[str], limit: int = 10) -> List[Topic]:
        """
        从微信公众号文章中提取热门选题
        """
        try:
            # 检查缓存
            cached_topics = self._load_cache()
            if cached_topics:
                self.logger.info(f"从缓存加载了 {len(cached_topics)} 个选题")
                return cached_topics[:limit]
            
            all_topics = []
            
            # 爬取并分析每个URL
            for url in wechat_urls:
                try:
                    self.logger.info(f"开始爬取文章: {url}")
                    
                    # 爬取文章信息
                    article_info = self.crawler.extract_article_info(url)
                    
                    if 'error' in article_info:
                        self.logger.warning(f"爬取失败: {article_info['error']}")
                        continue
                    
                    # 分析文章内容
                    analysis_result = self.analyzer.analyze_article(
                        article_info.get('title', ''),
                        article_info.get('content', '')
                    )
                    
                    # 生成选题
                    topics = self._generate_topics_from_analysis(article_info, analysis_result)
                    all_topics.extend(topics)
                    
                    # 添加延迟，避免被封
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"处理文章时出错 {url}: {str(e)}")
                    continue
            
            # 按热度排序并去重
            unique_topics = self._deduplicate_topics(all_topics)
            sorted_topics = sorted(unique_topics, key=lambda x: x.heat, reverse=True)
            
            # 缓存结果
            self._save_cache(sorted_topics)
            
            self.logger.info(f"成功生成 {len(sorted_topics)} 个选题")
            return sorted_topics[:limit]
            
        except Exception as e:
            self.logger.error(f"获取热门选题失败: {str(e)}")
            # 返回备用选题
            return await self._get_fallback_topics(limit)

    def _generate_topics_from_analysis(self, article_info: Dict, analysis_result: Dict) -> List[Topic]:
        """
        基于分析结果生成选题
        """
        topics = []
        
        # 从分析结果中提取信息
        category_info = analysis_result.get('category_info', {})
        heat_analysis = analysis_result.get('heat_analysis', {})
        keywords = analysis_result.get('keywords', [])
        topic_suggestions = analysis_result.get('topic_suggestions', [])
        
        # 映射分类
        category_mapping = {
            'AI工具': TopicCategory.AI_TOOLS,
            '电商变现': TopicCategory.E_COMMERCE,
            '内容创作': TopicCategory.CONTENT_CREATION,
            '技能变现': TopicCategory.SKILL_MONETIZATION,
            '投资理财': TopicCategory.INVESTMENT,
            '线上服务': TopicCategory.FREELANCE
        }
        
        primary_category = category_info.get('primary_category', '其他')
        topic_category = category_mapping.get(primary_category, TopicCategory.FREELANCE)
        
        # 基于建议生成Topic对象
        for i, suggestion in enumerate(topic_suggestions):
            try:
                topic = Topic(
                    id=len(topics) + 1,
                    title=suggestion['title'],
                    reason=suggestion['reason'],
                    category=topic_category,
                    heat=suggestion['heat_score'],
                    keywords=[kw['word'] for kw in keywords[:5]],
                    source_url=article_info.get('url', '')
                )
                topics.append(topic)
            except Exception as e:
                self.logger.warning(f"创建选题对象失败: {str(e)}")
                continue
        
        # 如果没有生成选题，创建一个基础选题
        if not topics:
            try:
                basic_topic = Topic(
                    id=1,
                    title=f"基于'{article_info.get('title', '未知文章')[:30]}'的副业机会分析",
                    reason=f"来源于{primary_category}领域的热门文章，{heat_analysis.get('description', '具有一定市场潜力')}",
                    category=topic_category,
                    heat=heat_analysis.get('total_score', 50),
                    keywords=[kw['word'] for kw in keywords[:3]],
                    source_url=article_info.get('url', '')
                )
                topics.append(basic_topic)
            except Exception as e:
                self.logger.error(f"创建基础选题失败: {str(e)}")
        
        return topics

    def _deduplicate_topics(self, topics: List[Topic]) -> List[Topic]:
        """
        选题去重，基于标题相似度
        """
        unique_topics = []
        seen_titles = set()
        
        for topic in topics:
            # 简单的去重策略：标题前20个字符
            title_key = topic.title[:20].lower()
            
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_topics.append(topic)
        
        return unique_topics

    def _load_cache(self) -> Optional[List[Topic]]:
        """
        加载缓存的选题
        """
        try:
            if not os.path.exists(self.cache_file):
                return None
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 检查缓存是否过期
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cache_time > self.cache_duration:
                return None
            
            # 重建Topic对象
            topics = []
            for topic_data in cache_data['topics']:
                try:
                    topic = Topic(**topic_data)
                    topics.append(topic)
                except Exception as e:
                    self.logger.warning(f"重建Topic对象失败: {str(e)}")
                    continue
            
            return topics
            
        except Exception as e:
            self.logger.warning(f"加载缓存失败: {str(e)}")
            return None

    def _save_cache(self, topics: List[Topic]):
        """
        保存选题到缓存
        """
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'topics': [topic.dict() for topic in topics]
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"已缓存 {len(topics)} 个选题")
            
        except Exception as e:
            self.logger.error(f"保存缓存失败: {str(e)}")

    async def _get_fallback_topics(self, limit: int) -> List[Topic]:
        """
        获取备用选题（当爬取失败时使用）
        """
        fallback_topics = [
            Topic(
                id=1,
                title="AI写作助手副业：ChatGPT文案代写月入8000+",
                reason="AI技术成熟，市场需求旺盛，入门门槛适中",
                category=TopicCategory.AI_TOOLS,
                heat=85,
                keywords=["AI写作", "ChatGPT", "文案", "代写"]
            ),
            Topic(
                id=2,
                title="小红书种草文案接单：单篇200元的内容变现",
                reason="品牌营销需求持续增长，种草文案市场火热",
                category=TopicCategory.CONTENT_CREATION,
                heat=78,
                keywords=["小红书", "种草", "文案", "品牌"]
            ),
            Topic(
                id=3,
                title="闲鱼无货源模式：新手也能月收入5000+",
                reason="电商门槛低，无需囤货，适合副业起步",
                category=TopicCategory.E_COMMERCE,
                heat=72,
                keywords=["闲鱼", "无货源", "电商", "副业"]
            )
        ]
        
        return fallback_topics[:limit]

    async def analyze_single_article(self, url: str) -> Dict:
        """
        分析单篇文章并返回详细信息
        """
        try:
            # 爬取文章
            article_info = self.crawler.extract_article_info(url)
            
            if 'error' in article_info:
                return {'error': article_info['error']}
            
            # 分析内容
            analysis_result = self.analyzer.analyze_article(
                article_info.get('title', ''),
                article_info.get('content', '')
            )
            
            # 生成选题
            topics = self._generate_topics_from_analysis(article_info, analysis_result)
            
            return {
                'article_info': article_info,
                'analysis_result': analysis_result,
                'generated_topics': [topic.dict() for topic in topics],
                'analyzed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"分析文章失败 {url}: {str(e)}")
            return {'error': str(e)}

    async def batch_analyze_articles(self, urls: List[str]) -> Dict:
        """
        批量分析多篇文章
        """
        results = {
            'success_count': 0,
            'error_count': 0,
            'articles': [],
            'all_topics': [],
            'summary': {}
        }
        
        for url in urls:
            try:
                result = await self.analyze_single_article(url)
                
                if 'error' not in result:
                    results['success_count'] += 1
                    results['articles'].append(result)
                    
                    # 收集所有选题
                    for topic_data in result['generated_topics']:
                        topic = Topic(**topic_data)
                        results['all_topics'].append(topic)
                else:
                    results['error_count'] += 1
                    
                # 添加延迟
                await asyncio.sleep(2)
                
            except Exception as e:
                results['error_count'] += 1
                self.logger.error(f"批量分析出错 {url}: {str(e)}")
        
        # 生成汇总信息
        results['summary'] = self._generate_batch_summary(results['all_topics'])
        
        # 去重并排序
        unique_topics = self._deduplicate_topics(results['all_topics'])
        results['recommended_topics'] = sorted(unique_topics, key=lambda x: x.heat, reverse=True)[:10]
        
        return results

    def _generate_batch_summary(self, topics: List[Topic]) -> Dict:
        """
        生成批量分析汇总
        """
        if not topics:
            return {}
        
        # 分类统计
        category_count = {}
        for topic in topics:
            category = topic.category.value
            category_count[category] = category_count.get(category, 0) + 1
        
        # 热度统计
        heat_scores = [topic.heat for topic in topics]
        avg_heat = sum(heat_scores) / len(heat_scores)
        
        # 关键词统计
        all_keywords = []
        for topic in topics:
            all_keywords.extend(topic.keywords)
        
        from collections import Counter
        top_keywords = Counter(all_keywords).most_common(10)
        
        return {
            'total_topics': len(topics),
            'category_distribution': category_count,
            'average_heat': round(avg_heat, 2),
            'top_keywords': [{'word': word, 'count': count} for word, count in top_keywords],
            'heat_range': {
                'min': min(heat_scores),
                'max': max(heat_scores),
                'avg': round(avg_heat, 2)
            }
        }