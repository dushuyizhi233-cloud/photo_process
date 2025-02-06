from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import os
import io
import base64

app = Flask(__name__)
CORS(app)

# 预设尺寸（宽x高，单位：像素）
SIZES = {
    "一寸": (295, 413),
    "二寸": (413, 579),
    "小一寸": (260, 378),
    "护照": (330, 420),
    "身份证": (358, 441)
}

def process_image(image, size_name):
    target_width, target_height = SIZES[size_name]
    
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
    return image.resize((target_width, target_height), Image.Resampling.LANCZOS)

@app.route('/')
def index():
    return send_file('static/index.html')

@app.route('/api/sizes', methods=['GET'])
def get_sizes():
    return jsonify(list(SIZES.keys()))

@app.route('/api/process', methods=['POST'])
def process():
    try:
        if 'image' not in request.files:
            return jsonify({'error': '没有上传图片'}), 400
            
        image_file = request.files['image']
        size_name = request.form.get('size')
        
        if size_name not in SIZES:
            return jsonify({'error': '无效的尺寸选择'}), 400
            
        # 处理图片
        image = Image.open(image_file)
        processed_image = process_image(image, size_name)
        
        # 转换为base64
        buffered = io.BytesIO()
        processed_image.save(buffered, format="JPEG", quality=95)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'image': f'data:image/jpeg;base64,{img_str}',
            'size': size_name
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 