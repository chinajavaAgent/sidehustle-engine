#!/usr/bin/env python3
"""
RPA多平台内容爬虫系统
基于浏览器自动化技术，无需API密钥，支持Google、YouTube、Reddit、Twitter等平台的高级搜索
使用Selenium和Playwright进行真实浏览器操作
"""

import asyncio
import json
import re
import time
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from urllib.parse import quote, urlencode
import os
from bs4 import BeautifulSoup

# RPA相关导入
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from .rpa_anti_detection import RPAAntiDetection

@dataclass
class ContentItem:
    """统一的内容项数据结构"""
    platform: str
    title: str
    content: str
    url: str
    author: str
    publish_time: str
    engagement_score: int  # 参与度评分
    quality_score: int     # 内容质量评分
    tags: List[str]
    media_type: str        # text, video, image, etc.
    
class RPAMultiPlatformCrawler:
    """RPA多平台内容爬虫 - 基于浏览器自动化"""
    
    def __init__(self, use_playwright: bool = True):
        self.logger = logging.getLogger(__name__)
        self.use_playwright = use_playwright and PLAYWRIGHT_AVAILABLE
        self.anti_detection = RPAAntiDetection()
        
        # 浏览器实例
        self.browser = None
        self.context = None
        self.driver = None
        
        # RPA搜索配置
        self.search_limits = {
            'google': 20,
            'youtube': 15,
            'reddit': 25,
            'twitter': 20
        }
        
        # 搜索延迟配置
        self.delays = {
            'between_searches': (3, 7),
            'page_load': (2, 5),
            'typing': (0.1, 0.3),
            'scroll': (1, 3)
        }
    
    async def __aenter__(self):
        await self.initialize_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup_browser()
    
    async def initialize_browser(self):
        """初始化浏览器"""
        try:
            if self.use_playwright:
                self.browser, self.context = await self.anti_detection.create_stealth_browser_playwright()
                self.logger.info("Playwright浏览器初始化成功")
            else:
                self.driver = self.anti_detection.create_stealth_browser_selenium()
                self.logger.info("Selenium浏览器初始化成功")
        except Exception as e:
            self.logger.error(f"浏览器初始化失败: {e}")
            raise
    
    async def cleanup_browser(self):
        """清理浏览器资源"""
        try:
            if self.use_playwright:
                if self.browser:
                    await self.browser.close()
            else:
                if self.driver:
                    self.driver.quit()
            self.logger.info("浏览器资源清理完成")
        except Exception as e:
            self.logger.warning(f"浏览器清理警告: {e}")
    
    async def search_all_platforms_rpa(self, query: str, time_range: str = "7d") -> List['RPAContentItem']:
        """
        使用RPA在所有平台上搜索内容
        
        Args:
            query: 搜索关键词
            time_range: 时间范围 (1d, 7d, 30d)
        """
        self.logger.info(f"开始RPA多平台搜索: {query}")
        
        all_content = []
        platforms = ['google', 'youtube', 'reddit', 'twitter']
        
        # 依次搜索各平台（避免并发导致检测）
        for platform in platforms:
            try:
                self.logger.info(f"正在搜索 {platform.upper()}...")
                
                if platform == 'google':
                    results = await self.search_google_rpa(query, time_range)
                elif platform == 'youtube':
                    results = await self.search_youtube_rpa(query, time_range)
                elif platform == 'reddit':
                    results = await self.search_reddit_rpa(query, time_range)
                elif platform == 'twitter':
                    results = await self.search_twitter_rpa(query, time_range)
                
                all_content.extend(results)
                
                # 平台间延迟
                delay = random.uniform(*self.delays['between_searches'])
                self.logger.info(f"{platform.upper()}搜索完成，获取{len(results)}条结果，等待{delay:.1f}秒")
                await asyncio.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"{platform.upper()} RPA搜索失败: {e}")
                continue
        
        # 按质量和参与度排序
        all_content.sort(key=lambda x: (x.confidence_score + sum(x.engagement_metrics.values())/100), reverse=True)
        
        self.logger.info(f"RPA搜索完成，共获取 {len(all_content)} 条内容")
        return all_content
    
    async def search_google(self, query: str, time_range: str) -> List[ContentItem]:
        """Google高级搜索"""
        if not self.google_api_key or not self.google_search_engine_id:
            self.logger.warning("Google API未配置，使用备用搜索")
            return await self._fallback_google_search(query)
        
        try:
            # 构建高级搜索参数
            params = {
                'key': self.google_api_key,
                'cx': self.google_search_engine_id,
                'q': f'"{query}" side hustle OR "passive income" OR monetization',
                'num': self.search_limits['google'],
                'dateRestrict': self._convert_time_range(time_range),
                'sort': 'date',
                'lr': 'lang_en',  # 英文内容
                'safe': 'active'
            }
            
            url = "https://www.googleapis.com/customsearch/v1"
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._parse_google_results(data)
                else:
                    self.logger.error(f"Google搜索API错误: {response.status}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Google搜索失败: {e}")
            return []
    
    async def search_twitter(self, query: str, time_range: str) -> List[ContentItem]:
        """Twitter高级搜索"""
        if not self.twitter_bearer_token:
            self.logger.warning("Twitter API未配置，跳过Twitter搜索")
            return []
        
        try:
            # Twitter API v2 高级搜索
            search_query = f'"{query}" (side hustle OR passive income OR monetization) -is:retweet lang:en'
            
            params = {
                'query': search_query,
                'max_results': min(self.search_limits['twitter'], 100),
                'tweet.fields': 'created_at,author_id,public_metrics,context_annotations,lang',
                'user.fields': 'username,verified,public_metrics',
                'expansions': 'author_id'
            }
            
            # 添加时间过滤
            if time_range != "all":
                start_time = self._get_start_time(time_range)
                params['start_time'] = start_time.isoformat()
            
            headers = {
                'Authorization': f'Bearer {self.twitter_bearer_token}',
                'Content-Type': 'application/json'
            }
            
            url = "https://api.twitter.com/2/tweets/search/recent"
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._parse_twitter_results(data)
                else:
                    self.logger.error(f"Twitter搜索API错误: {response.status}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Twitter搜索失败: {e}")
            return []
    
    async def search_reddit(self, query: str, time_range: str) -> List[ContentItem]:
        """Reddit高级搜索"""
        try:
            # Reddit API搜索 (使用公开API)
            params = {
                'q': f'"{query}" AND (side hustle OR passive income OR monetization)',
                'sort': 'hot',
                'time': self._convert_reddit_time(time_range),
                'limit': self.search_limits['reddit'],
                'type': 'link,sr'
            }
            
            # 搜索相关subreddits
            subreddits = [
                'entrepreneur', 'sidehustle', 'passiveincome', 
                'personalfinance', 'digitalnomad', 'freelance'
            ]
            
            all_results = []
            
            for subreddit in subreddits[:3]:  # 限制搜索范围
                url = f"https://www.reddit.com/r/{subreddit}/search.json"
                
                search_params = params.copy()
                search_params['restrict_sr'] = 'true'
                
                headers = {
                    'User-Agent': 'SideHustleEngine/1.0 (Content Research)'
                }
                
                async with self.session.get(url, params=search_params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = await self._parse_reddit_results(data, subreddit)
                        all_results.extend(results)
                    
                # 请求间隔
                await asyncio.sleep(1)
            
            return all_results[:self.search_limits['reddit']]
            
        except Exception as e:
            self.logger.error(f"Reddit搜索失败: {e}")
            return []
    
    async def search_youtube(self, query: str, time_range: str) -> List[ContentItem]:
        """YouTube高级搜索和视频内容解析"""
        if not self.youtube_api_key:
            self.logger.warning("YouTube API未配置，跳过YouTube搜索")
            return []
        
        try:
            # YouTube Data API v3 搜索
            params = {
                'key': self.youtube_api_key,
                'part': 'snippet',
                'q': f'"{query}" side hustle passive income monetization tutorial',
                'type': 'video',
                'order': 'relevance',
                'maxResults': self.search_limits['youtube'],
                'relevanceLanguage': 'en',
                'publishedAfter': self._get_start_time(time_range).isoformat() + 'Z'
            }
            
            url = "https://www.googleapis.com/youtube/v3/search"
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._parse_youtube_results(data)
                else:
                    self.logger.error(f"YouTube搜索API错误: {response.status}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"YouTube搜索失败: {e}")
            return []
    
    async def extract_video_content(self, video_id: str) -> Dict[str, str]:
        """
        提取YouTube视频的文本内容
        包括标题、描述、字幕等
        """
        try:
            # 获取视频详细信息
            params = {
                'key': self.youtube_api_key,
                'part': 'snippet,statistics',
                'id': video_id
            }
            
            url = "https://www.googleapis.com/youtube/v3/videos"
            
            video_info = {}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('items'):
                        item = data['items'][0]
                        snippet = item['snippet']
                        stats = item.get('statistics', {})
                        
                        video_info = {
                            'title': snippet.get('title', ''),
                            'description': snippet.get('description', ''),
                            'view_count': int(stats.get('viewCount', 0)),
                            'like_count': int(stats.get('likeCount', 0)),
                            'comment_count': int(stats.get('commentCount', 0))
                        }
            
            # 尝试获取字幕
            captions = await self._get_video_captions(video_id)
            if captions:
                video_info['captions'] = captions
            
            return video_info
            
        except Exception as e:
            self.logger.error(f"视频内容提取失败: {e}")
            return {}
    
    async def _get_video_captions(self, video_id: str) -> str:
        """获取YouTube视频字幕"""
        try:
            # 这里需要使用第三方库如youtube-transcript-api
            # 或者实现自定义的字幕解析逻辑
            
            # 备用方案：解析网页中的字幕信息
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    # 简单的字幕提取逻辑
                    # 实际应用中需要更复杂的解析
                    return self._extract_captions_from_html(html)
            
            return ""
            
        except Exception as e:
            self.logger.error(f"字幕获取失败: {e}")
            return ""
    
    def _extract_captions_from_html(self, html: str) -> str:
        """从HTML中提取字幕信息"""
        # 这是一个简化的实现
        # 实际需要解析YouTube的字幕数据
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找可能包含字幕的脚本标签
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'captions' in script.string:
                # 这里需要更复杂的JSON解析逻辑
                pass
        
        return ""
    
    # 辅助方法
    def _convert_time_range(self, time_range: str) -> str:
        """转换时间范围为Google API格式"""
        mapping = {
            '1d': 'd1',
            '7d': 'd7', 
            '30d': 'd30',
            'all': ''
        }
        return mapping.get(time_range, 'd7')
    
    def _convert_reddit_time(self, time_range: str) -> str:
        """转换时间范围为Reddit API格式"""
        mapping = {
            '1d': 'day',
            '7d': 'week',
            '30d': 'month',
            'all': 'all'
        }
        return mapping.get(time_range, 'week')
    
    def _get_start_time(self, time_range: str) -> datetime:
        """获取搜索开始时间"""
        now = datetime.utcnow()
        mapping = {
            '1d': now - timedelta(days=1),
            '7d': now - timedelta(days=7),
            '30d': now - timedelta(days=30),
            'all': now - timedelta(days=365)
        }
        return mapping.get(time_range, now - timedelta(days=7))
    
    async def _fallback_google_search(self, query: str) -> List[ContentItem]:
        """Google搜索备用方案"""
        # 使用DuckDuckGo或其他搜索引擎作为备用
        self.logger.info("使用备用搜索方案")
        return []
    
    async def _parse_google_results(self, data: Dict) -> List[ContentItem]:
        """解析Google搜索结果"""
        items = []
        
        for item in data.get('items', []):
            try:
                # 获取页面内容
                page_content = await self._fetch_page_content(item['link'])
                
                content_item = ContentItem(
                    platform='google',
                    title=item.get('title', ''),
                    content=page_content[:1000],  # 限制长度
                    url=item.get('link', ''),
                    author=item.get('displayLink', ''),
                    publish_time=datetime.now().isoformat(),
                    engagement_score=self._calculate_google_engagement(item),
                    quality_score=self._calculate_content_quality(page_content),
                    tags=[],
                    media_type='text'
                )
                
                items.append(content_item)
                
            except Exception as e:
                self.logger.warning(f"解析Google结果失败: {e}")
                continue
        
        return items
    
    async def _parse_twitter_results(self, data: Dict) -> List[ContentItem]:
        """解析Twitter搜索结果"""
        items = []
        
        tweets = data.get('data', [])
        users = {user['id']: user for user in data.get('includes', {}).get('users', [])}
        
        for tweet in tweets:
            try:
                author_id = tweet.get('author_id')
                author = users.get(author_id, {})
                metrics = tweet.get('public_metrics', {})
                
                content_item = ContentItem(
                    platform='twitter',
                    title=tweet.get('text', '')[:100] + '...',
                    content=tweet.get('text', ''),
                    url=f"https://twitter.com/i/status/{tweet['id']}",
                    author=author.get('username', ''),
                    publish_time=tweet.get('created_at', ''),
                    engagement_score=self._calculate_twitter_engagement(metrics),
                    quality_score=self._calculate_content_quality(tweet.get('text', '')),
                    tags=[],
                    media_type='text'
                )
                
                items.append(content_item)
                
            except Exception as e:
                self.logger.warning(f"解析Twitter结果失败: {e}")
                continue
        
        return items
    
    async def _parse_reddit_results(self, data: Dict, subreddit: str) -> List[ContentItem]:
        """解析Reddit搜索结果"""
        items = []
        
        posts = data.get('data', {}).get('children', [])
        
        for post_data in posts:
            try:
                post = post_data.get('data', {})
                
                content_item = ContentItem(
                    platform='reddit',
                    title=post.get('title', ''),
                    content=post.get('selftext', '')[:1000],
                    url=f"https://reddit.com{post.get('permalink', '')}",
                    author=post.get('author', ''),
                    publish_time=datetime.fromtimestamp(post.get('created_utc', 0)).isoformat(),
                    engagement_score=self._calculate_reddit_engagement(post),
                    quality_score=self._calculate_content_quality(post.get('selftext', '')),
                    tags=[subreddit],
                    media_type='text'
                )
                
                items.append(content_item)
                
            except Exception as e:
                self.logger.warning(f"解析Reddit结果失败: {e}")
                continue
        
        return items
    
    async def _parse_youtube_results(self, data: Dict) -> List[ContentItem]:
        """解析YouTube搜索结果"""
        items = []
        
        for item in data.get('items', []):
            try:
                snippet = item.get('snippet', {})
                video_id = item.get('id', {}).get('videoId')
                
                # 获取视频详细内容
                video_content = await self.extract_video_content(video_id)
                
                content = f"{snippet.get('description', '')}\n{video_content.get('captions', '')}"
                
                content_item = ContentItem(
                    platform='youtube',
                    title=snippet.get('title', ''),
                    content=content[:1000],
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    author=snippet.get('channelTitle', ''),
                    publish_time=snippet.get('publishedAt', ''),
                    engagement_score=self._calculate_youtube_engagement(video_content),
                    quality_score=self._calculate_content_quality(content),
                    tags=[],
                    media_type='video'
                )
                
                items.append(content_item)
                
            except Exception as e:
                self.logger.warning(f"解析YouTube结果失败: {e}")
                continue
        
        return items
    
    async def _fetch_page_content(self, url: str) -> str:
        """获取网页内容"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # 移除脚本和样式
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # 获取主要内容
                    text = soup.get_text()
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = '\n'.join(chunk for chunk in chunks if chunk)
                    
                    return text[:2000]  # 限制长度
                    
        except Exception as e:
            self.logger.warning(f"获取页面内容失败 {url}: {e}")
            
        return ""
    
    def _calculate_google_engagement(self, item: Dict) -> int:
        """计算Google结果的参与度评分"""
        # 基于网站权威性、标题质量等
        score = 50  # 基础分
        
        # 知名网站加分
        domain = item.get('displayLink', '').lower()
        high_authority_domains = ['medium.com', 'forbes.com', 'entrepreneur.com', 'inc.com']
        
        if any(domain.endswith(d) for d in high_authority_domains):
            score += 30
        
        return min(score, 100)
    
    def _calculate_twitter_engagement(self, metrics: Dict) -> int:
        """计算Twitter的参与度评分"""
        retweets = metrics.get('retweet_count', 0)
        likes = metrics.get('like_count', 0)
        replies = metrics.get('reply_count', 0)
        
        # 综合参与度计算
        engagement = retweets * 3 + likes + replies * 2
        
        # 转换为100分制
        if engagement < 10:
            return 20
        elif engagement < 100:
            return 40 + (engagement / 100) * 30
        else:
            return min(70 + (engagement / 1000) * 30, 100)
    
    def _calculate_reddit_engagement(self, post: Dict) -> int:
        """计算Reddit的参与度评分"""
        score = post.get('score', 0)
        comments = post.get('num_comments', 0)
        
        # Reddit评分计算
        engagement = score + comments * 2
        
        if engagement < 5:
            return 20
        elif engagement < 50:
            return 30 + (engagement / 50) * 40
        else:
            return min(70 + (engagement / 500) * 30, 100)
    
    def _calculate_youtube_engagement(self, video_content: Dict) -> int:
        """计算YouTube的参与度评分"""
        views = video_content.get('view_count', 0)
        likes = video_content.get('like_count', 0)
        comments = video_content.get('comment_count', 0)
        
        # YouTube参与度计算
        if views == 0:
            return 30
        
        engagement_rate = (likes + comments * 2) / views * 1000
        
        if engagement_rate < 1:
            return 20
        elif engagement_rate < 10:
            return 30 + engagement_rate * 5
        else:
            return min(80 + engagement_rate, 100)
    
    def _calculate_content_quality(self, text: str) -> int:
        """计算内容质量评分"""
        if not text:
            return 20
        
        score = 50  # 基础分
        
        # 长度评分
        if len(text) > 500:
            score += 20
        elif len(text) > 200:
            score += 10
        
        # 关键词密度
        quality_keywords = ['tutorial', 'guide', 'step', 'how to', 'strategy', 'tips', 'method']
        keyword_count = sum(text.lower().count(kw) for kw in quality_keywords)
        score += min(keyword_count * 5, 20)
        
        # 结构化内容
        if any(marker in text for marker in ['1.', '2.', '•', '-', 'Step']):
            score += 10
        
        return min(score, 100)


# 使用示例
async def main():
    """测试多平台爬虫"""
    async with MultiPlatformCrawler() as crawler:
        results = await crawler.search_all_platforms("passive income online", "7d")
        
        print(f"找到 {len(results)} 条内容:")
        for item in results[:5]:
            print(f"\n[{item.platform.upper()}] {item.title}")
            print(f"作者: {item.author}")
            print(f"参与度: {item.engagement_score}/100")
            print(f"质量: {item.quality_score}/100")
            print(f"内容: {item.content[:200]}...")

if __name__ == "__main__":
    asyncio.run(main())