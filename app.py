import os
import uuid
import base64
import logging
from flask import Flask, render_template, request, send_from_directory, jsonify
from PIL import Image, ImageEnhance, ImageFilter

# ---------------------------------------------------------
# 1. SERVER CONFIGURATION & VERCEL COMPATIBILITY
# ---------------------------------------------------------
app = Flask(__name__)

# Required for Vercel deployment: Map the app instance
app = app 

# Configure logging for production environment tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Vercel writeable directory is restricted to '/tmp'
UPLOAD_FOLDER = '/tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB Upload Limit

# ---------------------------------------------------------
# 2. VECTOR (SVG) CONVERSION ENGINE
# ---------------------------------------------------------
def create_vector_svg(png_source, svg_destination):
    """Wraps the processed image into a high-quality SVG container."""
    try:
        with open(png_source, "rb") as img_file:
            encoded_data = base64.b64encode(img_file.read()).decode('utf-8')
            with Image.open(png_source) as img:
                width, height = img.size
                svg_data = (
                    f'<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
                    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n'
                    f'  <image width="100%" height="100%" href="data:image/png;base64,{encoded_data}"/>\n'
                    f'</svg>'
                )
                with open(svg_destination, "w", encoding="utf-8") as f:
                    f.write(svg_data)
        return True
    except Exception as e:
        logger.error(f"SVG Engine Failure: {str(e)}")
        return False

# ---------------------------------------------------------
# 3. AI IMAGE UPSCALING LOGIC (CORE)
# ---------------------------------------------------------
def enhance_image_resolution(input_path, output_path, scale, output_format):
    """Core logic using Lanczos resampling and sharpness filters."""
    try:
        with Image.open(input_path) as img:
            img = img.convert("RGBA")
            
            # Step 1: High-fidelity resizing using Lanczos resampling
            new_dimensions = (int(img.width * scale), int(img.height * scale))
            img = img.resize(new_dimensions, Image.Resampling.LANCZOS)
            
            # Step 2: Apply advanced sharpness and detail filters
            img = img.filter(ImageFilter.DETAIL)
            sharp_enhancer = ImageEnhance.Sharpness(img)
            img = sharp_enhancer.enhance(2.1)
            
            # Step 3: Final Export based on selected format
            if output_format == "svg":
                temp_path = output_path.replace(".svg", "_temp.png")
                img.save(temp_path, "PNG")
                create_vector_svg(temp_path, output_path)
                if os.path.exists(temp_path): os.remove(temp_path)
            else:
                ext = "PNG" if output_format == "png" else "JPEG"
                img.save(output_path, format=ext, quality=95)
            return True
    except Exception as e:
        logger.error(f"Processing Logic Error: {str(e)}")
        return False

# ---------------------------------------------------------
# 4. API ENDPOINTS & ROUTES
# ---------------------------------------------------------
@app.route('/')
def index():
    """Renders the main application interface."""
    return render_template('index.html')

@app.route('/process_request', methods=['POST'])
def handle_api():
    """Handles incoming image uploads and triggers the AI engine."""
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    scale = float(request.form.get('scale', 2.0))
    file_format = request.form.get('format', 'png')
    
    if file.filename == '':
        return jsonify({"error": "Selected file is empty"}), 400

    # Generate unique identifiers for secure file handling
    request_id = str(uuid.uuid4())[:12]
    original_ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'png'
    
    source_p = os.path.join(app.config['UPLOAD_FOLDER'], f"src_{request_id}.{original_ext}")
    result_name = f"enhanced_{request_id}.{file_format}"
    result_p = os.path.join(app.config['UPLOAD_FOLDER'], result_name)
    
    file.save(source_p)
    
    # Execute Enhancement Engine
    if enhance_image_resolution(source_p, result_p, scale, file_format):
        return jsonify({
            "success": True, 
            "download_url": f"/get_file/{result_name}"
        })
    
    return jsonify({"error": "Neural engine failed to process image"}), 500

@app.route('/get_file/<filename>')
def get_file(filename):
    """Serves the final file with the professional custom name."""
    # Extract extension (png, jpg, or svg)
    ext = filename.split('.')[-1]
    
    # Send file with the requested 'ai-upscaler-pro' naming convention
    return send_from_directory(
        app.config['UPLOAD_FOLDER'], 
        filename, 
        as_attachment=True,
        download_name=f"ai-upscaler-pro.{ext}"
    )

if __name__ == '__main__':
    # Local development server entry point
    app.run(host='127.0.0.1', port=5000, debug=True)
