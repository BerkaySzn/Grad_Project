from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import io

class DetectionResult:
    def __init__(self, class_id, bounding_box, confidence_score):
        self.class_id = class_id
        self.bounding_box = bounding_box
        self.confidence_score = confidence_score

    def __repr__(self):
        return f"DetectionResult(class_id={self.class_id}, bounding_box={self.bounding_box}, confidence_score={self.confidence_score})"

class ObjectDetector:
    def __init__(self, model_path="C:/Users/BERKAY/Desktop/runs/detect/bitirme_yolo_model3/weights/best.pt"):
        """Initialize YOLO model.
        Args:
            model_path (str): Path to the YOLO model weights
        """
        self.model = YOLO(model_path)
        self.device = 'cpu'
        
    def detect_ingredients(self, image_bytes):
        """Detect ingredients in an image.
        Args:
            image_bytes (bytes): Image data in bytes
        Returns:
            list: List of detected ingredients with confidence scores
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Save temporary image for YOLO prediction
        temp_path = "temp_image.jpg"
        cv2.imwrite(temp_path, img)
        
        try:
            # Run inference using your existing detection code
            results = self.model.predict(source=temp_path, save=False, device=self.device)
            
            # Process results
            detections = []
            for r in results:
                for box in r.boxes:
                    class_id = int(box.cls[0])
                    coordinates = box.xywh[0].tolist()
                    confidence = float(box.conf[0])
                    
                    detection = DetectionResult(class_id, coordinates, confidence)
                    detections.append({
                        'class': str(class_id),  # You might want to map this to ingredient names
                        'confidence': confidence,
                        'bbox': coordinates
                    })
            
            return detections
            
        finally:
            # Clean up temporary file
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def detect_and_draw(self, image_bytes):
        """Detect objects and draw bounding boxes on the image.
        Args:
            image_bytes (bytes): Image data in bytes
        Returns:
            bytes: Annotated image in bytes
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Save temporary image for YOLO prediction
        temp_path = "temp_image.jpg"
        cv2.imwrite(temp_path, img)
        
        try:
            # Run inference and get results with boxes drawn
            results = self.model.predict(source=temp_path, save=False, device=self.device)
            
            # Get the plotted image with boxes
            for r in results:
                plotted_img = r.plot()
                
                # Convert back to bytes
                is_success, buffer = cv2.imencode(".jpg", plotted_img)
                if is_success:
                    return buffer.tobytes()
            
            return image_bytes
            
        finally:
            # Clean up temporary file
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path) 