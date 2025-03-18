from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTextEdit, QGraphicsDropShadowEffect, QSizePolicy
from PyQt5.QtCore import Qt, QTimer, QRectF, QDateTime, QSize
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush, QPainterPath, QTextDocument

class MessageModule(QWidget):
    """自定义消息模块，用于在聊天区域显示结构化的消息"""
    def __init__(self, message, role="assistant", parent=None):
        super().__init__(parent)
        self.message = message
        self.role = role
        self.opacity = 0.0
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_opacity)
        self.animation_timer.start(30)
        self.init_ui()

    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)  # 增加内边距
        main_layout.setSpacing(8)  # 增加组件间距
        
        # 创建消息头部（显示角色和时间）
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)  # 增加头部组件间距
        
        # 角色图标和名称
        if self.role == "user":
            role_icon = "👤"
            role_name = "用户"
            role_color = "#4285f4"  # 蓝色
            bg_color = "#e6f2ff"    # 更鲜明的淡蓝色背景
            border_color = "#a6c8ff"  # 更明显的边框
        elif self.role == "system":
            role_icon = "🔔"
            role_name = "系统"
            role_color = "#fbbc05"  # 黄色
            bg_color = "#fff8e6"    # 更鲜明的淡黄色背景
            border_color = "#ffdb99"  # 更明显的边框
        else:  # assistant
            role_icon = "🪼"
            role_name = "OpenManus"
            role_color = "#34a853"  # 绿色
            bg_color = "#e6ffee"    # 更鲜明的淡绿色背景
            border_color = "#99e6b3"  # 更明显的边框
        
        # 创建角色标签
        role_label = QLabel(f"{role_icon} {role_name}")
        role_label.setFont(QFont('Alibaba-PuHuiTi-Medium', 11, QFont.Bold))  # 增大字体
        role_label.setStyleSheet(f"color: {role_color}; padding: 2px 5px;")
        
        # 创建时间标签
        time_label = QLabel(QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss"))
        time_label.setFont(QFont('Alibaba-PuHuiTi-Medium', 9))
        time_label.setStyleSheet("color: #606266;")  # 稍微深一点的颜色
        time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        header_layout.addWidget(role_label)
        header_layout.addWidget(time_label, 1)  # 时间标签占据剩余空间
        
        # 创建消息内容
        content_widget = QTextEdit()
        content_widget.setReadOnly(True)
        content_widget.setFont(QFont('Alibaba-PuHuiTi-Medium', 11))  # 增大字体
        
        # 格式化消息内容
        formatted_message = self.format_message(self.message)
        content_widget.setHtml(formatted_message)
        
        # 设置样式
        content_widget.setStyleSheet(
            f"background-color: {bg_color}; "
            f"border: 2px solid {border_color}; "  # 加粗边框
            "border-radius: 10px; "  # 增大圆角
            "padding: 12px;"  # 增加内边距
        )
        
        # 自动调整高度 - 改进的方法
        self.adjust_content_height(content_widget, formatted_message)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)  # 增大阴影模糊半径
        shadow.setColor(QColor(0, 0, 0, 50))  # 增加阴影不透明度
        shadow.setOffset(0, 3)  # 增大阴影偏移
        content_widget.setGraphicsEffect(shadow)
        
        main_layout.addLayout(header_layout)
        main_layout.addWidget(content_widget)
        
        # 设置整体样式
        self.setStyleSheet(
            f"background-color: white; "
            f"border-radius: 12px; "  # 增大圆角
            f"margin: 8px;"  # 增加外边距
        )
        
        # 设置初始透明度
        self.setWindowOpacity(self.opacity)
    
    def adjust_content_height(self, content_widget, formatted_message):
        """更精确地计算并调整内容区域的高度"""
        # 获取可用宽度（考虑内边距和滚动条）
        available_width = content_widget.viewport().width() - 30  # 减去内边距和滚动条宽度
        
        # 创建文档计算实际高度
        doc = QTextDocument()
        doc.setHtml(formatted_message)
        doc.setDefaultFont(content_widget.font())
        doc.setTextWidth(available_width)
        
        # 计算文档高度并添加额外空间
        doc_height = doc.size().height() + 40  # 添加额外空间用于内边距
        
        # 设置最小高度，确保短消息也有足够的显示空间
        min_height = max(int(doc_height), 80)
        
        # 根据内容设置合适的高度，但限制最大高度以避免过长
        if min_height > 600:  # 如果内容非常长
            content_widget.setMinimumHeight(600)  # 设置最大高度
            content_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 启用滚动条
        else:
            content_widget.setMinimumHeight(min_height)
            content_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁用滚动条
        
        # 设置大小调整策略
        content_widget.setSizePolicy(
            QSizePolicy.Expanding,  # 水平方向扩展
            QSizePolicy.Fixed       # 垂直方向固定
        )
        
        # 更新布局
        content_widget.updateGeometry()
    
    def format_message(self, message):
        """格式化消息内容，支持代码块和基本Markdown"""
        # 处理代码块
        if "```" in message:
            parts = message.split("```")
            formatted = parts[0]
            
            for i in range(1, len(parts), 2):
                if i < len(parts):
                    # 代码块
                    code = parts[i].strip()
                    if code:
                        # 检查是否有语言标识
                        if "\n" in code:
                            lang, code_content = code.split("\n", 1)
                            lang = lang.strip()
                        else:
                            lang = ""
                            code_content = code
                        
                        formatted += f"""
                        <div style="background-color: #282c34; color: #abb2bf; 
                                    border-radius: 5px; padding: 10px; margin: 10px 0; 
                                    font-family: 'Consolas', monospace; overflow-x: auto;">
                        <div style="color: #e5c07b; margin-bottom: 5px;">{lang}</div>
                        <pre style="margin: 0; white-space: pre-wrap;">{code_content}</pre>
                        </div>
                        """
                    
                    # 添加代码块后的文本
                    if i + 1 < len(parts):
                        formatted += parts[i + 1]
            
            return formatted
        
        # 处理普通文本，支持简单的换行
        return message.replace("\n", "<br>")
    
    def update_opacity(self):
        """更新透明度，实现淡入效果"""
        if self.opacity < 1.0:
            self.opacity += 0.1
            self.setWindowOpacity(self.opacity)
        else:
            self.animation_timer.stop()
    
    def paintEvent(self, event):
        """自定义绘制事件，添加边框和背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制圆角矩形背景
        path = QPainterPath()
        # 将QRect转换为QRectF
        rect_f = QRectF(self.rect())
        path.addRoundedRect(rect_f, 10, 10)
        
        # 根据角色选择不同的边框颜色
        if self.role == "user":
            border_color = QColor("#4285f4")  # 蓝色
        elif self.role == "system":
            border_color = QColor("#fbbc05")  # 黄色
        else:  # assistant
            border_color = QColor("#34a853")  # 绿色
        
        # 绘制边框
        painter.setPen(QPen(border_color, 1))
        painter.drawPath(path)
        
        # 绘制背景
        painter.fillPath(path, QBrush(QColor(255, 255, 255)))
    
    def sizeHint(self):
        """提供合适的尺寸提示，帮助布局管理器正确排列组件"""
        # 获取当前大小
        size = super().sizeHint()
        # 返回更合适的宽度
        return QSize(size.width(), size.height())