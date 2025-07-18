import os
import glob
from ultralytics import YOLO
from PIL import Image
import json
from src.database import get_engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YOLODetector:
    def __init__(self):
        """Initialize YOLO model and database engine."""
        self.model = YOLO('yolov8n.pt')  # Load YOLOv8 nano model
        self.engine = get_engine()
    
    def detect_objects_in_image(self, image_path):
        """Run YOLO detection on a single image and return detections."""
        try:
            results = self.model(image_path)
            detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        detection = {
                            'class_id': int(box.cls[0]),
                            'class_name': self.model.names[int(box.cls[0])],
                            'confidence': float(box.conf[0]),
                            'bbox': box.xyxy[0].tolist()
                        }
                        detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"Error detecting objects in {image_path}: {e}")
            return []
    
    def process_all_images(self):
        """Process all images in the media directory, skipping already-processed ones."""
        image_pattern = "../../data/raw/media/**/*"
        image_files = glob.glob(image_pattern, recursive=True)
        
        # Filter for image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        image_files = [f for f in image_files if any(f.lower().endswith(ext) for ext in image_extensions)]
        
        for image_path in image_files:
            self.process_single_image(image_path)
    
    def is_image_processed(self, image_path):
        """Check if the image has already been processed (exists in the database)."""
        with self.engine.connect() as conn:
            query = text("""
                SELECT 1 FROM raw.image_detections WHERE image_path = :image_path LIMIT 1
            """)
            result = conn.execute(query, {'image_path': image_path}).fetchone()
            return result is not None
    
    def process_single_image(self, image_path):
        """Process a single image and store results if not already processed."""
        try:
            if self.is_image_processed(image_path):
                logger.info(f"Skipping already-processed image: {image_path}")
                return
            # Extract message_id from filename
            filename = os.path.basename(image_path)
            # Handle different filename formats
            # if filename.startswith('photo_'):
            #     logger.warning(f"Skipping file with non-message format: {filename}")
            #     return
            try:
                message_id = int(filename.split('_')[0])
            except Exception:
                logger.warning(f"Could not extract message_id from filename: {filename}")
                return
            detections = self.detect_objects_in_image(image_path)
            # Store detections in database
            with self.engine.connect() as conn:
                for detection in detections:
                    query = text("""
                        INSERT INTO raw.image_detections 
                        (message_id, image_path, detected_class, confidence_score, bbox_coordinates)
                        VALUES (:message_id, :image_path, :detected_class, :confidence_score, :bbox_coordinates)
                    """)
                    conn.execute(query, {
                        'message_id': message_id,
                        'image_path': image_path,
                        'detected_class': detection['class_name'],
                        'confidence_score': detection['confidence'],
                        'bbox_coordinates': json.dumps(detection['bbox'])
                    })
                conn.commit()
                logger.info(f"Processed {len(detections)} detections for {image_path}")
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
    
    def create_detections_table(self):
        """Create the image detections table if it doesn't exist."""
        with self.engine.connect() as conn:
            query = text("""
                CREATE TABLE IF NOT EXISTS raw.image_detections (
                    id SERIAL PRIMARY KEY,
                    message_id BIGINT,
                    image_path TEXT,
                    detected_class VARCHAR(100),
                    confidence_score FLOAT,
                    bbox_coordinates JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute(query)
            conn.commit()

if __name__ == "__main__":
    detector = YOLODetector()
    # detector.create_detections_table()
    # detector.process_all_images()
    import os 
    image_path = r"E:\Courses\10 Academy\Week 7\telegram-medical-data-pipeline\data\raw\media\CheMed123\2022-09-05\2_1662371829.jpg"
    detector.process_single_image(image_path)
    