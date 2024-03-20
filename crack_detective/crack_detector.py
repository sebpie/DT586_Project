from colorama import Fore, Style
from colorama import init as colorama_init
import cv2
import numpy as np
import patchify
from .cnn_module import Cnn, CnnVgg16
from . import utils
from threading import Thread

colorama_init()

color_scale = [
    # value  BGR
    (0.9,    (0,    0,   255)),     # Red
    (0.7,    (200,  0,   205 )),    # Purple
    # (0.5,    (105,  105, 105)),     # Grey
    (0.,      None)
    # (0. ,    (0, 255, 0))
]


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
        print(Fore.GREEN + f"Crack_Detector is READY." + Style.RESET_ALL)

    def _patch_coord(self, row, col):
        return (((col * self.model.width) + 1, (row * self.model.height) +1 ),
                ( ((col + 1) * self.model.width) - 2 , ((row + 1) * self.model.height) - 2 ))

    def box_label(self, frame, row, col, predictions=None):
        ((left, top), (right, bottom)) = (pt1, pt2) = self._patch_coord(row, col)
        print(f"coord: {(pt1, pt2)}")
        x = min(left, right) + col # * abs(pt1[0] -pt2[0])
        #y = int(abs(pt2[1] - pt1[1])/2) # + row * abs(pt2[1]-pt1[1])

        y = max(top, bottom) - 20

        # print(f"x: {x}, y:{y}")
        fontScale=.3
        color=(255, 0, 0)
        thickness = 1
        org = (x, y)
        # print(f"org: {org} - {left} - {right}")
        cv2.putText(frame, f"{(row, col)}", org, cv2.FONT_HERSHEY_SIMPLEX, fontScale, color, thickness, cv2.LINE_AA, False )

        if predictions is not None:
            value = predictions[row][col]
            fontScale = 0.5
            if value > 0.9:
                color = (0, 0, 255)
            else:
                color = (255, 255, 255)
            org = (x + 10, y -40)
            cv2.putText(frame, f"{value:.2f}", org, cv2.FONT_HERSHEY_SIMPLEX, fontScale, color, thickness, cv2.LINE_AA, False )

        return


    def _draw_borders(self, frame, predictions, row, col, thickness=2):
        # (top, right, bottom, left) = (False, False, False, False)
        last_row = predictions.shape[0] -1
        last_col = predictions.shape[1] -1

        (top_border, right_border, bottom_border, left_border) = (False, False, False, False)
        ((left, top), (right, bottom)) = (pt0, pt1) = self._patch_coord(row, col)

        # print(f"DRAW BORDER for {(row, col)}. bbox (left, top, right, bottom): {(left, top, right, bottom)}")


        def get_prediction(predictions, row, col):
            return predictions[row][col]

        prediction = get_prediction(predictions, row, col)

        color = getColor(prediction)
        if color is not None: # No color -> no grid drawing

                        # pt1, pt2 = self._patch_coord(idx_col, idx_row)
                        # # print(f"idx_row:\t{idx_row}\tidx_col:{idx_col}.\tpt1:{pt1}\t-\tpt2:{pt2}")
                        # cv2.rectangle(current_frame, pt1, pt2, color=color, thickness=2 )

            # cv2.rectangle(frame, ( top + 10, left + 10), (bottom -10, right - 10), color=color, thickness=2 )

            # print(f"frame shape: {frame.shape} vs prediction shape: {predictions.shape}")

            RED     = (0,   0,      255)
            YELLOW  = (0,   255,    255)
            BLUE    = (255, 0,      0)
            BLACK   = (0,   0,      0)
            WHITE   = (255, 255,    255)

            debug_color = {
                "top":      RED,
                "bottom" : YELLOW,
                "left"  : BLUE,
                "right" : WHITE
            }

            # top
            if row == 0 :
                top_border = True
                tcolor = (0, 255, 0)

            elif getColor(get_prediction(predictions, row=row -1, col=col)) != color:
                tcolor = (255, 0, 0)
                top_border = True

            if top_border == True:
                cv2.line(frame, (left, top), (right, top), color, thickness=thickness )


            # right
            if col == last_col:
                right_border = True
            else:
                if getColor( get_prediction(predictions, row= row, col = col+1 ) ) != color:
                    right_border = True
            if right_border:
                cv2.line(frame, (right, top), (right, bottom) , color, thickness=thickness )


            # bottom
            if row == last_row:
                bottom_border = True
            elif getColor(get_prediction(predictions, row=row +1, col=col) ) != color:
                bottom_border = True
            if bottom_border:
                cv2.line(frame, (left, bottom), (right, bottom), color, thickness=thickness )

            # left
            if col == 0:
                left_border = True
            elif getColor(get_prediction(predictions, row= row, col = col - 1) ) != color:
                left_border = True
            if left_border:
                cv2.line(frame, (left, top), (left, bottom), color, thickness=thickness )


        return (top_border, right_border, bottom_border, left_border)


    def _worker_batch(self):
        print(Fore.BLUE + f"(thread) crack_detector thread started.")
        for frame in self.buffer_in.stream():
            # print(f"Process frame size {frame.shape}")
            """Step 1: Patchify the frame in patches"""
            current_frame = frame.copy()
            patches = patchify.patchify(current_frame, (self.model.width, self.model.height, self.model.channels), step=self.model.width )

            """Step 2: Predict each patch with cracks"""
            # tile_x, tile_y =  (int(self.source.width / self.model.width) , int(self.source.height / self.model.height))
            tile_x, tile_y, *_ = patches.shape

            shape = (tile_x * tile_y,
                     self.model.width,
                     self.model.height,
                     self.model.channels)   # (18, 224, 224, 3)
            predictions = self.model.predict(np.reshape(patches, shape), verbose=0) #, batch=True
            predictions_shape = predictions.shape
            predictions = np.reshape(predictions, (tile_x, tile_y))

            # print(Fore.RED + f"Current frame shape: {current_frame.shape}" + Style.RESET_ALL)
            # print(Fore.RED + f"Patches shape: {patches.shape}" + Style.RESET_ALL)
            # print(Fore.RED + f"Patches reshaped to: {shape}" + Style.RESET_ALL)
            # print(Fore.RED + f"Prediction shape: {predictions_shape}" + Style.RESET_ALL)
            # print(Fore.RED + f"Prediction reshaped to: {predictions.shape}" + Style.RESET_ALL)

            for idx_row, row in enumerate(predictions):
                # print(f"enumerating row. Current {idx_row}, shape: {row.shape}")
                for idx_col, col in enumerate(row):
                    # for prediction in col:


                        """Step 3: Apply visualisation to positive patches"""
                        self._draw_borders(current_frame, predictions, idx_row, idx_col)
                        # self.box_label(current_frame,  idx_row, idx_col, predictions=predictions)

                        # pt1, pt2 = self._patch_coord(idx_col, idx_row)
                        # # print(f"idx_row:\t{idx_row}\tidx_col:{idx_col}.\tpt1:{pt1}\t-\tpt2:{pt2}")
                        # cv2.rectangle(current_frame, pt1, pt2, color=color, thickness=2 )

            """Step 4: Stitch up! (unpatchify)"""
            processed_frame = patchify.unpatchify(patches, frame.shape)

            """Step 5: Publish the results to subscribers"""
            # print(f"Done with this frame.")
            self.publish(processed_frame)
