from .auth import login_required
from . import VideoProcessing
from flask import Flask, Response, request
from flask import g

def get_videoprocessor():
    if 'videoprocessor' not in g:
        g.videoprocessor = VideoProcessing.VideoProcessor(width=720, height=400)
        g.videoprocessor.open()

    return g.videoprocessor


def init_app(app:Flask):

    # TODO: initialise list of possible input video

    @app.route("/live_stream")
    def live_stream():

        videoprocessor = get_videoprocessor()

        return Response(videoprocessor.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    """
    """
    @app.route("/api/input", methods = ["GET", "PUT"])
    @login_required()
    def control_input():
        match(request.method):
            case "GET":
                if 'video_input' not in g:
                    return {"error" : "No video input selected"} , 400

                return { 'video_input' : g.video_input }

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
    @login_required()
    def control_outut():
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
