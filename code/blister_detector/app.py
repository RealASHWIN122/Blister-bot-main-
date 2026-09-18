import os
from flask import Flask, render_template, request, jsonify, send_from_directory
import uuid
import predictor
from detector import detect_blisters
from config import UPLOAD_FOLDER, OUTPUT_FOLDER

app = Flask(__name__)

# Load model once on startup
predictor.init_model()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
        
    if file:
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, filename)
        
        file.save(input_path)
        
        try:
            contours = detect_blisters(input_path, output_path)
            return jsonify({
                'success': True,
                'original_url': f'/uploads/{filename}',
                'processed_url': f'/outputs/{filename}',
                'contour_count': len(contours)
            })
        except Exception as e:
            return jsonify({'error': str(e)})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/outputs/<filename>')
def output_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
