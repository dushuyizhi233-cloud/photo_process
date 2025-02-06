import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                            QVBoxLayout, QHBoxLayout, QWidget, QComboBox, 
                            QFileDialog, QMessageBox, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap, QFont, QIcon
from PIL import Image
import os

class PhotoProcessor(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 预设尺寸（宽x高，单位：像素）
        self.sizes = {
            "一寸（295x413）": (295, 413),
            "二寸（413x579）": (413, 579),
            "小一寸（260x378）": (260, 378),
            "护照（330x420）": (330, 420),
            "身份证（358x441）": (358, 441)
        }
        
        self.image_path = None
        self.preview_pixmap = None
        
        # 移到最后调用
        self.initUI()

    def initUI(self):
        self.setWindowTitle('证件照处理工具')
        self.setMinimumSize(600, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QPushButton {
                background-color: #4a69bd;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #1e3799;
            }
            QPushButton:pressed {
                background-color: #0c2461;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #dcdde1;
                border-radius: 4px;
                min-width: 200px;
            }
            QLabel {
                color: #2f3640;
            }
            QFrame#previewFrame {
                background-color: white;
                border: 2px dashed #dcdde1;
                border-radius: 8px;
                padding: 10px;
            }
        """)

        # 创建主窗口部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # 标题
        title_label = QLabel('证件照处理工具')
        title_label.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 选择图片按钮
        self.select_btn = QPushButton('选择图片')
        self.select_btn.clicked.connect(self.select_image)
        layout.addWidget(self.select_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # 尺寸选择
        size_layout = QHBoxLayout()
        size_label = QLabel('选择尺寸:')
        self.size_combo = QComboBox()
        self.size_combo.addItems(self.sizes.keys())
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_combo)
        layout.addLayout(size_layout)

        # 预览区域
        preview_container = QFrame()
        preview_container.setObjectName("previewFrame")
        preview_container.setMinimumSize(400, 400)
        preview_layout = QVBoxLayout(preview_container)
        
        preview_label = QLabel('预览区域')
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(preview_label)
        
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.preview_label)
        
        layout.addWidget(preview_container)

        # 处理按钮
        self.process_btn = QPushButton('处理并保存')
        self.process_btn.clicked.connect(self.process_image)
        layout.addWidget(self.process_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.image_path = file_path
            self.show_preview()

    def show_preview(self):
        if self.image_path:
            image = Image.open(self.image_path)
            # 调整预览图片大小
            preview_size = (350, 350)
            image.thumbnail(preview_size)
            # 转换为QPixmap显示
            qimage = QImage(image.tobytes(), 
                          image.width, 
                          image.height, 
                          QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
            self.preview_label.setPixmap(pixmap)
            self.preview_label.setScaledContents(True)

    def process_image(self):
        if not self.image_path:
            QMessageBox.warning(self, "警告", "请先选择图片")
            return
            
        selected_size = self.size_combo.currentText()
        target_width, target_height = self.sizes[selected_size]
        
        try:
            # 打开原图
            image = Image.open(self.image_path)
            
            # 计算裁剪尺寸
            original_ratio = image.width / image.height
            target_ratio = target_width / target_height
            
            if original_ratio > target_ratio:
                # 图片太宽，需要裁剪宽度
                new_width = int(image.height * target_ratio)
                left = (image.width - new_width) // 2
                image = image.crop((left, 0, left + new_width, image.height))
            else:
                # 图片太高，需要裁剪高度
                new_height = int(image.width / target_ratio)
                top = (image.height - new_height) // 2
                image = image.crop((0, top, image.width, top + new_height))
            
            # 调整到目标尺寸
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # 保存处理后的图片
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存图片",
                f"证件照_{selected_size}.jpg",
                "JPEG文件 (*.jpg)"
            )
            
            if save_path:
                image.save(save_path, quality=95)
                QMessageBox.information(self, "成功", "照片处理完成！")
        
        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理图片时出错：{str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PhotoProcessor()
    window.show()
    sys.exit(app.exec()) 