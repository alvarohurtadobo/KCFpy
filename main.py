import cv2
import sys
import argparse
import numpy as np 
from time import time

from lib.vehicle import Vehicle
from lib.background import Background

parser = argparse.ArgumentParser(description = 'Introduce arguments to run the tracker')
parser.add_argument('-i', '--input',  type = str, default = None, help = 'Introduce the input video to analyse')
parser.add_argument('-W', '--width',  type = int, default = 0, help = 'Introduce the desired frame width')
parser.add_argument('-H', '--height', type = int, default = 0, help = 'Introduce the desired frame height')
args = parser.parse_args()

selectingObject = False
initTracking = False
onTracking = False
ix, iy, cx, cy = -1, -1, -1, -1
w, h = 0, 0

duration = 0.01

# mouse callback function
def draw_boundingbox(event, x, y, flags, param):
	global selectingObject, initTracking, onTracking, ix, iy, cx,cy, w, h
	
	if event == cv2.EVENT_LBUTTONDOWN:
		selectingObject = True
		onTracking = False
		ix, iy = x, y
		cx, cy = x, y
	
	elif event == cv2.EVENT_MOUSEMOVE:
		cx, cy = x, y
	
	elif event == cv2.EVENT_LBUTTONUP:
		selectingObject = False
		if(abs(x-ix)>10 and abs(y-iy)>10):
			w, h = abs(x - ix), abs(y - iy)
			ix, iy = min(x, ix), min(y, iy)
			initTracking = True
		else:
			onTracking = False
	
	elif event == cv2.EVENT_RBUTTONDOWN:
		onTracking = False
		if(w>0):
			ix, iy = int(x-w/2), int(y-h/2)
			initTracking = True



if __name__ == '__main__':
	
	if args.input == None:
		cap = cv2.VideoCapture('/home/alvaro/test/sar.mp4')
	else:
		if(args.input.isdigit()):
			cap = cv2.VideoCapture(int(args.input))
		else:
			cap = cv2.VideoCapture(args.input)

	myVehicles = [Vehicle()]
	#tracker = kcftracker.KCFTracker(True, True, True)  # hog, fixed_window, multiscale
	#if you use hog feature, there will be a short pause after you draw a first boundingbox, that is due to the use of Numba.
	ret, frame = cap.read()
	myBackground = Background(frame, 4, False)

	cv2.namedWindow('tracking',cv2.WINDOW_NORMAL)
	cv2.setMouseCallback('tracking',draw_boundingbox)

	while(cap.isOpened()):
		ret, frame = cap.read()
		new_objects = myBackground.detect(frame)
		print('Detected {} objects'.format(len(new_objects)))
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

		if most_objects != []:
			remaining_rectangles, dropped_rectangles = myVehicles[0].purge_rectangles(most_objects)
			for rectangle in remaining_rectangles:
				ix, iy, w, h = rectangle
				#cv2.rectangle(frame,(ix,iy), (ix+w,iy+h), (200,200,200), 2)
				print('Rectangle problem: ',rectangle)
				cv2.rectangle(frame,(ix,iy), (ix+w,iy+h), (0,255,255), 1)
				myVehicles[0].set_point([ix,iy,w,h], frame)
				#tracker.init([ix,iy,w,h], frame)
				print('Not tracked')
				onTracking = True

			"""
			for rectangle in most_objects:
				ix, iy, w, h = rectangle
				#cv2.rectangle(frame,(ix,iy), (ix+w,iy+h), (200,200,200), 2)
				
				if srectangle_already_tracked([tracker._roi],rectangle):
					print('Already tracked',[tracker._roi],rectangle)
				else:
					print('Rectangle problem: ',rectangle)
					cv2.rectangle(frame,(ix,iy), (ix+w,iy+h), (0,255,255), 1)
					tracker.init([ix,iy,w,h], frame)
					print('Not tracked')
					onTracking = True
			"""

		if(selectingObject):
			#cv2.rectangle(frame,(ix,iy), (cx,cy), (0,255,255), 1)
			pass
		elif(initTracking):
			#cv2.rectangle(frame,(ix,iy), (ix+w,iy+h), (0,255,255), 1)
			#tracker.init([ix,iy,w,h], frame)
			initTracking = False
			onTracking = True
		elif(onTracking):
			t0 = time()
			boundingbox = myVehicles[0].update(frame)
			print('Updated')
			t1 = time()

			boundingbox = list(map(int, boundingbox))
			cv2.rectangle(frame,(boundingbox[0],boundingbox[1]), (boundingbox[0]+boundingbox[2],boundingbox[1]+boundingbox[3]), (0,0,255), 3)
			
			#duration = 0.8*duration + 0.2*(t1-t0)
			duration = t1-t0
			cv2.putText(frame, 'FPS: '+str(1/duration)[:4].strip('.'), (8,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

		cv2.imshow('tracking', frame)
		c = cv2.waitKey(1) & 0xFF
		if c==27 or c==ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()
