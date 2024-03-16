from colorama import Fore, Style
from colorama import init as colorama_init
import cv2
import numpy as np
import patchify
import random
from .cnn_module import Cnn, CnnVgg16
from . import utils
from threading import Thread

colorama_init()

color_scale = [
    # value  BGR
    (0.9,    (0, 0, 255)),
    (0.7,    (200, 0, 205 )),
    (0.,      None)
    # (0. ,    (0, 255, 0))
]


# class MockedModel(object):
#     width = 224
#     height = 224
#     channels = 3
#     def predict(self, image, batch=False):
#         if batch:
#             # Should reduce 3 dimensions from input shape
#             # print(f"input array shape: {image.shape}")
#             return np.random.rand( 3, 6, 1)
#         else:
#             return random.random()

def getColor(predict):
    for threshold, color in color_scale:
        if(predict >= threshold):
            return color

class CrackDetector(utils.Subscribable):

    def __set_source(self, source):
        self.source = source
        self.source.subscribe(self.buffer_in.put)
        self.width = self.source.width
        self.height = self.source.height

    def __set_model(self, model):
        self.model = model

        if(model is None):
            # self.model = MockedModel()
            self.model = CnnVgg16()
            model_loadfile = "test101.keras"
            self.model.load_model(model_loadfile)
            # print(f"Crack detector model {type(self.model)} loaded with {model_loadfile}")

    def __init__(self, source:utils.Subscribable, model : Cnn = None):
        super().__init__()
        self.buffer_in = utils.Buffer(10)

        self.__set_source(source)
        self.__set_model(model)

        self._t_worker = Thread(target=self._worker_batch, daemon=True)
        self._t_worker.start()


    def _patch_coord(self, row, col):
        return (((row * self.model.width) + 1, (col * self.model.height) +1 ),
                ( ((row + 1) * self.model.width) - 2 , ((col + 1) * self.model.height) - 2 ))

    def _worker_batch(self):
        for frame in self.buffer_in.stream():
            # print(f"Process frame size {frame.shape}")
            """Step 1: Patchify the frame in patches"""
            curent_frame = frame.copy()
            patches = patchify.patchify(curent_frame, (self.model.width, self.model.height, self.model.channels), step=self.model.width )

            """Step 2: Predict each patch with cracks"""
            tile_x, tile_y =  (int(self.source.width / self.model.width) , int(self.source.height / self.model.height))

            shape = (tile_x * tile_y,
                     self.model.width,
                     self.model.height,
                     self.model.channels)   # (18, 224, 224, 3)
            predictions = self.model.predict(np.reshape(patches, shape), verbose=0) #, batch=True
            # print(Fore.RED + f"Prediction shape: {predictions.shape}" + Style.RESET_ALL)
            predictions = np.reshape(predictions, (tile_y, tile_x, 1))

            for idx_row, row in enumerate(predictions):
                for idx_col, col in enumerate(row):
                    for prediction in col:

                        color = getColor(prediction)
                        if color is None: # No color -> no grid drawing
                            continue

                        """Step 3: Apply visualisation to positive patches"""
                        pt1, pt2 = self._patch_coord(idx_col, idx_row)
                        # print(f"idx_row:\t{idx_row}\tidx_col:{idx_col}.\tpt1:{pt1}\t-\tpt2:{pt2}")
                        cv2.rectangle(curent_frame, pt1, pt2, color=color, thickness=2 )

            """Step 4: Stitch up! (unpatchify)"""
            processed_frame = patchify.unpatchify(patches, frame.shape)

            """Step 5: Publish the results to subscribers"""
            # print(f"Done with this frame.")
            self.publish(processed_frame)


    # def _worker(self):
    #     for frame in self.buffer_in.stream():
    #         # print(f"Process frame size {frame.shape}")
    #         """Step 1: Patchify the frame in patches"""
    #         patches = patchify.patchify(frame.copy(), (self.model.width, self.model.height, self.model.channels), step=224 )

    #         """Step 2: Predict each patch with cracks"""
    #         print(f"Process {(len(patches), patches.shape)} patches for this frame")
    #         for row in patches:
    #             for col in row:
    #                  for patch in col:
    #                     # print(f"patch size: {patch.shape}")
    #                     # print(patch)

    #                     results = self.model.predict(col)
    #                     print(f"predict results shape: {results.shape}")

    #                     if results[0][0] > 0.5:
    #                         color = (0, 255, 0) # GREEN
    #                     else:
    #                         color = (0, 0, 255) # RED
    #                     patch.setflags(write=1)

    #                     """Step 3: Apply visualisation to positive patches"""
    #                     cv2.rectangle(patch, (1, 1), (self.model.width -2, self.model.height -2), color=color, thickness=2 )
    #                     # print("done drawing")


    #         """Step 4: Stitch up! (unpatchify)"""
    #         processed_frame = patchify.unpatchify(patches, frame.shape)

    #         """Step 5: Publish the results to subscribers"""
    #         # print(f"Done with this frame.")
    #         self.publish(processed_frame)
