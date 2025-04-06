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
            model_path = "C:/Users/BERKAY/Desktop/runs/detect/bitirme_yolo_model3/weights/best.pt"

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
            with open(temp_path, "wb") as f:
                f.write(image_bytes)

            # Read image and enhance edges
            image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
            
            # Convert to grayscale for edge detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Edge detection using Canny
            edges = cv2.Canny(blurred, 50, 150)
            
            # Dilate edges to make them more prominent
            kernel = np.ones((3,3), np.uint8)
            dilated_edges = cv2.dilate(edges, kernel, iterations=1)
            
            # Combine original image with enhanced edges
            edge_mask = cv2.cvtColor(dilated_edges, cv2.COLOR_GRAY2BGR)
            enhanced_image = cv2.addWeighted(image, 0.8, edge_mask, 0.2, 0)
            
            # Save the enhanced image
            cv2.imwrite(temp_path, enhanced_image)

            # Run YOLO detection on enhanced image
            results = self.model.predict(
                source=temp_path, save=False, device=self.device
            )

            detections = []
            for r in results:
                for box in r.boxes:
                    class_id = int(box.cls[0])
                    coordinates = box.xywh[0].tolist()
                    confidence = (
                        float(box.conf[0]) if box.conf is not None else 0.0
                    )

                    detections.append(
                        {
                            "class": class_id,
                            "confidence": confidence,
                            "bbox": coordinates,
                        }
                    )

            os.remove(temp_path)
            if not os.listdir(temp_dir):
                os.rmdir(temp_dir)

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
