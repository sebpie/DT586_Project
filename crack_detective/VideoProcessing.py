from queue import Queue
from threading import Thread
from typing import Callable
import cv2
import ffmpeg
import numpy as np
import os

DEFAULT_URL="rtmp://0.0.0.0:8000/live/stream"
DEFAULT_BUFFER_SIZE=60 # 2s at 30fps
DEFAULT_WIDTH=1280
DEFAULT_HEIGHT=720
DEFAULT_COLOR='bgr24'
PIXEL_SIZE= { "bgr24": 3, }


class VideoProcessor(object):
    ffmpeg_process = None
    _t_framegrabber: Thread = None

    def __init__(self,
                 color=DEFAULT_COLOR,
                 width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT,
                 framebuffer_size=DEFAULT_BUFFER_SIZE,
                 ffmpeg_path=None) -> None:
        self.color = color
        self.width = width
        self.height = height
        self.frame_buffer = Queue(maxsize=framebuffer_size)
        self.ffmpeg_path=ffmpeg_path
        self.subscribers = []

    def _framegrabber(self):
        while True:
            in_bytes = self.ffmpeg_process.stdout.read(self.width * self.height * PIXEL_SIZE[self.color])
            frame = np.frombuffer(in_bytes, np.uint8).reshape([self.height, self.width, PIXEL_SIZE[self.color]])

            self.dispatch(frame)

            # if(self.frame_buffer.full()):
            #     print(f"buffer is full. drop a frame.")
            #     self.frame_buffer.get(False) # Drops the oldest frame from the buffer
            # self.frame_buffer.put(frame)
        return

    def open(self, url=DEFAULT_URL):
        if url.startswith("rtmp://"):
            print(f"Start ffmpeg subprocess to capture {url}.")
            args = {"pipe_stdout" : True}
            if self.ffmpeg_path:
                args["cmd"] = self.ffmpeg_path
            self.ffmpeg_process = (
                ffmpeg
                .input(url, listen=1)
                .output('pipe:',
                        format='rawvideo',
                        pix_fmt=self.color,
                        s=f'{self.width}x{self.height}')
                .run_async(**args)
            )
            print(f"start thread to buffer ffmpeg output")
            self._t_framegrabber = Thread(target=self._framegrabber, daemon=True)
            self._t_framegrabber.start()
        else:
            #TODO: open video source as a file with opencv
            pass
        pass

    # def get_frame(self, frame, format=".jpg", width=None, height=None):

    #     return frame

    def dispatch(self, frame):
        # print(f"ENTER dispatch. number of subscribers: {len(self.subscribers)}")
        for cb, format, width, height in self.subscribers:
            # print(f"Dispatch to: {cb} height: {height}")
            if(height or width ):
                if not height:
                    height = int(self.height * width / self.width)
                if not width:
                    width = int(self.width * height / self.height)

                frame = cv2.resize(frame, (width , height), interpolation=cv2.INTER_AREA)

            if format != "raw":
                _, buffer = cv2.imencode(format, frame)
                frame = buffer.tobytes()

            cb(frame)



    def subscribe(self, callback:Callable[[bytes], None], format=".jpg", width=None, height=None) -> None:
        self.subscribers.append((callback, format, width, height))

    def unsubscribe(self, callback:Callable[[bytes], None]) -> None:
            subscriber = [item for item in self.subscribers if item[0] == callback ]
            self.subscribers.remove(subscriber)


def test_videoprocessor():
    print("Start the video processor (rtmp server / ffmpeg)")
    processor = VideoProcessor(height=1, width=1, framebuffer_size=30*60)
    processor.open()

    for frame in processor.gen_frames():
        print(f"processor generated a frame")

def version():
    print(f"version: {0.1}")

if __name__ == "__main__":
    test_videoprocessor()
