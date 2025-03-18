import os
import asyncio
from typing import Dict, List, Optional, Any, Literal
import pyautogui
import pyperclip
import win32gui
import win32con
import subprocess

from app.tool.base import BaseTool
from app.exceptions import ToolError
from app.logger import logger

class QQMusicControl(BaseTool):
    """QQ音乐控制工具，用于控制QQ音乐播放器 🎵"""

    name: str = "qqmusic_control"
    description: str = """
    控制QQ音乐播放器，实现播放、暂停、上一首、下一首、调整音量等功能。
    当您需要控制音乐播放时，请使用此工具。
    """
    parameters: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "(required) 要执行的操作类型",
                "enum": ["play", "pause", "next", "previous", "volume_up", "volume_down", 
                         "open", "close", "get_status", "get_current_song"],
            },
            "volume_step": {
                "type": "integer",
                "description": "调整音量的步长（百分比，1-100），默认为10",
                "default": 10,
            },
        },
        "required": ["action"],
    }

    _qqmusic_window: Optional[int] = None
    _last_active_window: Optional[int] = None
    _qqmusic_path: str = r"C:\Program Files (x86)\Tencent\QQMusic\QQMusic.exe"

    def __init__(self):
        """初始化QQ音乐控制工具 🚀"""
        super().__init__()
        self._qqmusic_window = None
        self._last_active_window = None
        # 尝试查找QQ音乐安装路径
        common_paths = [
            r"C:\Program Files (x86)\Tencent\QQMusic\QQMusic.exe",
            r"C:\Program Files\Tencent\QQMusic\QQMusic.exe",
            os.path.expanduser("~") + r"\AppData\Local\Tencent\QQMusic\QQMusic.exe"
        ]
        for path in common_paths:
            if os.path.exists(path):
                self._qqmusic_path = path
                break

    async def execute(
        self,
        *,
        action: Literal["play", "pause", "next", "previous", "volume_up", "volume_down", 
                        "open", "close", "get_status", "get_current_song"],
        volume_step: int = 10,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        执行QQ音乐控制操作 🔄
        
        Args:
            action: 要执行的操作类型
            volume_step: 调整音量的步长（百分比）
            
        Returns:
            操作结果
        """
        try:
            # 保存当前活动窗口，以便操作完成后恢复
            self._last_active_window = win32gui.GetForegroundWindow()
            
            # 如果是打开操作，直接执行
            if action == "open":
                return await self._open_qqmusic()
                
            # 其他操作需要确保QQ音乐已启动
            if action != "open":
                try:
                    await self._ensure_qqmusic_running()
                except Exception as e:
                    # 如果是控制操作，即使窗口识别失败也尝试发送快捷键
                    if action in ["play", "pause", "next", "previous", "volume_up", "volume_down"]:
                        logger.warning(f"QQ音乐窗口识别失败，但仍将尝试发送快捷键: {str(e)} ⚠️")
                    else:
                        # 对于需要窗口的操作，如获取状态，则返回错误
                        return {"success": False, "error": f"QQ音乐窗口识别失败: {str(e)} ❌"}
            
            # 根据操作类型执行相应功能
            if action == "play":
                return await self._play_music()
            elif action == "pause":
                return await self._pause_music()
            elif action == "next":
                return await self._next_song()
            elif action == "previous":
                return await self._previous_song()
            elif action == "volume_up":
                return await self._adjust_volume(volume_step)
            elif action == "volume_down":
                return await self._adjust_volume(-volume_step)
            elif action == "close":
                return await self._close_qqmusic()
            elif action == "get_status":
                return await self._get_status()
            elif action == "get_current_song":
                return await self._get_current_song()
            else:
                raise ToolError(f"不支持的操作: {action} ❌")
                
        except Exception as e:
            logger.error(f"QQ音乐控制出错: {str(e)} ❌")
            return {"success": False, "error": str(e)}
        finally:
            # 恢复之前的活动窗口
            if self._last_active_window:
                try:
                    win32gui.SetForegroundWindow(self._last_active_window)
                except:
                    pass

    async def _ensure_qqmusic_running(self) -> None:
        """确保QQ音乐应用程序正在运行 🔍"""
        # 查找QQ音乐窗口 - 使用更广泛的窗口标题匹配
        self._qqmusic_window = None
        
        # 尝试查找各种可能的QQ音乐窗口标题
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                # 更宽松的匹配条件
                if "QQ音乐" in window_title or "QQMusic" in window_title:
                    windows.append((hwnd, window_title))
            return True
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        if windows:
            # 找到了QQ音乐窗口
            self._qqmusic_window = windows[0][0]
            logger.info(f"找到QQ音乐窗口: {windows[0][1]} ✅")
        else:
            # 尝试启动QQ音乐
            logger.info("QQ音乐未运行，尝试启动QQ音乐应用程序 🚀")
            result = await self._open_qqmusic()
            
            if not result.get("success", False):
                raise ToolError("无法启动QQ音乐，请确认安装路径是否正确 ❌")
        
        # 确保窗口已激活
        if self._qqmusic_window:
            try:
                # 尝试恢复并激活窗口
                win32gui.ShowWindow(self._qqmusic_window, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(self._qqmusic_window)
                await asyncio.sleep(1.0)  # 增加等待时间，确保窗口完全激活
            except Exception as e:
                logger.error(f"激活QQ音乐窗口失败: {str(e)} ⚠️")
                # 继续执行，因为即使窗口激活失败，快捷键可能仍然有效

    async def _open_qqmusic(self) -> Dict[str, Any]:
        """打开QQ音乐应用程序 🚀"""
        try:
            # 先检查QQ音乐是否已经在运行
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if "QQ音乐" in window_title or "QQMusic" in window_title:
                        windows.append((hwnd, window_title))
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            if windows:
                # 找到了QQ音乐窗口
                self._qqmusic_window = windows[0][0]
                win32gui.ShowWindow(self._qqmusic_window, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(self._qqmusic_window)
                logger.info(f"QQ音乐已经在运行，已激活窗口: {windows[0][1]} ✅")
                return {"success": True, "message": f"QQ音乐已经在运行，已激活窗口 ✅"}
            
            # 检查QQ音乐安装路径
            if not os.path.exists(self._qqmusic_path):
                # 尝试查找其他可能的安装路径
                common_paths = [
                    r"C:\Program Files (x86)\Tencent\QQMusic\QQMusic.exe",
                    r"C:\Program Files\Tencent\QQMusic\QQMusic.exe",
                    os.path.expanduser("~") + r"\AppData\Local\Tencent\QQMusic\QQMusic.exe",
                    r"D:\Program Files (x86)\Tencent\QQMusic\QQMusic.exe",
                    r"D:\Program Files\Tencent\QQMusic\QQMusic.exe"
                ]
                
                for path in common_paths:
                    if os.path.exists(path):
                        self._qqmusic_path = path
                        logger.info(f"找到QQ音乐安装路径: {path} ✅")
                        break
                else:
                    # 尝试通过进程名查找
                    import psutil
                    for proc in psutil.process_iter(['name', 'exe']):
                        try:
                            if 'QQMusic' in proc.info['name'] or 'QQ音乐' in proc.info['name']:
                                if proc.info['exe']:
                                    self._qqmusic_path = proc.info['exe']
                                    logger.info(f"通过进程找到QQ音乐: {self._qqmusic_path} ✅")
                                    break
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                            pass
                    else:
                        raise ToolError("未找到QQ音乐安装路径，请确认QQ音乐是否已安装 ❌")
            
            # 启动QQ音乐
            logger.info(f"尝试启动QQ音乐: {self._qqmusic_path} 🚀")
            process = subprocess.Popen(self._qqmusic_path)
            
            # 等待QQ音乐启动，增加超时时间
            for i in range(15):  # 增加到15秒
                await asyncio.sleep(1)
                logger.info(f"等待QQ音乐启动... ({i+1}/15) ⏳")
                
                # 检查进程是否还在运行
                if process.poll() is not None:
                    logger.error(f"QQ音乐进程已退出，返回码: {process.returncode} ❌")
                    break
                
                # 尝试查找QQ音乐窗口
                windows = []
                win32gui.EnumWindows(enum_windows_callback, windows)
                if windows:
                    self._qqmusic_window = windows[0][0]
                    win32gui.SetForegroundWindow(self._qqmusic_window)
                    logger.info(f"QQ音乐已成功启动: {windows[0][1]} ✅")
                    return {"success": True, "message": "QQ音乐已成功启动 ✅"}
            
            # 如果超时但进程仍在运行，可能是窗口标题不匹配
            if process.poll() is None:
                logger.warning("QQ音乐可能已启动但无法识别窗口，尝试使用快捷键控制 ⚠️")
                return {"success": True, "message": "QQ音乐可能已启动但无法识别窗口，将尝试使用快捷键控制 ⚠️"}
            
            return {"success": False, "message": "QQ音乐启动超时或失败 ⏱️"}
            
        except Exception as e:
            logger.error(f"打开QQ音乐失败: {str(e)} ❌")
            raise ToolError(f"打开QQ音乐失败: {str(e)} ❌")

    async def _close_qqmusic(self) -> Dict[str, Any]:
        """关闭QQ音乐应用程序 🛑"""
        try:
            if not self._qqmusic_window:
                return {"success": False, "message": "QQ音乐未运行 ⚠️"}
            
            # 发送关闭消息
            win32gui.PostMessage(self._qqmusic_window, win32con.WM_CLOSE, 0, 0)
            logger.info("已发送关闭命令到QQ音乐 🛑")
            
            # 等待QQ音乐关闭
            for _ in range(5):
                await asyncio.sleep(1)
                try:
                    # 检查窗口是否还存在
                    if not win32gui.IsWindow(self._qqmusic_window):
                        self._qqmusic_window = None
                        return {"success": True, "message": "QQ音乐已成功关闭 ✅"}
                except:
                    self._qqmusic_window = None
                    return {"success": True, "message": "QQ音乐已成功关闭 ✅"}
            
            return {"success": False, "message": "QQ音乐关闭失败 ❌"}
            
        except Exception as e:
            raise ToolError(f"关闭QQ音乐失败: {str(e)} ❌")

    async def _play_music(self) -> Dict[str, Any]:
        """播放音乐 ▶️"""
        try:
            # 使用快捷键 Ctrl+Alt+F5 播放/暂停
            logger.info("正在发送播放命令(Ctrl+Alt+F5) ▶️")
            # 确保应用程序处于前台或使用全局快捷键
            pyautogui.hotkey('ctrl', 'alt', 'f5')
            await asyncio.sleep(1.0)  # 增加等待时间
            
            # 尝试获取当前歌曲，但即使失败也返回成功
            try:
                song_info = await self._get_current_song()
                current_song = song_info.get("current_song", "未知")
            except:
                current_song = "无法获取当前歌曲信息"
            
            return {
                "success": True, 
                "message": "已发送播放命令 ▶️",
                "current_song": current_song
            }
            
        except Exception as e:
            logger.error(f"播放音乐失败: {str(e)} ❌")
            raise ToolError(f"播放音乐失败: {str(e)} ❌")

    async def _pause_music(self) -> Dict[str, Any]:
        """暂停音乐 ⏸️"""
        try:
            # 使用快捷键 Ctrl+Alt+F5 播放/暂停
            logger.info("正在发送暂停命令(Ctrl+Alt+F5) ⏸️")
            pyautogui.hotkey('ctrl', 'alt', 'f5')
            await asyncio.sleep(1.0)  # 增加等待时间
            
            return {
                "success": True, 
                "message": "已发送暂停命令 ⏸️"
            }
            
        except Exception as e:
            logger.error(f"暂停音乐失败: {str(e)} ❌")
            raise ToolError(f"暂停音乐失败: {str(e)} ❌")

    async def _next_song(self) -> Dict[str, Any]:
        """播放下一首歌曲 ⏭️"""
        try:
            # 使用快捷键 Ctrl+Alt+Right 切换到下一首
            logger.info("正在发送下一首命令(Ctrl+Alt+Right) ⏭️")
            pyautogui.hotkey('ctrl', 'alt', 'right')
            
            # 等待切换
            await asyncio.sleep(1.5)  # 增加等待时间
            
            # 尝试获取当前歌曲，但即使失败也返回成功
            try:
                song_info = await self._get_current_song()
                current_song = song_info.get("current_song", "未知")
            except:
                current_song = "无法获取当前歌曲信息"
            
            return {
                "success": True, 
                "message": "已切换到下一首歌曲 ⏭️",
                "current_song": current_song
            }
            
        except Exception as e:
            logger.error(f"下一首操作失败: {str(e)} ❌")
            raise ToolError(f"下一首操作失败: {str(e)} ❌")

    async def _previous_song(self) -> Dict[str, Any]:
        """播放上一首歌曲 ⏮️"""
        try:
            # 使用快捷键 Ctrl+Alt+Left 切换到上一首
            logger.info("正在发送上一首命令(Ctrl+Alt+Left) ⏮️")
            pyautogui.hotkey('ctrl', 'alt', 'left')
            
            # 等待切换
            await asyncio.sleep(1.5)  # 增加等待时间
            
            # 尝试获取当前歌曲，但即使失败也返回成功
            try:
                song_info = await self._get_current_song()
                current_song = song_info.get("current_song", "未知")
            except:
                current_song = "无法获取当前歌曲信息"
            
            return {
                "success": True, 
                "message": "已切换到上一首歌曲 ⏮️",
                "current_song": current_song
            }
            
        except Exception as e:
            logger.error(f"上一首操作失败: {str(e)} ❌")
            raise ToolError(f"上一首操作失败: {str(e)} ❌")

    async def _adjust_volume(self, volume_step: int) -> Dict[str, Any]:
        """调整音量大小 🔊"""
        try:
            # 确保音量步长在合理范围内
            volume_step = max(-100, min(100, volume_step))
            
            # 根据音量步长的正负决定是增加还是减少音量
            if volume_step > 0:
                # 增加音量，使用Ctrl+Alt+Up
                logger.info(f"正在增加音量 {volume_step}% 🔊")
                for _ in range(volume_step // 5 or 1):  # 每次调整约5%
                    pyautogui.hotkey('ctrl', 'alt', 'up')
                    await asyncio.sleep(0.2)  # 增加每次调整间的等待时间
                message = f"已增加音量 {volume_step}% 🔊"
            else:
                # 减少音量，使用Ctrl+Alt+Down
                logger.info(f"正在减少音量 {abs(volume_step)}% 🔉")
                for _ in range(abs(volume_step) // 5 or 1):  # 每次调整约5%
                    pyautogui.hotkey('ctrl', 'alt', 'down')
                    await asyncio.sleep(0.2)  # 增加每次调整间的等待时间
                message = f"已减少音量 {abs(volume_step)}% 🔉"
            
            # 最后等待一下，确保所有快捷键都被处理
            await asyncio.sleep(0.5)
            
            return {"success": True, "message": message}
            
        except Exception as e:
            logger.error(f"调整音量失败: {str(e)} ❌")
            raise ToolError(f"调整音量失败: {str(e)} ❌")

    async def _get_status(self) -> Dict[str, Any]:
        """获取QQ音乐当前状态 📊"""
        try:
            if not self._qqmusic_window:
                return {"success": False, "message": "QQ音乐未运行 ⚠️", "status": "未运行"}
            
            # 获取窗口标题，通常包含当前播放状态
            window_title = win32gui.GetWindowText(self._qqmusic_window)
            
            # 判断是否正在播放
            # 如果窗口标题包含歌曲名称，通常表示正在播放
            if window_title and window_title != "QQ音乐":
                status = "播放中"
            else:
                status = "已暂停或未播放"
            
            # 获取当前歌曲信息
            song_info = await self._get_current_song()
            
            return {
                "success": True,
                "status": status,
                "current_song": song_info.get("current_song", "未知"),
                "window_title": window_title
            }
            
        except Exception as e:
            logger.error(f"获取QQ音乐状态失败: {str(e)} ❌")
            return {"success": False, "error": str(e), "status": "未知"}

    async def _get_current_song(self) -> Dict[str, Any]:
        """获取当前播放的歌曲信息 🎵"""
        try:
            if not self._qqmusic_window:
                return {"success": False, "message": "QQ音乐未运行 ⚠️", "current_song": "未知"}
            
            # 获取窗口标题，通常包含当前歌曲名称
            window_title = win32gui.GetWindowText(self._qqmusic_window)
            
            # 解析窗口标题获取歌曲信息
            if window_title and window_title != "QQ音乐":
                # 窗口标题通常格式为 "歌曲名 - 歌手 - QQ音乐"
                parts = window_title.split(" - ")
                if len(parts) >= 2:
                    song_name = parts[0].strip()
                    artist = parts[1].strip()
                    current_song = f"{song_name} - {artist}"
                else:
                    current_song = window_title.replace("QQ音乐", "").strip()
            else:
                current_song = "未播放或无法获取"
            
            return {
                "success": True,
                "current_song": current_song,
                "window_title": window_title
            }
            
        except Exception as e:
            logger.error(f"获取当前歌曲信息失败: {str(e)} ❌")
            return {"success": False, "error": str(e), "current_song": "未知"}

    async def reset(self) -> Dict[str, Any]:
        """重置QQ音乐控制工具状态 🔄"""
        try:
            # 保存当前窗口句柄
            temp_window = self._qqmusic_window
            temp_last_active = self._last_active_window
            
            # 重置状态
            self._qqmusic_window = None
            self._last_active_window = None
            
            # 如果之前有活动窗口，尝试恢复
            if temp_last_active:
                try:
                    win32gui.SetForegroundWindow(temp_last_active)
                except:
                    pass
                    
            return {"success": True, "message": "QQ音乐控制工具已重置 ✅"}
            
        except Exception as e:
            logger.error(f"重置QQ音乐控制工具失败: {str(e)} ❌")