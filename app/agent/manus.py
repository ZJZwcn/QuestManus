from pydantic import Field


from app.agent.toolcall import ToolCallAgent
from app.prompt.manus import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.tool import Terminate, ToolCollection
from app.tool.browser_use_tool import BrowserUseTool
from app.tool.file_saver import FileSaver
from app.tool.python_execute import PythonExecute
from app.tool.baidu_search import BaiduSearch
from app.tool.wechat_message import WeChatMessage
from app.tool.wechat_official_account import WeChatOfficialAccount
from app.tool.edge_search import EdgeBrowser
from app.tool.math_tool import CalculatorTool
from app.tool.system_operation import SystemOperationTool
from app.tool.media_process import MediaProcessTool
from app.tool.Redbook_summarize import RedbookSummarize
from app.tool.app_launcher import AppLauncher
from app.tool.qqmusic_control import QQMusicControl


class Manus(ToolCallAgent):
    """
    一个用于解决各种任务的多功能通用代理 🌟

    该代理扩展了PlanningAgent，具有全面的工具和功能集，
    包括Python执行、网页浏览、文件操作和信息检索，
    能够处理各种用户请求 🛠️
    """

    name: str = "Manus"
    description: str = (
        "一个能够使用多种工具解决各种任务的多功能代理 🧰"
    )

    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT

    # 向工具集合中添加通用工具
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            PythonExecute(), BrowserUseTool(), FileSaver(), Terminate(), BaiduSearch(), AppLauncher(),
            WeChatMessage(), WeChatOfficialAccount(), QQMusicControl(),
            EdgeBrowser(), CalculatorTool(), SystemOperationTool(),  MediaProcessTool(), RedbookSummarize()
        )
    )

    max_steps: int = 20