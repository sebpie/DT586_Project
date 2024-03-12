from flask import Flask, Response, render_template, jsonify
import cv2
import threading
import secrets

app = Flask(__name__)

# Initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple clients
# are viewing the stream)
outputFrame = None
lock = threading.Lock()

# Store generated stream keys
stream_keys = set()

def generate_frames():
    # Grab global references to the output frame and lock variables
    global outputFrame, lock

    while True:
        # Wait until the lock is acquired
        with lock:
            # Check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue

            # Encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            
            # Ensure the frame was successfully encoded
            if not flag:
                continue

        # Yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
            bytearray(encodedImage) + b'\r\n')

def generate_stream_key():
    # Generate a unique stream key
    stream_key = secrets.token_hex(16)
    stream_keys.add(stream_key)
    
    # Generate the stream URL
    stream_url = f"http://127.0.0.1:8000/video_feed/{stream_key}"
    
    return jsonify({"stream_key": stream_key, "stream_url": stream_url})

@app.route("/")
def index():
    # Return the rendered template
    return render_template("index.html")

@app.route("/video_feed/<stream_key>")
def video_feed(stream_key):
    # Check if the stream key is valid
    if stream_key not in stream_keys:
        return "Invalid stream key", 403
    
    # Return the response generated along with the specific media
    # type (MIME type)
    return Response(generate_frames(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route("/generate_stream_key", methods=["POST"])
def generate_stream_key_route():
    return generate_stream_key()

if __name__ == '__main__':
    # Start the Flask app
    app.run(host="0.0.0.0", port=8000, debug=True,
        threaded=True, use_reloader=False)
