from .auth import login_required
from . import VideoProcessing
from .utils import Buffer
from flask import Flask, Response, jsonify, request
from flask import session, current_app
import os
import cv2

from colorama import init as colorama_init
from colorama import Fore, Back, Style

videoprocessor : VideoProcessing.VideoProcessor = None
video_sources = []

def create_videoprocessor(url=None, app:Flask=None) -> VideoProcessing.VideoProcessor:
    print(f"Creating a new VideoProcessor instance.")

    # if using Windows, specify path to ffmpeg binary
    if os.name == "nt":
        if app is None:
            app = current_app
        ffmpeg_path = os.path.join(app.root_path, "bin", "ffmpeg.exe")

    videoprocessor = VideoProcessing.VideoProcessor(url, ffmpeg_path=ffmpeg_path)

    videoprocessor.start()

    return videoprocessor

def get_videoprocessor():
    global videoprocessor
    if not videoprocessor or videoprocessor.ffmpeg_process.poll() is not None:
        print(Fore.RED + f"no videoprocessor found. Creating one." + Style.RESET_ALL)
        videoprocessor = create_videoprocessor()

    return videoprocessor

def init_app(app:Flask):

    # TODO: initialise list of possible input video
    global video_sources
    video_sources.append("rtmp://0.0.0.0:8000/live/stream")

    global videoprocessor
    videoprocessor = create_videoprocessor(video_sources[0], app)


    @app.route("/live_stream", methods=['GET'])
    def live_stream():
        print(Fore.BLUE + f"ENTER /live_stream" + Style.RESET_ALL)
        videoprocessor = get_videoprocessor()
        buffer = Buffer(maxsize=60)

        width=int(request.args.get("width", None))
        height=int(request.args.get("height", None))

        videoprocessor.subscribe(buffer.put)

        def format_frame(frame, format=".jpg", width=None, height=None):
            # Resize frame if required
            if(height or width ):
                if not height:
                    height = int(videoprocessor.height * width / videoprocessor.width)
                if not width:
                    width = int(videoprocessor.width * height / videoprocessor.height)

                # print(Fore.YELLOW + f"frame type: {type(frame)}")
                # print(f"Resize frame (type:{type(frame)}) to {width}x{height} (types: {type(width)}, {type(height)})")
                frame = cv2.resize(frame, (width , height), interpolation=cv2.INTER_AREA)

            # Encode the image to given format
            _, b = cv2.imencode(format, frame)
            return b.tobytes()


        def gen_frames(buffer):
            nonlocal width, height

            try:
                for frame in buffer.stream():

                    frame_jpg = format_frame(frame, width=width, height=height)

                    yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + frame_jpg + b'\r\n')  # concat frame one by one and show result
            finally:
                # print(Fore.RED + f"live_stream() returned. Taking care of garbage collection")
                # print(f"UNsubscribing {callback}"+ Style.RESET_ALL)
                videoprocessor.unsubscribe(buffer.put)

        # return Response(((b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n' for frame in buffer.stream())),
        return Response(gen_frames(buffer),
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
