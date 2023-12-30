import cv2
import time
import math
import hmac
import hashlib
import base64
import requests
import json

# Custom classes and methods for detection
from humandetect import run_human_detection
from drowningdetect import run_drowning_detection
from vesselsegment import run_vessel_segmentation
from vesselcontrol import send_command
from human import Human

def movevessel(target, boat, angle):
    """Navigate the vessel towards a target for rescue."""
    home_y = 100  # Shoreline Y coordinate for boat return
    global target_recovered, vessel_on_move, destination_arrived_time

    # Calculate the slope and angle to the target
    slope_to_target = (target[1] - boat[1]) / (target[0] - boat[0])
    angle_radians = math.atan(slope_to_target)
    angle_target = math.degrees(angle_radians)

    # Navigate the vessel based on angle and distance to target
    if not vessel_on_move:
        if angle < angle_target * 0.7 or angle > angle_target * 1.3:
            send_command("left turn")
            return False
        else:
            send_command("forward")
            vessel_on_move = True
            return False
    else:
        if not target_reached:
            send_command("forward")
            if calculate_distance(boat, target) < 100:
                send_command("stop")
                destination_arrived_time = time.time()
                send_alert("The vessel has reached the target")
                return False
        else:
            if angle < -210 or angle > -150:
                send_command("left turn")
                return False
            elif time.time() - destination_arrived_time > 10:
                send_command("forward")
                if boat[1] < home_y:
                    send_command("stop")
                    send_alert("The vessel has safely rescued the target and brought it to the shore")
                    return True
    return False


def check_emergency():
    """Checks for emergencies like individuals in the danger zone or potential drowning incidents."""
    global invididuals_in_frame, danger_line_height
    for i in invididuals_in_frame:
        # Skip if the individual is already a target for rescue
        if i.target:
            continue

        # Check if an individual is in the restricted (danger) zone
        if i.in_restricted_zone:
            # If the individual has moved out of the danger zone
            if i.center[1] > danger_line_height:
                i.in_restricted_zone = False
                send_alert("The target has evacuated the danger zone")
            # If the individual has been in the danger zone for more than 5 seconds
            elif (time.time() - i.restricted_zone_entry_time) > 5:
                i.target = True  # Mark as a target for rescue
                send_alert("The target has not left danger zone. Deploying vessel for rescue...")
            # If the individual is detected inside the danger zone
            elif i.center[1] < danger_line_height:
                i.in_restricted_zone = True
                send_alert("An individual has been spotted in the danger zone")

        # Check for drowning detection
        if len(i.drowning_detection_bool) > 1:
            if not i.recent_bool_added:
                i.drowning_detection_bool.append(0)
            # Evaluate the drowning detection over time
            if (time.time() - i.drowning_detection_time > 5):
                if sum(i.drowning_detection_bool)/len(i.drowning_detection_bool) < 0.5:
                    send_alert("The target has recovered from drowning")
                    i.drowning_detection_time = None
                    i.drowning_detection_bool = []
                else:
                    i.target = True  # Mark as a target for rescue
                    send_alert("A target is drowning. Immediately deploying vessel for rescue...")


def update_detection():
    """Updates the detection of individuals in the frame, tracking their positions and states."""
    global invididuals_in_frame, pose_model_results, detection_model_results, deployment_in_progress

    # If there are no individuals currently tracked, initialize tracking
    if len(invididuals_in_frame) == 0:
        # Create Human instances for each detected individual
        for i in pose_model_results:
            inviduals_in_frame.append(Human(i[0], i[1], i[2]))

        # Prepare lists for matching current and new detections
        lst_for_matching_current = [i.center for i in inviduals_in_frame]
        lst_for_matching_detection = [j[2] for j in detection_model_results]

        # Match detected individuals in the current frame
        current_matches = match_humans_between_frame(lst_for_matching_detection, lst_for_matching_current)
        for i in current_matches:
            if i != 'new':
                # Update existing individuals with drowning detection status
                inviduals_in_frame[i[1]].drowning_detection_bool.append(1)
                inviduals_in_frame[i[1]].drowning_detection_time = time.time()
            else:
                # Add new individuals detected as drowning
                for j in i[1]:
                    inviduals_in_frame.append(Human(detection_model_results[j][0], detection_model_results[j][1], detection_model_results[j][2]))
                    inviduals_in_frame[-1].drowning_detection_time = time.time()
                    inviduals_in_frame[-1].drowning_detection_bool.append(1)
                    send_alert("An individual is showing drowning behavior. Will monitor closely for further updates")

    else:
        # Update tracking for existing individuals
        lst_for_matching_current = [i.center for i in inviduals_in_frame]
        lst_for_pose = [j[2] for j in detection_model_results]
        current_matches = match_humans_between_frame(lst_for_pose, lst_for_matching_current)
        for i in current_matches:
            if i != 'new':
                # Update position and bounding box for existing individuals
                inviduals_in_frame[i[1]].top_left = pose_model_results[i[0]][0]
                inviduals_in_frame[i[1]].bot_right = pose_model_results[i[0]][1]
                inviduals_in_frame[i[1]].center = time.time()
            else:
                # Add new individuals detected in the frame
                for j in i[1]:
                    inviduals_in_frame.append(Human(pose_model_results[j][0], pose_model_results[j][1], pose_model_results[j][2]))

        # Repeat matching for drowning detection
        lst_for_matching_detection = [j[2] for j in detection_model_results]
        current_matches = match_humans_between_frame(lst_for_matching_detection, lst_for_matching_current)
        for i in current_matches:
            if i != 'new':
                # Update drowning detection status for existing individuals
                inviduals_in_frame[i[1]].drowning_detection_bool.append(1)
                inviduals_in_frame[i[1]].recent_bool_added = True
                if inviduals_in_frame[i[1]].drowning_detection_time is not None:
                    inviduals_in_frame[i[1]].drowning_detection_time = time.time()
            else:
                # Add new individuals detected as potentially drowning
                for j in i[1]:
                    inviduals_in_frame.append(Human(detection_model_results[j][0], detection_model_results[j][1], detection_model_results[j][2]))
                    inviduals_in_frame[-1].drowning_detection_time = time.time()
                    inviduals_in_frame[-1].drowning_detection_bool.append(1)


