const { createApp } = Vue;

const app = createApp({
    data() {
        return {
            sizes: {},
            selectedSize: '',
            previewImage: null,
            processedImage: null,
            processing: false,
            error: null
        }
    },
    mounted() {
        this.loadSizes();
    },
    methods: {
        async loadSizes() {
            try {
                const response = await fetch('/api/sizes');
                this.sizes = await response.json();
                if (Object.keys(this.sizes).length > 0) {
                    this.selectedSize = Object.keys(this.sizes)[0];
                }
            } catch (error) {
                console.error('加载尺寸失败:', error);
                this.error = '加载尺寸失败';
            }
        },
        
        handleImageSelect(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    this.previewImage = e.target.result;
                    this.processedImage = null;
                };
                reader.readAsDataURL(file);
            }
        },
        
        async processImage() {
            const imageInput = document.getElementById('imageInput');
            if (!imageInput.files[0]) {
                alert('请选择图片');
                return;
            }

            const formData = new FormData();
            formData.append('image', imageInput.files[0]);
            formData.append('size', this.selectedSize);

            this.processing = true;
            this.error = null;

            try {
                const response = await fetch('/api/process', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                if (data.error) {
                    throw new Error(data.error);
                }
                
                this.processedImage = data;
                this.previewImage = data.image;
            } catch (error) {
                console.error('处理失败:', error);
                this.error = `处理失败: ${error.message}`;
                alert(this.error);
            } finally {
                this.processing = false;
            }
        },
        
        downloadImage() {
            if (this.processedImage) {
                const link = document.createElement('a');
                link.href = this.processedImage.image;
                link.download = `证件照_${this.processedImage.size}.jpg`;
                link.click();
            }
        }
    }
});

app.mount('#app'); 