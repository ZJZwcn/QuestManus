import asyncio
from PyQt5.QtCore import QThread, pyqtSignal
from app.logger import logger, _logger

class AsyncWorker(QThread):
    result_ready = pyqtSignal(str)
    log_ready = pyqtSignal(str)

    def __init__(self, agent, prompt):
        super().__init__()
        self.agent = agent
        self.prompt = prompt
        self.is_running = True

    # 保持原有工作线程的其他方法不变（run、stop等）
    # [此处保留原始AsyncWorker类的完整实现，因篇幅限制省略具体方法]
    def run(self):
        # 重定向logger输出到我们的信号
        from app.logger import logger, _logger
        
        # 创建一个自定义的sink来捕获日志
        def log_sink(message):
            record = message.record
            if record["level"].name in ["INFO", "WARNING", "ERROR", "CRITICAL"]:
                # 提取时间并格式化
                time_str = record["time"].strftime("%Y-%m-%d %H:%M:%S")
                # 获取消息内容
                msg = record["message"]
                
                # 过滤掉大模型的回答内容，只保留操作语句
                # 通常大模型回答较长且包含特定格式，这里简单过滤
                if len(msg) < 200 and not msg.startswith("{") and not "```" in msg:
                    # 只显示时间和消息内容
                    log_text = f"[{time_str}] {msg}"
                    self.log_ready.emit(log_text)
        
        # 添加自定义sink到logger
        log_id = _logger.add(log_sink, level="INFO")
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 创建一个Future对象用于取消任务
            self.task = asyncio.ensure_future(self.agent.run(self.prompt), loop=loop)
            
            # 运行任务直到完成或被取消
            while not self.task.done() and self.is_running:
                loop.run_until_complete(asyncio.sleep(0.1))
                
            # 如果任务被取消
            if not self.is_running and not self.task.done():
                self.task.cancel()
                self.result_ready.emit("任务已被用户取消")
                self.log_ready.emit("[系统] 任务已被用户手动停止")
            elif self.task.done():
                # 获取任务结果
                result = self.task.result()
                self.result_ready.emit("任务已完成")
            
            loop.close()
        except asyncio.CancelledError:
            self.result_ready.emit("任务已被用户取消")
            self.log_ready.emit("[系统] 任务已被用户手动停止")
        except Exception as e:
            self.result_ready.emit(f"任务执行出错: {str(e)}")
            self.log_ready.emit(f"[系统] 任务执行出错: {str(e)}")
        finally:
            # 移除自定义sink
            _logger.remove(log_id)
    
    def stop(self):
        """停止当前任务执行"""
        self._stop_requested = True
        # 确保代理状态被重置
        from app.schema import AgentState
        if hasattr(self, 'agent') and self.agent:
            self.agent.state = AgentState.IDLE
            self.agent.current_step = 0
            
            # 尝试中断正在执行的任务
            if hasattr(self.agent, 'current_task') and self.agent.current_task:
                try:
                    # 取消当前任务
                    if hasattr(self.agent.current_task, 'cancel'):
                        self.agent.current_task.cancel()
                    self.agent.current_task = None
                except Exception as e:
                    logger.error(f"取消任务时出错: {str(e)}")
            
            # 清理代理的工具状态
            if hasattr(self.agent, 'tools'):
                for tool_name, tool in self.agent.tools.items():
                    if hasattr(tool, '_reset_state'):
                        try:
                            tool._reset_state()
                        except:
                            pass
                    
        # 发出任务已停止的信号
        self.log_ready.emit("系统: 任务已被用户停止")