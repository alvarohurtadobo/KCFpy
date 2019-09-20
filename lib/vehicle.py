#! /home/alvaro/virtualenv/lucam/bin/python3.6
from time import time
import lib.kcftracker as kcftracker
from lib.tools import rectangle_percentage_coincidence

class Vehicle():
    # Class variables
    last_vehicle_id = 0
    all_used = False
    initial_life_span = 30
    last_update_time = time()

    def __init__(self):
        # Declare variables to be used
        self.vehicle_id = 0
        self.external_object_position = [0,0,0,0]
        self.tracked_object_position = [0,0,0,0]
        self.confirmed_vehicle = False
        self.tracking = False
        self.plot_point1 = (0,0)
        self.plot_point2 = (0,0)
        self.rectangle_coincidence = 0
        self.area = 0
        self._life_span = Vehicle.initial_life_span            # 10 frames update and delete
        self.tracker = kcftracker.KCFTracker(False, True, True)  # hog, fixed_window, multiscale

    def track_new_object(self, point_list, frame):
        # When tracking new objects:
        # Give an ID
        self.vehicle_id = Vehicle.last_vehicle_id
        Vehicle.last_vehicle_id = Vehicle.last_vehicle_id + 1
        #print('Creating new object {}'.format(self.vehicle_id))
        # Init points to track
        #print('Core problem: ',point_list)
        self.tracker.init(point_list, frame)
        # Increase life span to origin
        self._life_span = Vehicle.initial_life_span
        # Set status to tracking
        self.tracking = True
        print("Tracking new object {}".format(self.vehicle_id))

    def update(self, frame):
        # Update current tracker according to current frame
        if sum(self.tracker._roi)==0:
            self.plot_point1 = (0,0)
            self.plot_point2 = (0,0)
            return self.tracker._roi

        self.tracked_object_position = self.tracker.update(frame)
        self.plot_point1 = (int(self.tracked_object_position[0]),
                            int(self.tracked_object_position[1]))
        self.plot_point2 = (int(self.tracked_object_position[0]+self.tracked_object_position[2]),
                            int(self.tracked_object_position[1]+self.tracked_object_position[3]))
        self.area = self.tracked_object_position[2] * self.tracked_object_position[3]
        return self.tracked_object_position

    def purge_rectangles(self, remaining_rectangles, frame):
        # The object drops the one rectangle with the biggest area:
        # The list of remaining rectangles stay
        self.external_object_position = [0,0,0,0]
        print("Received list: {}".format(remaining_rectangles))
        self._life_span -= 1
        new_remaining_rectangles = []
        for index in range(len(remaining_rectangles)):
            rectangle = remaining_rectangles[index]
            #if rectangle_already_tracked([self.tracker._roi],rectangle):
            print("Comparing {} with {}".format(self.tracker._roi, rectangle))
            self.rectangle_coincidence = rectangle_percentage_coincidence(self.tracker._roi, rectangle)
            if self.rectangle_coincidence > 0.6:
                self.external_object_position = rectangle
                self._life_span += 1
                if self.rectangle_coincidence > 0.8:
                    # If the coincidence is high enough we reset the object
                    print("Rectangle {} matches".format(rectangle))
                    self._life_span = Vehicle.initial_life_span
                    self.tracker.init(self.external_object_position, frame)                    
                #del remaining_rectangles[index]
                # break here to only drop one object at a time
            elif self.rectangle_coincidence < 0.2:
                new_remaining_rectangles.append(rectangle)

        if self._life_span <= 0:
            self.kill()
            #print('Removing object {}'.format(self.vehicle_id))

        print("Returned list: {}".format(new_remaining_rectangles))
 
        return new_remaining_rectangles

    def kill(self):
        self._life_span = 0
        self.tracker._roi = (0.0,0.0,0.0,0.0)
        self.tracking = False
        if self.tracking:
            print("Stopped tracking object {}".format(self.vehicle_id))


