"""计算器工具，用于控制Windows计算器应用程序"""
import asyncio
import os
import subprocess
import time
from typing import Any, Dict, Literal, Optional

import pyautogui
import pyperclip
import win32con
import win32gui

from app.exceptions import ToolError
from app.logger import get_logger
from app.tool.base import BaseTool, ToolResult

logger = get_logger(__name__)

class CalculatorTool(BaseTool):
    """计算器工具，用于控制Windows计算器应用程序 🧮"""

    name: str = "calculator"
    description: str = "控制Windows计算器应用程序，执行数学计算、科学计算等功能 🔢"
    parameters: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "要执行的操作类型",
                "enum": ["open", "close", "calculate", "switch_mode", "get_result", "clear"],
            },
            "expression": {
                "type": "string",
                "description": "要计算的表达式，例如 '1+2*3'",
            },
            "mode": {
                "type": "string",
                "description": "计算器模式",
                "enum": ["standard", "scientific", "programmer", "date"],
            },
        },
        "required": ["action"],
    }

    _calculator_window: Optional[int] = None
    _last_active_window: Optional[int] = None
    _last_result: Optional[str] = None

    def __init__(self):
        """初始化计算器工具 🚀"""
        super().__init__()
        self._calculator_window = None
        self._last_active_window = None
        self._last_result = None

    async def execute(
        self,
        *,
        action: Literal["open", "close", "calculate", "switch_mode", "get_result", "clear"],
        expression: Optional[str] = None,
        mode: Optional[Literal["standard", "scientific", "programmer", "date"]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        执行计算器操作 🔄
        
        Args:
            action: 要执行的操作类型
            expression: 要计算的表达式
            mode: 计算器模式
            
        Returns:
            操作结果
        """
        try:
            # 保存当前活动窗口，以便操作完成后恢复
            self._last_active_window = win32gui.GetForegroundWindow()
            
            # 根据操作类型执行相应功能
            if action == "open":
                return await self._open_calculator()
                
            # 检查计算器是否已启动（除了open操作外的所有操作都需要计算器已启动）
            if action != "open":
                await self._ensure_calculator_running()
            
            if action == "close":
                return await self._close_calculator()
                
            elif action == "calculate":
                if not expression:
                    raise ToolError("计算操作需要提供表达式 ❌")
                return await self._calculate(expression)
                
            elif action == "switch_mode":
                if not mode:
                    raise ToolError("切换模式需要提供目标模式 ❌")
                return await self._switch_mode(mode)
                
            elif action == "get_result":
                return await self._get_result()
                
            elif action == "clear":
                return await self._clear()
                
            else:
                raise ToolError(f"不支持的操作: {action} ❌")
                
        except Exception as e:
            logger.error(f"计算器操作失败: {str(e)} ❌")
            return {"success": False, "error": str(e)}
        finally:
            # 恢复之前的活动窗口
            if self._last_active_window:
                try:
                    win32gui.SetForegroundWindow(self._last_active_window)
                except:
                    pass

    async def _ensure_calculator_running(self) -> None:
        """确保计算器应用程序正在运行 🔍"""
        # 查找计算器窗口
        self._calculator_window = win32gui.FindWindow("ApplicationFrameWindow", "计算器")
        
        if not self._calculator_window:
            # 尝试启动计算器
            logger.info("计算器未运行，尝试启动计算器应用程序 🚀")
            await self._open_calculator()
            
            # 等待计算器启动
            for _ in range(5):
                await asyncio.sleep(1)
                self._calculator_window = win32gui.FindWindow("ApplicationFrameWindow", "计算器")
                if self._calculator_window:
                    break
            else:
                raise ToolError("计算器启动超时 ⏱️")
        
        # 激活计算器窗口
        win32gui.ShowWindow(self._calculator_window, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(self._calculator_window)
        await asyncio.sleep(0.5)  # 等待窗口激活

    async def _open_calculator(self) -> Dict[str, Any]:
        """
        打开计算器应用程序 📱
        
        Returns:
            打开结果
        """
        try:
            # 检查计算器是否已经运行
            existing_window = win32gui.FindWindow("ApplicationFrameWindow", "计算器")
            if existing_window:
                self._calculator_window = existing_window
                win32gui.ShowWindow(existing_window, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(existing_window)
                return {
                    "success": True,
                    "message": "计算器已经在运行，已切换到计算器窗口 ✅"
                }
            
            # 启动计算器
            subprocess.Popen("calc.exe")
            
            # 等待计算器启动
            for _ in range(5):
                await asyncio.sleep(1)
                self._calculator_window = win32gui.FindWindow("ApplicationFrameWindow", "计算器")
                if self._calculator_window:
                    break
            else:
                raise ToolError("计算器启动超时 ⏱️")
            
            return {
                "success": True,
                "message": "计算器已成功启动 ✅"
            }
        except Exception as e:
            raise ToolError(f"启动计算器失败: {str(e)} ❌")

    async def _close_calculator(self) -> Dict[str, Any]:
        """
        关闭计算器应用程序 🚪
        
        Returns:
            关闭结果
        """
        if not self._calculator_window:
            return {
                "success": True,
                "message": "计算器未运行 ℹ️"
            }
        
        # 激活计算器窗口
        win32gui.SetForegroundWindow(self._calculator_window)
        await asyncio.sleep(0.3)
        
        # 发送Alt+F4关闭窗口
        pyautogui.hotkey('alt', 'f4')
        await asyncio.sleep(0.5)
        
        self._calculator_window = None
        self._last_result = None
        
        return {
            "success": True,
            "message": "计算器已关闭 ✅"
        }

    async def _calculate(self, expression: str) -> Dict[str, Any]:
        """
        执行计算表达式 🔢
        
        Args:
            expression: 要计算的表达式
            
        Returns:
            计算结果
        """
        # 激活计算器窗口
        win32gui.SetForegroundWindow(self._calculator_window)
        await asyncio.sleep(0.3)
        
        # 清除之前的计算
        await self._clear()
        
        # 输入表达式
        for char in expression:
            if char == '+':
                pyautogui.press('+')
            elif char == '-':
                pyautogui.press('-')
            elif char == '*':
                pyautogui.press('*')
            elif char == '/':
                pyautogui.press('/')
            elif char == '(':
                pyautogui.press('(')
            elif char == ')':
                pyautogui.press(')')
            elif char == '.':
                pyautogui.press('.')
            elif char == '^':
                # 在标准计算器中没有直接的^键，可能需要切换到科学计算器
                await self._switch_mode("scientific")
                pyautogui.hotkey('shift', '6')  # 输入^符号
            elif char.isdigit():
                pyautogui.press(char)
            elif char.isspace():
                continue  # 忽略空格
            else:
                logger.warning(f"忽略不支持的字符: {char}")
            
            await asyncio.sleep(0.1)
        
        # 按下等号获取结果
        pyautogui.press('enter')
        await asyncio.sleep(0.5)
        
        # 获取结果
        result = await self._get_result()
        
        return {
            "success": True,
            "expression": expression,
            "result": result.get("result", "未知"),
            "message": f"计算完成: {expression} = {result.get('result', '未知')} ✅"
        }

    async def _switch_mode(self, mode: str) -> Dict[str, Any]:
        """
        切换计算器模式 🔄
        
        Args:
            mode: 目标模式
            
        Returns:
            切换结果
        """
        # 激活计算器窗口
        win32gui.SetForegroundWindow(self._calculator_window)
        await asyncio.sleep(0.3)
        
        # 打开菜单
        pyautogui.hotkey('alt')
        await asyncio.sleep(0.3)
        
        # 根据模式选择相应选项
        if mode == "standard":
            pyautogui.press('1')
        elif mode == "scientific":
            pyautogui.press('2')
        elif mode == "programmer":
            pyautogui.press('3')
        elif mode == "date":
            pyautogui.press('4')
        else:
            return {
                "success": False,
                "error": f"不支持的模式: {mode} ❌"
            }
        
        await asyncio.sleep(0.5)
        
        return {
            "success": True,
            "message": f"已切换到{mode}模式 ✅"
        }

    async def _get_result(self) -> Dict[str, Any]:
        """
        获取计算结果 📊
        
        Returns:
            当前计算结果
        """
        # 激活计算器窗口
        win32gui.SetForegroundWindow(self._calculator_window)
        await asyncio.sleep(0.3)
        
        # 复制结果到剪贴板
        pyautogui.hotkey('ctrl', 'c')
        await asyncio.sleep(0.3)
        
        # 从剪贴板获取结果
        result = pyperclip.paste()
        
        # 保存最后一次结果
        self._last_result = result
        
        return {
            "success": True,
            "result": result,
            "message": f"当前计算结果: {result} ✅"
        }

    async def _clear(self) -> Dict[str, Any]:
        """
        清除计算器 🧹
        
        Returns:
            清除结果
        """
        # 激活计算器窗口
        win32gui.SetForegroundWindow(self._calculator_window)
        await asyncio.sleep(0.3)
        
        # 按ESC键清除当前输入
        pyautogui.press('escape')
        await asyncio.sleep(0.2)
        
        # 再按一次清除所有
        pyautogui.press('escape')
        await asyncio.sleep(0.2)
        
        self._last_result = None
        
        return {
            "success": True,
            "message": "计算器已清除 ✅"
        }