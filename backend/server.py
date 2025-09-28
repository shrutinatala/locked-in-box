from flask import Flask, request, jsonify
import numpy as np
# import cv2
# import time
# from ultralytics import YOLO
# import os

#from extract_name import extract_name_from_id

app = Flask(__name__)

# YOLO model (replace with fine-tuned weights for ID detection)
#yolo = YOLO("yolov8n.pt")

# esp32 capture resolution
XRES, YRES = 640, 480

# convert to bgr in order to input the frame into yolo
def rgb565_to_bgr(img_bytes, w, h):
    arr = np.frombuffer(img_bytes, dtype=np.uint8)
    arr16 = arr.view(dtype=np.uint16)
    r = ((arr16 >> 11) & 0x1F).astype(np.uint8)
    g = ((arr16 >> 5) & 0x3F).astype(np.uint8)
    b = (arr16 & 0x1F).astype(np.uint8)
    r = ((r.astype(np.uint16) * 255) // 31).astype(np.uint8)
    g = ((g.astype(np.uint16) * 255) // 63).astype(np.uint8)
    b = ((b.astype(np.uint16) * 255) // 31).astype(np.uint8)
    bgr = np.stack([b, g, r], axis=1).reshape((h, w, 3))
    return bgr

@app.route("/upload", methods=["POST"])
def upload():
    if request.content_type != 'image/jpeg':
        return jsonify({"error": "Not a jpeg"}), 400
    
    img_bytes = request.data
    save_path = f"uploads/test_image.jpg"
    
    with open(save_path, "wb") as f:
        f.write(img_bytes)

    return jsonify({"msg": "Image recieved and saved as {save_path}"})

    '''
    frame = np.frombuffer(img_bytes, dtype=np.uint8)
    try:
        frame_bgr = rgb565_to_bgr(img_bytes, XRES, YRES)
    except Exception:
        return {"status": "error", "msg": "bad frame"}
        '''
    
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