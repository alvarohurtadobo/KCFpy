# 

# Simple Background substration class, this class emulates the object detection with output alike:
# [{'box': [84, 39, 99, 117], 'confidence': 0.9924306273460388, 'keypoints': {'left_eye': (104, 83), 'right_eye': (148, 75), 'nose': (123, 104), 'mouth_left': (118, 133), 'mouth_right': (153, 127)}}]

# This code is tested on Opencv 4.1.0

import cv2
import numpy as np

class Background():
    def __init__(self, image = None, scale = 1, show = False):
        # Storing variables
        self.scaleFactor = scale
        self.show = show
        if image.any():
            self._width = image.shape[0]
            self._height = image.shape[1]

        #Auxiliar parameters
        self.fgbgNew = cv2.createBackgroundSubtractorMOG2()

        self.w_min = int(0.4*self._width//self.scaleFactor//2)
        self.h_min = int(0.4*self._height//self.scaleFactor//2)
        self.h_max = int(1.4*self._width//self.scaleFactor//2)
        self.w_max = int(1.4*self._height//self.scaleFactor//2)

        self.optimal_step = 1

        self.imagenActual = np.zeros((self._width//self.scaleFactor,self._height//self.scaleFactor,3))
        self.low_resolution_image = cv2.resize(image,(int(self._width//self.scaleFactor),int(self._height//self.scaleFactor)))

    def detect(self,imagenActual):
        #self.imagenActual = cv2.cvtColor(imagenActual,cv2.COLOR_BGR2GRAY)
        if self.scaleFactor != 1:
            # If the we do not state a resolution scale we do not need to resize
            self.low_resolution_image = cv2.resize(imagenActual,(imagenActual.shape[1]//self.scaleFactor,imagenActual.shape[0]//self.scaleFactor))
        else:
            self.low_resolution_image = imagenActual
        
        self.imagenActual = cv2.GaussianBlur(self.low_resolution_image,(17,17),0)
        #self.imagenActualBS = cv2.medianBlur(self.imagenActualBS,11,0)
        #self.imagenActualBS = cv2.morphologyEx(self.imagenActualBS, cv2.MORPH_OPEN, self.kernel)
        fgmask = self.fgbgNew.apply(self.imagenActual)
        
        #fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, self.kernel)
        if self.show:
            cv2.imshow('Mask', fgmask)
        if cv2.__version__.startswith("3."):
            _, contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)  #,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        else:
            contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)  #,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        rectangles = []
        for (index, contour) in enumerate(contours):
            (x, y, w, h) = cv2.boundingRect(contour)
            confidence = 0.5
            # We add to our list the appropriate sizes only
            if ((h > self.h_min) or (w > self.w_min)) and ((h < self.h_max) or (w < self.w_max)):
                confidence = 0.9
                rectangles.append({'box': [self.scaleFactor*x, self.scaleFactor*y, self.scaleFactor*w, self.scaleFactor*h], 'confidence': confidence, 'keypoints': {'mid_point': (x+w//2, y+h//2), 'plate': (x+w//2, y+3//4*h)}})
                #if self.show:
                #    self.low_resolution_image = cv2.rectangle(self.low_resolution_image, (x,y), (x+w,y+h), (255,255,255), 2, -1)
            else:
                confidence = 0.3
            
        return rectangles

    def get_low_resolution_image(self):
        return self.low_resolution_image

