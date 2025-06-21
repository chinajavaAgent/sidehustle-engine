#!/usr/bin/env python3
"""
RPA多平台内容爬虫系统
基于浏览器自动化技术，无需API密钥，支持Google、YouTube、Reddit、Twitter等平台的高级搜索
使用Playwright进行真实浏览器操作
"""

import asyncio
import re
import random
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import logging
from urllib.parse import quote

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from .rpa_anti_detection import RPAAntiDetection

@dataclass
class RPAContentItem:
    """RPA抓取的内容项数据结构"""
    platform: str
    title: str
    content: str
    url: str
    author: str
    engagement_metrics: Dict[str, Any]  # 平台特定的参与度指标
    confidence_score: float             # 内容置信度评分 (0-1)
    scraped_at: str                    # 抓取时间

class RPAMultiPlatformCrawler:
    """RPA多平台内容爬虫 - 基于浏览器自动化"""
    
    def __init__(self, use_playwright: bool = True):
        self.logger = logging.getLogger(__name__)
        self.use_playwright = use_playwright and PLAYWRIGHT_AVAILABLE
        self.anti_detection = RPAAntiDetection()
        
        # 浏览器实例
        self.browser = None
        self.context = None
        
        # RPA搜索配置
        self.search_limits = {
            'google': 15,
            'youtube': 10,
            'reddit': 15,
            'twitter': 10
        }
        
        # 搜索延迟配置
        self.delays = {
            'between_searches': (3, 7),
            'page_load': (2, 5)
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
                raise NotImplementedError("当前版本主要支持Playwright")
        except Exception as e:
            self.logger.error(f"浏览器初始化失败: {e}")
            raise
    
    async def cleanup_browser(self):
        """清理浏览器资源"""
        try:
            if self.browser:
                await self.browser.close()
            self.logger.info("浏览器资源清理完成")
        except Exception as e:
            self.logger.warning(f"浏览器清理警告: {e}")
    
    async def search_all_platforms_rpa(self, query: str, time_range: str = "7d") -> List[RPAContentItem]:
        """
        使用RPA在所有平台上搜索内容
        
        Args:
            query: 搜索关键词
            time_range: 时间范围 (1d, 7d, 30d)
        """
        self.logger.info(f"开始RPA多平台搜索: {query}")
        
        all_content = []
        # 从稳定的平台开始，YouTube暂时跳过
        platforms = ['google', 'reddit']  # 优先测试稳定平台
        
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
                
                all_content.extend(results)
                
                # 平台间延迟
                delay = random.uniform(*self.delays['between_searches'])
                self.logger.info(f"{platform.upper()}搜索完成，获取{len(results)}条结果，等待{delay:.1f}秒")
                await asyncio.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"{platform.upper()} RPA搜索失败: {e}")
                # 继续搜索其他平台而不是完全失败
                continue
        
        # 按质量和参与度排序
        if all_content:
            all_content.sort(key=lambda x: x.confidence_score, reverse=True)
        
        self.logger.info(f"RPA搜索完成，共获取 {len(all_content)} 条内容")
        return all_content
    
    async def search_google_rpa(self, query: str, time_range: str) -> List[RPAContentItem]:
        """Google RPA高级搜索"""
        results = []
        page = await self.context.new_page()
        
        try:
            # 访问Google
            await page.goto('https://www.google.com', wait_until='networkidle')
            await self.anti_detection.simulate_human_behavior_playwright(page)
            
            # 构建搜索查询
            search_query = f'{query} ("side hustle" OR "passive income" OR monetization OR tutorial)'
            
            # 输入搜索词 - Google使用textarea
            search_selectors = ['textarea[name="q"]', 'input[name="q"]', '#APjFqb']
            search_box = None
            
            for selector in search_selectors:
                try:
                    search_box = await page.wait_for_selector(selector, timeout=5000)
                    if search_box:
                        break
                except:
                    continue
            
            if not search_box:
                raise Exception("未找到Google搜索框")
            
            await search_box.click()
            await page.wait_for_timeout(random.randint(500, 1500))
            
            # 模拟人类输入
            await search_box.fill('')  # 清空
            await self.anti_detection.type_like_human_playwright(page, search_selectors[0], search_query)
            await page.keyboard.press('Enter')
            
            # 等待结果加载 - 使用更宽松的选择器
            await page.wait_for_timeout(3000)
            await self.anti_detection.simulate_human_behavior_playwright(page)
            
            # 提取搜索结果 - 尝试多种选择器
            search_results = []
            result_selectors = ['div.g', '.yuRUbf', '[data-ved]', 'div[data-hveid]']
            
            for selector in result_selectors:
                search_results = await page.query_selector_all(selector)
                if search_results:
                    self.logger.info(f"使用选择器 {selector} 找到 {len(search_results)} 个结果")
                    break
            
            if not search_results:
                # 如果没有找到结果，可能遇到验证码或被阻止
                page_content = await page.content()
                if 'captcha' in page_content.lower() or 'blocked' in page_content.lower():
                    self.logger.warning("Google搜索被阻止或需要验证码")
                else:
                    self.logger.warning("未找到搜索结果元素")
                return []
            
            for i, result in enumerate(search_results[:self.search_limits['google']]):
                try:
                    # 提取标题和链接
                    title_element = await result.query_selector('h3')
                    link_element = await result.query_selector('a')
                    snippet_element = await result.query_selector('.VwiC3b')
                    
                    if title_element and link_element:
                        title = await title_element.inner_text()
                        url = await link_element.get_attribute('href')
                        snippet = await snippet_element.inner_text() if snippet_element else ''
                        
                        # 创建内容项
                        item = RPAContentItem(
                            platform='google',
                            title=title,
                            content=snippet,
                            url=url,
                            author=self._extract_domain_from_url(url),
                            engagement_metrics={'ranking': len(search_results) - i},
                            confidence_score=self._calculate_google_confidence(title, snippet),
                            scraped_at=datetime.now().isoformat()
                        )
                        
                        results.append(item)
                        
                except Exception as e:
                    self.logger.warning(f"解析Google结果项失败: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Google RPA搜索失败: {e}")
        finally:
            await page.close()
            
        return results
    
    async def search_youtube_rpa(self, query: str, time_range: str) -> List[RPAContentItem]:
        """YouTube RPA高级搜索"""
        results = []
        page = await self.context.new_page()
        
        try:
            # 访问YouTube
            await page.goto('https://www.youtube.com', wait_until='networkidle')
            await self.anti_detection.simulate_human_behavior_playwright(page)
            
            # 构建搜索查询
            search_query = f'{query} side hustle passive income tutorial'
            
            # 点击搜索框并输入
            search_box = await page.wait_for_selector('input#search', timeout=10000)
            await search_box.click()
            await page.wait_for_timeout(random.randint(500, 1500))
            
            await self.anti_detection.type_like_human_playwright(page, 'input#search', search_query)
            
            # 点击搜索按钮
            search_button = await page.wait_for_selector('button#search-icon-legacy', timeout=5000)
            await search_button.click()
            
            # 等待搜索结果
            await page.wait_for_selector('ytd-video-renderer', timeout=15000)
            await self.anti_detection.simulate_human_behavior_playwright(page)
            
            # 提取视频结果
            video_elements = await page.query_selector_all('ytd-video-renderer')
            
            for video in video_elements[:self.search_limits['youtube']]:
                try:
                    # 提取视频信息
                    title_element = await video.query_selector('a#video-title')
                    channel_element = await video.query_selector('#channel-info #text a')
                    views_element = await video.query_selector('#metadata-line span:first-child')
                    
                    if title_element:
                        title = await title_element.inner_text()
                        video_url = await title_element.get_attribute('href')
                        if video_url:
                            video_url = f'https://www.youtube.com{video_url}'
                        
                        channel = await channel_element.inner_text() if channel_element else 'Unknown'
                        views_text = await views_element.inner_text() if views_element else '0 views'
                        
                        # 解析观看次数
                        views = self._parse_youtube_views(views_text)
                        
                        # 创建内容项
                        item = RPAContentItem(
                            platform='youtube',
                            title=title,
                            content=f'YouTube video: {title}',
                            url=video_url,
                            author=channel,
                            engagement_metrics={
                                'views': views,
                                'platform_score': min(views / 1000, 100)
                            },
                            confidence_score=self._calculate_youtube_confidence(title, views),
                            scraped_at=datetime.now().isoformat()
                        )
                        
                        results.append(item)
                        
                except Exception as e:
                    self.logger.warning(f"解析YouTube视频失败: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"YouTube RPA搜索失败: {e}")
        finally:
            await page.close()
            
        return results
    
    async def search_reddit_rpa(self, query: str, time_range: str) -> List[RPAContentItem]:
        """Reddit RPA高级搜索"""
        results = []
        subreddits = ['entrepreneur', 'sidehustle', 'passive_income']
        
        for subreddit in subreddits:
            page = await self.context.new_page()
            
            try:
                self.logger.info(f"正在搜索 r/{subreddit}")
                
                # 使用老版本Reddit更容易解析
                search_url = f'https://old.reddit.com/r/{subreddit}/search/?q={quote(query)}&restrict_sr=1&sort=relevance'
                await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                await page.wait_for_timeout(3000)
                
                # 使用old.reddit.com的简单选择器
                post_elements = await page.query_selector_all('.thing')
                
                if not post_elements:
                    self.logger.warning(f"在 r/{subreddit} 未找到帖子元素")
                    continue
                
                self.logger.info(f"在 r/{subreddit} 找到 {len(post_elements)} 个帖子")
                
                for i, post in enumerate(post_elements[:6]):  # 每个subreddit最多6个结果
                    try:
                        # 提取标题 (old reddit)
                        title_element = await post.query_selector('.title a')
                        if not title_element:
                            continue
                        
                        title = await title_element.inner_text()
                        if not title or len(title.strip()) < 5:
                            continue
                        
                        # 提取链接
                        post_url = await title_element.get_attribute('href')
                        if post_url and not post_url.startswith('http'):
                            post_url = f'https://old.reddit.com{post_url}'
                        
                        # 提取作者
                        author_element = await post.query_selector('.author')
                        author = await author_element.inner_text() if author_element else 'Unknown'
                        
                        # 创建内容项
                        item = RPAContentItem(
                            platform='reddit',
                            title=title.strip(),
                            content=f'Reddit discussion from r/{subreddit}',
                            url=post_url if post_url else f'https://reddit.com/r/{subreddit}',
                            author=author,
                            engagement_metrics={
                                'subreddit': subreddit,
                                'position': i + 1,
                                'platform_score': 60
                            },
                            confidence_score=self._calculate_reddit_confidence(title),
                            scraped_at=datetime.now().isoformat()
                        )
                        
                        results.append(item)
                        self.logger.debug(f"提取Reddit帖子 {i+1}: {title[:50]}...")
                        
                    except Exception as e:
                        self.logger.warning(f"解析Reddit帖子 {i+1} 失败: {e}")
                        continue
                
                self.logger.info(f"r/{subreddit} 搜索完成，获取 {len([r for r in results if r.engagement_metrics.get('subreddit') == subreddit])} 条结果")
                
            except Exception as e:
                self.logger.error(f"Reddit {subreddit} 搜索失败: {e}")
            finally:
                await page.close()
            
            # subreddit间的延迟
            await asyncio.sleep(random.uniform(2, 4))
        
        return results
    
    # 辅助解析方法
    def _extract_domain_from_url(self, url: str) -> str:
        """从URL提取域名"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return 'Unknown'
    
    def _parse_youtube_views(self, views_text: str) -> int:
        """解析YouTube观看次数"""
        try:
            # 移除文字，只保留数字
            views_clean = re.sub(r'[^0-9.]', '', views_text)
            if 'K' in views_text.upper():
                return int(float(views_clean) * 1000)
            elif 'M' in views_text.upper():
                return int(float(views_clean) * 1000000)
            elif 'B' in views_text.upper():
                return int(float(views_clean) * 1000000000)
            else:
                return int(views_clean) if views_clean else 0
        except:
            return 0
    
    # 置信度计算方法
    def _calculate_google_confidence(self, title: str, snippet: str) -> float:
        """计算Google结果置信度"""
        base_score = 0.7
        
        # 标题相关性
        if any(keyword in title.lower() for keyword in ['tutorial', 'guide', 'how to', 'step']):
            base_score += 0.15
        
        # 内容质量
        if len(snippet) > 100:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _calculate_youtube_confidence(self, title: str, views: int) -> float:
        """计算YouTube结果置信度"""
        base_score = 0.6
        
        # 标题相关性
        if any(keyword in title.lower() for keyword in ['tutorial', 'guide', 'how to', 'review']):
            base_score += 0.2
        
        # 观看次数
        if views > 10000:
            base_score += 0.15
        elif views > 1000:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _calculate_reddit_confidence(self, title: str) -> float:
        """计算Reddit结果置信度"""
        base_score = 0.65
        
        # 标题相关性
        if any(keyword in title.lower() for keyword in ['guide', 'tips', 'experience', 'success']):
            base_score += 0.15
        
        return min(base_score, 1.0)


# 使用示例
async def main():
    """测试RPA多平台爬虫"""
    async with RPAMultiPlatformCrawler(use_playwright=True) as crawler:
        results = await crawler.search_all_platforms_rpa("ai automation", "7d")
        
        print(f"\n🎯 RPA搜索完成，找到 {len(results)} 条内容:")
        
        platforms = {}
        for item in results:
            if item.platform not in platforms:
                platforms[item.platform] = []
            platforms[item.platform].append(item)
        
        for platform, items in platforms.items():
            print(f"\n📊 [{platform.upper()}] - {len(items)}条结果:")
            for item in items[:3]:  # 显示每个平台前3个结果
                print(f"  ✓ {item.title[:80]}...")
                print(f"    作者: {item.author}")
                print(f"    置信度: {item.confidence_score:.2f}")
                print(f"    URL: {item.url}")
                print()

if __name__ == "__main__":
    asyncio.run(main())