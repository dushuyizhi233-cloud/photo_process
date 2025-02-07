from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
import io
import base64
from image_processor import ImageProcessor
from config import PHOTO_SIZES
import logging
from functools import wraps
import asyncio
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
CORS(app)
processor = ImageProcessor()
executor = ThreadPoolExecutor(max_workers=4)
logger = logging.getLogger('FlaskApp')

def async_route(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapped

def validate_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'image' not in request.files:
            return jsonify({'error': '没有上传图片'}), 400
        
        file = request.files['image']
        if not file.filename:
            return jsonify({'error': '没有选择文件'}), 400
            
        if not processor.is_valid_file(file.filename, request.content_length):
            return jsonify({
                'error': f'无效的文件。允许的格式：{", ".join(ALLOWED_EXTENSIONS)}，最大大小：{MAX_FILE_SIZE/1024/1024}MB'
            }), 400
            
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return send_file('static/index.html')

@app.route('/api/sizes', methods=['GET'])
def get_sizes():
    """获取所有支持的尺寸"""
    try:
        sizes_with_dimensions = {
            name: f"{dims[0]}x{dims[1]}" 
            for name, dims in PHOTO_SIZES.items()
        }
        return jsonify(sizes_with_dimensions)
    except Exception as e:
        logger.error(f"Error in get_sizes: {str(e)}")
        return jsonify({'error': '获取尺寸列表失败'}), 500

@app.route('/api/process', methods=['POST'])
@validate_request
@async_route
async def process():
    """处理图片的异步路由"""
    try:
        image_file = request.files['image']
        size_name = request.form.get('size')
        brightness = float(request.form.get('brightness', 1.0))
        contrast = float(request.form.get('contrast', 1.0))

        if size_name not in PHOTO_SIZES:
            return jsonify({'error': '无效的尺寸选择'}), 400

        # 在线程池中处理图片
        loop = asyncio.get_event_loop()
        processed_image = await loop.run_in_executor(
            executor,
            processor.process_image,
            image_file,
            size_name,
            brightness,
            contrast
        )

        # 转换为base64
        buffered = io.BytesIO()
        processed_image.save(buffered, format="JPEG", quality=95)
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return jsonify({
            'image': f'data:image/jpeg;base64,{img_str}',
            'size': size_name
        })

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/custom-size', methods=['POST'])
@validate_request
@async_route
async def process_custom_size():
    """处理自定义尺寸的图片"""
    try:
        width = int(request.form.get('width', 0))
        height = int(request.form.get('height', 0))
        
        if width <= 0 or height <= 0:
            return jsonify({'error': '无效的尺寸'}), 400
            
        # 创建临时尺寸名称
        temp_size_name = f"custom_{width}x{height}"
        PHOTO_SIZES[temp_size_name] = (width, height)
        
        # 处理图片
        response = await process()
        
        # 清理临时尺寸
        del PHOTO_SIZES[temp_size_name]
        
        return response
        
    except ValueError:
        return jsonify({'error': '无效的尺寸参数'}), 400
    except Exception as e:
        logger.error(f"Error processing custom size: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
