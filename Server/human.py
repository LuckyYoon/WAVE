class Human:
    def __init__(self, top_left, bot_right, center):
        """
        Initializes a new Human object representing an individual detected in the video frame.

        :param top_left: The top-left coordinates of the bounding box around the detected individual.
        :param bot_right: The bottom-right coordinates of the bounding box around the detected individual.
        :param center: The center coordinates of the bounding box around the detected individual.

        The Human class tracks various attributes of an individual detected in the surveillance area,
        such as their location, whether they are in a restricted zone, their drowning status, and if they are a target for rescue.
        """

        self.top_left = top_left  # Top-left coordinates of the bounding box
        self.bot_right = bot_right  # Bottom-right coordinates of the bounding box
        self.center = center  # Center coordinates of the bounding box

        self.in_restricted_zone = False  # Flag to indicate if the individual is in a restricted zone
        self.restricted_zone_entry_time = None  # Time when the individual entered the restricted zone (if applicable)

        self.drowning_detection_time = None  # Time when potential drowning was first detected
        self.drowning_detection_bool = []  # List to track successive drowning detections (True/False)

        self.recent_bool_added = False  # Flag to indicate if a new detection was recently added to drowning_detection_bool
        self.target = False  # Flag to indicate if the individual is a target for rescue operations
