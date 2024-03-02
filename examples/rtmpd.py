import ffmpeg
import cv2
import numpy as np

from queue import Queue

url = "rtmp://0.0.0.0:8000/live"

width = 1280
height = 720

frame_buffer = Queue(maxsize=60)

process = (
    ffmpeg
    .input(url, listen=1)
    .output('pipe:', format='rawvideo', pix_fmt='bgr24', s='{}x{}'.format(width, height))
    .run_async(pipe_stdout=True)
)


while True:
    in_bytes = process.stdout.read(width * height * 3)
    frame = np.frombuffer(in_bytes, np.uint8).reshape([height, width, 3])

    if(frame_buffer.full()):
        frame_buffer.get(False) # Drops the oldest frame from the buffer
    frame_buffer.put(frame)


    # Display the resulting frame
    cv2.imshow('frame', frame)

    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()