# FoliumScope

A Flask-based web application for leaf image classification using a Keras deep learning model.

## Features

- Upload leaf images and get predictions for disease/health status.
- Uses a pre-trained Keras model.
- REST API endpoints for prediction and health check.
- Frontend with HTML/CSS/JS.

## Project Structure

- `app.py` - Main Flask application.
- `models/` - Contains the trained Keras model (`hackmodel.h5`).
- `uploads/` - Stores uploaded images (ignored by git).
- `static/` - Static files (CSS, JS).
- `templates/` - HTML templates.
- `requirements.txt` - Python dependencies.

## Setup

1. Clone the repository.
2. Create a virtual environment and activate it.
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the app:
   ```sh
   python app.py
   ```

## API

- `POST /predict` - Upload an image and get prediction.
- `GET /health` - Health check endpoint.

## Notes

- The `uploads/` and `models/` folders are git-ignored by default.
- For deployment, ensure your model file is present in `models/`.
