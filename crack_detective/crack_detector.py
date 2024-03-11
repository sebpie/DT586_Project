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

    def __set_source(self, source):
        self.source = source
        self.source.subscribe(self.buffer_in.put)
        self.width = self.source.width
        self.height = self.source.height

    def __set_model(self, model):
        self.model = model

        if(model is None):
            self.model = MockedModel()

    def __init__(self, source:utils.Subscribable, model : MockedModel = None):
        super().__init__()
        self.buffer_in = utils.Buffer(10)

        self.__set_source(source)
        self.__set_model(model)

        self._t_worker = Thread(target=self._worker, daemon=True)
        self._t_worker.start()

    def _worker(self):
        for frame in self.buffer_in.stream():
            # print(f"Process frame size {frame.shape}")
            """Step 1: Patchify the frame in patches"""
            patches = patchify.patchify(frame.copy(), (self.model.width, self.model.height, self.model.channels), step=224 )

            """Step 2: Predict each patch with cracks"""
            # print(f"Process {(len(patches), patches.shape)} patches for this frame")
            for row in patches:
                for col in row:
                    for patch in col:
                        # print(f"patch size: {patch.shape}")
                        # print(patch)
                        if self.model.predict(patch) > 0.5:
                            color = (0, 255, 0) # GREEN
                        else:
                            color = (0, 0, 255) # RED
                        patch.setflags(write=1)

                        """Step 3: Apply visualisation to positive patches"""
                        cv2.rectangle(patch, (0, 0), (self.model.width, self.model.height), color=color, thickness=2 )
                        # print("done drawing")


            """Step 4: Stitch up! (unpatchify)"""
            processed_frame = patchify.unpatchify(patches, frame.shape)

            """Step 5: Publish the results to subscribers"""
            # print(f"Done with this frame.")
            self.publish(processed_frame)
