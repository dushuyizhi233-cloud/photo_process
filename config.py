import os

# 基础配置
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
CACHE_DIR = 'cache'
LOG_DIR = 'logs'

# 预设尺寸（宽x高，单位：像素）
PHOTO_SIZES = {
    "一寸": (295, 413),
    "二寸": (413, 579),
    "小一寸": (260, 378),
    "护照": (330, 420),
    "身份证": (358, 441)
}

# 图片处理配置
INITIAL_COMPRESSION_SIZE = (1000, 1000)  # 大图片初始压缩尺寸
JPEG_QUALITY = 95
CACHE_EXPIRY_DAYS = 7  # 缓存过期时间（天）

# 创建必要的目录
for directory in [CACHE_DIR, LOG_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory) 