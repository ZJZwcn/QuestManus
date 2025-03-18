import asyncio
import os
import time
from typing import List, Dict, Any, Optional, Union
from urllib.parse import quote_plus

from app.tool.base import BaseTool, ToolError

# 尝试导入selenium相关库
try:
    from selenium import webdriver
    from selenium.webdriver.edge.service import Service
    from selenium.webdriver.edge.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    EDGE_AVAILABLE = True
except ImportError:
    EDGE_AVAILABLE = False


class BaiduSearch(BaseTool):
    name: str = "baidu_search"
    description: str = """执行百度搜索并返回相关链接列表。
当您需要查找网络信息、获取最新数据或研究特定主题时，请使用此工具。
该工具返回与搜索查询匹配的URL列表和搜索结果摘要。
"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "(required) 提交给百度的搜索查询。",
            },
            "num_results": {
                "type": "integer",
                "description": "(optional) 要返回的搜索结果数量。默认为10。",
                "default": 10,
            },
            "include_snippets": {
                "type": "boolean",
                "description": "(optional) 是否包含搜索结果的文本摘要。默认为True。",
                "default": True,
            },
        },
        "required": ["query"],
    }
    
    _edge_driver: Optional[Any] = None

    async def execute(
        self, 
        query: str, 
        num_results: int = 10, 
        include_snippets: bool = True
    ) -> Union[List[str], Dict[str, Any]]:
        """
        使用Edge浏览器执行百度搜索并返回URL列表和可选的摘要。

        Args:
            query (str): 提交给百度的搜索查询。
            num_results (int, optional): 要返回的搜索结果数量。默认为10。
            include_snippets (bool, optional): 是否包含搜索结果的文本摘要。默认为True。

        Returns:
            Union[List[str], Dict[str, Any]]: 如果include_snippets为False，则返回URL列表；
                                             否则返回包含URL和摘要的字典。
        """
        # 检查Edge浏览器是否可用
        if not EDGE_AVAILABLE:
            raise ToolError("无法使用Edge浏览器，请安装必要的库: pip install selenium webdriver-manager")
            
        # 在线程池中运行搜索以防止阻塞
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None, lambda: self._search_with_edge(query, num_results, include_snippets)
        )
        
        return results
    
    def _search_with_edge(
        self, 
        query: str, 
        num_results: int, 
        include_snippets: bool
    ) -> Union[List[str], Dict[str, Any]]:
        """使用Edge浏览器执行百度搜索"""
        try:
            # 初始化Edge浏览器
            print("正在初始化Edge浏览器...")
            edge_options = Options()
            edge_options.add_argument("--headless")  # 无头模式
            edge_options.add_argument("--disable-gpu")
            edge_options.add_argument("--disable-notifications")  # 禁用通知
            edge_options.add_experimental_option("excludeSwitches", ["enable-logging"])  # 禁用日志
            
            # 初始化Edge驱动
            service = Service(EdgeChromiumDriverManager().install())
            self._edge_driver = webdriver.Edge(service=service, options=edge_options)
            
            # 访问百度搜索页面
            print(f"正在搜索: {query}")
            encoded_query = quote_plus(query)
            self._edge_driver.get(f"https://www.baidu.com/s?wd={encoded_query}")
            
            # 等待搜索结果加载
            WebDriverWait(self._edge_driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".result, .c-container"))
            )
            
            # 抓取搜索结果
            search_results = []
            result_elements = self._edge_driver.find_elements(By.CSS_SELECTOR, ".result, .c-container")
            
            for i, element in enumerate(result_elements):
                if i >= num_results:
                    break
                
                try:
                    # 提取链接
                    link_element = element.find_element(By.CSS_SELECTOR, "a[href]:not([href=''])") 
                    link = link_element.get_attribute("href")
                    
                    # 如果链接是百度跳转链接，尝试获取真实URL
                    if "www.baidu.com/link" in link:
                        try:
                            # 点击链接获取真实URL (可选，可能会导致页面跳转)
                            # 这里我们直接使用百度的跳转链接
                            pass
                        except:
                            pass
                    
                    # 提取标题
                    try:
                        title_element = element.find_element(By.CSS_SELECTOR, "h3")
                        title = title_element.text
                    except:
                        title = "无标题"
                    
                    # 提取摘要
                    try:
                        snippet_element = element.find_element(By.CSS_SELECTOR, ".c-abstract, .content-right_8Zs40")
                        snippet = snippet_element.text
                    except:
                        snippet = "无摘要"
                    
                    search_results.append({
                        "title": title,
                        "url": link,
                        "snippet": snippet
                    })
                    
                except Exception as e:
                    print(f"提取搜索结果时出错: {str(e)}")
                    continue
            
            # 关闭浏览器
            self._edge_driver.quit()
            self._edge_driver = None
            
            # 返回结果
            if include_snippets:
                return {
                    "query": query,
                    "results": search_results,
                    "links": [result["url"] for result in search_results]
                }
            else:
                return [result["url"] for result in search_results]
            
        except Exception as e:
            if self._edge_driver:
                self._edge_driver.quit()
                self._edge_driver = None
            raise ToolError(f"使用Edge浏览器搜索时出错: {str(e)}")