import os
from ultralytics import YOLO
import cv2
import numpy as np


class DetectionResult:
    def __init__(self, class_id, bounding_box, confidence_score):
        self.class_id = class_id
        self.bounding_box = bounding_box
        self.confidence_score = confidence_score

    def __repr__(self):
        return f"DetectionResult(class_id={self.class_id}, bounding_box={self.bounding_box}, confidence_score={self.confidence_score})"


class ObjectDetector:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = r"C:\Users\aycaa\OneDrive\Masaüstü\bitirme.test\bestv5.pt"

        print(f"Loading YOLO model from: {model_path}")
        self.model = YOLO(model_path)
        self.device = "cpu"
        print("YOLO model loaded successfully")

    def detect_ingredients(self, image_bytes):
        try:
            temp_dir = "temp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            temp_path = os.path.join(temp_dir, "temp_image.jpg")

            image = cv2.imdecode(np.frombuffer(
                image_bytes, np.uint8), cv2.IMREAD_COLOR)
            cv2.imwrite(temp_path, image)

           results = self.model.predict(source=temp_path,save=False,
    device=self.device,
    imgsz=640  # CLI ile aynı boyut
)

            )

            detections = []
            for r in results:
                for box in r.boxes:
                    class_id = int(box.cls[0])
                    coordinates = box.xywh[0].tolist()
                    confidence = float(
                        box.conf[0]) if box.conf is not None else 0.0

                    detections.append(
                        {
                            "class": class_id,
                            "confidence": confidence,
                            "bbox": coordinates,
                        }
                    )

            counts = {}
            for d in detections:
                class_id = d["class"]
                if class_id in counts:
                    counts[class_id] += 1
                else:
                    counts[class_id] = 1

            return detections, counts

        except Exception as e:
            print(f"Error in detect_ingredients: {str(e)}")
            raise

        finally:
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
            except Exception as e:
                print(f"Error cleaning up temporary files: {str(e)}")

    def detect_and_draw(self, image_bytes):
        try:
            temp_dir = "temp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            temp_path = os.path.join(temp_dir, "temp_image.jpg")

            with open(temp_path, "wb") as f:
                f.write(image_bytes)

            results = self.model.predict(
                source=temp_path, save=False, device=self.device
            )

            for r in results:
                plotted_img = r.plot()
                is_success, buffer = cv2.imencode(".jpg", plotted_img)
                if is_success:
                    return buffer.tobytes()

            return image_bytes

        except Exception as e:
            print(f"Error in detect_and_draw: {str(e)}")
            raise

        finally:
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
            except Exception as e:
                print(f"Error cleaning up temporary files: {str(e)}")
