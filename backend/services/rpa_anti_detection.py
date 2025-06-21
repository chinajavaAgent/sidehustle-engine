#!/usr/bin/env python3
"""
RPA反检测和代理轮换系统
实现高级反爬虫检测策略，确保稳定的数据获取
"""

import asyncio
import time
import random
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import os
import requests
from urllib.parse import urlparse

# 浏览器自动化
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

@dataclass
class ProxyConfig:
    """代理配置"""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = "http"  # http, https, socks5
    success_count: int = 0
    failure_count: int = 0
    last_used: Optional[datetime] = None
    response_time: float = 0.0
    is_active: bool = True

@dataclass
class BrowserFingerprint:
    """浏览器指纹"""
    user_agent: str
    viewport_size: Tuple[int, int]
    screen_resolution: Tuple[int, int]
    timezone: str
    language: str
    webgl_vendor: str
    webgl_renderer: str
    plugins: List[str]
    fonts: List[str]

class RPAAntiDetection:
    """RPA反检测系统"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 代理池
        self.proxy_pool: List[ProxyConfig] = []
        self.current_proxy_index = 0
        
        # 浏览器指纹池
        self.fingerprint_pool: List[BrowserFingerprint] = []
        self.current_fingerprint_index = 0
        
        # 反检测配置
        self.config = {
            'min_request_delay': 2,
            'max_request_delay': 8,
            'mouse_movement_probability': 0.7,
            'scroll_probability': 0.6,
            'click_delay_range': (0.1, 0.5),
            'typing_delay_range': (0.05, 0.2),
            'page_load_timeout': 30,
            'proxy_rotation_interval': 10,  # 每10个请求轮换代理
            'fingerprint_rotation_interval': 5,  # 每5个请求轮换指纹
            'max_retries_per_proxy': 3,
            'request_counter': 0
        }
        
        # 初始化指纹和代理
        self._initialize_fingerprints()
        self._load_proxy_list()
    
    def _initialize_fingerprints(self):
        """初始化浏览器指纹库"""
        fingerprints = [
            BrowserFingerprint(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport_size=(1366, 768),
                screen_resolution=(1920, 1080),
                timezone="America/New_York",
                language="en-US",
                webgl_vendor="Google Inc. (Intel)",
                webgl_renderer="ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)",
                plugins=["Chrome PDF Plugin", "Chrome PDF Viewer", "Native Client"],
                fonts=["Arial", "Times New Roman", "Courier New", "Helvetica"]
            ),
            BrowserFingerprint(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport_size=(1440, 900),
                screen_resolution=(2560, 1600),
                timezone="America/Los_Angeles",
                language="en-US",
                webgl_vendor="Apple Inc.",
                webgl_renderer="Apple GPU",
                plugins=["Chrome PDF Plugin", "Chrome PDF Viewer"],
                fonts=["Arial", "Helvetica", "Times", "Courier"]
            ),
            BrowserFingerprint(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport_size=(1280, 720),
                screen_resolution=(1920, 1080),
                timezone="Europe/London",
                language="en-GB",
                webgl_vendor="Mesa",
                webgl_renderer="llvmpipe (LLVM 12.0.0, 256 bits)",
                plugins=["Chrome PDF Plugin"],
                fonts=["DejaVu Sans", "Liberation Sans", "Ubuntu"]
            ),
            BrowserFingerprint(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
                viewport_size=(1366, 768),
                screen_resolution=(1920, 1080),
                timezone="America/Chicago",
                language="en-US",
                webgl_vendor="Mozilla",
                webgl_renderer="Mozilla -- llvmpipe (LLVM 12.0.0, 256 bits)",
                plugins=["OpenH264 Video Codec", "Widevine Content Decryption Module"],
                fonts=["Arial", "Times New Roman", "Courier New"]
            )
        ]
        
        self.fingerprint_pool = fingerprints
        random.shuffle(self.fingerprint_pool)
    
    def _load_proxy_list(self):
        """加载代理列表"""
        # 这里可以从文件或API加载代理列表
        # 示例代理（实际使用时需要替换为真实代理）
        proxy_sources = [
            # 免费代理示例（实际使用时建议购买稳定的代理服务）
            {"host": "proxy1.example.com", "port": 8080},
            {"host": "proxy2.example.com", "port": 3128},
            {"host": "proxy3.example.com", "port": 1080, "protocol": "socks5"},
        ]
        
        for proxy_data in proxy_sources:
            proxy = ProxyConfig(
                host=proxy_data["host"],
                port=proxy_data["port"],
                protocol=proxy_data.get("protocol", "http"),
                username=proxy_data.get("username"),
                password=proxy_data.get("password")
            )
            self.proxy_pool.append(proxy)
        
        # 如果没有配置代理，添加本地直连
        if not self.proxy_pool:
            self.logger.warning("未配置代理，将使用直连模式")
    
    def get_next_proxy(self) -> Optional[ProxyConfig]:
        """获取下一个可用代理"""
        if not self.proxy_pool:
            return None
        
        # 过滤可用代理
        active_proxies = [p for p in self.proxy_pool if p.is_active]
        if not active_proxies:
            # 如果所有代理都不可用，重置状态
            for proxy in self.proxy_pool:
                proxy.is_active = True
                proxy.failure_count = 0
            active_proxies = self.proxy_pool
        
        # 选择最少使用的代理
        active_proxies.sort(key=lambda x: (x.failure_count, x.success_count))
        
        self.current_proxy_index = (self.current_proxy_index + 1) % len(active_proxies)
        return active_proxies[self.current_proxy_index]
    
    def get_next_fingerprint(self) -> BrowserFingerprint:
        """获取下一个浏览器指纹"""
        self.current_fingerprint_index = (self.current_fingerprint_index + 1) % len(self.fingerprint_pool)
        return self.fingerprint_pool[self.current_fingerprint_index]
    
    def should_rotate_proxy(self) -> bool:
        """判断是否需要轮换代理"""
        return self.config['request_counter'] % self.config['proxy_rotation_interval'] == 0
    
    def should_rotate_fingerprint(self) -> bool:
        """判断是否需要轮换指纹"""
        return self.config['request_counter'] % self.config['fingerprint_rotation_interval'] == 0
    
    async def create_stealth_browser_playwright(self) -> Tuple[Browser, BrowserContext]:
        """创建隐身浏览器（Playwright）"""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright not available")
        
        fingerprint = self.get_next_fingerprint()
        # 暂时禁用代理，使用直连
        # proxy = self.get_next_proxy()
        
        playwright = await async_playwright().start()
        
        # 浏览器启动参数
        launch_options = {
            "headless": True,
            "args": [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--disable-features=VizDisplayCompositor",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-field-trial-config",
                "--disable-back-forward-cache",
                "--disable-background-networking",
                "--enable-features=NetworkService,NetworkServiceLogging",
                "--disable-ipc-flooding-protection",
                f"--window-size={fingerprint.viewport_size[0]},{fingerprint.viewport_size[1]}"
            ]
        }
        
        browser = await playwright.chromium.launch(**launch_options)
        
        # 创建上下文（不使用代理）
        context_options = {
            "viewport": {"width": fingerprint.viewport_size[0], "height": fingerprint.viewport_size[1]},
            "user_agent": fingerprint.user_agent,
            "locale": fingerprint.language,
            "timezone_id": fingerprint.timezone,
            "ignore_https_errors": True,
            "java_script_enabled": True,
        }
        
        context = await browser.new_context(**context_options)
        
        # 注入反检测脚本
        await context.add_init_script(self._get_stealth_script())
        
        return browser, context
    
    def create_stealth_browser_selenium(self) -> webdriver.Chrome:
        """创建隐身浏览器（Selenium）"""
        fingerprint = self.get_next_fingerprint()
        proxy = self.get_next_proxy()
        
        # Chrome选项
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(f"--user-agent={fingerprint.user_agent}")
        chrome_options.add_argument(f"--window-size={fingerprint.viewport_size[0]},{fingerprint.viewport_size[1]}")
        
        # 代理配置
        if proxy:
            if proxy.protocol == "socks5":
                chrome_options.add_argument(f"--proxy-server=socks5://{proxy.host}:{proxy.port}")
            else:
                chrome_options.add_argument(f"--proxy-server={proxy.protocol}://{proxy.host}:{proxy.port}")
        
        # 禁用图片加载以提高速度
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.media_stream": 2,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # 执行反检测脚本
        driver.execute_script(self._get_stealth_script())
        
        return driver
    
    def _get_stealth_script(self) -> str:
        """获取反检测脚本"""
        return """
        // 隐藏webdriver属性
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        // 重写Chrome对象
        window.chrome = {
            runtime: {},
            // etc.
        };
        
        // 重写插件数组
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        // 重写语言
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
        
        // 伪造WebGL指纹
        const getParameter = WebGLRenderingContext.getExtension.toString().replace('getExtension', 'getParameter');
        WebGLRenderingContext.prototype.getParameter = new Function('return ' + getParameter)();
        
        // 隐藏自动化痕迹
        const originalQuery = window.document.querySelector;
        window.document.querySelector = function(selector) {
            if (selector === 'iframe[src*="recaptcha"]') {
                return null;
            }
            return originalQuery.apply(this, arguments);
        };
        
        // 添加鼠标事件监听
        let mouseX = 0, mouseY = 0;
        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
        });
        
        // 重写Date对象以避免时区检测
        const originalDate = Date;
        Date = class extends originalDate {
            getTimezoneOffset() {
                return 300; // UTC-5 (EST)
            }
        };
        """
    
    async def simulate_human_behavior_playwright(self, page: Page):
        """模拟人类行为（Playwright）"""
        try:
            # 随机滚动
            if random.random() < self.config['scroll_probability']:
                scroll_distance = random.randint(100, 500)
                await page.evaluate(f"window.scrollBy(0, {scroll_distance})")
                await page.wait_for_timeout(random.randint(500, 1500))
            
            # 随机鼠标移动
            if random.random() < self.config['mouse_movement_probability']:
                viewport = page.viewport_size
                x = random.randint(50, viewport['width'] - 50)
                y = random.randint(50, viewport['height'] - 50)
                await page.mouse.move(x, y)
                await page.wait_for_timeout(random.randint(100, 500))
            
            # 随机暂停
            await page.wait_for_timeout(random.randint(
                self.config['min_request_delay'] * 1000,
                self.config['max_request_delay'] * 1000
            ))
            
        except Exception as e:
            self.logger.warning(f"模拟人类行为失败: {e}")
    
    def simulate_human_behavior_selenium(self, driver: webdriver.Chrome):
        """模拟人类行为（Selenium）"""
        try:
            # 随机滚动
            if random.random() < self.config['scroll_probability']:
                scroll_distance = random.randint(100, 500)
                driver.execute_script(f"window.scrollBy(0, {scroll_distance})")
                time.sleep(random.uniform(0.5, 1.5))
            
            # 随机鼠标移动
            if random.random() < self.config['mouse_movement_probability']:
                actions = ActionChains(driver)
                x_offset = random.randint(-100, 100)
                y_offset = random.randint(-100, 100)
                actions.move_by_offset(x_offset, y_offset).perform()
                time.sleep(random.uniform(0.1, 0.5))
            
            # 随机暂停
            time.sleep(random.uniform(
                self.config['min_request_delay'],
                self.config['max_request_delay']
            ))
            
        except Exception as e:
            self.logger.warning(f"模拟人类行为失败: {e}")
    
    async def type_like_human_playwright(self, page: Page, selector: str, text: str):
        """模拟人类输入（Playwright）"""
        element = await page.query_selector(selector)
        if element:
            await element.click()
            await page.wait_for_timeout(random.randint(100, 300))
            
            for char in text:
                await element.type(char)
                delay = random.uniform(*self.config['typing_delay_range'])
                await page.wait_for_timeout(int(delay * 1000))
    
    def type_like_human_selenium(self, driver: webdriver.Chrome, element, text: str):
        """模拟人类输入（Selenium）"""
        element.click()
        time.sleep(random.uniform(0.1, 0.3))
        
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(*self.config['typing_delay_range']))
    
    def mark_proxy_success(self, proxy: ProxyConfig, response_time: float):
        """标记代理成功"""
        proxy.success_count += 1
        proxy.last_used = datetime.now()
        proxy.response_time = response_time
        
        # 重置失败计数
        if proxy.failure_count > 0:
            proxy.failure_count = max(0, proxy.failure_count - 1)
    
    def mark_proxy_failure(self, proxy: ProxyConfig):
        """标记代理失败"""
        proxy.failure_count += 1
        proxy.last_used = datetime.now()
        
        # 如果失败次数过多，暂时禁用
        if proxy.failure_count >= self.config['max_retries_per_proxy']:
            proxy.is_active = False
            self.logger.warning(f"代理 {proxy.host}:{proxy.port} 已被禁用")
    
    def get_request_headers(self, fingerprint: BrowserFingerprint) -> Dict[str, str]:
        """获取请求头"""
        return {
            'User-Agent': fingerprint.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': f'{fingerprint.language},en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
    
    def increment_request_counter(self):
        """增加请求计数器"""
        self.config['request_counter'] += 1
    
    def reset_request_counter(self):
        """重置请求计数器"""
        self.config['request_counter'] = 0
    
    def load_proxies_from_file(self, file_path: str):
        """从文件加载代理列表"""
        try:
            with open(file_path, 'r') as f:
                proxy_list = f.readlines()
            
            for line in proxy_list:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split(':')
                    if len(parts) >= 2:
                        proxy = ProxyConfig(
                            host=parts[0],
                            port=int(parts[1]),
                            username=parts[2] if len(parts) > 2 else None,
                            password=parts[3] if len(parts) > 3 else None
                        )
                        self.proxy_pool.append(proxy)
            
            self.logger.info(f"从文件加载了 {len(self.proxy_pool)} 个代理")
            
        except Exception as e:
            self.logger.error(f"加载代理文件失败: {e}")
    
    def test_proxy(self, proxy: ProxyConfig) -> bool:
        """测试代理可用性"""
        try:
            proxy_url = f"{proxy.protocol}://"
            if proxy.username and proxy.password:
                proxy_url += f"{proxy.username}:{proxy.password}@"
            proxy_url += f"{proxy.host}:{proxy.port}"
            
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            start_time = time.time()
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxies,
                timeout=10
            )
            
            if response.status_code == 200:
                response_time = time.time() - start_time
                self.mark_proxy_success(proxy, response_time)
                self.logger.info(f"代理 {proxy.host}:{proxy.port} 测试成功，响应时间: {response_time:.2f}s")
                return True
            else:
                self.mark_proxy_failure(proxy)
                return False
                
        except Exception as e:
            self.mark_proxy_failure(proxy)
            self.logger.warning(f"代理 {proxy.host}:{proxy.port} 测试失败: {e}")
            return False
    
    def get_proxy_statistics(self) -> Dict[str, Any]:
        """获取代理统计信息"""
        active_proxies = [p for p in self.proxy_pool if p.is_active]
        total_success = sum(p.success_count for p in self.proxy_pool)
        total_failure = sum(p.failure_count for p in self.proxy_pool)
        
        return {
            'total_proxies': len(self.proxy_pool),
            'active_proxies': len(active_proxies),
            'total_requests': total_success + total_failure,
            'success_rate': total_success / (total_success + total_failure) if total_success + total_failure > 0 else 0,
            'average_response_time': sum(p.response_time for p in self.proxy_pool if p.response_time > 0) / len([p for p in self.proxy_pool if p.response_time > 0]) if any(p.response_time > 0 for p in self.proxy_pool) else 0
        }


# 使用示例
async def main():
    """测试反检测系统"""
    anti_detection = RPAAntiDetection()
    
    # 测试代理
    for proxy in anti_detection.proxy_pool:
        if anti_detection.test_proxy(proxy):
            print(f"代理可用: {proxy.host}:{proxy.port}")
    
    # 创建隐身浏览器
    if PLAYWRIGHT_AVAILABLE:
        browser, context = await anti_detection.create_stealth_browser_playwright()
        page = await context.new_page()
        
        try:
            await page.goto("https://httpbin.org/headers")
            await anti_detection.simulate_human_behavior_playwright(page)
            
            content = await page.content()
            print("页面内容获取成功")
            
        finally:
            await browser.close()
    
    # 显示统计信息
    stats = anti_detection.get_proxy_statistics()
    print(f"代理统计: {stats}")

if __name__ == "__main__":
    asyncio.run(main())