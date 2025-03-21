from ultralytics import YOLO
import cv2
import numpy as np
import os


class DetectionResult:
    def __init__(self, class_id, bounding_box, confidence_score):
        self.class_id = class_id
        self.bounding_box = bounding_box
        self.confidence_score = confidence_score

    def __repr__(self):
        return f"DetectionResult(class_id={self.class_id}, bounding_box={self.bounding_box}, confidence_score={self.confidence_score})"


class ObjectDetector:
    def __init__(self, model_path=None):
        """Initialize YOLO model."""
        if model_path is None:
            model_path = "C:/Users/Monster/Desktop/best.pt_dosyası/best.pt"

        print(f"Loading YOLO model from: {model_path}")
        self.model = YOLO(model_path)
        self.device = "cpu"
        print("YOLO model loaded successfully")

    def detect_ingredients(self, image_bytes):
        """Detect ingredients in an image."""
        try:
            # Create temp directory if it doesn't exist
            temp_dir = "temp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            # Save temporary image for YOLO prediction
            temp_path = os.path.join(temp_dir, "temp_image.jpg")

            # Convert bytes to file
            with open(temp_path, "wb") as f:
                f.write(image_bytes)

            # Get detections
            results = self.model.predict(
                source=temp_path, save=False, device=self.device
            )

            # Process results
            detections = []
            for r in results:
                for box in r.boxes:
                    class_id = int(box.cls[0])
                    coordinates = box.xywh[0].tolist()
                    confidence = float(box.conf[0])

                    detections.append(
                        {
                            "class": class_id,
                            "confidence": confidence,
                            "bbox": coordinates,
                        }
                    )

            print(f"Found {len(detections)} detections")
            return detections

        except Exception as e:
            print(f"Error in detect_ingredients: {str(e)}")
            raise

        finally:
            # Clean up temporary file
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
            except Exception as e:
                print(f"Error cleaning up temporary files: {str(e)}")

    def detect_and_draw(self, image_bytes):
        """Detect objects and draw bounding boxes on the image."""
        try:
            # Create temp directory if it doesn't exist
            temp_dir = "temp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            # Save temporary image for YOLO prediction
            temp_path = os.path.join(temp_dir, "temp_image.jpg")

            # Convert bytes to file
            with open(temp_path, "wb") as f:
                f.write(image_bytes)

            # Run inference and get results with boxes drawn
            results = self.model.predict(
                source=temp_path, save=False, device=self.device
            )

            # Get the plotted image with boxes
            for r in results:
                plotted_img = r.plot()
                # Convert to bytes
                is_success, buffer = cv2.imencode(".jpg", plotted_img)
                if is_success:
                    return buffer.tobytes()

            return image_bytes

        except Exception as e:
            print(f"Error in detect_and_draw: {str(e)}")
            raise

        finally:
            # Clean up temporary file
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
            except Exception as e:
                print(f"Error cleaning up temporary files: {str(e)}")
