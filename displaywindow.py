from Xlib import display, X
import Xlib
import numpy as np
import cv2
class DisplayWindow:
    def __init__(self, window_id):
        self.d = display.Display()
        self.window = self.d.create_resource_object('window', window_id)

    def get_pixel_rgb(self, pos):
        raw = self.window.get_image(int(pos[0]), int(pos[1]), 1, 1, Xlib.X.ZPixmap, 0xffffffff)
        rgb = raw.data
        r, g, b = rgb[2], rgb[1], rgb[0]  # Pygame color channels are reversed compared to Xlib
        return (r, g, b)
    def take_screenshot(self):
        geometry = self.window.get_geometry()
        width, height = geometry.width, geometry.height

        raw = self.window.get_image(0, 0, width, height, X.ZPixmap, 0xffffffff)

        # Create a numpy array from the raw data
        image = np.ndarray(shape=(height, width, 4), dtype=np.uint8, buffer=raw.data)

        # Convert to BGR color order (assuming RGBA input)
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)

        return image_bgr, width, height
