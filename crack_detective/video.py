from .auth import login_required
from . import VideoProcessing
from .utils import Buffer
from flask import Flask, Response, jsonify, request
from flask import session, current_app
import os

from colorama import init as colorama_init
from colorama import Fore, Back, Style

videoprocessor : VideoProcessing.VideoProcessor = None
video_sources = []

def create_videoprocessor(url=None) -> VideoProcessing.VideoProcessor:
    print(f"Creating a new VideoProcessor instance.")
    # specify output format 720x400
    videoprocessor = VideoProcessing.VideoProcessor(width=720, height=400)

    # if using Windows, specify path to ffmpeg binary
    if os.name == "nt":
        videoprocessor.ffmpeg_path = os.path.join(current_app.root_path, "bin", "ffmpeg.exe")

    # if "video_input" in session:
    #     videoprocessor.open(session["video_input"])
    # else:
    #     videoprocessor.open()
    videoprocessor.open(url)

    return videoprocessor

def get_videoprocessor():
    global videoprocessor
    if not videoprocessor or videoprocessor.ffmpeg_process.poll() is not None:
        videoprocessor = create_videoprocessor()

    return videoprocessor

def init_app(app:Flask):

    # TODO: initialise list of possible input video
    global video_sources
    video_sources.append("rtmp://0.0.0.0:8000/live/stream")

    global videoprocessor
    videoprocessor = create_videoprocessor(video_sources[0])


    @app.route("/live_stream")
    def live_stream():

        videoprocessor = get_videoprocessor()
        buffer = Buffer(maxsize=60)
        def callback(frame):
            nonlocal buffer
            # print(Fore.GREEN + f"Adding frame to buffer. (size: {buffer.qsize()}) " + Style.RESET_ALL)
            buffer.put(frame)

        # print(f"Subscribing with : {callback}")
        videoprocessor.subscribe(callback, width=640, height=360)

        def gen_frames():
            nonlocal callback
            n = 0
            try:
                for frame in buffer.stream():
                    n = n + 1
                    # print(Fore.RED + f"get frame #{n}/{buffer.qsize()}. size: {len(frame)}" + Style.RESET_ALL)
                    yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
            finally:
                # print(Fore.RED + f"live_stream() returned. Taking care of garbage collection")
                # print(f"UNsubscribing {callback}"+ Style.RESET_ALL)
                videoprocessor.unsubscribe(callback)

        # return Response(*(b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n' for frame in buffer.stream()),
        print(Fore.RED + f"live return"+ Style.RESET_ALL)
        return Response(gen_frames(),
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
