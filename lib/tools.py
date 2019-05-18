"""
Some tools

"""

def rectangle_percentage_coincidence(reference_rectangle, rectangle):
    # The rectangles must be in the form: x, y, w, h
    # The next three lines calculate the overlap area between the two rectangles:
    # Reference rectangle:
    best_x_min, best_y_min = reference_rectangle[0], reference_rectangle[1]
    best_x_max, best_y_max = best_x_min + reference_rectangle[2], best_y_min + reference_rectangle[3]
    reference_area = (best_x_max - best_x_min) * (best_y_max - best_y_min)

    # Overlap rectangle:
    x0, y0, x1, y1 =  rectangle[0], rectangle[1], rectangle[0] + rectangle[2], rectangle[1]+ rectangle[3]
    x_overlap = max(0, min(x1, best_x_max) - max(x0, best_x_min))
    y_overlap = max(0, min(y1, best_y_max) - max(y0, best_y_min))
    overlapArea = x_overlap * y_overlap
    if reference_area == 0:
        return 0
    coincidence = overlapArea/reference_area
    #print('Overlap area: {}/ Reference: {} = {}'.format(overlapArea,reference_area,coincidence))
    return coincidence

def tracker_already_tracked(trackers, rectangle):
    for tracker in trackers:
        if rectangle_percentage_coincidence(tracker._roi, rectangle) > 0.7:
            return True 
    return False

def rectangle_already_tracked(rectangles, rectangle):
    """
    The rectangle comes in the form x, y, w, h
    """
    for current_rectangle in rectangles:
        if rectangle_percentage_coincidence(current_rectangle, rectangle) > 0.6:
            return True 
    return False