def make_signature():
    """
    Generates a signature for authenticating with the Naver Cloud SMS API.
    This signature is required for making secure API requests.
    """
    # Get current timestamp in milliseconds and convert to string
    timestamp = str(int(time.time() * 1000))

    # Access key and secret key for Naver Cloud SMS API
    access_key = "access_key"  # Replace with actual access key
    secret_key = "secret_key"  # Replace with actual secret key
    # Convert secret key to bytes for cryptographic operations
    secret_key_bytes = bytes(secret_key, 'UTF-8')

    # Define the HTTP method and URI for the API request
    method = "POST"
    URI = '/sms/v2/services/{service_key}/messages'  # Replace {service_key} with actual service key

    # Construct the message used to create the signature
    message = method + " " + URI + "\n" + timestamp + "\n" + access_key
    message_bytes = bytes(message, 'UTF-8')

    # Create the signing key using HMAC-SHA256 algorithm
    signingKey = base64.b64encode(hmac.new(secret_key_bytes, message_bytes, digestmod=hashlib.sha256).digest())

    # Return the generated signing key
    return signingKey

def send_alert(details):
    """
    Sends an alert to authorities using the Naver Cloud SMS API.
    This function constructs the request and posts it to the API endpoint.
    """
    # Get current timestamp in milliseconds and convert to string
    timestamp = str(int(time.time() * 1000))
    
    # Define the base URL and URI for the Naver Cloud SMS API
    URL = 'https://sens.apigw.ntruss.com'
    URI = '/sms/v2/services/{service_key}/messages'  # Replace {service_key} with actual service key

    # Create the request header with necessary information for authentication
    header = {
        "Content-Type": "application/json; charset=utf-8",
        "x-ncp-apigw-timestamp": timestamp,
        "x-ncp-iam-access-key": 'access_key',  # Replace with actual access key
        "x-ncp-apigw-signature-v2": make_signature()  # Call make_signature() to generate the signature
    }

    # Construct the data payload for the SMS message
    data = {
        "type": "SMS",
        "from": "WAVE",  # Sender ID or phone number
        "subject": "Emergency",
        "content": f"{details}",  # The message content, passed as a parameter
        "messages": [
            {
                "to": "authorities"  # Recipient, replace with actual phone number or group identifier
            }
        ]
    }

    # Make the POST request to the API and capture the result
    result = requests.post(URL + URI, headers=header, data=json.dumps(data))

    # Return the result of the POST request
    return result


