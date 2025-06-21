#!/usr/bin/env python3
"""
测试微信文章分析功能
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.intelligent_topic_service import IntelligentTopicService

async def test_wechat_analysis():
    """测试微信文章分析功能"""
    print("🚀 开始测试微信文章分析功能...")
    
    service = IntelligentTopicService()
    
    # 测试URL（您提供的链接）
    test_urls = [
        "https://mp.weixin.qq.com/s/LZgG-5uE8fGaJAiqb0FGYQ"
    ]
    
    print(f"📋 测试链接: {test_urls[0]}")
    
    try:
        # 测试单篇文章分析
        print("\n=== 单篇文章分析 ===")
        result = await service.analyze_single_article(test_urls[0])
        
        if 'error' in result:
            print(f"❌ 分析失败: {result['error']}")
            print("🔄 这通常是由于微信的反爬限制，使用备用数据...")
            
            # 获取备用选题
            fallback_topics = await service._get_fallback_topics(5)
            print(f"✅ 生成了 {len(fallback_topics)} 个备用选题:")
            
            for i, topic in enumerate(fallback_topics, 1):
                print(f"  {i}. {topic.title}")
                print(f"     分类: {topic.category.value}")
                print(f"     热度: {topic.heat}")
                print(f"     理由: {topic.reason}")
                print()
        else:
            print("✅ 分析成功!")
            article_info = result['article_info']
            print(f"📰 文章标题: {article_info['title']}")
            print(f"👤 作者: {article_info['author']}")
            print(f"📅 发布时间: {article_info['publish_time']}")
            print(f"📊 内容长度: {len(article_info['content'])} 字符")
            
            print(f"\n🎯 生成选题数量: {len(result['generated_topics'])}")
            for i, topic in enumerate(result['generated_topics'], 1):
                print(f"  {i}. {topic['title']}")
                print(f"     分类: {topic['category']}")
                print(f"     热度: {topic['heat']}")
                print()
        
        # 测试批量分析
        print("\n=== 批量分析测试 ===")
        topics = await service.get_trending_topics_from_wechat(test_urls, 5)
        
        print(f"✅ 批量分析完成，共生成 {len(topics)} 个选题:")
        for i, topic in enumerate(topics, 1):
            print(f"  {i}. {topic.title}")
            print(f"     分类: {topic.category.value}")
            print(f"     热度: {topic.heat}")
            print(f"     关键词: {', '.join(topic.keywords[:3])}")
            print()
            
    except Exception as e:
        print(f"❌ 测试过程出错: {str(e)}")
        print("🔄 这可能是网络连接或反爬限制导致的")

if __name__ == "__main__":
    asyncio.run(test_wechat_analysis())