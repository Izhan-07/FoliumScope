import os
import logging
import numpy as np
import tensorflow as tf
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from PIL import Image

# -------------------------
# Logging setup
# -------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------
# Flask app setup
# -------------------------
app = Flask(__name__)

# -------------------------
# Model setup
# -------------------------
MODEL_PATH = "models/hackmodel.tflite"
CLASS_NAMES = ['Grassy Shoots', 'Healthy', 'Mites', 'Ring Spot', 'YLD']

interpreter = None
input_details = None
output_details = None

def load_tflite_model():
    global interpreter, input_details, output_details
    interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    logger.info("✅ TFLite model loaded successfully")

# Load model on startup
load_tflite_model()

# -------------------------
# Helper: Prediction
# -------------------------
def model_predict(img_path):
    logger.info("Starting prediction")

    # Load and preprocess image
    img = Image.open(img_path).convert('RGB')
    logger.info(f"Image opened: {img.size}, mode: {img.mode}")

    img = img.resize((256, 256))
    logger.info("Image resized to 256x256")

    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0).astype(np.float32) / 255.0
    logger.info(f"Input shape: {img_array.shape}")

    # Run inference
    interpreter.set_tensor(input_details[0]['index'], img_array)
    logger.info("Tensor set")

    interpreter.invoke()
    logger.info("Interpreter invoked")

    predictions = interpreter.get_tensor(output_details[0]['index'])
    logger.info(f"Raw predictions: {predictions[0]}")

    predicted_class = CLASS_NAMES[np.argmax(predictions[0])]
    confidence = round(100 * np.max(predictions[0]), 2)

    return predicted_class, confidence

# -------------------------
# Routes
# -------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)
        os.makedirs('uploads', exist_ok=True)
        file.save(filepath)

        predicted_class, confidence = model_predict(filepath)

        return jsonify({
            'class': predicted_class,
            'confidence': confidence
        })

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return "OK", 200

# -------------------------
# Run app
# -------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
