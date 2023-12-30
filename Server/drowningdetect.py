from ultralytics import YOLO
import numpy as np

model_detect = None  # Global variable to hold the detection model

def initialize_detection_model():
    """
    Initializes the detection model using the YOLO framework.
    This function loads the model weights only if the model has not been previously initialized.
    """
    global model_detect  # Reference the global variable
    # Load the model only if it hasn't been initialized before
    if model_detect is None:
        model_detect = YOLO('model_weights/detect.pt')  # Load model with specified weights
        

def run_drowning_detection(frame):
    """
    Runs the drowning detection on the given frame using the YOLO model.
    This function detects individuals who might be drowning and returns their bounding box coordinates.

    :param frame: The video frame to be processed for drowning detection.
    :return: A list of detected individuals with their bounding box coordinates and center points.
    """
    output_list = []  # List to store output results
    initialize_detection_model()  # Ensure the model is loaded

    # Run the model prediction on the frame
    results = model_detect.predict(frame, verbose=False, conf=0.3)
    results_box = results[0].boxes  # Extract bounding boxes from the results

    # Process each detected bounding box
    for i in range(len(results_box.cls.tolist())):
        coordinates = [float(i) for i in results_box.xyxy.tolist()[i]]
        top_left_x1, top_left_y1, bot_right_x2, bot_right_y2 = coordinates
        cls = int(results_box.cls.tolist()[0])
        # Check if the class is '1', indicating drowning
        if cls == 1:
            # Calculate top-left, bottom-right, and center coordinates
            top_left = (int(top_left_x1), int(top_left_y1)),
            bot_right = (int(bot_right_x2), int(bot_right_y2)),
            center = (int(top_left_x1 + bot_right_x2) // 2, int(top_left_y1 + bot_right_y2) // 2)
            # Append the calculated coordinates to the output list
            output_list.append([top_left, bot_right, center])

    return output_list  # Return the list of detected individuals