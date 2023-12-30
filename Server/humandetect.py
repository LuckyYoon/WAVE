from ultralytics import YOLO  # Import the YOLO object detection framework
import numpy as np  # Import numpy for numerical operations

# Initialize the YOLOv8 Pose model as a global variable
model_pose = None

def initialize_pose_model():
    """
    Initializes the pose detection model using the YOLO framework.
    This function loads the model with pre-trained weights for human pose detection.
    It ensures the model is loaded only once to conserve resources.
    """
    global model_pose  # Reference the global model variable
    if model_pose is None:
        # Load the YOLO model with specified weights for human pose detection
        model_pose = YOLO('model_weights/yolov8n-pose.pt')


def run_human_detection(frame):
    """
    Performs human detection on a given video frame using the YOLO pose model.
    This function identifies individuals in the frame and returns their bounding box coordinates.

    :param frame: The video frame to process for human detection.
    :return: A list of detected individuals with their bounding box coordinates and center points.
    """
    output_list = []  # List to store the detection results
    initialize_pose_model()  # Ensure the pose model is loaded

    # Run the model prediction on the frame
    results = model_pose.predict(frame, verbose=False, conf=0.3)
    results_box = results[0].boxes  # Extract bounding boxes from the results

    # Process each detected bounding box
    for i in range(len(results_box.cls.tolist())):
        coordinates = [float(i) for i in results_box.xyxy.tolist()[i]]
        top_left_x1, top_left_y1, bot_right_x2, bot_right_y2 = coordinates
        cls = int(results_box.cls.tolist()[0])
        # Check if the class is '0', indicating human detection
        if cls == 0:
            # Calculate top-left, bottom-right, and center coordinates
            top_left = (int(top_left_x1), int(top_left_y1)),
            bot_right = (int(bot_right_x2), int(bot_right_y2)),
            center = (int(top_left_x1 + bot_right_x2) // 2, int(top_left_y1 + bot_right_y2) // 2)
            # Append the calculated coordinates to the output list
            output_list.append([top_left, bot_right, center])

    return output_list  # Return the list of detected individuals
