from PyQt5.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt5.QtCore import QPoint, QPropertyAnimation, QSize, QEasingCurve, QTimer, QRectF, Qt
from PyQt5.QtGui import (QColor, QPainter, QPen, QBrush, QLinearGradient,  
                         QRadialGradient, QPainterPath, QImage, QPainterPathStroker)
import math

class AnimatedButton(QPushButton):
    """支持悬停动画和炫彩效果的自定义按钮"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMouseTracking(True)
        self.hovered = False
        self.processing = False
        self.mouse_pos = QPoint(0, 0)
        self.color_timer = QTimer(self)
        self.color_timer.timeout.connect(self.update_color)
        self.color_timer.start(30)
        self.color_offset = 0
        self.default_style = ""
        self.hover_style = ""
        self.processing_style = ""
        self.setFixedHeight(40)

        # 阴影效果
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.shadow.setOffset(3, 3)
        self.setGraphicsEffect(self.shadow)

        # 动画设置
        self.animation = QPropertyAnimation(self, b"size")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.update_style()

    def update_style(self):
        """更新按钮样式"""
        self.default_style = (
            "background-color: #4285f4; color: white; padding: 8px 15px; "
            "border-radius: 5px; font-weight: bold; border: none; text-align: center;"
        )
        self.hover_style = (
            "background-color: #5c9aff; color: white; padding: 8px 15px; "
            "border-radius: 5px; font-weight: bold; border: none; text-align: center;"
        )
        self.processing_style = (
            "background-color: #ff7043; color: white; padding: 8px 15px; "
            "border-radius: 5px; font-weight: bold; border: none; text-align: center;"
        )
        self.setStyleSheet(self.default_style)

    def set_processing(self, is_processing):
        """设置处理状态"""
        self.processing = is_processing
        if is_processing:
            self.setStyleSheet(self.processing_style)
            original_size = self.size()
            new_size = QSize(int(original_size.width() * 1.15), 
                            int(original_size.height() * 1.15))
            original_pos = self.pos()
            width_diff = new_size.width() - original_size.width()
            height_diff = new_size.height() - original_size.height()
            new_pos = QPoint(original_pos.x() - width_diff // 2, 
                            original_pos.y() - height_diff // 2)
            
            self.animation.setStartValue(original_size)
            self.animation.setEndValue(new_size)
            
            self.pos_animation = QPropertyAnimation(self, b"pos")
            self.pos_animation.setDuration(200)
            self.pos_animation.setEasingCurve(QEasingCurve.OutCubic)
            self.pos_animation.setStartValue(original_pos)
            self.pos_animation.setEndValue(new_pos)
            
            self.animation.start()
            self.pos_animation.start()
            self.shadow.setBlurRadius(30)
            self.shadow.setColor(QColor(0, 0, 0, 150))
        else:
            self.setStyleSheet(self.default_style)
            current_size = self.size()
            current_pos = self.pos()
            original_size = QSize(int(current_size.width() / 1.15), int(current_size.height() / 1.15))
            
            width_diff = current_size.width() - original_size.width()
            height_diff = current_size.height() - original_size.height()
            original_pos = QPoint(current_pos.x() + width_diff // 2, current_pos.y() + height_diff // 2)
            
            self.animation.setStartValue(current_size)
            self.animation.setEndValue(original_size)
            
            self.pos_animation = QPropertyAnimation(self, b"pos")
            self.pos_animation.setDuration(200)
            self.pos_animation.setEasingCurve(QEasingCurve.OutCubic)
            self.pos_animation.setStartValue(current_pos)
            self.pos_animation.setEndValue(original_pos)
            
            self.animation.start()
            self.pos_animation.start()
            self.shadow.setBlurRadius(15)
            self.shadow.setColor(QColor(0, 0, 0, 80))
        self.update()

    def update_color(self):
        """更新颜色效果"""
        if self.hovered or self.processing:
            self.color_offset = (self.color_offset + 5) % 360
            self.update()

    def enterEvent(self, event):
        self.hovered = True
        original_size = self.size()
        new_size = QSize(int(original_size.width() * 1.15), 
                       int(original_size.height() * 1.15))
        original_pos = self.pos()
        width_diff = new_size.width() - original_size.width()
        height_diff = new_size.height() - original_size.height()
        new_pos = QPoint(original_pos.x() - width_diff // 2, 
                        original_pos.y() - height_diff // 2)
        
        self.animation.setStartValue(original_size)
        self.animation.setEndValue(new_size)
        
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setDuration(200)
        self.pos_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.pos_animation.setStartValue(original_pos)
        self.pos_animation.setEndValue(new_pos)
        
        self.animation.start()
        self.pos_animation.start()
        self.setStyleSheet(self.hover_style)
        self.shadow.setBlurRadius(30)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hovered = False
        current_size = self.size()
        current_pos = self.pos()
        original_size = QSize(int(current_size.width() / 1.15), int(current_size.height() / 1.15))
        
        width_diff = current_size.width() - original_size.width()
        height_diff = current_size.height() - original_size.height()
        original_pos = QPoint(current_pos.x() + width_diff // 2, current_pos.y() + height_diff // 2)
        
        self.animation.setStartValue(current_size)
        self.animation.setEndValue(original_size)
        
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setDuration(200)
        self.pos_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.pos_animation.setStartValue(current_pos)
        self.pos_animation.setEndValue(original_pos)
        
        self.animation.start()
        self.pos_animation.start()
        self.setStyleSheet(self.default_style)
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        super().leaveEvent(event)

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.pos()
        self.update()
        super().mouseMoveEvent(event)

    def paintEvent(self, event):
        if self.hovered or self.processing:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            super().paintEvent(event)
            
            buffer = QImage(self.size(), QImage.Format_ARGB32_Premultiplied)
            buffer.fill(Qt.transparent)
            temp_painter = QPainter(buffer)
            temp_painter.setRenderHint(QPainter.Antialiasing)
            
            radial_gradient = QLinearGradient(0, 0, self.width(), self.height())
            if self.processing:
                radial_gradient.setColorAt(0, QColor.fromHsv((self.color_offset + 0) % 360, 255, 255, 150))
                radial_gradient.setColorAt(0.5, QColor.fromHsv((self.color_offset + 30) % 360, 255, 255, 100))
                radial_gradient.setColorAt(1, QColor.fromHsv((self.color_offset + 60) % 360, 255, 255, 50))
            else:
                radial_gradient.setColorAt(0, QColor.fromHsv((self.color_offset + 240) % 360, 255, 255, 150))
                radial_gradient.setColorAt(0.5, QColor.fromHsv((self.color_offset + 120) % 360, 255, 255, 100))
                radial_gradient.setColorAt(1, QColor.fromHsv(self.color_offset % 360, 255, 255, 50))
            
            temp_painter.setPen(Qt.NoPen)
            temp_painter.setBrush(QBrush(radial_gradient))
            temp_painter.drawRoundedRect(0, 0, self.width(), self.height(), 5, 5)
            
            path = QPainterPath()
            if self.processing:
                mouse_x = self.width() // 2
                mouse_y = self.height() // 2
            else:
                mouse_x = self.mouse_pos.x()
                mouse_y = self.mouse_pos.y()
            radius = 40
            
            angle = (self.color_offset * 2) % 360
            ctrl1_x = mouse_x + radius * 1.5 * math.cos(math.radians(angle))
            ctrl1_y = mouse_y + radius * 1.5 * math.sin(math.radians(angle))
            ctrl2_x = mouse_x + radius * 1.5 * math.cos(math.radians(angle + 120))
            ctrl2_y = mouse_y + radius * 1.5 * math.sin(math.radians(angle + 120))
            ctrl3_x = mouse_x + radius * 1.5 * math.cos(math.radians(angle + 240))
            ctrl3_y = mouse_y + radius * 1.5 * math.sin(math.radians(angle + 240))
            
            path.moveTo(mouse_x + radius, mouse_y)
            path.cubicTo(ctrl1_x, ctrl1_y, ctrl2_x, ctrl2_y, mouse_x, mouse_y + radius)
            path.cubicTo(ctrl2_x, ctrl2_y, ctrl3_x, ctrl3_y, mouse_x - radius, mouse_y)
            path.cubicTo(ctrl3_x, ctrl3_y, ctrl1_x, ctrl1_y, mouse_x, mouse_y - radius)
            path.cubicTo(ctrl1_x, ctrl1_y, ctrl2_x, ctrl2_y, mouse_x + radius, mouse_y)
            
            glow_gradient = QRadialGradient(self.mouse_pos, radius * 2)
            glow_gradient.setColorAt(0.0, QColor(255, 255, 255, 180))
            glow_gradient.setColorAt(0.3, QColor(255, 255, 255, 120))
            glow_gradient.setColorAt(0.7, QColor(255, 255, 255, 60))
            glow_gradient.setColorAt(1.0, QColor(255, 255, 255, 0))
            
            temp_painter.setCompositionMode(QPainter.CompositionMode_Screen)
            temp_painter.setBrush(QBrush(glow_gradient))
            temp_painter.setPen(QPen(Qt.transparent))
            temp_painter.drawPath(path)
            
            env_gradient = QRadialGradient(self.rect().center(), self.width() / 2)
            env_gradient.setColorAt(0, QColor.fromHsv(self.color_offset % 360, 150, 255, 30))
            env_gradient.setColorAt(1, QColor.fromHsv(self.color_offset % 360, 150, 255, 0))
            temp_painter.setBrush(QBrush(env_gradient))
            temp_painter.drawRect(0, 0, self.width(), self.height())
            
            temp_painter.end()
            painter.drawImage(0, 0, buffer)
        else:
            super().paintEvent(event)