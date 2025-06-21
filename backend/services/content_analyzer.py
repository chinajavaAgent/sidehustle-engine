"""
智能内容分析器 - 使用中文分词和主题提取
"""

import jieba
import jieba.analyse
from collections import Counter
import re
from typing import List, Dict, Tuple
from datetime import datetime
import json

class ContentAnalyzer:
    def __init__(self):
        # 初始化jieba分词
        jieba.initialize()
        
        # 副业相关词典
        self.side_hustle_dict = {
            'AI工具': [
                'AI', '人工智能', 'ChatGPT', 'GPT', 'AIGC', 'AI绘画', 'Midjourney', 
                'Stable Diffusion', 'AI写作', '机器学习', '深度学习', '算法', 
                '自动化', '智能化', 'AI变现', 'AI工具', 'AI应用'
            ],
            '电商变现': [
                '电商', '淘宝', '天猫', '京东', '拼多多', '闲鱼', '咸鱼', '二手',
                '亚马逊', '跨境电商', '独立站', 'Shopify', '店铺', '选品', '运营',
                '直通车', '刷单', '客服', '物流', '供应链', '代购', '微商'
            ],
            '内容创作': [
                '短视频', '抖音', '快手', '视频号', '小红书', 'B站', '知乎', '公众号',
                '写作', '文案', '剧本', '拍摄', '剪辑', '配音', '直播', '带货',
                '自媒体', '内容', '创作', '博主', 'UP主', 'KOL', '网红', '流量'
            ],
            '技能变现': [
                '设计', 'UI设计', '平面设计', '网页设计', '编程', '开发', '程序员',
                '翻译', '配音', '写作', '文案', '咨询', '培训', '教学', '辅导',
                '专业技能', '服务外包', '威客', '猪八戒', '一品威客', '自由职业'
            ],
            '投资理财': [
                '投资', '理财', '股票', '基金', '债券', '期货', '外汇', '数字货币',
                '比特币', '以太坊', '房产', '保险', '信托', 'P2P', '众筹', '风投',
                '财务自由', '被动收入', '资产配置', '投资组合'
            ],
            '线上服务': [
                '在线教育', '知识付费', '课程', '培训', '咨询', '心理咨询',
                '法律咨询', '医疗咨询', '远程工作', '虚拟助手', '客服',
                '数据录入', '调研', '问卷', '测试', '众包'
            ]
        }
        
        # 热度指标词汇
        self.heat_indicators = {
            '时效性': ['2024', '最新', '新出', '刚刚', '最近', '今年', '这个月'],
            '收益性': ['月入', '年收入', '万元', '千元', '赚钱', '盈利', '收益', '变现'],
            '热门性': ['爆火', '火爆', '热门', '流行', '趋势', '风口', '机会'],
            '实用性': ['实战', '干货', '教程', '指南', '攻略', '方法', '技巧', '经验'],
            '成功性': ['成功', '逆袭', '突破', '实现', '达到', '获得', '赢得']
        }
        
        # 添加自定义词典
        self._add_custom_words()

    def _add_custom_words(self):
        """添加自定义词汇到jieba词典"""
        for category, words in self.side_hustle_dict.items():
            for word in words:
                jieba.add_word(word)
        
        for category, words in self.heat_indicators.items():
            for word in words:
                jieba.add_word(word)

    def analyze_article(self, title: str, content: str) -> Dict:
        """
        全面分析文章内容
        """
        # 合并标题和内容
        full_text = f"{title} {content}"
        
        # 基础分析
        basic_info = self._basic_analysis(title, content)
        
        # 关键词提取
        keywords = self._extract_keywords(full_text)
        
        # 主题分类
        category_info = self._classify_content(full_text, keywords)
        
        # 热度分析
        heat_analysis = self._analyze_heat(full_text)
        
        # 情感分析
        sentiment = self._analyze_sentiment(full_text)
        
        # 生成选题建议
        topic_suggestions = self._generate_topic_suggestions(
            title, keywords, category_info, heat_analysis
        )
        
        return {
            'basic_info': basic_info,
            'keywords': keywords,
            'category_info': category_info,
            'heat_analysis': heat_analysis,
            'sentiment': sentiment,
            'topic_suggestions': topic_suggestions,
            'analyzed_at': datetime.now().isoformat()
        }

    def _basic_analysis(self, title: str, content: str) -> Dict:
        """基础文本分析"""
        # 字数统计
        title_len = len(title)
        content_len = len(content)
        
        # 段落统计
        paragraphs = content.split('\n')
        paragraph_count = len([p for p in paragraphs if p.strip()])
        
        # 句子统计
        sentences = re.split(r'[。！？.!?]', content)
        sentence_count = len([s for s in sentences if s.strip()])
        
        return {
            'title_length': title_len,
            'content_length': content_len,
            'total_length': title_len + content_len,
            'paragraph_count': paragraph_count,
            'sentence_count': sentence_count,
            'avg_sentence_length': content_len / sentence_count if sentence_count > 0 else 0
        }

    def _extract_keywords(self, text: str, top_k: int = 20) -> List[Dict]:
        """提取关键词"""
        # 使用TF-IDF提取关键词
        keywords_tfidf = jieba.analyse.extract_tags(
            text, topK=top_k, withWeight=True
        )
        
        # 使用TextRank提取关键词
        keywords_textrank = jieba.analyse.textrank(
            text, topK=top_k, withWeight=True
        )
        
        # 合并并去重
        all_keywords = {}
        
        for word, weight in keywords_tfidf:
            all_keywords[word] = {
                'word': word,
                'tfidf_weight': weight,
                'textrank_weight': 0,
                'final_weight': weight
            }
        
        for word, weight in keywords_textrank:
            if word in all_keywords:
                all_keywords[word]['textrank_weight'] = weight
                # 综合权重
                all_keywords[word]['final_weight'] = (
                    all_keywords[word]['tfidf_weight'] + weight
                ) / 2
            else:
                all_keywords[word] = {
                    'word': word,
                    'tfidf_weight': 0,
                    'textrank_weight': weight,
                    'final_weight': weight / 2
                }
        
        # 按综合权重排序
        sorted_keywords = sorted(
            all_keywords.values(),
            key=lambda x: x['final_weight'],
            reverse=True
        )
        
        return sorted_keywords[:15]

    def _classify_content(self, text: str, keywords: List[Dict]) -> Dict:
        """内容分类分析"""
        category_scores = {}
        
        # 基于关键词匹配计算分类得分
        for category, category_words in self.side_hustle_dict.items():
            score = 0
            matched_words = []
            
            for keyword_info in keywords:
                word = keyword_info['word']
                weight = keyword_info['final_weight']
                
                # 检查关键词是否在分类词典中
                for category_word in category_words:
                    if category_word in word or word in category_word:
                        score += weight * 10  # 权重放大
                        matched_words.append(word)
                        break
            
            # 直接文本匹配
            for category_word in category_words:
                count = text.lower().count(category_word.lower())
                if count > 0:
                    score += count * 2
                    if category_word not in matched_words:
                        matched_words.append(category_word)
            
            if score > 0:
                category_scores[category] = {
                    'score': score,
                    'matched_words': matched_words[:5],  # 最多显示5个匹配词
                    'confidence': min(score / 20, 1.0)  # 置信度
                }
        
        # 排序并返回结果
        sorted_categories = sorted(
            category_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        primary_category = sorted_categories[0] if sorted_categories else ('其他', {'score': 0, 'matched_words': [], 'confidence': 0})
        
        return {
            'primary_category': primary_category[0],
            'primary_confidence': primary_category[1]['confidence'],
            'all_categories': dict(sorted_categories[:3]),  # 返回前3个分类
            'category_distribution': {cat: info['score'] for cat, info in sorted_categories}
        }

    def _analyze_heat(self, text: str) -> Dict:
        """热度分析"""
        heat_scores = {}
        total_score = 0
        
        for indicator_type, words in self.heat_indicators.items():
            score = 0
            matched_words = []
            
            for word in words:
                count = text.count(word)
                if count > 0:
                    score += count * 5  # 每个匹配词5分
                    matched_words.append(f"{word}({count})")
            
            heat_scores[indicator_type] = {
                'score': score,
                'matched_words': matched_words
            }
            total_score += score
        
        # 计算总热度（0-100分）
        heat_level = min(total_score, 100)
        
        # 热度等级
        if heat_level >= 80:
            level = "极热"
        elif heat_level >= 60:
            level = "较热"
        elif heat_level >= 40:
            level = "中等"
        elif heat_level >= 20:
            level = "一般"
        else:
            level = "较冷"
        
        return {
            'total_score': heat_level,
            'level': level,
            'indicators': heat_scores,
            'description': self._generate_heat_description(heat_scores, heat_level)
        }

    def _generate_heat_description(self, heat_scores: Dict, total_score: int) -> str:
        """生成热度描述"""
        descriptions = []
        
        for indicator_type, info in heat_scores.items():
            if info['score'] > 0:
                descriptions.append(f"{indicator_type}指标得分{info['score']}")
        
        if not descriptions:
            return "缺乏明显的热度指标"
        
        main_desc = "、".join(descriptions[:2])  # 最多显示2个主要指标
        
        return f"{main_desc}，综合热度{total_score}分"

    def _analyze_sentiment(self, text: str) -> Dict:
        """简单的情感分析"""
        positive_words = ['成功', '赚钱', '收益', '机会', '优势', '简单', '容易', '快速', '有效']
        negative_words = ['困难', '风险', '失败', '亏损', '难以', '复杂', '昂贵', '危险']
        
        positive_count = sum(text.count(word) for word in positive_words)
        negative_count = sum(text.count(word) for word in negative_words)
        
        if positive_count > negative_count:
            sentiment = "积极"
        elif negative_count > positive_count:
            sentiment = "消极"
        else:
            sentiment = "中性"
        
        return {
            'sentiment': sentiment,
            'positive_score': positive_count,
            'negative_score': negative_count,
            'confidence': abs(positive_count - negative_count) / max(len(text) / 100, 1)
        }

    def _generate_topic_suggestions(self, title: str, keywords: List[Dict], 
                                  category_info: Dict, heat_analysis: Dict) -> List[Dict]:
        """生成选题建议"""
        suggestions = []
        
        # 获取主要关键词
        top_keywords = [kw['word'] for kw in keywords[:5]]
        primary_category = category_info['primary_category']
        
        # 生成选题模板
        templates = [
            f"{primary_category}新趋势：{top_keywords[0]}变现指南",
            f"2024年{top_keywords[0]}副业机会深度解析",
            f"从零开始做{primary_category}：{top_keywords[0]}实战经验",
            f"{top_keywords[0]}赚钱攻略：月入过万不是梦",
            f"揭秘{primary_category}暴利项目：{top_keywords[0]}操作指南"
        ]
        
        for i, template in enumerate(templates[:3]):  # 生成3个建议
            suggestions.append({
                'id': f"suggest_{i+1}",
                'title': template,
                'category': primary_category,
                'heat_score': heat_analysis['total_score'],
                'keywords': top_keywords[:3],
                'reason': f"基于'{title}'分析生成，{heat_analysis['description']}",
                'confidence': category_info['primary_confidence']
            })
        
        return suggestions

# 测试函数
def test_analyzer():
    """测试内容分析器"""
    analyzer = ContentAnalyzer()
    
    # 测试文本
    title = "AI绘画副业月入过万：从Midjourney到商业变现的完整指南"
    content = """
    随着AI技术的发展，AI绘画已经成为2024年最热门的副业方向之一。
    很多人通过Midjourney、Stable Diffusion等工具，实现了月入5000到20000的收益。
    
    今天我要分享的是一个真实的案例：小王是一个普通的上班族，
    通过学习AI绘画技术，在3个月内建立了自己的副业收入流。
    
    第一步：掌握AI绘画工具的使用
    第二步：寻找客户和接单渠道
    第三步：建立个人品牌和作品集
    第四步：扩大业务规模
    
    经过实战验证，这个方法确实有效，值得推荐给想要开始副业的朋友。
    """
    
    print("开始分析内容...")
    result = analyzer.analyze_article(title, content)
    
    print(f"\n=== 基础信息 ===")
    basic = result['basic_info']
    print(f"标题长度: {basic['title_length']}")
    print(f"内容长度: {basic['content_length']}")
    print(f"段落数: {basic['paragraph_count']}")
    
    print(f"\n=== 关键词 ===")
    for kw in result['keywords'][:5]:
        print(f"{kw['word']}: {kw['final_weight']:.3f}")
    
    print(f"\n=== 分类信息 ===")
    category = result['category_info']
    print(f"主要分类: {category['primary_category']}")
    print(f"置信度: {category['primary_confidence']:.2f}")
    
    print(f"\n=== 热度分析 ===")
    heat = result['heat_analysis']
    print(f"热度得分: {heat['total_score']}")
    print(f"热度等级: {heat['level']}")
    print(f"描述: {heat['description']}")
    
    print(f"\n=== 选题建议 ===")
    for suggestion in result['topic_suggestions']:
        print(f"- {suggestion['title']}")
        print(f"  分类: {suggestion['category']}, 热度: {suggestion['heat_score']}")

if __name__ == "__main__":
    test_analyzer()