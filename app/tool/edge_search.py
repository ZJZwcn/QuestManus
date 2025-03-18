import asyncio
import os
from typing import List, Dict, Optional, Any, Union
import time

from app.tool.base import BaseTool, ToolError, ToolResult

# 尝试导入 selenium 相关模块
try:
    from selenium import webdriver
    from selenium.webdriver.edge.service import Service
    from selenium.webdriver.edge.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class EdgeBrowser(BaseTool):
    """Microsoft Edge 浏览器控制工具"""

    name: str = "edge_browser"
    description: str = """控制 Microsoft Edge 浏览器执行各种操作。
可以用于打开网页、执行搜索、截图、获取页面内容等操作。
当您需要浏览网页、搜索信息或与网页交互时，请使用此工具。
"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "(required) 要执行的命令，可选值: open, search, navigate, screenshot, get_content, close",
                "enum": ["open", "search", "navigate", "screenshot", "get_content", "close"]
            },
            "url": {
                "type": "string",
                "description": "用于 open 和 navigate 命令的 URL。如果不提供协议，将默认使用 http://",
            },
            "query": {
                "type": "string",
                "description": "用于 search 命令的搜索查询",
            },
            "selector": {
                "type": "string",
                "description": "用于 get_content 命令的 CSS 选择器，用于获取特定元素的内容",
            },
            "screenshot_path": {
                "type": "string",
                "description": "用于 screenshot 命令的截图保存路径",
            },
            "timeout": {
                "type": "integer",
                "description": "等待页面加载的超时时间（秒），默认为 30 秒",
                "default": 30,
            },
        },
        "required": ["command"],
    }

    _driver: Optional[webdriver.Edge] = None

    async def execute(
        self,
        command: str,
        url: Optional[str] = None,
        query: Optional[str] = None,
        selector: Optional[str] = None,
        screenshot_path: Optional[str] = None,
        timeout: int = 30,
        **kwargs
    ) -> Union[str, Dict[str, Any], List[str]]:
        """
        执行 Edge 浏览器操作。

        Args:
            command: 要执行的命令
            url: 用于 open 和 navigate 命令的 URL
            query: 用于 search 命令的搜索查询
            selector: 用于 get_content 命令的 CSS 选择器
            screenshot_path: 用于 screenshot 命令的截图保存路径
            timeout: 等待页面加载的超时时间（秒）

        Returns:
            操作结果，根据命令不同返回不同类型的数据
        """
        if not SELENIUM_AVAILABLE:
            raise ToolError("无法使用 Edge 浏览器工具，请安装 selenium 库: pip install selenium")

        # 在线程池中运行浏览器操作以防止阻塞
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, lambda: self._execute_sync(command, url, query, selector, screenshot_path, timeout)
        )
        
        return result

    def _execute_sync(
        self,
        command: str,
        url: Optional[str] = None,
        query: Optional[str] = None,
        selector: Optional[str] = None,
        screenshot_path: Optional[str] = None,
        timeout: int = 30,
    ) -> Union[str, Dict[str, Any], List[str]]:
        """同步执行浏览器操作"""
        try:
            if command == "open":
                return self._open_browser(url)
            elif command == "search":
                return self._search(query, timeout)
            elif command == "navigate":
                return self._navigate(url, timeout)
            elif command == "screenshot":
                return self._take_screenshot(screenshot_path)
            elif command == "get_content":
                return self._get_content(selector, timeout)
            elif command == "close":
                return self._close_browser()
            else:
                raise ToolError(f"未知命令: {command}")
        except Exception as e:
            raise ToolError(f"执行 Edge 浏览器操作时出错: {str(e)}")

    def _open_browser(self, url: Optional[str] = None) -> str:
        """打开 Edge 浏览器"""
        if self._driver is not None:
            return "浏览器已经打开"

        try:
            # 配置 Edge 选项
            options = Options()
            options.add_argument("--start-maximized")  # 最大化窗口
            options.add_argument("--disable-extensions")  # 禁用扩展
            options.add_argument("--disable-popup-blocking")  # 禁用弹出窗口阻止
            options.add_argument("--disable-notifications")  # 禁用通知
            
            # 创建 Edge 驱动
            self._driver = webdriver.Edge(options=options)
            
            # 如果提供了 URL，则导航到该 URL
            if url:
                if not url.startswith(('http://', 'https://')):
                    url = 'http://' + url
                self._driver.get(url)
                return f"已打开 Edge 浏览器并导航到 {url}"
            else:
                self._driver.get("edge://newtab/")
                return "已打开 Edge 浏览器"
        except WebDriverException as e:
            raise ToolError(f"无法启动 Edge 浏览器: {str(e)}")

    def _search(self, query: Optional[str], timeout: int) -> Dict[str, Any]:
        """在 Edge 浏览器中执行搜索"""
        if not query:
            raise ToolError("搜索命令需要提供查询参数")
        
        if self._driver is None:
            self._open_browser()
        
        try:
            # 导航到必应搜索
            self._driver.get("https://www.bing.com")
            
            # 等待搜索框加载
            search_box = WebDriverWait(self._driver, timeout).until(
                EC.presence_of_element_located((By.ID, "sb_form_q"))
            )
            
            # 输入搜索查询
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            
            # 等待搜索结果加载
            WebDriverWait(self._driver, timeout).until(
                EC.presence_of_element_located((By.ID, "b_results"))
            )
            
            # 获取搜索结果
            results = []
            result_elements = self._driver.find_elements(By.CSS_SELECTOR, "#b_results .b_algo h2 a")
            
            for element in result_elements[:5]:  # 获取前 5 个结果
                title = element.text
                link = element.get_attribute("href")
                results.append({"title": title, "url": link})
            
            return {
                "query": query,
                "url": self._driver.current_url,
                "results": results
            }
        except TimeoutException:
            raise ToolError(f"搜索超时，请检查网络连接或增加超时时间")
        except Exception as e:
            raise ToolError(f"执行搜索时出错: {str(e)}")

    def _navigate(self, url: Optional[str], timeout: int) -> str:
        """导航到指定 URL"""
        if not url:
            raise ToolError("导航命令需要提供 URL 参数")
        
        if self._driver is None:
            return self._open_browser(url)
        
        try:
            # 确保 URL 有协议前缀
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            
            # 导航到 URL
            self._driver.get(url)
            
            # 等待页面加载
            WebDriverWait(self._driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            return f"已成功导航到 {url}"
        except TimeoutException:
            raise ToolError(f"页面加载超时，请检查网络连接或增加超时时间")
        except Exception as e:
            raise ToolError(f"导航到 {url} 时出错: {str(e)}")

    def _take_screenshot(self, screenshot_path: Optional[str]) -> str:
        """截取当前页面的屏幕截图"""
        if self._driver is None:
            raise ToolError("浏览器未打开，请先使用 open 命令打开浏览器")
        
        if not screenshot_path:
            # 使用默认路径
            screenshot_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = os.path.join(screenshot_dir, f"screenshot_{int(time.time())}.png")
        
        try:
            self._driver.save_screenshot(screenshot_path)
            return f"已保存屏幕截图到 {screenshot_path}"
        except Exception as e:
            raise ToolError(f"截图时出错: {str(e)}")

    def _get_content(self, selector: Optional[str], timeout: int) -> Dict[str, Any]:
        """获取页面内容"""
        if self._driver is None:
            raise ToolError("浏览器未打开，请先使用 open 命令打开浏览器")
        
        try:
            # 等待页面加载完成
            WebDriverWait(self._driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            result = {
                "url": self._driver.current_url,
                "title": self._driver.title,
            }
            
            if selector:
                # 等待选择器对应的元素加载
                try:
                    element = WebDriverWait(self._driver, timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    result["selected_content"] = element.text
                except TimeoutException:
                    result["selected_content"] = f"未找到匹配选择器 '{selector}' 的元素"
            else:
                # 获取页面文本内容
                result["content"] = self._driver.find_element(By.TAG_NAME, "body").text
            
            return result
        except Exception as e:
            raise ToolError(f"获取页面内容时出错: {str(e)}")

    def _close_browser(self) -> str:
        """关闭浏览器"""
        if self._driver is None:
            return "浏览器已经关闭"
        
        try:
            self._driver.quit()
            self._driver = None
            return "已关闭 Edge 浏览器"
        except Exception as e:
            raise ToolError(f"关闭浏览器时出错: {str(e)}")