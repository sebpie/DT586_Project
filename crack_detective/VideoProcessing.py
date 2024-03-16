from threading import Thread
import ffmpeg
import math
import numpy as np
from colorama import Fore, Style
from colorama import init as colorama_init
from .utils import Subscribable

DEFAULT_URL="rtmp://0.0.0.0:8000/live/stream"
DEFAULT_WIDTH=1280
DEFAULT_HEIGHT=720
DEFAULT_PXLFMT='bgr24'
PIXEL_SIZE= { "bgr24": 3, }

DEFAULT_MODEL_INPUTSHAPE=(224,224,3)

colorama_init()


class RTMPServer(Subscribable):
    ffmpeg_process = None
    _t_framegrabber: Thread = None

    def __init__(self,
                 url=None,
                 pix_fmt=DEFAULT_PXLFMT,
                 width=DEFAULT_WIDTH,
                 height=DEFAULT_HEIGHT,
                 model_inputshape=None,
                 src_inputshape=None,
                 ffmpeg_path=None) -> None:

        super().__init__()

        self.url = url or DEFAULT_URL
        self.pxl_fmt = pix_fmt or DEFAULT_PXLFMT
        self.width = width or DEFAULT_WIDTH
        self.height = height or DEFAULT_WIDTH
        self.ffmpeg_path=ffmpeg_path
        self.model_inputshape = model_inputshape or DEFAULT_MODEL_INPUTSHAPE
        self.src_inputshape=src_inputshape or (1280, 720, 3)


    def _framegrabber(self):
        print(f"--thread framegrabber--")
        while True:
            in_bytes = self.ffmpeg_process.stdout.read(self.width * self.height * PIXEL_SIZE[self.pxl_fmt])

            if self.ffmpeg_process.poll() is not None:
                print(Fore.RED + "ffmpeg process is dead." + Style.RESET_ALL)
                break

            if len(in_bytes) == 0:
                print(f"Error reading from FFMPEG. poll: {self.ffmpeg_process.poll()}")
                continue

            frame = np.frombuffer(in_bytes, np.uint8).reshape([self.height, self.width, PIXEL_SIZE[self.pxl_fmt]])

            if type(frame) is not np.ndarray:
                print(Fore.Yellow + f"couldnt convert frame to 'numpy.ndarray'" + Style.RESET_ALL)
            else:
                self.publish(frame)

        print(Fore.YELLOW  + "restarting ffmpeg" + Style.RESET_ALL)
        self.start()


    def preprocess_croppadding(self):
        # PREVIOUS CODE
            # .filter("pad", width=6*224, height=4*224, x=(1280-6*224)/2, y=0, color="green")
            # .filter("crop", w=6*224, h=3*224, x=0, y=(720-3*224)/2)

        print(f"width:{self.src_inputshape[0]}, height:{self.src_inputshape[1]}, grid: ({self.model_inputshape})")

        def padding_ratio(padd, length, grid):
            padding = padd - length
            return padding / grid

        def offset(padd, length, grid):
            # padding = padd - length
            # padding_ratio = padding / grid
            # print(f"padd: {padd}, length: {length}, grid: {grid} -> padding: {padding} -> ratio: {padding_ratio}")

            if padding_ratio(padd, length, grid) < 0.5:
                # last box is filled mostly with padding
                pad_offset = int((padd - length )/2)
                crop_offset = int((padd - length)/2)  #(720-3*224)/2)
            else:
                # last box is mostly filled with image
                pad_offset = 0
                crop_offset = 0

            return pad_offset, crop_offset

        def tiles(pad, length, grid):
            if padding_ratio(pad, length, grid) < .5:
                return int(pad/grid)
            else:
                return int(pad/grid) -1

        pad_args = {
            "width" : math.ceil(self.src_inputshape[0] / self.model_inputshape[0]) * self.model_inputshape[0],
            "height": math.ceil(self.src_inputshape[1] / self.model_inputshape[1]) * self.model_inputshape[1],
            "x"     : 0,
            "y"     : 0,
        }

        tiles_x = tiles(pad_args["width"], self.src_inputshape[0], self.model_inputshape[0])
        tiles_y = tiles(pad_args["height"], self.src_inputshape[1], self.model_inputshape[1])

        print(f"tiling: {tiles_x} x {tiles_y}")
        crop_args = {
            "w": int(tiles_x * self.model_inputshape[0]),
            "h": int(tiles_y * self.model_inputshape[1]),
            "x": 0,
            "y": 0
        }

        pad_args["x"], crop_args["x"] = offset(pad_args["width"], self.src_inputshape[0], self.model_inputshape[0])
        pad_args["y"], crop_args["y"] = offset(pad_args["height"], self.src_inputshape[1], self.model_inputshape[1])

        return pad_args, crop_args, tiles_x, tiles_y


    def start(self):

            print(f"Start ffmpeg subprocess to capture {self.url}.")

            pad_args, crop_args, self.tiles_x, self.tiles_y = self.preprocess_croppadding()

            print(Fore.RED + f"padding: {pad_args}" + Style.RESET_ALL)
            print(Fore.RED + f"cropping: {crop_args}" + Style.RESET_ALL)
            self.width = crop_args["w"]
            self.height = crop_args["h"]

            args = {"pipe_stdout" : True}
            if self.ffmpeg_path:
                args["cmd"] = self.ffmpeg_path
            self.ffmpeg_process = (
                ffmpeg
                .input(self.url, listen=1)
                .filter("fps", fps=30, round="up")
                .filter("pad", color="green", **pad_args)
                .filter("crop", **crop_args)
                .output('pipe:',
                        format='rawvideo',
                        pix_fmt=self.pxl_fmt,
                        s=f'{self.width}x{self.height}')
                .global_args("-nostdin", "-hide_banner", "-loglevel", "warning")
                .run_async(**args)
            )
            print(Fore.GREEN + f"ffmpeg is running. {Style.RESET_ALL}. {self.ffmpeg_process}.")
            # print(f"start thread to buffer ffmpeg output")
            self._t_framegrabber = Thread(target=self._framegrabber, daemon=True)
            self._t_framegrabber.start()
