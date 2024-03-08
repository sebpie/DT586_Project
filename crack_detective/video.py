from .auth import login_required
from . import VideoProcessing
from .utils import Buffer
from flask import Flask, Response, jsonify, request
from flask import g, current_app
import os

def get_videoprocessor() -> VideoProcessing.VideoProcessor:
    if 'videoprocessor' not in g:
        # specify output format 720x400
        g.videoprocessor = VideoProcessing.VideoProcessor(width=720, height=400)

        # if using Windows, specify path to ffmpeg binary
        if os.name == "nt":
            g.videoprocessor.ffmpeg_path = os.path.join(current_app.root_path, "bin", "ffmpeg.exe")

        if "video_input" in g:
            g.videoprocessor.open(g.video_input)
        else:
            g.videoprocessor.open()

    return g.videoprocessor

video_sources = []

def init_app(app:Flask):

    # TODO: initialise list of possible input video
    global video_sources
    video_sources.append("rtmp://0.0.0.0:8000/live/stream")


    @app.route("/live_stream")
    def live_stream():

        videoprocessor = get_videoprocessor()
        buffer = Buffer(maxsize=60)
        def callback(frame):
            nonlocal buffer
            buffer.put(frame)

        videoprocessor.subscribe(callback, width=640, height=360)

        # def gen_frames():
        #     while True:
        #         frame = buffer.stream()
        #         yield (b'--frame\r\n'
        #                 b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

        return Response(((b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') for frame in buffer.stream()),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    """
    """
    @app.route("/api/input", methods = ["GET", "PUT"])
    @login_required
    def control_input():
        match(request.method):
            case "GET":
                ret = { "video_sources": video_sources}

                if 'video_input' in g:
                    ret['video_input'] = g.video_input

                return jsonify(ret)

            case "PUT":
                try:
                    g.video_input = request.json["video_input"]
                    # TODO: propagate the change

                    return 200
                except KeyError:
                    return {"error" : "folder name is missing"}, 400

        return {"error" : "Invalid request"}, 400

    """
    """
    @app.route("/api/output", methods = ["GET", "PUT"])
    @login_required
    def control_output():
        match(request.method):
            case "GET":
                if 'output_dir' not in g:
                    return 404, "No folder selected"

                return { 'output_dir' : g.output_dir }

            case "PUT":
                try:
                    g.output_dir = request.json['output_dir']
                    return 200
                except KeyError:
                    return {"error" : "folder name is missing"}, 400


        return {"error" : "Invalid request"}, 400



    return
