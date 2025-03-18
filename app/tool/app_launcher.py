import os
import time
import asyncio
import subprocess
import win32gui
import win32con
import win32api
import win32com.client
import pyautogui
import pyperclip
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from app.tool.base import BaseTool
from app.exceptions import ToolError
from app.logger import logger


class AppLauncher(BaseTool):
    """应用程序启动工具，用于打开系统中的任何应用程序 🚀"""

    name: str = "app_launcher"
    description: str = """
    打开系统中的任何应用程序。
    首先会检查是否存在explorer.exe快捷方式（应用程序列表），如果不存在则自动创建。
    然后通过搜索应用程序名称并启动它。
    当您需要打开任何系统应用或已安装的软件时，请使用此工具。
    """
    parameters: dict = {
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "description": "(required) 要打开的应用程序名称",
            },
            "create_shortcut": {
                "type": "boolean",
                "description": "是否需要创建explorer.exe快捷方式（如果不存在）",
                "default": True,
            },
            "wait_time": {
                "type": "integer",
                "description": "等待应用程序启动的最长时间（秒）",
                "default": 10,
            },
        },
        "required": ["app_name"],
    }

    _explorer_shortcut_path: str = None
    _apps_window: Optional[int] = None
    _last_active_window: Optional[int] = None

    def __init__(self):
        """初始化应用程序启动工具 🚀"""
        super().__init__()
        self._explorer_shortcut_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            "explorer.exe.lnk"
        )
        self._apps_window = None
        self._last_active_window = None

    async def execute(
        self,
        app_name: str,
        create_shortcut: bool = True,
        wait_time: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行应用程序启动操作 🔄
        
        Args:
            app_name: 要打开的应用程序名称
            create_shortcut: 是否需要创建explorer.exe快捷方式（如果不存在）
            wait_time: 等待应用程序启动的最长时间（秒）
            
        Returns:
            操作结果
        """
        try:
            # 保存当前活动窗口，以便操作完成后恢复
            self._last_active_window = win32gui.GetForegroundWindow()
            
            # 检查快捷方式是否存在，如果不存在且create_shortcut为True，则创建
            if create_shortcut and not os.path.exists(self._explorer_shortcut_path):
                await self._create_explorer_shortcut()
            
            # 打开应用程序
            result = await self._open_application(app_name, wait_time)
            
            return result
                
        except Exception as e:
            logger.error(f"应用程序启动失败: {str(e)} ❌")
            return {"success": False, "error": str(e)}
        finally:
            # 恢复之前的活动窗口
            if self._last_active_window:
                try:
                    win32gui.SetForegroundWindow(self._last_active_window)
                except:
                    pass

    async def _create_explorer_shortcut(self) -> None:
        """
        创建explorer.exe快捷方式（应用程序列表）🔗
        
        这个快捷方式指向Windows的应用程序列表视图
        """
        try:
            logger.info("正在创建explorer.exe快捷方式 🔗")
            
            # 使用Windows Script Host创建快捷方式
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(self._explorer_shortcut_path)
            shortcut.TargetPath = "%windir%\\explorer.exe"
            shortcut.Arguments = "shell:::{4234d49b-0245-4df3-b780-3893943456e1}"
            shortcut.Description = "应用程序列表"
            shortcut.IconLocation = "%windir%\\explorer.exe,0"
            shortcut.save()
            
            logger.info(f"explorer.exe快捷方式已创建: {self._explorer_shortcut_path} ✅")
            
            # 验证快捷方式是否创建成功
            if not os.path.exists(self._explorer_shortcut_path):
                # 如果通过WScript创建失败，尝试通过模拟用户操作创建
                await self._create_shortcut_manually()
                
        except Exception as e:
            logger.error(f"创建explorer.exe快捷方式失败: {str(e)} ❌")
            # 尝试通过模拟用户操作创建
            await self._create_shortcut_manually()

    async def _create_shortcut_manually(self) -> None:
        """
        通过模拟用户操作手动创建快捷方式 🖱️
        """
        try:
            # 获取桌面路径
            desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop")
            
            # 右键点击桌面空白处
            pyautogui.click(x=100, y=100, button="right")
            await asyncio.sleep(0.5)
            
            # 点击"新建"
            for option in ["新建", "New"]:
                try:
                    position = pyautogui.locateOnScreen(f"{option}.png", confidence=0.8)
                    if position:
                        center = pyautogui.center(position)
                        pyautogui.click(center)
                        break
                except:
                    continue
            
            await asyncio.sleep(0.5)
            
            # 点击"快捷方式"
            for option in ["快捷方式", "Shortcut"]:
                try:
                    position = pyautogui.locateOnScreen(f"{option}.png", confidence=0.8)
                    if position:
                        center = pyautogui.center(position)
                        pyautogui.click(center)
                        break
                except:
                    continue
            
            await asyncio.sleep(1)
            
            # 在"请键入对象的位置"输入框中输入
            pyperclip.copy("%windir%\\explorer.exe shell:::{4234d49b-0245-4df3-b780-3893943456e1}")
            pyautogui.hotkey("ctrl", "v")
            await asyncio.sleep(0.5)
            
            # 点击"下一步"
            pyautogui.press("tab")
            pyautogui.press("enter")
            await asyncio.sleep(0.5)
            
            # 在输入框中输入"explorer.exe"
            pyperclip.copy("explorer.exe")
            pyautogui.hotkey("ctrl", "v")
            await asyncio.sleep(0.5)
            
            # 点击"完成"
            pyautogui.press("tab")
            pyautogui.press("enter")
            await asyncio.sleep(0.5)
            
            # 将快捷方式移动到项目目录
            source_path = os.path.join(desktop_path, "explorer.exe.lnk")
            if os.path.exists(source_path):
                import shutil
                shutil.move(source_path, self._explorer_shortcut_path)
                logger.info(f"explorer.exe快捷方式已手动创建并移动: {self._explorer_shortcut_path} ✅")
            
        except Exception as e:
            raise ToolError(f"手动创建explorer.exe快捷方式失败: {str(e)} ❌")

    async def _open_application(self, app_name: str, wait_time: int) -> Dict[str, Any]:
        """
        打开指定的应用程序 🚀
        
        Args:
            app_name: 要打开的应用程序名称
            wait_time: 等待应用程序启动的最长时间（秒）
            
        Returns:
            操作结果
        """
        try:
            # 首先尝试直接运行应用程序（适用于常见应用）
            try:
                subprocess.Popen(app_name)
                logger.info(f"尝试直接运行应用程序: {app_name} 🚀")
                
                # 等待应用程序启动
                for _ in range(wait_time):
                    await asyncio.sleep(1)
                    # 检查应用程序是否已启动
                    if self._is_app_running(app_name):
                        return {
                            "success": True,
                            "message": f"已成功启动应用程序: {app_name} ✅",
                            "method": "direct_run"
                        }
            except:
                logger.info(f"直接运行应用程序失败，尝试通过应用程序列表打开: {app_name} 🔄")
            
            # 如果直接运行失败，通过应用程序列表打开
            # 打开explorer.exe快捷方式
            if not os.path.exists(self._explorer_shortcut_path):
                raise ToolError(f"找不到explorer.exe快捷方式: {self._explorer_shortcut_path} ❌")
            
            os.startfile(self._explorer_shortcut_path)
            await asyncio.sleep(2)
            
            # 查找应用程序列表窗口
            self._apps_window = win32gui.GetForegroundWindow()
            if not self._apps_window:
                raise ToolError("无法获取应用程序列表窗口 ❌")
            
            # 激活窗口
            win32gui.ShowWindow(self._apps_window, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(self._apps_window)
            await asyncio.sleep(1)
            
            # 在搜索框中搜索应用程序
            pyautogui.hotkey("ctrl", "f")  # 激活搜索
            await asyncio.sleep(0.5)
            
            # 清空搜索框
            pyautogui.hotkey("ctrl", "a")
            pyautogui.press("delete")
            await asyncio.sleep(0.5)
            
            # 输入应用程序名称
            pyperclip.copy(app_name)
            pyautogui.hotkey("ctrl", "v")
            await asyncio.sleep(2)  # 等待搜索结果
            
            # 点击第一个搜索结果
            # 获取窗口位置和大小
            window_rect = win32gui.GetWindowRect(self._apps_window)
            window_width = window_rect[2] - window_rect[0]
            window_height = window_rect[3] - window_rect[1]
            
            # 点击搜索结果区域的第一个结果
            result_x = window_rect[0] + window_width * 0.3
            result_y = window_rect[1] + window_height * 0.3
            pyautogui.click(result_x, result_y)
            await asyncio.sleep(0.5)
            
            # 按回车键打开应用程序
            pyautogui.press("enter")
            
            # 等待应用程序启动
            app_started = False
            for _ in range(wait_time):
                await asyncio.sleep(1)
                # 检查应用程序是否已启动
                if self._is_app_running(app_name):
                    app_started = True
                    break
            
            # 关闭应用程序列表窗口
            try:
                win32gui.PostMessage(self._apps_window, win32con.WM_CLOSE, 0, 0)
            except:
                pass
            
            if app_started:
                return {
                    "success": True,
                    "message": f"已成功启动应用程序: {app_name} ✅",
                    "method": "apps_list"
                }
            else:
                return {
                    "success": False,
                    "message": f"应用程序可能已启动，但无法确认: {app_name} ⚠️",
                    "method": "apps_list"
                }
            
        except Exception as e:
            raise ToolError(f"打开应用程序失败: {str(e)} ❌")

    def _is_app_running(self, app_name: str) -> bool:
        """
        检查应用程序是否正在运行 🔍
        
        Args:
            app_name: 应用程序名称
            
        Returns:
            应用程序是否正在运行
        """
        try:
            # 获取所有窗口标题
            def enum_window_titles():
                titles = []
                def enum_windows_proc(hwnd, lParam):
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if title and len(title) > 0:
                            titles.append(title.lower())
                    return True
                win32gui.EnumWindows(enum_windows_proc, None)
                return titles
            
            # 获取所有进程名称
            import psutil
            process_names = [proc.name().lower() for proc in psutil.process_iter()]
            
            # 检查应用程序名称是否在窗口标题或进程名称中
            app_name_lower = app_name.lower()
            window_titles = enum_window_titles()
            
            # 检查窗口标题
            for title in window_titles:
                if app_name_lower in title:
                    return True
            
            # 检查进程名称
            for proc_name in process_names:
                if app_name_lower in proc_name or proc_name in app_name_lower:
                    return True
                
            # 特殊情况处理
            special_cases = {
                "word": ["winword.exe", "microsoft word"],
                "excel": ["excel.exe", "microsoft excel"],
                "powerpoint": ["powerpnt.exe", "microsoft powerpoint"],
                "chrome": ["chrome.exe", "google chrome"],
                "edge": ["msedge.exe", "microsoft edge"],
                "firefox": ["firefox.exe", "mozilla firefox"],
                "photoshop": ["photoshop.exe", "adobe photoshop"],
                "illustrator": ["illustrator.exe", "adobe illustrator"],
                "visual studio": ["devenv.exe", "visual studio"],
                "vscode": ["code.exe", "visual studio code"],
                "notepad": ["notepad.exe"],
                "calculator": ["calc.exe"],
                "paint": ["mspaint.exe"],
                "explorer": ["explorer.exe"],
                "微信": ["wechat.exe", "weixin.exe"],
                "qq": ["qq.exe", "tencent"],
                "钉钉": ["dingtalk.exe"],
                "企业微信": ["wework.exe", "wxwork.exe"],
                "迅雷": ["thunder.exe"],
                "百度网盘": ["baidunetdisk.exe"],
                "网易云音乐": ["cloudmusic.exe"],
                "腾讯会议": ["wemeet.exe"],
                "zoom": ["zoom.exe"],
            }
            
            # 检查特殊情况
            for key, values in special_cases.items():
                if key in app_name_lower:
                    for proc_name in process_names:
                        for value in values:
                            if value in proc_name:
                                return True
            
            return False
            
        except Exception as e:
            logger.error(f"检查应用程序运行状态时出错: {str(e)} ❌")
            return False