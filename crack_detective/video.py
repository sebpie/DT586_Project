from . import VideoProcessing
from flask import Flask, Response
from flask import g

def get_videoprocessor():
    if 'videoprocessor' not in g:
        g.videoprocessor = VideoProcessing.VideoProcessor(width=720, height=400)
        g.videoprocessor.open()

    return g.videoprocessor


def init_app(app:Flask):
    @app.route("/live_stream")
    def live_stream():

        videoprocessor = get_videoprocessor()

        return Response(videoprocessor.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    return
