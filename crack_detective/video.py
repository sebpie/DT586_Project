import base64
import datetime

from .cnn_module import Cnn, CnnOriginal, CnnVgg16
from .crack_detector  import CrackDetector
from .auth import login_required
from . import VideoProcessing
from .utils import Buffer
from flask import Flask, Response, jsonify, request
from flask import session, current_app
import os
import cv2

from colorama import init as colorama_init
from colorama import Fore, Back, Style

rtmp_server : VideoProcessing.RTMPServer = None
video_sources = []
video_processors = {} # "stream_name" : Subscribable

def create_rtmpserver(model:Cnn, url=None, app:Flask=None, ffmpeg_path=None) -> VideoProcessing.RTMPServer:

    # if using Windows, specify path to ffmpeg binary
    if not ffmpeg_path and os.name == "nt":
        if app is None:
            app = current_app
        ffmpeg_path = os.path.join(app.root_path, "bin", "ffmpeg.exe")

    rtmp_server = VideoProcessing.RTMPServer(url, ffmpeg_path=ffmpeg_path, model_inputshape=(model.width, model.height))
    rtmp_server.start()

    return rtmp_server


def init_app(app:Flask):
    global video_processors

    # TODO: initialise list of possible input video
    global video_sources
    video_sources.append("rtmp://0.0.0.0:8000/live/stream")

    # model = CnnOriginal(load="CNN_Orig-224x224-Mendelay_FULL.keras")

    # model = CnnOriginal(width=80, height=80, load="CNN_Orig-80x80-Mendelay_FULL.keras")
    match(app.config["MODEL"]):
        case "ORIG":
            model = CnnOriginal(width=app.config["MODEL_SIZE_X"],
                                height=app.config["MODEL_SIZE_X"],
                                load=app.config["MODEL_FILE"])
        case "VGG16":
            model = CnnOriginal(width=app.config["MODEL_SIZE_X"],
                                height=app.config["MODEL_SIZE_X"],
                                load=app.config["MODEL_FILE"])


    rtmp_server = create_rtmpserver(model, video_sources[0], app)
    video_processors["preprocessed"] = rtmp_server
    video_processors["processed"] = CrackDetector(rtmp_server, model)

    @app.route("/stream/<stream_name>", methods=['GET'])
    def stream_preprocessed(stream_name):

        print(Fore.BLUE + f"ENTER /stream/{stream_name}" + Style.RESET_ALL)
        videoprocessor = video_processors[stream_name]
        print(f"working with videoprocessor: {videoprocessor}")
        buffer = Buffer(maxsize=60)

        width=request.args.get("width", None)
        height=request.args.get("height", None)

        videoprocessor.subscribe(buffer.put)

        def format_frame(frame, format=".jpg", width=None, height=None):
            # Resize frame if required
            resized_frame = None
            if(height or width ):
                if not height:
                    width = int(int)
                    height = int(videoprocessor.height * width / videoprocessor.width)
                if not width:
                    height = int(height)
                    width = int(videoprocessor.width * height / videoprocessor.height)

                # print(Fore.YELLOW + f"frame type: {type(frame)}")
                # print(f"Resize frame (type:{type(frame)}) to {width}x{height} (types: {type(width)}, {type(height)})")
                resized_frame = cv2.resize(frame, (width , height), interpolation=cv2.INTER_AREA)
            else:
                 resized_frame = frame

            # Encode the image to given format
            _, b = cv2.imencode(format, resized_frame)
            return b.tobytes()


        def gen_frames(buffer, width=None, height=None):
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
        return Response(gen_frames(buffer, width, height),
                        mimetype='multipart/x-mixed-replace; boundary=frame')



    @app.route('/api/take_picture', methods=['POST'])
    def save_image():
        try:
            data = request.json
            image_data = data.get('image_data')
            if image_data:
                # Decode the base64 image data
                image_binary = base64.b64decode(image_data.split(',')[1])
                # Save the image to the images folder
                # folder_name = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')  # Format: YYYY-MM-DD
                folder_path = current_app["output_dir"]
                image_filename = os.path.join(folder_path, f'captured_image_{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.png')
                with open(image_filename, 'wb') as f:
                    f.write(image_binary)
                return jsonify({'message': 'Image saved successfully', 'filename': f'{image_filename}'})
            else:
                return jsonify({'error': 'No image data received'})
        except Exception as e:
            return jsonify({'error': 'Error saving image: ' + str(e)})



    @app.route("/api/take_picture", methods=['PUT'])
    def take_picture():
        buffer = Buffer()
        source = video_processors["processed"]
        source.subscribe(buffer.put)
        pic = buffer.get()

        # get selected folder

        # filename

        return {"error" : "not implemented"}, 501

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
                if 'output_dir' not in current_app:
                    return 404, "No folder selected"

                return { 'output_dir' : current_app.output_dir }

            case "PUT":
                try:
                    current_app["output_dir"] = request.json['output_dir']
                    return 200
                except KeyError:
                    return {"error" : "folder name is missing"}, 400


        return {"error" : "Invalid request"}, 400

    return
