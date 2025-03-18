import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget,
                            QSplitter, QFrame, QListWidget, QFileDialog, QScrollArea, 
                            QGraphicsDropShadowEffect, QLineEdit)
from PyQt5.QtCore import Qt, QDateTime, QTimer, pyqtSlot
from PyQt5.QtGui import QFont, QIcon, QFontDatabase, QColor
from .components.buttons import AnimatedButton
from .components.message import MessageModule
from .workers.async_worker import AsyncWorker
from app.agent.manus import Manus
from app.logger import logger

class QuestManusGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # 获取资源绝对路径
        if getattr(sys, 'frozen', False):
            self.base_dir = sys._MEIPASS
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # 加载自定义字体
        font_id = QFontDatabase.addApplicationFont('app/GUI/config/font/DingTalk JinBuTi.ttf')
        if font_id < 0:
            logger.warning("无法加载阿里巴巴普惠体，将使用系统默认字体")
        # 设置应用图标
        app_icon = QIcon('app/GUI/config/icons/app.png')
        self.setWindowIcon(app_icon)
        # 初始化Agent实例
        self.agent = Manus()
        
        # 初始化界面
        self.init_ui()
        self.is_first_message = True
        self.history_records = []
        self.history_index = -1
        self.last_uploaded_file = None
        self.last_uploaded_type = None

        # 添加任务停止标记
        self.task_stopped_by_user = False

    def init_ui(self):
        # 设置窗口基本属性
        self.setWindowTitle('QuestManus AI 助手')
        self.setGeometry(100, 100, 1000, 700)
        
        # 设置窗口样式，增加立体感
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            QLabel {
                color: #333333;
            }
            QTextEdit, QLineEdit, QListWidget {
                border: 1px solid #dcdfe6;
                border-radius: 8px;
                background-color: white;
                selection-background-color: #4285f4;
                selection-color: white;
            }
            QSplitter::handle {
                background-color: transparent;
                width: 1px;
            }
            QStatusBar {
                background-color: #f8f9fa;
                color: #606266;
                border-top: 1px solid #dcdfe6;
            }
        """)
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)  # 增加间距
        
        # 创建水平分割器，用于分隔聊天区域和历史记录区域
        splitter = QSplitter(Qt.Horizontal)
        
        # 创建标题布局
        title_layout = QHBoxLayout()
        
        
        # 添加标题
        title_label = QLabel('🪼 QuestManus')
        title_font = QFont('DingTalk JinBuTi', 28, QFont.Bold) 
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label)
        title_layout.setAlignment(Qt.AlignCenter)
        
        main_layout.addLayout(title_layout)
        # 添加阴影效果
        title_shadow = QGraphicsDropShadowEffect()
        title_shadow.setBlurRadius(15)
        title_shadow.setColor(QColor(0, 0, 0, 50))
        title_shadow.setOffset(2, 2)
        title_label.setGraphicsEffect(title_shadow)
        main_layout.addWidget(title_label)
        
        # 添加副标题
        subtitle_label = QLabel('您的全能 AI 助手')
        subtitle_font = QFont('DingTalk Sans', 14) 
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle_label)
        
        # 添加分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #dcdfe6; min-height: 2px;")
        main_layout.addWidget(line)
        
        # 创建左侧面板（聊天区域）
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        
        chat_title = QLabel('对话区域')
        chat_title.setFont(QFont('Alibaba-PuHuiTi-Medium', 12, QFont.Bold))
        chat_title.setAlignment(Qt.AlignCenter)
        chat_layout.addWidget(chat_title)
        
        # 创建聊天区域
        self.chat_scroll_area = QScrollArea()
        self.chat_scroll_area.setWidgetResizable(True)
        self.chat_scroll_area.setStyleSheet(
            "background-color: #f8f9fa; border-radius: 8px; border: 1px solid #dcdfe6;"
        )
        
        # 创建容器widget来放置消息模块
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(15, 15, 15, 15)
        
        # 添加阴影效果
        chat_shadow = QGraphicsDropShadowEffect()
        chat_shadow.setBlurRadius(20)
        chat_shadow.setColor(QColor(0, 0, 0, 30))
        chat_shadow.setOffset(0, 2)
        self.chat_scroll_area.setGraphicsEffect(chat_shadow)
        
        # 设置滚动区域的widget
        self.chat_scroll_area.setWidget(self.chat_container)
        chat_layout.addWidget(self.chat_scroll_area)
        
        # 创建右侧面板（历史记录区域）
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_layout.setContentsMargins(0, 0, 0, 0)
        
        history_title = QLabel('历史记录')
        history_title.setFont(QFont('Alibaba-PuHuiTi-Medium', 12, QFont.Bold))
        history_title.setAlignment(Qt.AlignCenter)
        history_layout.addWidget(history_title)
        
        # 创建历史记录列表
        self.history_list = QListWidget()
        self.history_list.setFont(QFont('Alibaba-PuHuiTi-Medium', 9))
        self.history_list.setStyleSheet(
            "background-color: white; border-radius: 8px; padding: 10px; border: 1px solid #dcdfe6;"
        )
        # 添加阴影效果
        history_shadow = QGraphicsDropShadowEffect()
        history_shadow.setBlurRadius(20)
        history_shadow.setColor(QColor(0, 0, 0, 30))
        history_shadow.setOffset(0, 2)
        self.history_list.setGraphicsEffect(history_shadow)
        # 连接双击信号
        self.history_list.itemDoubleClicked.connect(self.load_history_item)
        history_layout.addWidget(self.history_list)
        
        # 添加到分割器
        splitter.addWidget(history_widget)
        splitter.addWidget(chat_widget)
        splitter.setSizes([300, 700])  # 设置初始大小比例
        
        main_layout.addWidget(splitter, stretch=1)
        
        # 创建输入区域
        input_layout = QHBoxLayout()
        
        # 添加文件上传按钮
        self.upload_file_button = AnimatedButton('📄')
        self.upload_file_button.setFont(QFont('Alibaba-PuHuiTi-Medium', 10, QFont.Bold))
        self.upload_file_button.setToolTip('上传文档文件')
        self.upload_file_button.clicked.connect(self.upload_file)
        
        # 添加图片上传按钮
        self.upload_image_button = AnimatedButton('🖼️')
        self.upload_image_button.setFont(QFont('Alibaba-PuHuiTi-Medium', 10, QFont.Bold))
        self.upload_image_button.setToolTip('上传图片')
        self.upload_image_button.clicked.connect(self.upload_image)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText('输入您的问题或任务...')
        self.input_field.setFont(QFont('Alibaba-PuHuiTi-Medium', 10))
        self.input_field.setStyleSheet(
            "padding: 12px; border: 1px solid #dcdfe6; border-radius: 8px; background-color: white;"
        )
        # 添加输入框阴影效果
        input_shadow = QGraphicsDropShadowEffect()
        input_shadow.setBlurRadius(15)
        input_shadow.setColor(QColor(0, 0, 0, 30))
        input_shadow.setOffset(0, 2)
        self.input_field.setGraphicsEffect(input_shadow)
        self.input_field.returnPressed.connect(self.send_prompt)
        # 安装事件过滤器以捕获上下键
        self.input_field.installEventFilter(self)
        
        # 使用自定义的AnimatedButton替代普通QPushButton
        self.action_button = AnimatedButton('发送')
        self.action_button.setFont(QFont('Alibaba-PuHuiTi-Medium', 10, QFont.Bold))
        self.action_button.clicked.connect(self.handle_action_button)
        
        # 设置按钮的不同状态样式
        self.action_button.send_style = (
            "background-color: #4285f4; color: white; padding: 8px 15px; "
            "border-radius: 5px; font-weight: bold; border: none; text-align: center;"
        )
        self.action_button.stop_style = (
            "background-color: #e74c3c; color: white; padding: 8px 15px; "
            "border-radius: 5px; font-weight: bold; border: none; text-align: center;"
        )
        self.action_button.hover_send_style = (
            "background-color: #5c9aff; color: white; padding: 8px 15px; "
            "border-radius: 5px; font-weight: bold; border: none; text-align: center;"
        )
        self.action_button.hover_stop_style = (
            "background-color: #c0392b; color: white; padding: 8px 15px; "
            "border-radius: 5px; font-weight: bold; border: none; text-align: center;"
        )
        
        # 初始化为发送模式
        self.action_button.default_style = self.action_button.send_style
        self.action_button.hover_style = self.action_button.hover_send_style
        self.action_button.is_send_mode = True
        self.action_button.update_style()
        
        input_layout.addWidget(self.upload_file_button)
        input_layout.addWidget(self.upload_image_button)
        input_layout.addWidget(self.input_field, stretch=4)
        input_layout.addWidget(self.action_button, stretch=1)
        
        main_layout.addLayout(input_layout)
        
        # 添加状态栏
        self.statusBar().showMessage('就绪')
        self.statusBar().setStyleSheet("padding: 5px; font-size: 12px;")
        
        # 显示欢迎信息
        welcome_msg = "欢迎使用 QuestManus AI 助手！请输入您的问题或任务，我将尽力帮助您。"
        self.add_message(welcome_msg, "system")
    
    def eventFilter(self, obj, event):
        """处理输入框的键盘事件，实现上下键浏览历史记录"""
        if obj is self.input_field and event.type() == event.KeyPress:
            # 只有当输入框为空时才处理上下键
            if self.input_field.text().strip() == "":
                key = event.key()
                if key == Qt.Key_Up:
                    self.navigate_history(direction="up")
                    return True
                elif key == Qt.Key_Down:
                    self.navigate_history(direction="down")
                    return True
        return super().eventFilter(obj, event)

    def add_message(self, content, role="assistant"):
        """添加新消息到聊天区域"""
        # 创建新的消息模块
        message_module = MessageModule(content, role)
        
        # 添加到布局
        self.chat_layout.addWidget(message_module)
        
        # 滚动到底部
        QTimer.singleShot(100, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        """滚动到聊天区域底部"""
        self.chat_scroll_area.verticalScrollBar().setValue(
            self.chat_scroll_area.verticalScrollBar().maximum()
        )
    
    def clear_chat(self):
        """清空聊天区域"""
        # 移除所有消息模块
        while self.chat_layout.count():
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def upload_file(self):
        """上传文档文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择文档文件", 
            "", 
            "文本文件 (*.txt);;Python文件 (*.py);;所有文件 (*.*)"
        )
        
        if file_path:
            # 获取文件名
            file_name = os.path.basename(file_path)
            # 在输入框中添加文件路径提示
            current_text = self.input_field.text()
            if current_text and not current_text.endswith(" "):
                current_text += " "
            self.input_field.setText(f"{current_text}[已上传文档: {file_name}] ")
            self.input_field.setFocus()
            # 将光标移到末尾
            self.input_field.setCursorPosition(len(self.input_field.text()))
            
            # 存储文件路径供后续处理
            self.last_uploaded_file = file_path
            self.last_uploaded_type = "document"
            
            # 在状态栏显示提示
            self.statusBar().showMessage(f'已上传文档: {file_name}')
    
    def upload_image(self):
        """上传图片文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择图片", 
            "", 
            "图片文件 (*.jpg *.jpeg *.png *.gif *.bmp *.webp);;所有文件 (*.*)"
        )
        
        if file_path:
            # 获取文件名
            file_name = os.path.basename(file_path)
            # 在输入框中添加文件路径提示
            current_text = self.input_field.text()
            if current_text and not current_text.endswith(" "):
                current_text += " "
            self.input_field.setText(f"{current_text}[已上传图片: {file_name}] ")
            self.input_field.setFocus()
            # 将光标移到末尾
            self.input_field.setCursorPosition(len(self.input_field.text()))
            
            # 存储文件路径供后续处理
            self.last_uploaded_file = file_path
            self.last_uploaded_type = "image"
            
            # 在状态栏显示提示
            self.statusBar().showMessage(f'已上传图片: {file_name}')

    def navigate_history(self, direction):
        """根据方向在历史记录中导航"""
        if not self.history_records:
            return
            
        if direction == "up":
            # 向上浏览历史记录（更早的记录）
            if self.history_index < len(self.history_records) - 1:
                self.history_index += 1
        else:  # direction == "down"
            # 向下浏览历史记录（更新的记录）
            if self.history_index > 0:
                self.history_index -= 1
            elif self.history_index == 0:
                # 如果已经到最新的记录，则清空输入框并重置索引
                self.history_index = -1
                self.input_field.clear()
                return

        if 0 <= self.history_index < len(self.history_records):
            # 提取历史记录中的问题部分（去除时间戳）
            history_item = self.history_records[len(self.history_records) - 1 - self.history_index]
            question = history_item.split(" - ", 1)[1] if " - " in history_item else history_item
            self.input_field.setText(question)
            # 将光标移到末尾
            self.input_field.setCursorPosition(len(question))

    def load_history_item(self, item):
        """双击历史记录项时加载到输入框"""
        text = item.text()
        # 提取问题部分（去除时间戳）
        question = text.split(" - ", 1)[1] if " - " in text else text
        self.input_field.setText(question)
        self.input_field.setFocus()
        # 将光标移到末尾
        self.input_field.setCursorPosition(len(question))

    def send_prompt(self):
        prompt = self.input_field.text().strip()
        if not prompt:
            return
        
        # 处理上传的文件
        has_uploaded_file = False
        file_info = ""
        
        if self.last_uploaded_file and self.last_uploaded_type:
            has_uploaded_file = True
            file_path = self.last_uploaded_file
            file_name = os.path.basename(file_path)
            file_info = f"\n[已上传{self.last_uploaded_type}: {file_name}，路径: {file_path}]"
            
            # 修改提示，添加文件处理指令
            if self.last_uploaded_type == "image":
                # 从提示中移除上传图片的标记
                prompt = prompt.replace(f"[已上传图片: {file_name}] ", "").replace(f"[已上传图片: {file_name}]", "")
                # 添加图片处理指令
                prompt = f"请使用MediaProcessTool处理这张图片: {file_path}。{prompt}"
            else:  # document
                # 从提示中移除上传文档的标记
                prompt = prompt.replace(f"[已上传文档: {file_name}] ", "").replace(f"[已上传文档: {file_name}]", "")
                # 添加文档处理指令
                prompt = f"请使用MediaProcessTool处理这个文档: {file_path}。{prompt}"
            
        # 清空输入框
        self.input_field.clear()
        # 重置历史浏览索引
        self.history_index = -1
        
        # 获取当前时间
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        
        # 添加到历史记录
        history_item = f"{current_time} - {prompt}"
        self.history_records.append(history_item)
        self.update_history_list()
        
        # 如果不是第一条发送消息，则清除上一次的聊天内容
        if not self.is_first_message:
            self.clear_chat()
            # 添加欢迎消息
            welcome_msg = "欢迎使用 QuestManus AI 助手！请输入您的问题或任务，我将尽力帮助您。"
            self.add_message(welcome_msg, "system")
        else:
            self.is_first_message = False
        
        # 显示用户输入
        display_prompt = prompt
        if file_info:
            display_prompt += file_info
        self.add_message(display_prompt, "user")
        
        # 显示处理中信息
        self.add_message("正在处理您的请求...", "assistant")
        self.statusBar().showMessage('处理中...')
        
        # 禁用输入，切换按钮为停止模式
        self.input_field.setEnabled(False)
        self.set_button_mode(is_send_mode=False)
        
        # 禁用上传按钮
        self.upload_file_button.setEnabled(False)
        self.upload_image_button.setEnabled(False)

        # 设置按钮为处理状态
        self.action_button.set_processing(True)
        
        # 创建并启动工作线程
        self.worker = AsyncWorker(self.agent, prompt)
        self.worker.result_ready.connect(self.handle_result)
        self.worker.log_ready.connect(self.handle_log)  # 连接日志信号
        self.worker.start()
        
        # 重置上传文件状态
        self.last_uploaded_file = None
        self.last_uploaded_type = None

    def stop_execution(self):
        """停止当前正在执行的任务"""
        if hasattr(self, 'worker') and self.worker.isRunning():
            # 调用worker的stop方法
            self.worker.stop()
            # 重置代理状态为IDLE
            from app.schema import AgentState
            self.agent.state = AgentState.IDLE
            self.agent.current_step = 0
            # 禁用按钮，防止多次点击
            self.action_button.setEnabled(False)
            self.statusBar().showMessage('正在停止...')
            
            # 添加定时器，确保在停止处理完成后重新启用按钮并切换回发送模式
            QTimer.singleShot(1000, self.reset_after_stop)
            
            # 添加标记，表示任务已被用户主动停止
            self.task_stopped_by_user = True

    def handle_action_button(self):
        """处理动作按钮点击，根据当前模式执行发送或停止操作"""
        if self.action_button.is_send_mode:
            self.send_prompt()
        else:
            self.stop_execution()
    
    def set_button_mode(self, is_send_mode):
        """切换按钮模式"""
        if is_send_mode:
            # 切换到发送模式
            self.action_button.setText('发送')
            self.action_button.default_style = self.action_button.send_style
            self.action_button.hover_style = self.action_button.hover_send_style
            self.action_button.is_send_mode = True
        else:
            # 切换到停止模式
            self.action_button.setText('停止')
            self.action_button.default_style = self.action_button.stop_style
            self.action_button.hover_style = self.action_button.hover_stop_style
            self.action_button.is_send_mode = False
        
        self.action_button.update_style()

    @pyqtSlot(str)
    def handle_result(self, result):
        """处理代理返回的结果"""
        # 移除处理中的消息
        if self.chat_layout.count() > 0:
            last_item = self.chat_layout.itemAt(self.chat_layout.count() - 1)
            if last_item and last_item.widget():
                last_item.widget().deleteLater()
        
        # 显示结果
        self.add_message(result, "assistant")
        
        # 滚动到底部
        # 修正这里：将 chat_area 改为 chat_scroll_area
        self.chat_scroll_area.verticalScrollBar().setValue(
            self.chat_scroll_area.verticalScrollBar().maximum()
        )
        
        # 恢复状态
        self.statusBar().showMessage('就绪')
        self.input_field.setEnabled(True)
        
        # 切换回发送模式并启用按钮
        self.set_button_mode(is_send_mode=True)
        self.action_button.setEnabled(True)
        
        # 启用上传按钮
        self.upload_file_button.setEnabled(True)
        self.upload_image_button.setEnabled(True)
        
        # 取消按钮的处理状态
        self.action_button.set_processing(False)
        
        self.input_field.setFocus()

    @pyqtSlot(str)
    def handle_log(self, log_text):
        """处理日志信息"""
        # 格式化日志信息，使其更加明显
        formatted_log = f"📋 系统日志: {log_text}"
        # 显示日志信息
        self.add_message(formatted_log, "system")
        
        # 确保滚动到最新消息
        self.scroll_to_bottom()
    
    def update_history_list(self):
        """更新历史记录列表"""
        self.history_list.clear()
        for item in self.history_records:
            self.history_list.addItem(item)
        
        # 滚动到底部
        if self.history_list.count() > 0:
            self.history_list.scrollToItem(self.history_list.item(self.history_list.count() - 1))
        
        # 修正这里：将 chat_area 改为 chat_scroll_area
        self.chat_scroll_area.verticalScrollBar().setValue(
            self.chat_scroll_area.verticalScrollBar().maximum()
        )

    def reset_after_stop(self):
        """停止操作完成后重置界面状态"""
        # 重新启用按钮
        self.action_button.setEnabled(True)
        # 切换回发送模式
        self.set_button_mode(True)
        # 更新状态栏
        self.statusBar().showMessage('已停止执行，可以发送新的指令')
        # 清理可能正在运行的工具
        self.cleanup_running_tools()
        
        # 添加一条系统消息，表示任务已被停止
        if hasattr(self, 'task_stopped_by_user') and self.task_stopped_by_user:
            self.add_message("任务已被用户停止，可以发送新的指令。", role="system")
            self.task_stopped_by_user = False
        
    def cleanup_running_tools(self):
        """清理可能正在运行的工具"""
        try:
            # 尝试关闭或重置正在使用的工具
            if hasattr(self.agent, 'tools') and self.agent.tools:
                for tool_name, tool in self.agent.tools.items():
                    # 对于QQ音乐控制工具，调用reset方法
                    if tool_name == "qqmusic_control" and hasattr(tool, 'reset'):
                        asyncio.run(tool.reset())
                        logger.info("已重置QQ音乐控制工具状态")
                    
                    # 对于其他可能需要清理的工具，可以在这里添加相应的处理逻辑
                    # 例如微信工具等
                    if tool_name in ["wechat_message", "wechat_official_account"] and hasattr(tool, '_last_active_window'):
                        tool._wechat_window = None
                        tool._last_active_window = None
                        logger.info(f"已重置{tool_name}工具状态")
                    
                    # 对于bash工具，调用stop方法
                    if tool_name == "bash" and hasattr(tool, 'stop'):
                        tool.stop()
                        logger.info("已停止bash会话")
        except Exception as e:
            logger.error(f"清理工具时出错: {str(e)}")