import os
import pytesseract
from PIL import Image
import cv2
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# Create necessary directories
for folder in [UPLOAD_FOLDER, PROCESSED_FOLDER]:
    os.makedirs(folder, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def comprehensive_image_processing(image_path, unique_id):
    logger.info(f"Starting comprehensive image processing for {image_path}")
    
    # Load image with OpenCV
    original = cv2.imread(image_path)
    if original is None:
        logger.error(f"Failed to load image at {image_path}")
        return None
    
    # Store different processed versions
    processed_versions = []
    
    # Save the original processed version
    original_processed = os.path.join(PROCESSED_FOLDER, f"{unique_id}_original.jpg")
    cv2.imwrite(original_processed, original)
    processed_versions.append(("Original", original_processed))
    
    # Convert to grayscale
    gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    
    # 1) Basic processing - Otsu's thresholding
    _, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    basic_path = os.path.join(PROCESSED_FOLDER, f"{unique_id}_basic.jpg")
    cv2.imwrite(basic_path, thresh1)
    processed_versions.append(("Basic Threshold", basic_path))
    
    # 2) Adaptive thresholding
    adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                    cv2.THRESH_BINARY, 11, 2)
    adaptive_path = os.path.join(PROCESSED_FOLDER, f"{unique_id}_adaptive.jpg")
    cv2.imwrite(adaptive_path, adaptive)
    processed_versions.append(("Adaptive Threshold", adaptive_path))
    
    # 3) Denoising
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    denoise_path = os.path.join(PROCESSED_FOLDER, f"{unique_id}_denoised.jpg")
    cv2.imwrite(denoise_path, denoised)
    processed_versions.append(("Denoised", denoise_path))
    
    # 4) Denoised + Otsu
    _, denoised_thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    denoised_thresh_path = os.path.join(PROCESSED_FOLDER, f"{unique_id}_denoised_thresh.jpg")
    cv2.imwrite(denoised_thresh_path, denoised_thresh)
    processed_versions.append(("Denoised + Threshold", denoised_thresh_path))
    
    # 5) Contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    enhanced_path = os.path.join(PROCESSED_FOLDER, f"{unique_id}_enhanced.jpg")
    cv2.imwrite(enhanced_path, enhanced)
    processed_versions.append(("Contrast Enhanced", enhanced_path))
    
    # 6) Enhanced + Otsu
    _, enhanced_thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    enhanced_thresh_path = os.path.join(PROCESSED_FOLDER, f"{unique_id}_enhanced_thresh.jpg")
    cv2.imwrite(enhanced_thresh_path, enhanced_thresh)
    processed_versions.append(("Enhanced + Threshold", enhanced_thresh_path))
    
    # 7) Dilation and Erosion
    kernel = np.ones((1, 1), np.uint8)
    dilated = cv2.dilate(gray, kernel, iterations=1)
    eroded = cv2.erode(dilated, kernel, iterations=1)
    morph_path = os.path.join(PROCESSED_FOLDER, f"{unique_id}_morphology.jpg")
    cv2.imwrite(morph_path, eroded)
    processed_versions.append(("Morphological Ops", morph_path))
    
    # 8) Sharpen image
    blurred = cv2.GaussianBlur(gray, (0, 0), 3)
    sharpened = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)
    sharpen_path = os.path.join(PROCESSED_FOLDER, f"{unique_id}_sharpened.jpg")
    cv2.imwrite(sharpen_path, sharpened)
    processed_versions.append(("Sharpened", sharpen_path))
    
    # 9) Invert image (helps with white text on dark backgrounds)
    inverted = cv2.bitwise_not(gray)
    inverted_path = os.path.join(PROCESSED_FOLDER, f"{unique_id}_inverted.jpg")
    cv2.imwrite(inverted_path, inverted)
    processed_versions.append(("Inverted", inverted_path))
    
    # 10) Scale the image (helps with very small text)
    height, width = gray.shape
    scaled = cv2.resize(gray, (width*2, height*2), interpolation=cv2.INTER_CUBIC)
    scaled_path = os.path.join(PROCESSED_FOLDER, f"{unique_id}_scaled.jpg")
    cv2.imwrite(scaled_path, scaled)
    processed_versions.append(("Scaled", scaled_path))
    
    # 11) Try correcting skew
    try:
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
        for contour in contours:
            rect = cv2.minAreaRect(contour)
            angle = rect[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            if abs(angle) > 0.5:
                (h, w) = gray.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, 
                                        borderMode=cv2.BORDER_REPLICATE)
                rotated_path = os.path.join(PROCESSED_FOLDER, f"{unique_id}_rotated.jpg")
                cv2.imwrite(rotated_path, rotated)
                processed_versions.append(("Skew Corrected", rotated_path))
                break
    except Exception as e:
        logger.error(f"Skew correction failed: {str(e)}")
    
    logger.info(f"Completed processing {len(processed_versions)} versions for {image_path}")
    return processed_versions

def extract_best_text(processed_versions, language='eng'):
    logger.info(f"Starting text extraction for {len(processed_versions)} image versions")
    
    best_text = ""
    best_confidence = 0
    best_method = ""
    
    # Try different PSM modes
    psm_modes = [6, 3, 4, 1, 11]
    
    for version_name, img_path in processed_versions:
        for psm in psm_modes:
            try:
                custom_config = f'--psm {psm} --oem 3 -l {language} --dpi 300'
                ocr_data = pytesseract.image_to_data(
                    Image.open(img_path), 
                    config=custom_config, 
                    output_type=pytesseract.Output.DICT
                )
                text_parts = []
                confidence_sum = 0
                word_count = 0
                
                for index in range(len(ocr_data['text'])):
                    if ocr_data['text'][index].strip() and ocr_data['conf'][index] > 0:
                        text_parts.append(ocr_data['text'][index])
                        confidence_sum += ocr_data['conf'][index]
                        word_count += 1
                
                text = " ".join(text_parts)
                avg_confidence = confidence_sum / word_count if word_count > 0 else 0
                
                if text and len(text) > len(best_text) or (len(text) == len(best_text) and avg_confidence > best_confidence):
                    best_text = text
                    best_confidence = avg_confidence
                    best_method = f"{version_name} with PSM {psm}"
                    logger.info(f"New best text found with {best_method} (Confidence: {best_confidence:.2f})")
            
            except Exception as e:
                logger.error(f"Error extracting text from {img_path} with PSM {psm}: {str(e)}")
    
    if best_text:
        logger.info(f"Best text extracted using {best_method} with confidence {best_confidence:.2f}")
    else:
        logger.warning("No text could be extracted from any processed version")
    
    return best_text, best_confidence, best_method