def match_humans_between_frame(list1, list2):
    """
    Matches humans between two frames based on their spatial coordinates.
    This function is used to track the movement of individuals between successive video frames.
    """

    def calculate_distance(coord1, coord2):
        """Calculate the Euclidean distance between two points."""
        # Use the Euclidean distance formula to find the distance between two points
        return math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)

    # Initialize a list to store the distances between coordinates in the two lists
    distance_list = []
    for i, coord1 in enumerate(list1):
        for j, coord2 in enumerate(list2):
            # Calculate the distance between each pair of coordinates
            distance = calculate_distance(coord1, coord2)
            # Append the indices and distance to the distance list
            distance_list.append((i, j, distance))

    # Sort the list by distance to find the closest pairs first
    distance_list.sort(key=lambda x: x[2])

    # Initialize lists to keep track of matched and unmatched indices
    matches = []  # Stores the matched pairs
    lst1_matched = []  # Tracks indices from list1 that have been matched
    lst2_matched = []  # Tracks indices from list2 that have been matched
    new_list = []  # Stores new unmatched indices from list1

    # Iterate through the sorted distance list to find matches
    for i, j, distance in distance_list:
        # If neither index has been matched yet, add them as a match
        if i not in lst1_matched and j not in lst2_matched:
            matches.append([i, j])
            lst1_matched.append(i)
            lst2_matched.append(j)
        # If all indices in list1 have been matched, exit the loop
        if len(lst1_matched) == len(list1):
            break

    # Find any indices from list1 that were not matched
    for i in range(len(list1)):
        if i not in lst1_matched:
            new_list.append(i)
    # Add these unmatched indices as new detections
    matches.append(["new", new_list])

    # Return the list of matches and new detections
    return matches

                        
if __name__ == "__main__":
    # Initialize video capture from the default camera
    cap = cv2.VideoCapture(0)
    default_font = cv2.FONT_HERSHEY_SIMPLEX  # Default font for text on video frames
    detection_efficient, danger_efficient = 6, 1.5  # Coefficients for line heights
    invididuals_in_frame = []  # List to keep track of individuals in the frame
    target_reached = False  # Flag to check if rescue target is reached
    vessel_on_move = False  # Flag to check if the rescue vessel is moving
    destination_arrived_time = None  # Time when the vessel reaches the destination

    # Define colors for drawing on the frame
    green = (0, 255, 0)
    orange = (0, 165, 255)
    blue = (255, 0, 0)
    yellow = (0, 255, 255)
    red = (0, 0, 255)

    # Start processing video frames
    while cap.isOpened():
        ret, frame = cap.read()  # Read a frame from the video capture
        height, width = frame.shape[0], frame.shape[1]  # Get frame dimensions
        if not ret:  # Break loop if frame not read correctly
            break

        # Draw detection and danger lines on the frame
        detection_line_height = int(detection_efficient * height / 10)
        cv2.line(frame, (0, detection_line_height), (width, detection_line_height), blue, 2)
        cv2.putText(frame, 'Detection Line', (10, detection_line_height - 10), default_font, 1, blue, 4)

        danger_line_height = int(danger_efficient * height / 10)
        cv2.line(frame, (0, danger_line_height), (width, danger_line_height), orange, 2)
        cv2.putText(frame, 'Danger Line', (10, danger_line_height - 10), default_font, 1, orange, 4)

        # Run human and drowning detection models on the frame
        pose_model_results = run_human_detection(frame)
        detection_model_results = run_drowning_detection(frame)
        update_detection()  # Update the detection status of individuals
        check_emergency()  # Check for any emergencies such as drowning

        # Process each individual detected in the frame
        for index, i in enumerate(invididuals_in_frame):
            if i.target:  # If the individual is marked as a rescue target
                # Run vessel segmentation to locate and navigate the rescue vessel
                segmentation_model_results = run_vessel_segmentation(frame)
                cv2.rectangle(frame, segmentation_model_results[0], segmentation_model_results[2], green, 2)
                cv2.putText(frame, 'Boat', (segmentation_model_results[0][0], segmentation_model_results[2][1] - 10), default_font, 1, green, 4)
                rescue_result = movevessel(i.center, segmentation_model_results[4], segmentation_model_results[5])
                if rescue_result:  # If rescue is successful, mark for removal
                    remove_individual = index

            # Draw bounding boxes and labels for individuals based on their status
            if i.in_restricted_zone:
                cv2.rectangle(frame, i.top_left, i.bot_right, red, 2)
                cv2.putText(frame, 'In Restricted Zone', (i.top_left[0], i.top_left[1] - 10), default_font, 1, red, 4)
            elif len(i.drowning_detection_bool) > 0 and i.target:
                cv2.rectangle(frame, i.top_left, i.bot_right, red, 2)
                cv2.putText(frame, 'Drowning', (i.top_left[0], i.top_left[1] - 10), default_font, 1, red, 4)
            elif len(i.drowning_detection_bool) > 0:
                cv2.rectangle(frame, i.top_left, i.bot_right, yellow, 2)
                cv2.putText(frame, 'Potential Drowning', (i.top_left[0], i.top_left[1] - 10), default_font, 1, yellow, 4)
            else:
                cv2.rectangle(frame, i.top_left, i.bot_right, yellow, 2)
                cv2.putText(frame, 'Swimming', (i.top_left[0], i.top_left[1] - 10), default_font, 1, yellow, 4)

        # Remove rescued individual from the tracking list
        if rescue_result is True:
            invididuals_in_frame.pop(remove_individual)

        # Display the processed frame
        cv2.imshow('WAVE', frame)
        # Exit the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture object and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
