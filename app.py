from __future__ import division, print_function
# coding=utf-8
import sys
import os
import glob
import re
import numpy as np
from werkzeug.utils import secure_filename
from PIL import Image
import logging

# Keras
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.models import load_model
from keras.utils import load_img, img_to_array

# importing tensorflow for prediction
import tensorflow as tf
from tensorflow.keras import models, layers
import matplotlib.pyplot as plt
import numpy as np

# Flask utils
from flask import Flask, redirect, url_for, request, render_template, jsonify, flash

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a flask app
app = Flask(__name__)
app.secret_key = 'foliumscope-secret-key-2024'  # Add secret key for flash messages

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Model saved with Keras model.save()
MODEL_PATH = 'models/hackmodel.h5'

# Load your trained model
try:
    model = load_model(MODEL_PATH)
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    model = None

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(file_path):
    """Validate if uploaded file is a valid image"""
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False

def model_predict(img_path, model):
    """Enhanced prediction function with error handling"""
    try:
        class_names = ['Grassy Shoots', 'Healthy', 'Mites', 'Ring Spot', 'YLD']

        # Load and preprocess image
        img = Image.open(img_path)

        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize image
        img = img.resize((256, 256))
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)

        # Normalize pixel values
        img_array = img_array / 255.0

        # Make prediction
        predictions = model.predict(img_array)

        # Get predicted class and confidence
        predicted_class = class_names[np.argmax(predictions[0])]
        confidence = round(100 * (np.max(predictions[0])), 2)

        logger.info(f"Prediction: {predicted_class} with {confidence}% confidence")

        return predicted_class, confidence

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise Exception(f"Failed to analyze image: {str(e)}")

@app.route('/', methods=['GET'])
def index():
    """Main page route"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def upload():
    """Enhanced prediction endpoint with better error handling"""
    if request.method == 'POST':
        try:
            # Check if file was uploaded
            if 'file' not in request.files:
                return jsonify({'error': 'No file uploaded'}), 400

            file = request.files['file']

            # Check if file was selected
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400

            # Check file extension
            if not allowed_file(file.filename):
                return jsonify({'error': 'Invalid file type. Please upload JPG, PNG, or JPEG files.'}), 400

            # Check if model is loaded
            if model is None:
                return jsonify({'error': 'Model not available. Please try again later.'}), 500

            # Secure filename and save file
            filename = secure_filename(file.filename)
            # Add timestamp to avoid filename conflicts
            import time
            timestamp = str(int(time.time()))
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            file.save(file_path)

            # Validate uploaded image
            if not validate_image(file_path):
                os.remove(file_path)  # Clean up invalid file
                return jsonify({'error': 'Invalid image file. Please upload a valid image.'}), 400

            # Make prediction
            predicted_class, confidence = model_predict(file_path, model)

            # Clean up uploaded file (optional - remove if you want to keep uploads)
            # os.remove(file_path)

            # Return result with confidence
            result = f"{predicted_class} ({confidence}% confidence)"
            return jsonify({
                'result': result,
                'class': predicted_class,
                'confidence': confidence
            })

        except Exception as e:
            logger.error(f"Upload error: {e}")
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Method not allowed'}), 405

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'upload_folder': os.path.exists(UPLOAD_FOLDER)
    })

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 5MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {e}")
    return jsonify({'error': 'Internal server error. Please try again.'}), 500

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
