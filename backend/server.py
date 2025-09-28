from flask import Flask, request, jsonify
import numpy as np
from inference_sdk import InferenceHTTPClient
import cv2
# import time
# from ultralytics import YOLO
# import os

#from extract_name import extract_name_from_id

app = Flask(__name__)

# YOLO model (replace with fine-tuned weights for ID detection)
#yolo = YOLO("yolov8n.pt")

# esp32 capture resolution
XRES, YRES = 160, 120

# convert to bgr in order to input the frame into yolo
def rgb565_to_bgr(img_bytes, w, h, save_path):
    arr16 = np.frombuffer(img_bytes, dtype=np.uint16).reshape((h, w))
    # arr16 = arr.view(dtype=np.uint16)

    r = ((arr16 >> 11) & 0x1F).astype(np.uint8)
    g = ((arr16 >> 5) & 0x3F).astype(np.uint8)
    b = (arr16 & 0x1F).astype(np.uint8)
    
    # convert to bgr
    r = ((r * 255) // 31).astype(np.uint8)
    g = ((g * 255) // 63).astype(np.uint8)
    b = ((b * 255) // 31).astype(np.uint8)
    bgr = np.dstack([b, g, r]).reshape((h, w, 3))

    return bgr

@app.route("/upload", methods=["POST"])
def upload():
    img_bytes = request.data
    save_path = f"uploads/test_image.jpg"
    
    # Check if it's a JPEG image
    if request.content_type == 'image/jpeg':
        # Save JPEG directly
        with open(save_path, "wb") as f:
            f.write(img_bytes)
    else:
        # Assume it's RGB565 data from ESP32
        try:
            img_bgr = rgb565_to_bgr(img_bytes, XRES, YRES, save_path)
            # Save the converted BGR image as JPEG
            cv2.imwrite(save_path, img_bgr)
        except Exception as e:
            return jsonify({"status": "error", "msg": f"bad frame: {str(e)}"}), 400
    
    CLIENT = InferenceHTTPClient(
        api_url="https://serverless.roboflow.com",
        api_key="OfejNA03kkSvfV1s7jrG"
    )

    result = CLIENT.infer(save_path, model_id="id-card-detection-xtiwy/3")

    return jsonify({"msg": f"Image received and saved as {save_path}. Roboflow result: {result}"})
    
'''
    # send to yolo to predict if ID
    results = yolo.predict(frame_bgr, conf=0.25, verbose=False)

    detections = []
    send_to_gemini = False
    for r in results:
        for box in r.boxes:
            cls = yolo.names[int(box.cls)]
            conf = float(box.conf)
            xyxy = box.xyxy.cpu().numpy().tolist()[0]
            detections.append({"cls": cls, "conf": conf, "xyxy": xyxy})

            # if ID, send to gemini
            if cls.lower() == "id_card":  # <- must match YOLO label
                send_to_gemini = True

    # write frame to filename
    filename = f"frame_{int(time.time())}.png"
    cv2.imwrite(filename, frame_bgr)

    # extract name if ID
    name = None
    if send_to_gemini:
        name = extract_name_from_id(filename)

    # return results
    return jsonify({"status": "ok", "detections": detections, "name": name})
'''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)