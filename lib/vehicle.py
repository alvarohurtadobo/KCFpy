import lib.kcftracker as kcftracker
from lib.tools import rectangle_already_tracked

class Vehicle():
    # Class variables
    last_vehicle_id = 0
    all_used = False

    def __init__(self):
        vehicle_id = 0
        self.tracker = kcftracker.KCFTracker(True, True, True)  # hog, fixed_window, multiscale
        pass

    def set_point(self, point_list, frame ):
        self.tracker.init(point_list, frame)

    def update(self, frame):
        return self.tracker.update(frame)

    def purge_rectangles(self, rectangles_list):
        remaining_rectangles = []
        dropped_rectangles = []
        for rectangle in rectangles_list:
            if rectangle_already_tracked([self.tracker._roi],rectangle):
                dropped_rectangles.append(rectangle)
            else:
                remaining_rectangles.append(rectangle)
        return remaining_rectangles, dropped_rectangles


