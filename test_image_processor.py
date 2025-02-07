import unittest
import os
import io
from PIL import Image
from image_processor import ImageProcessor
from config import PHOTO_SIZES, CACHE_DIR

class TestImageProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = ImageProcessor()
        self.test_image = self.create_test_image()

    def create_test_image(self, size=(800, 600)):
        """创建测试用图片"""
        image = Image.new('RGB', size, color='white')
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        return img_byte_arr

    def test_file_validation(self):
        """测试文件验证"""
        # 有效文件
        self.assertTrue(
            self.processor.is_valid_file('test.jpg', 1024 * 1024)
        )
        # 无效扩展名
        self.assertFalse(
            self.processor.is_valid_file('test.txt', 1024 * 1024)
        )
        # 文件过大
        self.assertFalse(
            self.processor.is_valid_file('test.jpg', 20 * 1024 * 1024)
        )

    def test_image_processing(self):
        """测试图片处理"""
        size_name = list(PHOTO_SIZES.keys())[0]
        target_width, target_height = PHOTO_SIZES[size_name]

        # 处理图片
        processed = self.processor.process_image(self.test_image, size_name)
        
        # 验证尺寸
        self.assertEqual(processed.size, (target_width, target_height))

    def test_image_adjustments(self):
        """测试图片调整"""
        image = Image.open(self.test_image)
        
        # 测试亮度调整
        brightened = self.processor.adjust_image(image, brightness=1.5)
        self.assertIsNotNone(brightened)
        
        # 测试对比度调整
        contrasted = self.processor.adjust_image(image, contrast=1.5)
        self.assertIsNotNone(contrasted)

    def test_caching(self):
        """测试缓存功能"""
        size_name = list(PHOTO_SIZES.keys())[0]
        
        # 首次处理（应该没有缓存）
        self.test_image.seek(0)
        processed1 = self.processor.process_image(self.test_image, size_name)
        
        # 再次处理（应该使用缓存）
        self.test_image.seek(0)
        processed2 = self.processor.process_image(self.test_image, size_name)
        
        # 验证两次处理结果相同
        self.assertEqual(
            processed1.tobytes(),
            processed2.tobytes()
        )

    def tearDown(self):
        """清理测试环境"""
        # 清理测试过程中创建的缓存文件
        for filename in os.listdir(CACHE_DIR):
            if filename.startswith('test_'):
                os.remove(os.path.join(CACHE_DIR, filename))

if __name__ == '__main__':
    unittest.main() 