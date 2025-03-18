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

class WeChatMessage(BaseTool):
    """微信消息工具，用于控制电脑微信客户端 📱"""

    name: str = "wechat_message"
    description: str = "控制电脑微信客户端，发送消息、获取聊天记录、管理联系人等功能 🔄"
    parameters: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "要执行的操作类型",
                "enum": ["send_message", "search_contact", "get_chat_history", "switch_chat", "get_contacts", "check_status"],
            },
            "contact_name": {
                "type": "string",
                "description": "联系人或群聊名称",
            },
            "message": {
                "type": "string",
                "description": "要发送的消息内容",
            },
            "message_count": {
                "type": "integer",
                "description": "要获取的聊天记录数量",
                "default": 10,
            },
        },
        "required": ["action"],
    }

    _wechat_window: Optional[int] = None
    _last_active_window: Optional[int] = None

    def __init__(self):
        """初始化微信消息工具 🚀"""
        super().__init__()
        self._wechat_window = None
        self._last_active_window = None

    async def execute(
        self,
        *,
        action: Literal["send_message", "search_contact", "get_chat_history", "switch_chat", "get_contacts", "check_status"],
        contact_name: Optional[str] = None,
        message: Optional[str] = None,
        message_count: int = 10,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        执行微信操作 🔄
        
        Args:
            action: 要执行的操作类型
            contact_name: 联系人或群聊名称
            message: 要发送的消息内容
            message_count: 要获取的聊天记录数量
            
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
            if action == "send_message":
                if not contact_name:
                    raise ToolError("发送消息需要提供联系人名称 ❌")
                if not message:
                    raise ToolError("发送消息需要提供消息内容 ❌")
                return await self._send_message(contact_name, message)
                
            elif action == "search_contact":
                if not contact_name:
                    raise ToolError("搜索联系人需要提供联系人名称 ❌")
                return await self._search_contact(contact_name)
                
            elif action == "get_chat_history":
                if not contact_name:
                    raise ToolError("获取聊天记录需要提供联系人名称 ❌")
                return await self._get_chat_history(contact_name, message_count)
                
            elif action == "switch_chat":
                if not contact_name:
                    raise ToolError("切换聊天需要提供联系人名称 ❌")
                return await self._switch_chat(contact_name)
                
            elif action == "get_contacts":
                return await self._get_contacts()
                
            elif action == "check_status":
                return await self._check_status()
                
            else:
                raise ToolError(f"不支持的操作: {action} ❌")
                
        except Exception as e:
            logger.error(f"微信操作失败: {str(e)} ❌")
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
        await asyncio.sleep(0.5)  # 等待窗口激活

    async def _send_message(self, contact_name: str, message: str) -> Dict[str, Any]:
        """
        发送微信消息 📨
        
        Args:
            contact_name: 联系人或群聊名称
            message: 要发送的消息内容
            
        Returns:
            发送结果
        """
        # 切换到指定联系人聊天窗口
        switch_result = await self._switch_chat(contact_name)
        if not switch_result.get("success", False):
            return switch_result
        
        # 复制消息到剪贴板
        pyperclip.copy(message)
        
        # 粘贴消息
        pyautogui.hotkey('ctrl', 'v')
        await asyncio.sleep(0.3)
        
        # 发送消息
        pyautogui.press('enter')
        await asyncio.sleep(0.5)
        
        return {
            "success": True, 
            "message": f"已向 {contact_name} 发送消息 ✅", 
            "content": message
        }

    async def _search_contact(self, contact_name: str) -> Dict[str, Any]:
        """
        搜索联系人 🔍
        
        Args:
            contact_name: 要搜索的联系人名称
            
        Returns:
            搜索结果
        """
        # 激活微信窗口
        win32gui.SetForegroundWindow(self._wechat_window)
        
        # 点击搜索框
        pyautogui.hotkey('ctrl', 'f')
        await asyncio.sleep(0.3)
        
        # 清空搜索框
        pyautogui.hotkey('ctrl', 'a')
        await asyncio.sleep(0.2)
        pyautogui.press('delete')
        await asyncio.sleep(0.2)
        
        # 输入联系人名称
        pyperclip.copy(contact_name)
        pyautogui.hotkey('ctrl', 'v')
        await asyncio.sleep(1)
        
        # 获取搜索结果（这里只能模拟，无法直接获取搜索结果列表）
        return {
            "success": True,
            "message": f"已搜索联系人: {contact_name} 🔍",
            "note": "请在微信界面查看搜索结果"
        }

    async def _get_chat_history(self, contact_name: str, message_count: int = 10) -> Dict[str, Any]:
        """
        获取聊天记录 📜
        
        Args:
            contact_name: 联系人或群聊名称
            message_count: 要获取的消息数量
            
        Returns:
            聊天记录
        """
        # 切换到指定联系人聊天窗口
        switch_result = await self._switch_chat(contact_name)
        if not switch_result.get("success", False):
            return switch_result
        
        # 由于微信没有提供API，这里只能模拟获取聊天记录
        # 实际上无法直接获取，这里返回提示信息
        return {
            "success": True,
            "message": f"由于微信客户端限制，无法直接获取与 {contact_name} 的聊天记录 ℹ️",
            "note": "可以使用截图功能捕获当前可见的聊天记录"
        }

    async def _switch_chat(self, contact_name: str) -> Dict[str, Any]:
        """
        切换到指定联系人的聊天窗口 🔄
        
        Args:
            contact_name: 联系人或群聊名称
            
        Returns:
            切换结果
        """
        # 激活微信窗口
        win32gui.SetForegroundWindow(self._wechat_window)
        
        # 点击搜索框
        pyautogui.hotkey('ctrl', 'f')
        await asyncio.sleep(0.3)
        
        # 清空搜索框
        pyautogui.hotkey('ctrl', 'a')
        await asyncio.sleep(0.2)
        pyautogui.press('delete')
        await asyncio.sleep(0.2)
        
        # 输入联系人名称
        pyperclip.copy(contact_name)
        pyautogui.hotkey('ctrl', 'v')
        await asyncio.sleep(1)
        
        # 按回车选择第一个搜索结果
        pyautogui.press('enter')
        await asyncio.sleep(0.5)
        
        return {
            "success": True,
            "message": f"已切换到与 {contact_name} 的聊天窗口 ✅"
        }

    async def _get_contacts(self) -> Dict[str, Any]:
        """
        获取联系人列表 👥
        
        Returns:
            联系人列表信息
        """
        # 由于微信没有提供API，这里只能模拟获取联系人列表
        # 实际上无法直接获取，这里返回提示信息
        return {
            "success": True,
            "message": "由于微信客户端限制，无法直接获取完整联系人列表 ℹ️",
            "note": "可以使用搜索功能查找特定联系人"
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