#!/usr/bin/env python3
"""
视频内容提取和转文本服务
支持YouTube视频的字幕提取、音频转文本等功能
"""

import asyncio
import aiohttp
import json
import re
import os
import tempfile
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from urllib.parse import parse_qs, urlparse
import subprocess

@dataclass
class VideoTranscript:
    """视频转录数据结构"""
    video_id: str
    title: str
    duration: int
    language: str
    transcript_text: str
    timestamps: List[Dict]  # [{"start": 0, "duration": 5, "text": "..."}]
    confidence_score: float
    source: str  # "captions", "auto_generated", "audio_transcription"

class VideoContentExtractor:
    """视频内容提取器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.session = None
        
        # 支持的语言
        self.supported_languages = ['en', 'zh', 'es', 'fr', 'de', 'ja', 'ko']
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def extract_youtube_content(self, video_url: str) -> VideoTranscript:
        """
        从YouTube视频提取完整内容
        
        Args:
            video_url: YouTube视频URL
            
        Returns:
            VideoTranscript对象包含完整的转录内容
        """
        try:
            video_id = self._extract_video_id(video_url)
            if not video_id:
                raise ValueError("无效的YouTube URL")
            
            self.logger.info(f"开始提取视频内容: {video_id}")
            
            # 1. 获取视频基本信息
            video_info = await self._get_video_info(video_id)
            
            # 2. 尝试获取官方字幕
            captions = await self._get_official_captions(video_id)
            
            if captions:
                transcript = VideoTranscript(
                    video_id=video_id,
                    title=video_info.get('title', ''),
                    duration=video_info.get('duration', 0),
                    language=captions.get('language', 'en'),
                    transcript_text=captions.get('text', ''),
                    timestamps=captions.get('timestamps', []),
                    confidence_score=0.95,  # 官方字幕置信度高
                    source='captions'
                )
                
                self.logger.info(f"成功获取官方字幕，长度: {len(transcript.transcript_text)}")
                return transcript
            
            # 3. 尝试获取自动生成字幕
            auto_captions = await self._get_auto_generated_captions(video_id)
            
            if auto_captions:
                transcript = VideoTranscript(
                    video_id=video_id,
                    title=video_info.get('title', ''),
                    duration=video_info.get('duration', 0),
                    language=auto_captions.get('language', 'en'),
                    transcript_text=auto_captions.get('text', ''),
                    timestamps=auto_captions.get('timestamps', []),
                    confidence_score=0.80,  # 自动字幕置信度中等
                    source='auto_generated'
                )
                
                self.logger.info(f"成功获取自动字幕，长度: {len(transcript.transcript_text)}")
                return transcript
            
            # 4. 备用方案：音频转文本
            self.logger.info("尝试音频转文本...")
            audio_transcript = await self._audio_to_text(video_id, video_info)
            
            if audio_transcript:
                transcript = VideoTranscript(
                    video_id=video_id,
                    title=video_info.get('title', ''),
                    duration=video_info.get('duration', 0),
                    language='en',  # 假设英文
                    transcript_text=audio_transcript.get('text', ''),
                    timestamps=audio_transcript.get('timestamps', []),
                    confidence_score=0.70,  # 音频转文本置信度较低
                    source='audio_transcription'
                )
                
                self.logger.info(f"音频转文本成功，长度: {len(transcript.transcript_text)}")
                return transcript
            
            # 5. 最后备用：使用视频描述
            description = video_info.get('description', '')
            if description:
                transcript = VideoTranscript(
                    video_id=video_id,
                    title=video_info.get('title', ''),
                    duration=video_info.get('duration', 0),
                    language='en',
                    transcript_text=description,
                    timestamps=[],
                    confidence_score=0.30,  # 仅描述，置信度低
                    source='description_fallback'
                )
                
                self.logger.warning(f"仅获取到视频描述作为内容")
                return transcript
            
            raise Exception("无法获取任何视频内容")
            
        except Exception as e:
            self.logger.error(f"视频内容提取失败: {e}")
            raise
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """从YouTube URL提取视频ID"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\\n?#]+)',
            r'youtube\.com\/v\/([^&\\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    async def _get_video_info(self, video_id: str) -> Dict:
        """获取YouTube视频基本信息"""
        if not self.youtube_api_key:
            return await self._fallback_video_info(video_id)
        
        try:
            params = {
                'key': self.youtube_api_key,
                'part': 'snippet,contentDetails,statistics',
                'id': video_id
            }
            
            url = "https://www.googleapis.com/youtube/v3/videos"
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('items'):
                        item = data['items'][0]
                        snippet = item['snippet']
                        content_details = item['contentDetails']
                        statistics = item.get('statistics', {})
                        
                        # 解析时长
                        duration = self._parse_duration(content_details.get('duration', 'PT0S'))
                        
                        return {
                            'title': snippet.get('title', ''),
                            'description': snippet.get('description', ''),
                            'duration': duration,
                            'view_count': int(statistics.get('viewCount', 0)),
                            'like_count': int(statistics.get('likeCount', 0)),
                            'channel_title': snippet.get('channelTitle', ''),
                            'published_at': snippet.get('publishedAt', '')
                        }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"获取视频信息失败: {e}")
            return {}
    
    async def _get_official_captions(self, video_id: str) -> Optional[Dict]:
        """获取官方字幕"""
        try:
            # 使用youtube-transcript-api库的逻辑
            # 这里实现简化版本
            
            captions_url = f"https://www.youtube.com/api/timedtext?v={video_id}&lang=en&fmt=json3"
            
            async with self.session.get(captions_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._parse_captions_data(data)
            
            return None
            
        except Exception as e:
            self.logger.warning(f"获取官方字幕失败: {e}")
            return None
    
    async def _get_auto_generated_captions(self, video_id: str) -> Optional[Dict]:
        """获取自动生成字幕"""
        try:
            # 尝试多种自动字幕格式
            lang_codes = ['en', 'a.en']  # 'a.en' 表示自动生成英文字幕
            
            for lang in lang_codes:
                captions_url = f"https://www.youtube.com/api/timedtext?v={video_id}&lang={lang}&fmt=json3"
                
                async with self.session.get(captions_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = await self._parse_captions_data(data)
                        if result:
                            return result
            
            return None
            
        except Exception as e:
            self.logger.warning(f"获取自动字幕失败: {e}")
            return None
    
    async def _parse_captions_data(self, data: Dict) -> Optional[Dict]:
        """解析字幕数据"""
        try:
            if not data or 'events' not in data:
                return None
            
            events = data['events']
            full_text = ""
            timestamps = []
            
            for event in events:
                if 'segs' in event:
                    start_time = event.get('tStartMs', 0) / 1000  # 转换为秒
                    duration = event.get('dDurationMs', 0) / 1000
                    
                    text_parts = []
                    for seg in event['segs']:
                        if 'utf8' in seg:
                            text_parts.append(seg['utf8'])
                    
                    if text_parts:
                        text = ''.join(text_parts).strip()
                        if text:
                            full_text += text + " "
                            timestamps.append({
                                'start': start_time,
                                'duration': duration,
                                'text': text
                            })
            
            if full_text:
                return {
                    'text': full_text.strip(),
                    'timestamps': timestamps,
                    'language': 'en'
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"解析字幕数据失败: {e}")
            return None
    
    async def _audio_to_text(self, video_id: str, video_info: Dict) -> Optional[Dict]:
        """
        音频转文本 (备用方案)
        需要安装 yt-dlp 和 whisper
        """
        try:
            # 检查视频时长，避免处理过长视频
            duration = video_info.get('duration', 0)
            if duration > 1800:  # 30分钟限制
                self.logger.warning(f"视频过长({duration}s)，跳过音频转文本")
                return None
            
            # 使用 yt-dlp 下载音频
            temp_dir = tempfile.mkdtemp()
            audio_file = os.path.join(temp_dir, f"{video_id}.mp3")
            
            # 下载音频命令
            download_cmd = [
                'yt-dlp',
                '-x',  # 仅音频
                '--audio-format', 'mp3',
                '--audio-quality', '5',  # 较低质量以减少文件大小
                '-o', audio_file.replace('.mp3', '.%(ext)s'),
                f'https://www.youtube.com/watch?v={video_id}'
            ]
            
            # 执行下载
            result = await asyncio.create_subprocess_exec(
                *download_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                self.logger.error(f"音频下载失败: {stderr.decode()}")
                return None
            
            # 使用 Whisper 转录
            if os.path.exists(audio_file):
                transcript = await self._whisper_transcribe(audio_file)
                
                # 清理临时文件
                try:
                    os.remove(audio_file)
                    os.rmdir(temp_dir)
                except:
                    pass
                
                return transcript
            
            return None
            
        except Exception as e:
            self.logger.error(f"音频转文本失败: {e}")
            return None
    
    async def _whisper_transcribe(self, audio_file: str) -> Optional[Dict]:
        """使用Whisper进行音频转录"""
        try:
            # 这里需要安装 openai-whisper
            # pip install openai-whisper
            
            cmd = [
                'whisper',
                audio_file,
                '--model', 'base',  # 使用基础模型
                '--language', 'en',
                '--output_format', 'json',
                '--output_dir', os.path.dirname(audio_file)
            ]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                # 读取生成的JSON文件
                json_file = audio_file.replace('.mp3', '.json')
                if os.path.exists(json_file):
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 清理JSON文件
                    os.remove(json_file)
                    
                    # 解析转录结果
                    segments = data.get('segments', [])
                    full_text = data.get('text', '')
                    
                    timestamps = []
                    for segment in segments:
                        timestamps.append({
                            'start': segment.get('start', 0),
                            'duration': segment.get('end', 0) - segment.get('start', 0),
                            'text': segment.get('text', '').strip()
                        })
                    
                    return {
                        'text': full_text.strip(),
                        'timestamps': timestamps,
                        'language': 'en'
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Whisper转录失败: {e}")
            return None
    
    async def _fallback_video_info(self, video_id: str) -> Dict:
        """备用视频信息获取方案"""
        try:
            # 通过网页爬取基本信息
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._parse_video_info_from_html(html)
            
            return {}
            
        except Exception as e:
            self.logger.error(f"备用视频信息获取失败: {e}")
            return {}
    
    def _parse_video_info_from_html(self, html: str) -> Dict:
        """从HTML解析视频信息"""
        info = {}
        
        # 提取标题
        title_match = re.search(r'"title":"([^"]+)"', html)
        if title_match:
            info['title'] = title_match.group(1)
        
        # 提取描述
        desc_match = re.search(r'"shortDescription":"([^"]+)"', html)
        if desc_match:
            info['description'] = desc_match.group(1)
        
        # 提取时长
        duration_match = re.search(r'"lengthSeconds":"(\d+)"', html)
        if duration_match:
            info['duration'] = int(duration_match.group(1))
        
        return info
    
    def _parse_duration(self, duration_str: str) -> int:
        """解析ISO 8601时长格式为秒数"""
        # PT1H2M10S -> 3730 seconds
        import re
        
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        
        if match:
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)
            
            return hours * 3600 + minutes * 60 + seconds
        
        return 0
    
    async def batch_extract_videos(self, video_urls: List[str]) -> List[VideoTranscript]:
        """批量提取多个视频内容"""
        self.logger.info(f"开始批量提取 {len(video_urls)} 个视频")
        
        # 并发处理，限制并发数
        semaphore = asyncio.Semaphore(3)  # 最多3个并发
        
        async def extract_with_semaphore(url):
            async with semaphore:
                try:
                    return await self.extract_youtube_content(url)
                except Exception as e:
                    self.logger.error(f"提取失败 {url}: {e}")
                    return None
        
        tasks = [extract_with_semaphore(url) for url in video_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤成功的结果
        transcripts = []
        for result in results:
            if isinstance(result, VideoTranscript):
                transcripts.append(result)
        
        self.logger.info(f"成功提取 {len(transcripts)} 个视频内容")
        return transcripts


# 使用示例
async def main():
    """测试视频内容提取"""
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # 示例URL
        "https://youtu.be/dQw4w9WgXcQ"
    ]
    
    async with VideoContentExtractor() as extractor:
        for url in test_urls:
            try:
                transcript = await extractor.extract_youtube_content(url)
                print(f"\n视频: {transcript.title}")
                print(f"时长: {transcript.duration}秒")
                print(f"来源: {transcript.source}")
                print(f"置信度: {transcript.confidence_score}")
                print(f"内容预览: {transcript.transcript_text[:200]}...")
                
            except Exception as e:
                print(f"提取失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())