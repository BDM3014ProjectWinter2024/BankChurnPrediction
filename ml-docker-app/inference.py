import joblib
import os
import numpy as np
from flask import Flask, request, jsonify

app = Flask(__name__)
# Set debug mode on
app.debug = True

# Function to load the model
def model_fn(model_dir):
    # Load the model from the model_dir
    script_dir = os.path.dirname(model_dir)
    model_path = os.path.join(script_dir, "random_forest.pkl")
    model = joblib.load(model_path)
    return model

# Function to perform inference
def predict_fn(input_data, model):
    # Check if input_data is in JSON format
    if isinstance(input_data, dict) and 'instances' in input_data:
        input_data_np = np.array(input_data['instances'])
    elif isinstance(input_data, list) and isinstance(input_data[0], list):
        input_data_np = np.array(input_data)
    else:
        raise ValueError('Input data format not supported')
    
    # Perform inference using the loaded model
    predictions = model.predict(input_data_np)
    return predictions.tolist()

# Entry point for SageMaker /invocations endpoint
@app.route('/invocations', methods=['POST'])
def predict():
    # Load the model
    model = model_fn(os.path.realpath(__file__))
    content_type = request.headers.get('Content-Type')
    
    # Parse input data based on content type
    if content_type == 'application/json':
        input_data = request.json
    elif content_type == 'text/csv':
        input_data = request.data.decode('utf-8').split('\n')
        # Split CSV rows into lists of values
        input_data = [row.split(',') for row in input_data if row.strip()]
        input_data = input_data[1:]  # Remove header row from data

    # Perform inference
    predictions = predict_fn(input_data, model)

    # Return predictions
    return jsonify({'predictions': predictions})

# Entry point for SageMaker /ping endpoint
@app.route('/ping', methods=['GET'])
def ping():
    return '', 200  # Return HTTP 200 OK with an empty body to indicate that the container is healthy

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
