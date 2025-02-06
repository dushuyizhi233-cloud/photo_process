# 证件照处理工具

一个简单易用的证件照处理工具，使用 Python 和 PyQt6 开发。

## 功能特点

- 支持多种常用证件照尺寸
- 智能裁剪和缩放
- 美观的图形界面
- 实时预览功能

## 支持的证件照尺寸

- 一寸（295x413）
- 二寸（413x579）
- 小一寸（260x378）
- 护照（330x420）
- 身份证（358x441）

## 安装说明

1. 克隆仓库：
bash
git clone https://github.com/你的用户名/photo-processor.git
cd photo-processor
2. 创建虚拟环境（推荐）：
bash
python -m venv .venv
Windows
.venv\Scripts\activate
Linux/Mac
source .venv/bin/activate
3. 安装依赖：
bash
pip install -r requirements.txt

## 使用方法

1. 运行程序：
bash
python src/main.py
2. 点击"选择图片"按钮选择需要处理的照片
3. 从下拉菜单中选择目标尺寸
4. 查看预览效果
5. 点击"处理并保存"按钮，选择保存位置

## 开发环境

- Python 3.8+
- PyQt6
- Pillow

## 许可证

MIT License

## 贡献指南

欢迎提交 Issue 和 Pull Request！