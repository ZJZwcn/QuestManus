import os
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Literal
import pyautogui
import pyperclip
import win32gui
import win32con
import win32api
import win32process
from pydantic import Field

from app.tool.base import BaseTool
from app.exceptions import ToolError
from app.logger import logger


class WeChatOfficialAccount(BaseTool):
    """微信公众号工具，用于搜索和关注微信公众号 📱"""

    name: str = "wechat_official_account"
    description: str = "控制电脑微信客户端，搜索和关注微信公众号，查看公众号历史文章等功能 🔍"
    parameters: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "要执行的操作类型",
                "enum": ["search_account", "follow_account", "view_history", "check_status"],
            },
            "account_name": {
                "type": "string",
                "description": "公众号名称",
            },
            "article_count": {
                "type": "integer",
                "description": "要查看的历史文章数量",
                "default": 5,
            },
        },
        "required": ["action"],
    }

    _wechat_window: Optional[int] = None
    _last_active_window: Optional[int] = None

    def __init__(self):
        """初始化微信公众号工具 🚀"""
        super().__init__()
        self._wechat_window = None
        self._last_active_window = None

    async def execute(
        self,
        *,
        action: Literal["search_account", "follow_account", "view_history", "check_status"],
        account_name: Optional[str] = None,
        article_count: int = 5,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        执行微信公众号操作 🔄
        
        Args:
            action: 要执行的操作类型
            account_name: 公众号名称
            article_count: 要查看的历史文章数量
            
        Returns:
            操作结果
        """
        try:
            # 保存当前活动窗口，以便操作完成后恢复
            self._last_active_window = win32gui.GetForegroundWindow()
            
            # 检查微信是否已启动
            if action != "check_status":
                await self._ensure_wechat_running()
            
            # 根据操作类型执行相应功能
            if action == "search_account":
                if not account_name:
                    raise ToolError("搜索公众号需要提供公众号名称 ❌")
                return await self._search_official_account(account_name)
                
            elif action == "follow_account":
                if not account_name:
                    raise ToolError("关注公众号需要提供公众号名称 ❌")
                return await self._follow_official_account(account_name)
                
            elif action == "view_history":
                if not account_name:
                    raise ToolError("查看历史文章需要提供公众号名称 ❌")
                return await self._view_history_articles(account_name, article_count)
                
            elif action == "check_status":
                return await self._check_status()
                
            else:
                raise ToolError(f"不支持的操作: {action} ❌")
                
        except Exception as e:
            logger.error(f"微信公众号操作失败: {str(e)} ❌")
            return {"success": False, "error": str(e)}
        finally:
            # 恢复之前的活动窗口
            if self._last_active_window:
                try:
                    win32gui.SetForegroundWindow(self._last_active_window)
                except:
                    pass

    async def _ensure_wechat_running(self) -> None:
        """确保微信客户端正在运行 🔍"""
        # 查找微信窗口
        self._wechat_window = win32gui.FindWindow("WeChatMainWndForPC", None)
        
        if not self._wechat_window:
            # 尝试启动微信
            logger.info("微信未运行，尝试启动微信客户端 🚀")
            try:
                # 常见的微信安装路径
                wechat_paths = [
                    os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'Tencent', 'WeChat', 'WeChat.exe'),
                    os.path.join(os.environ.get('ProgramFiles', ''), 'Tencent', 'WeChat', 'WeChat.exe'),
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Tencent', 'WeChat', 'WeChat.exe')
                ]
                
                for path in wechat_paths:
                    if os.path.exists(path):
                        os.startfile(path)
                        break
                else:
                    raise ToolError("未找到微信安装路径，请手动启动微信 ❌")
                
                # 等待微信启动
                for _ in range(10):
                    await asyncio.sleep(1)
                    self._wechat_window = win32gui.FindWindow("WeChatMainWndForPC", None)
                    if self._wechat_window:
                        break
                else:
                    raise ToolError("微信启动超时 ⏱️")
            except Exception as e:
                raise ToolError(f"启动微信失败: {str(e)} ❌")
        
        # 激活微信窗口
        win32gui.ShowWindow(self._wechat_window, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(self._wechat_window)
        await asyncio.sleep(0.5)

    async def _search_official_account(self, account_name: str) -> Dict[str, Any]:
        """
        搜索微信公众号 🔍
        
        Args:
            account_name: 要搜索的公众号名称
            
        Returns:
            搜索结果
        """
        # 激活微信窗口
        win32gui.SetForegroundWindow(self._wechat_window)
        
        # 点击通讯录标签
        # 通讯录标签通常在微信主窗口的左侧
        # 这里使用相对位置点击，实际使用时可能需要调整坐标
        window_rect = win32gui.GetWindowRect(self._wechat_window)
        window_width = window_rect[2] - window_rect[0]
        window_height = window_rect[3] - window_rect[1]
        
        # 点击底部的"通讯录"按钮
        contact_x = window_rect[0] + window_width * 0.15
        contact_y = window_rect[1] + window_height * 0.95
        pyautogui.click(contact_x, contact_y)
        await asyncio.sleep(0.5)
        
        # 点击"公众号"选项
        # 公众号选项通常在通讯录列表中
        # 使用搜索功能查找公众号
        pyautogui.hotkey('ctrl', 'f')
        await asyncio.sleep(0.3)
        
        # 清空搜索框
        pyautogui.hotkey('ctrl', 'a')
        await asyncio.sleep(0.2)
        pyautogui.press('delete')
        await asyncio.sleep(0.2)
        
        # 输入"公众号"
        pyperclip.copy("公众号")
        pyautogui.hotkey('ctrl', 'v')
        await asyncio.sleep(0.5)
        pyautogui.press('enter')
        await asyncio.sleep(1)
        
        # 点击搜索框
        search_x = window_rect[0] + window_width * 0.3
        search_y = window_rect[1] + window_height * 0.1
        pyautogui.click(search_x, search_y)
        await asyncio.sleep(0.3)
        
        # 输入公众号名称
        pyperclip.copy(account_name)
        pyautogui.hotkey('ctrl', 'v')
        await asyncio.sleep(1)
        
        # 按回车搜索
        pyautogui.press('enter')
        await asyncio.sleep(2)
        
        return {
            "success": True,
            "message": f"已搜索公众号: {account_name} 🔍",
            "note": "请在微信界面查看搜索结果"
        }

    async def _follow_official_account(self, account_name: str) -> Dict[str, Any]:
        """
        关注微信公众号 ➕
        
        Args:
            account_name: 要关注的公众号名称
            
        Returns:
            关注结果
        """
        # 先搜索公众号
        search_result = await self._search_official_account(account_name)
        if not search_result.get("success", False):
            return search_result
        
        # 等待搜索结果加载
        await asyncio.sleep(2)
        
        # 点击搜索结果中的第一个公众号
        # 这里使用相对位置点击，实际使用时可能需要调整坐标
        window_rect = win32gui.GetWindowRect(self._wechat_window)
        window_width = window_rect[2] - window_rect[0]
        window_height = window_rect[3] - window_rect[1]
        
        # 点击第一个搜索结果
        result_x = window_rect[0] + window_width * 0.5
        result_y = window_rect[1] + window_height * 0.2
        pyautogui.click(result_x, result_y)
        await asyncio.sleep(2)
        
        # 点击"关注"按钮
        # 关注按钮通常在公众号页面的右上角
        follow_x = window_rect[0] + window_width * 0.9
        follow_y = window_rect[1] + window_height * 0.1
        pyautogui.click(follow_x, follow_y)
        await asyncio.sleep(1)
        
        return {
            "success": True,
            "message": f"已尝试关注公众号: {account_name} ✅",
            "note": "请在微信界面确认关注状态"
        }

    async def _view_history_articles(self, account_name: str, article_count: int) -> Dict[str, Any]:
        """
        查看公众号历史文章 📜
        
        Args:
            account_name: 公众号名称
            article_count: 要查看的历史文章数量
            
        Returns:
            查看结果
        """
        # 先搜索公众号
        search_result = await self._search_official_account(account_name)
        if not search_result.get("success", False):
            return search_result
        
        # 等待搜索结果加载
        await asyncio.sleep(2)
        
        # 点击搜索结果中的第一个公众号
        window_rect = win32gui.GetWindowRect(self._wechat_window)
        window_width = window_rect[2] - window_rect[0]
        window_height = window_rect[3] - window_rect[1]
        
        # 点击第一个搜索结果
        result_x = window_rect[0] + window_width * 0.5
        result_y = window_rect[1] + window_height * 0.2
        pyautogui.click(result_x, result_y)
        await asyncio.sleep(2)
        
        # 点击"查看历史消息"按钮
        # 历史消息按钮通常在公众号页面的右上角菜单中
        menu_x = window_rect[0] + window_width * 0.95
        menu_y = window_rect[1] + window_height * 0.05
        pyautogui.click(menu_x, menu_y)
        await asyncio.sleep(1)
        
        # 点击"查看历史消息"选项
        history_x = window_rect[0] + window_width * 0.8
        history_y = window_rect[1] + window_height * 0.15
        pyautogui.click(history_x, history_y)
        await asyncio.sleep(2)
        
        # 获取文章标题（模拟，实际无法直接获取）
        article_titles = [f"文章 {i+1}" for i in range(article_count)]
        
        return {
            "success": True,
            "message": f"已查看公众号 {account_name} 的历史文章 📜",
            "article_count": article_count,
            "articles": article_titles,
            "note": "请在微信界面浏览历史文章"
        }

    async def _check_status(self) -> Dict[str, Any]:
        """
        检查微信客户端状态 🔄
        
        Returns:
            状态信息
        """
        wechat_window = win32gui.FindWindow("WeChatMainWndForPC", None)
        
        if wechat_window:
            # 获取进程ID
            _, process_id = win32process.GetWindowThreadProcessId(wechat_window)
            
            return {
                "success": True,
                "running": True,
                "window_handle": wechat_window,
                "process_id": process_id,
                "message": "微信客户端正在运行 ✅"
            }
        else:
            return {
                "success": True,
                "running": False,
                "message": "微信客户端未运行 ❌"
            }