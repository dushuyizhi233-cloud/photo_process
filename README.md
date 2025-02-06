# 证件照处理工具

一个简单易用的证件照处理工具，使用 Python 和 PyQt6 开发。

## 功能特点

- 支持多种常用证件照尺寸
- 智能裁剪和缩放
- 美观的图形界面
- 实时预览功能

## 系统要求

- 操作系统：Windows/Linux/MacOS
- Python 3.8 或更高版本
- 内存：至少 2GB RAM
- 磁盘空间：50MB 以上

## 支持的证件照尺寸

- 一寸（295x413）
- 二寸（413x579）
- 小一寸（260x378）
- 护照（330x420）
- 身份证（358x441）

## 安装说明

1. 克隆仓库：
   ```bash
   git clone https://github.com/你的用户名/photo-processor.git
   cd photo-processor
   ```

2. 创建虚拟环境（推荐）：

   Windows:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

   Linux/Mac:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

1. 运行程序：
   ```bash
   python src/main.py
   ```

2. 使用步骤：
   - 点击"选择图片"按钮选择需要处理的照片
   - 从下拉菜单中选择目标尺寸
   - 查看预览效果
   - 点击"处理并保存"按钮，选择保存位置

## 开发环境

- Python 3.8+
- PyQt6 6.6.1
- Pillow 10.2.0

## 常见问题

1. 如果安装依赖时出现错误，请确保您的 pip 是最新版本：
   ```bash
   python -m pip install --upgrade pip
   ```

2. 如果运行程序时出现 "ModuleNotFoundError"，请确保已经激活虚拟环境并正确安装了所有依赖。

## 许可证

本项目采用 MIT License 开源许可证。详情请查看 [LICENSE](LICENSE) 文件。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件至：[您的邮箱]

## 更新日志

### v1.0.0 (2024-01)
- 初始版本发布
- 支持基本的证件照处理功能