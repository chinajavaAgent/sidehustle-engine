"""
微信公众号文章爬虫服务
注意：需要遵守版权法律法规，仅用于学习和分析目的
"""

import requests
import time
import re
import json
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs
import hashlib
from datetime import datetime
import logging

class WeChatCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(self.headers)
        
        # 设置请求间隔，避免被封
        self.request_delay = 2
        
        # 日志配置
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def extract_article_info(self, url: str) -> Dict:
        """
        从微信文章URL提取基本信息
        """
        try:
            # 解析URL获取基本参数
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            # 尝试获取文章内容
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取文章信息
            article_info = {
                'url': url,
                'title': self._extract_title(soup),
                'author': self._extract_author(soup),
                'publish_time': self._extract_publish_time(soup),
                'content': self._extract_content(soup),
                'account_name': self._extract_account_name(soup),
                'biz': query_params.get('__biz', [''])[0],
                'extracted_at': datetime.now().isoformat()
            }
            
            return article_info
            
        except Exception as e:
            self.logger.error(f"提取文章信息失败 {url}: {str(e)}")
            return {'url': url, 'error': str(e)}

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取文章标题"""
        title_selectors = [
            '#activity-name',
            '.rich_media_title',
            'h1',
            'title'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        
        return "未找到标题"

    def _extract_author(self, soup: BeautifulSoup) -> str:
        """提取作者信息"""
        author_selectors = [
            '.rich_media_meta_text',
            '.profile_nickname',
            '#js_author_name'
        ]
        
        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        
        return "未知作者"

    def _extract_publish_time(self, soup: BeautifulSoup) -> str:
        """提取发布时间"""
        time_selectors = [
            '#publish_time',
            '.rich_media_meta_text',
            '[data-time]'
        ]
        
        for selector in time_selectors:
            element = soup.select_one(selector)
            if element:
                # 尝试提取时间文本
                time_text = element.get_text().strip()
                # 使用正则匹配时间格式
                time_pattern = r'\d{4}-\d{2}-\d{2}|\d{4}年\d{1,2}月\d{1,2}日'
                match = re.search(time_pattern, time_text)
                if match:
                    return match.group()
        
        return datetime.now().strftime('%Y-%m-%d')

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """提取文章正文内容"""
        content_selectors = [
            '#js_content',
            '.rich_media_content',
            '.rich_media_wrp'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # 清理HTML标签，只保留文本
                text = element.get_text().strip()
                # 清理多余的空白字符
                text = re.sub(r'\s+', ' ', text)
                return text[:2000]  # 限制长度
        
        return "未找到正文内容"

    def _extract_account_name(self, soup: BeautifulSoup) -> str:
        """提取公众号名称"""
        account_selectors = [
            '.profile_nickname',
            '#js_name',
            '.account_nickname'
        ]
        
        for selector in account_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        
        return "未知公众号"

    def analyze_content_for_topics(self, content: str) -> Dict:
        """
        分析文章内容，提取可能的选题信息
        """
        # 关键词提取
        keywords = self._extract_keywords(content)
        
        # 主题分类
        category = self._classify_topic(content, keywords)
        
        # 热度评估
        heat_score = self._calculate_heat_score(content, keywords)
        
        return {
            'keywords': keywords,
            'category': category,
            'heat_score': heat_score,
            'content_length': len(content),
            'analysis_time': datetime.now().isoformat()
        }

    def _extract_keywords(self, content: str) -> List[str]:
        """提取关键词"""
        # 副业相关关键词
        side_hustle_keywords = [
            '副业', '兼职', '赚钱', '收入', '创业', '变现', '接单', 
            'AI', '短视频', '自媒体', '电商', '直播', '写作', '设计',
            '技能', '在线', '远程', '自由职业', '被动收入', '财务自由'
        ]
        
        found_keywords = []
        for keyword in side_hustle_keywords:
            if keyword in content:
                # 计算关键词出现频次
                count = content.count(keyword)
                if count > 0:
                    found_keywords.append(f"{keyword}({count})")
        
        return found_keywords[:10]  # 返回前10个关键词

    def _classify_topic(self, content: str, keywords: List[str]) -> str:
        """对内容进行主题分类"""
        categories = {
            'AI工具': ['AI', '人工智能', '机器学习', 'ChatGPT', '绘画', '写作助手'],
            '电商变现': ['电商', '淘宝', '京东', '拼多多', '闲鱼', '亚马逊', '跨境'],
            '内容创作': ['短视频', '抖音', '快手', '小红书', 'B站', '写作', '拍摄'],
            '技能变现': ['设计', '编程', '翻译', '咨询', '培训', '教学', '辅导'],
            '投资理财': ['投资', '理财', '股票', '基金', '房产', '保险'],
            '自由职业': ['远程', '自由', '威客', '外包', '咨询', '顾问']
        }
        
        content_lower = content.lower()
        category_scores = {}
        
        for category, category_keywords in categories.items():
            score = 0
            for keyword in category_keywords:
                if keyword.lower() in content_lower:
                    score += content_lower.count(keyword.lower())
            category_scores[category] = score
        
        # 返回得分最高的分类
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return '其他'

    def _calculate_heat_score(self, content: str, keywords: List[str]) -> int:
        """计算热度评分"""
        base_score = 50
        
        # 关键词数量加分
        keyword_score = len(keywords) * 2
        
        # 内容长度加分
        length_score = min(len(content) // 100, 20)
        
        # 特定热词加分
        hot_words = ['最新', '2024', '爆火', '月入', '万元', '成功', '实战', '干货']
        hot_score = sum(5 for word in hot_words if word in content)
        
        total_score = base_score + keyword_score + length_score + hot_score
        return min(total_score, 100)  # 最高100分

    def generate_topic_from_content(self, article_info: Dict) -> Dict:
        """
        基于文章内容生成选题推荐
        """
        content = article_info.get('content', '')
        title = article_info.get('title', '')
        
        # 分析内容
        analysis = self.analyze_content_for_topics(content)
        
        # 生成选题标题
        topic_title = self._generate_topic_title(title, analysis['keywords'])
        
        # 生成推荐理由
        reason = self._generate_topic_reason(analysis)
        
        return {
            'id': hashlib.md5(topic_title.encode()).hexdigest()[:8],
            'title': topic_title,
            'reason': reason,
            'category': analysis['category'],
            'heat': analysis['heat_score'],
            'keywords': [kw.split('(')[0] for kw in analysis['keywords']],
            'source_url': article_info.get('url', ''),
            'source_title': title,
            'generated_at': datetime.now().isoformat()
        }

    def _generate_topic_title(self, original_title: str, keywords: List[str]) -> str:
        """生成选题标题"""
        # 提取主要关键词
        main_keywords = [kw.split('(')[0] for kw in keywords[:3]]
        
        if not main_keywords:
            return f"基于'{original_title[:20]}'的副业机会分析"
        
        # 生成标题模板
        templates = [
            f"{main_keywords[0]}副业新机会：从入门到月入过万",
            f"2024年{main_keywords[0]}赚钱指南：实战经验分享",
            f"{main_keywords[0]}变现全攻略：普通人也能做到",
            f"揭秘{main_keywords[0]}副业：{main_keywords[1] if len(main_keywords) > 1 else '新手'}必看",
            f"{main_keywords[0]}接单实战：月收入5000+的方法"
        ]
        
        # 随机选择一个模板
        import random
        return random.choice(templates)

    def _generate_topic_reason(self, analysis: Dict) -> str:
        """生成推荐理由"""
        category = analysis['category']
        heat_score = analysis['heat_score']
        keywords_count = len(analysis['keywords'])
        
        reasons = []
        
        if heat_score > 80:
            reasons.append("当前热度极高")
        elif heat_score > 60:
            reasons.append("市场关注度较高")
        
        if keywords_count > 5:
            reasons.append("涉及多个热门领域")
        
        category_reasons = {
            'AI工具': "AI技术发展迅速，市场需求大",
            '电商变现': "电商平台用户基数大，变现机会多", 
            '内容创作': "内容消费需求旺盛，创作门槛逐渐降低",
            '技能变现': "技能服务市场成熟，单价相对较高",
            '投资理财': "财富管理需求增长，学习意愿强",
            '自由职业': "远程工作趋势明显，时间灵活"
        }
        
        if category in category_reasons:
            reasons.append(category_reasons[category])
        
        return "，".join(reasons) if reasons else "具有一定的市场潜力"

# 使用示例和测试函数
def test_crawler():
    """测试爬虫功能"""
    crawler = WeChatCrawler()
    
    # 测试URL
    test_url = "https://mp.weixin.qq.com/s/LZgG-5uE8fGaJAiqb0FGYQ"
    
    print("开始爬取文章...")
    article_info = crawler.extract_article_info(test_url)
    
    if 'error' not in article_info:
        print(f"文章标题: {article_info['title']}")
        print(f"作者: {article_info['author']}")
        print(f"公众号: {article_info['account_name']}")
        print(f"发布时间: {article_info['publish_time']}")
        print(f"内容长度: {len(article_info['content'])} 字符")
        
        # 生成选题
        print("\n生成选题推荐...")
        topic = crawler.generate_topic_from_content(article_info)
        print(f"选题标题: {topic['title']}")
        print(f"推荐理由: {topic['reason']}")
        print(f"分类: {topic['category']}")
        print(f"热度: {topic['heat']}")
        print(f"关键词: {', '.join(topic['keywords'])}")
    else:
        print(f"爬取失败: {article_info['error']}")

if __name__ == "__main__":
    test_crawler()