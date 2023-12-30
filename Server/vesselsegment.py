#vesselsegment.py
from ultralytics import YOLO  # Import the YOLO model for object detection
import numpy as np  # Import numpy for numerical operations

model_seg = None  # Global variable to hold the segmentation model

def initialize_segmentation_model():
    """
    Initializes the vessel segmentation model using the YOLO framework.
    This function loads the model with pre-trained weights for vessel segmentation.
    It ensures the model is loaded only once to save resources.
    """
    global model_seg  # Reference the global model variable
    if model_seg is None:
        # Load the YOLO model with specified weights for vessel segmentation
        model_seg = YOLO('model_weights/segment.pt')
        

def run_vessel_segmentation(frame):
    """
    Performs vessel segmentation on a given video frame.
    This function identifies and calculates various parameters of the vessel, such as its position and orientation.

    :param frame: The video frame to process for vessel segmentation.
    :return: A list containing the coordinates of the vessel's corners, its center, and orientation angle.
    """
    output_list = []  # List to store the segmentation results
    initialize_segmentation_model()  # Ensure the segmentation model is loaded

    # Run the model prediction on the frame
    results = model_seg(frame)

    # Process the results if any vessel is detected
    if results[0].masks is not None:
        re_box = results[0].boxes
        re_mask = results[0].masks
        re_conf = float(re_box[0].conf.tolist()[0])
        re_cls = int(re_box[0].cls.tolist()[0])

        # Check if the detected class is a vessel
        if re_cls == 0:
            xy_boat_array = re_mask[0].xy[0]
            top_left = xy_boat_array.min(axis=0)
            bottom_right = xy_boat_array.max(axis=0)

            # Calculate slope and perpendicular slope of the vessel
            slope = (bottom_right[1] - top_left[1]) / (bottom_right[0] - top_left[0])
            perp_slope = -1 / slope

            # Calculate midpoints and deltas for vessel's top and bottom
            mid_x, mid_y = (top_left[0] + bottom_right[0]) / 2, (top_left[1] + bottom_right[1]) / 2
            delta_x = (length / 2) / ((1 + perp_slope**2) ** 0.5)
            delta_y = perp_slope * delta_x

            # Determine coordinates for top right and bottom left of the vessel
            top_right = (mid_x - delta_x, mid_y - delta_y)
            bottom_left = (mid_x + delta_x, mid_y + delta_y)

            # Calculate the center points of the top and bottom edges
            top_center = ((top_left[0] + top_right[0]) // 2, (top_left[1] + top_right[1]) // 2)
            bottom_center = ((bottom_left[0] + bottom_right[0]) // 2, (bottom_left[1] + bottom_right[1]) // 2)

            # Compute the angle of the vessel's orientation
            boat_slope = (top_center[1] - bottom_center[1]) / (top_center[0] - bottom_center[0])
            angle_radians = math.atan(boat_slope)
            angle = math.degrees(angle_radians)

            # Calculate the center point of the vessel
            boat_center_x = (top_center[0] + bottom_center[0]) // 2
            boat_center_y = (top_center[1] + bottom_center[1]) // 2
            center = (boat_center_x, boat_center_y)

            # Compile the output list with vessel's details
            output_list = [top_left, top_right, bottom_right, bottom_left, center, angle]

    return output_list  # Return the vessel's segmentation details
