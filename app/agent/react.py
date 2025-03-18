from abc import ABC, abstractmethod
from typing import Optional

from pydantic import Field

from app.agent.base import BaseAgent
from app.llm import LLM
from app.schema import AgentState, Memory


class ReActAgent(BaseAgent, ABC):
    name: str
    description: Optional[str] = None

    system_prompt: Optional[str] = None
    next_step_prompt: Optional[str] = None

    llm: Optional[LLM] = Field(default_factory=LLM)
    memory: Memory = Field(default_factory=Memory)
    state: AgentState = AgentState.IDLE

    max_steps: int = 10
    current_step: int = 0

    @abstractmethod
    async def think(self) -> bool:
        """处理当前状态并决定下一步行动 🤔"""

    @abstractmethod
    async def act(self) -> str:
        """执行已决定的行动 🏃"""

    async def step(self) -> str:
        """执行单个步骤：思考和行动 🔄"""
        should_act = await self.think()
        if not should_act:
            return "思考完成 - 无需采取行动 ✅"
        return await self.act()
