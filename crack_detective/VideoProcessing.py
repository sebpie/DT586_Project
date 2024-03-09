from queue import Queue
from threading import Thread
from typing import Callable
import cv2
import ffmpeg
import numpy as np
from colorama import Fore, Style
from colorama import init as colorama_init

DEFAULT_URL="rtmp://0.0.0.0:8000/live/stream"
DEFAULT_BUFFER_SIZE=60 # 2s at 30fps
DEFAULT_WIDTH=1280
DEFAULT_HEIGHT=720
DEFAULT_COLOR='bgr24'
PIXEL_SIZE= { "bgr24": 3, }

colorama_init()

class VideoProcessor(object):
    ffmpeg_process = None
    _t_framegrabber: Thread = None

    def __init__(self,
                 url=None,
                 color=DEFAULT_COLOR,
                 width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT,
                #  framebuffer_size=DEFAULT_BUFFER_SIZE,
                 ffmpeg_path=None) -> None:
        self.url = url or DEFAULT_URL
        self.color = color or DEFAULT_COLOR
        self.width = width or DEFAULT_WIDTH
        self.height = height or DEFAULT_WIDTH
        # self.frame_buffer = Queue(maxsize=framebuffer_size)
        self.ffmpeg_path=ffmpeg_path

        # subscribers: a lit of callback methods that consumers register.
        self.subscribers = []

        print(f"New instance of VideoProcessor: {self.__dict__}")

    def _framegrabber(self):
        print(f"--thread framegrabber--")
        while True:
            in_bytes = self.ffmpeg_process.stdout.read(self.width * self.height * PIXEL_SIZE[self.color])

            if self.ffmpeg_process.poll() is not None:
                print(Fore.RED + "ffmpeg process is dead." + Style.RESET_ALL)
                break

            if len(in_bytes) == 0:
                print(f"Error reading from FFMPEG. poll: {self.ffmpeg_process.poll()}")
                continue

            frame = np.frombuffer(in_bytes, np.uint8).reshape([self.height, self.width, PIXEL_SIZE[self.color]])

            if type(frame) is not np.ndarray:
                print(Fore.Yellow + f"couldnt convert frame to 'numpy.ndarray'" + Style.RESET_ALL)
            else:
                for callback in self.subscribers:
                    callback(frame)
        print(Fore.YELLOW  + "restarting ffmpeg" + Style.RESET_ALL)
        self.start()


    def start(self):

        if self.url.startswith("rtmp://"):
            print(f"Start ffmpeg subprocess to capture {self.url}.")
            args = {"pipe_stdout" : True}
            if self.ffmpeg_path:
                args["cmd"] = self.ffmpeg_path
            self.ffmpeg_process = (
                ffmpeg
                .input(self.url, listen=1)
                .filter("fps", fps=30, round="up")
                .output('pipe:',
                        format='rawvideo',
                        pix_fmt=self.color,
                        s=f'{self.width}x{self.height}')
                .global_args("-nostdin", "-hide_banner", "-log_level", "warning")
                .run_async(**args)
            )
            print(f"ffmpeg is running: {self.ffmpeg_process}. Poll(): {self.ffmpeg_process.poll()}")
            print(f"start thread to buffer ffmpeg output")
            self._t_framegrabber = Thread(target=self._framegrabber, daemon=True)
            self._t_framegrabber.start()
        else:
            #TODO: open video source as a file with opencv
            pass
        pass


    def subscribe(self, callback:Callable[[bytes], None]) -> None:
        self.subscribers.append(callback)

    def unsubscribe(self, callback:Callable[[bytes ], None]) -> None:
            # subscriber = [item for item in self.subscribers if item == callback ][0]
            # self.subscribers.remove(subscriber)
            self.subscribers.remove(callback)
