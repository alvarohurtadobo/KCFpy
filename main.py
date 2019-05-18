import cv2
import sys
import argparse
import numpy as np 
from time import time

from lib.vehicle import Vehicle
from lib.background import Background

from lib.tools import rectangle_percentage_coincidence

parser = argparse.ArgumentParser(description = 'Introduce arguments to run the tracker')
parser.add_argument('-i', '--input',  type = str, default = None, help = 'Introduce the input video to analyse')
parser.add_argument('-W', '--width',  type = int, default = 0, help = 'Introduce the desired frame width')
parser.add_argument('-H', '--height', type = int, default = 0, help = 'Introduce the desired frame height')
args = parser.parse_args()

ix, iy, cx, cy = -1, -1, -1, -1
w, h = 0, 0

duration = 0.01


if __name__ == '__main__':
	
	if args.input == None:
		cap = cv2.VideoCapture('/home/alvaro/test/sar.mp4')
	else:
		if(args.input.isdigit()):
			cap = cv2.VideoCapture(int(args.input))
		else:
			cap = cv2.VideoCapture(args.input)

	myVehicles = [Vehicle(),Vehicle()]
	#if you use hog feature, there will be a short pause after you draw a first boundingbox, that is due to the use of Numba.
	ret, frame = cap.read()
	#frame = cv2.resize(frame,(80,60))
	myBackground = Background(frame, 4, False)

	cv2.namedWindow('tracking',cv2.WINDOW_NORMAL)

	auxiliar_time = time()

	while(cap.isOpened()):
		ret, frame = cap.read()
		new_objects = myBackground.detect(frame)
		sure_objects = [my_object['box'] for my_object in new_objects]

		most_objects = sure_objects
		"""
		last_area = 0
		for rectangle in sure_objects:
			_, _, w, h = rectangle
			new_area = w*h
			if new_area > last_area:
				last_area = new_area
				most_objects.append(rectangle)
			if len(most_objects)
		"""
		# If stated we change the working frame resolution
		if args.width and args.height:
			frame = cv2.resize(frame,(args.width,args.height))
		if not ret:
			break

		# Update
		myVehicles[0].update(frame)
		myVehicles[1].update(frame)
		if rectangle_percentage_coincidence(myVehicles[0].tracked_object_position,myVehicles[1].tracked_object_position) > 0.8:
			if myVehicles[1].area > myVehicles[0].area:
				myVehicles[1].kill()
			else:
				myVehicles[0].kill()
		# Plot updated objects
		cv2.rectangle(frame,myVehicles[0].plot_point1, myVehicles[0].plot_point2, (0,0,255), 3)
		cv2.putText(frame, 'ID: {} left {}, {}%'.format(myVehicles[0].vehicle_id,myVehicles[0]._life_span,int(100*myVehicles[0].rectangle_coincidence)), myVehicles[0].plot_point1, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50,50,50), 2)
		cv2.rectangle(frame,myVehicles[1].plot_point1, myVehicles[1].plot_point2, (0,255,0), 3)
		cv2.putText(frame, 'ID: {} left {}, {}%'.format(myVehicles[1].vehicle_id,myVehicles[1]._life_span,int(100*myVehicles[1].rectangle_coincidence)), myVehicles[1].plot_point1, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50,50,50), 2)

		if most_objects != []:
			# Feed and Purge
			remaining_rectangles = myVehicles[0].purge_rectangles(most_objects, frame)
			remaining_rectangles = myVehicles[1].purge_rectangles(remaining_rectangles, frame)

			if len(remaining_rectangles)>1:
				biggest_rectangle = remaining_rectangles[0]
				if (myVehicles[0].tracking == False):
					myVehicles[0].track_new_object(list(biggest_rectangle), frame)
				if (myVehicles[1].tracking == False):
					myVehicles[1].track_new_object(list(biggest_rectangle), frame)
				
				for rectangle in remaining_rectangles:
					ix, iy, w, h = rectangle	
					cv2.rectangle(frame,(ix,iy), (ix+w,iy+h), (220,220,220), 2)

		period = 1/(time() - auxiliar_time)
		cv2.putText(frame, 'FPS: {0:.2f}'.format(period), (8,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
		auxiliar_time = time()

		cv2.imshow('tracking', frame)
		c = cv2.waitKey(1) & 0xFF
		if c==27 or c==ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()
