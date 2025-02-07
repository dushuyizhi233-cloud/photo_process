import os
import hashlib
from datetime import datetime, timedelta
from PIL import Image, ImageEnhance, ExifTags
import logging
from config import *

# 配置日志
logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'image_processor.log'),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ImageProcessor')

class ImageProcessor:
    def __init__(self):
        self.cleanup_cache()

    @staticmethod
    def get_file_hash(file_data):
        """计算文件的MD5哈希值"""
        return hashlib.md5(file_data).hexdigest()

    @staticmethod
    def is_valid_file(filename, filesize):
        """验证文件类型和大小"""
        return ('.' in filename and 
                filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS and 
                filesize <= MAX_FILE_SIZE)

    def cleanup_cache(self):
        """清理过期的缓存文件"""
        try:
            expiry = datetime.now() - timedelta(days=CACHE_EXPIRY_DAYS)
            for filename in os.listdir(CACHE_DIR):
                filepath = os.path.join(CACHE_DIR, filename)
                if os.path.getctime(filepath) < expiry.timestamp():
                    os.remove(filepath)
        except Exception as e:
            logger.error(f"Cache cleanup error: {str(e)}")

    def get_cached_image(self, file_hash, size_name):
        """获取缓存的图片"""
        cache_path = os.path.join(CACHE_DIR, f"{file_hash}_{size_name}.jpg")
        if os.path.exists(cache_path):
            return Image.open(cache_path)
        return None

    def cache_image(self, image, file_hash, size_name):
        """缓存处理后的图片"""
        try:
            cache_path = os.path.join(CACHE_DIR, f"{file_hash}_{size_name}.jpg")
            image.save(cache_path, quality=JPEG_QUALITY)
        except Exception as e:
            logger.error(f"Cache save error: {str(e)}")

    def compress_image(self, image):
        """压缩大图片"""
        if max(image.size) > max(INITIAL_COMPRESSION_SIZE):
            image.thumbnail(INITIAL_COMPRESSION_SIZE, Image.Resampling.LANCZOS)
        return image

    def adjust_image(self, image, brightness=1.0, contrast=1.0):
        """调整图片亮度和对比度"""
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(brightness)
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)
        return image

    @staticmethod
    def fix_image_orientation(image):
        """修复图片方向"""
        try:
            # 复制图片以保留原始数据
            image = image.copy()
            original_size = image.size
            logger.info(f"Original image size: {original_size}")
            
            if hasattr(image, '_getexif'):  # 只处理有EXIF信息的图片
                exif = image._getexif()
                if exif is not None:
                    logger.info(f"EXIF data found")
                    orientation_key = None
                    for key, value in ExifTags.TAGS.items():
                        if value == 'Orientation':
                            orientation_key = key
                            break
                    
                    if orientation_key is not None and orientation_key in exif:
                        orientation = exif[orientation_key]
                        logger.info(f"Found orientation: {orientation}")
                        
                        rotation_map = {
                            2: [Image.Transpose.FLIP_LEFT_RIGHT],
                            3: [Image.Transpose.ROTATE_180],
                            4: [Image.Transpose.FLIP_TOP_BOTTOM],
                            5: [Image.Transpose.FLIP_LEFT_RIGHT, Image.Transpose.ROTATE_90],
                            6: [Image.Transpose.ROTATE_270],
                            7: [Image.Transpose.FLIP_LEFT_RIGHT, Image.Transpose.ROTATE_270],
                            8: [Image.Transpose.ROTATE_90]
                        }
                        
                        if orientation in rotation_map:
                            for operation in rotation_map[orientation]:
                                image = image.transpose(operation)
                                logger.info(f"Applied transformation: {operation}")
                    else:
                        logger.info("No orientation data in EXIF")
                else:
                    logger.info("No EXIF data found")
            else:
                logger.info("Image does not support EXIF")
            
            # 检查处理后的尺寸是否发生变化
            final_size = image.size
            logger.info(f"Final image size: {final_size}")
            
            # 如果宽高比发生了变化（可能是不当的旋转导致），尝试修正
            orig_ratio = original_size[0] / original_size[1]
            final_ratio = final_size[0] / final_size[1]
            
            if abs(orig_ratio - final_ratio) > 0.01:  # 允许一点点误差
                logger.warning(f"Aspect ratio changed significantly: {orig_ratio:.2f} -> {final_ratio:.2f}")
                # 如果宽高比发生显著变化，可能需要额外的旋转修正
                if final_ratio < 1 and orig_ratio > 1:  # 如果图片变得太窄
                    image = image.transpose(Image.Transpose.ROTATE_90)
                    logger.info("Applied additional 90 degree rotation to correct aspect ratio")
            
            return image
            
        except Exception as e:
            logger.error(f"Error fixing image orientation: {str(e)}")
            # 如果出错，返回原始图片
            return image.copy()

    def process_image(self, image_file, size_name, brightness=1.0, contrast=1.0):
        """处理图片的主要方法"""
        try:
            # 计算文件哈希
            file_data = image_file.read()
            file_hash = self.get_file_hash(file_data)
            image_file.seek(0)

            # 检查缓存
            cached_image = self.get_cached_image(file_hash, size_name)
            if cached_image:
                logger.info(f"Cache hit for {file_hash}_{size_name}")
                return cached_image

            # 处理图片
            image = Image.open(image_file)
            logger.info(f"Original image mode: {image.mode}, size: {image.size}")
            
            # 转换为RGB模式（如果不是的话）
            if image.mode != 'RGB':
                image = image.convert('RGB')
                logger.info("Converted image to RGB mode")
            
            # 修复图片方向
            image = self.fix_image_orientation(image)
            logger.info(f"After orientation fix - size: {image.size}")
            
            # 获取目标尺寸
            target_width, target_height = PHOTO_SIZES[size_name]
            logger.info(f"Target size: {target_width}x{target_height}")
            
            # 压缩大图片
            original_size = image.size
            image = self.compress_image(image)
            if original_size != image.size:
                logger.info(f"Image compressed from {original_size} to {image.size}")
            
            # 计算裁剪尺寸
            original_ratio = image.width / image.height
            target_ratio = target_width / target_height
            logger.info(f"Original ratio: {original_ratio:.2f}, Target ratio: {target_ratio:.2f}")
            
            # 如果原始图片和目标方向不一致，进行旋转
            is_original_portrait = image.height > image.width
            is_target_portrait = target_height > target_width
            
            if is_original_portrait != is_target_portrait:
                logger.info("Rotating image to match target orientation")
                # 使用ROTATE_270代替ROTATE_90来避免上下颠倒
                image = image.transpose(Image.Transpose.ROTATE_270)
                # 重新计算比例
                original_ratio = image.width / image.height
            
            if original_ratio > target_ratio:
                new_width = int(image.height * target_ratio)
                left = (image.width - new_width) // 2
                image = image.crop((left, 0, left + new_width, image.height))
                logger.info(f"Cropped width to: {new_width}")
            else:
                new_height = int(image.width / target_ratio)
                top = (image.height - new_height) // 2
                image = image.crop((0, top, image.width, top + new_height))
                logger.info(f"Cropped height to: {new_height}")
            
            # 调整到目标尺寸
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            logger.info(f"Resized to target: {image.size}")
            
            # 调整亮度和对比度
            image = self.adjust_image(image, brightness, contrast)
            
            # 缓存处理后的图片
            self.cache_image(image, file_hash, size_name)
            
            return image

        except Exception as e:
            logger.error(f"Image processing error: {str(e)}")
            raise 