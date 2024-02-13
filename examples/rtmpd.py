import ffmpeg
import cv2
import numpy as np

url = "rtmp://0.0.0.0:8000/live"

width = 1280
height = 720


process = (
    ffmpeg
    .input(url, listen=1)
    .output('pipe:', format='rawvideo', pix_fmt='bgr24')
    .run_async(pipe_stdout=True)
)


while True:
    in_bytes = process.stdout.read(width * height * 3)

    frame = np.frombuffer(in_bytes, np.uint8).reshape([height, width, 3])


    # Display the resulting frame
    cv2.imshow('frame', frame)
    # import time
    # filename = f"out.d/{time.strftime('%Y%m%d-%H%M%S')}.jpg"
    # cv2.imwrite(filename, frame)
    if cv2.waitKey(1) == ord('q'):
        break
    # When everything done, release the capture
    # rtmp.release()
cv2.destroyAllWindows()