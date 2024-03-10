import cv2
import numpy as np
import patchify
import random
from . import utils
from threading import Thread

class MockedModel(object):
    width = 224
    height = 224
    channels = 3
    def predict(self, image):
        return random.random()


class CrackDetector(utils.Subscribable):
    buffer_in = utils.Buffer(10)
    buffer_out = utils.Buffer(10)

    def __init__(self, source:utils.Subscribable, model : MockedModel = None):
        self.source = source
        source.subscribe(self.buffer_in.put)
        self.model = model

        if(model is None):
            self.model = MockedModel()

        self._t_worker = Thread(target=self._worker, daemon=True)
        self._t_worker.start()

    def _worker(self):
        for frame in self.buffer_in.stream():
            """Step 1: Patchify the frame in patches"""
            patches = patchify.patchify(frame, (self.model.width, self.model.height, self.model.channels), step=1 )

            """Step 2: Predict each patch with cracks"""
            # prediction_matrix = self.model.predict(patches)

            """Step 3: Apply visualisation to positive patches"""
            # draw box outline

            """Step 4: Stitch up! (unpatchify)"""
            processed_frame = patchify.unpatchify(patches, frame.shape)

            """Step 5: Publish the results to subscribers"""
            self.publish(processed_frame)
