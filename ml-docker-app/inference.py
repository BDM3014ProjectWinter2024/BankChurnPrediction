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
    
    model = joblib.load(os.path.join(model_dir, "random_forest.pkl"))
    return model

# Function to perform inference
def predict_fn(input_data, model):
    # Convert input data to numpy array
    input_data_np = np.array(input_data['instances'])
    
    # Perform inference using the loaded model
    predictions = model.predict(input_data_np)
    return predictions.tolist()

# Entry point for SageMaker /invocations endpoint
@app.route('/invocations', methods=['POST'])
def predict():
    # Load the model
    model = model_fn("/opt/ml/model")

    # Parse input data
    input_data = request.json

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
