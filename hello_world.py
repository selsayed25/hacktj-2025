from flask import Flask, render_template, request, send_file, url_for, redirect
from ocr import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return render_template('index.html', error='No file selected')
    
    file = request.files['file']
    
    if file.filename == '':
        return render_template('index.html', error='No file selected')
    
    language = request.form.get('language', 'eng')
    
    # Check if the file is allowed based on the extension
    if file and allowed_file(file.filename):
        try:
            # Generate unique identifier for this job
            unique_id = str(uuid.uuid4())
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            
            # Save uploaded file
            temp_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}.{file_extension}")
            file.save(temp_path)
            
            # Process based on file type
            all_text = []
            processing_details = []
            
            if file_extension == 'pdf':
                # Convert PDF to images
                pdf_pages = pdf2image.convert_from_path(temp_path, dpi=300)
                for page_num, page in enumerate(pdf_pages):
                    # Save the PDF page as an image
                    page_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_page_{page_num}.jpg")
                    page.save(page_path, 'JPEG')
                    
                    # Process the image with our comprehensive pipeline
                    processed_versions = comprehensive_image_processing(page_path, f"{unique_id}_page_{page_num}")
                    
                    if processed_versions:
                        # Extract text from all processed versions
                        text, confidence, method = extract_best_text(processed_versions, language)
                        all_text.append(f"Page {page_num + 1}:\n{text}\n")
                        processing_details.append(f"Page {page_num + 1}: Used {method} with confidence {confidence:.2f}")
                    
                    # Clean up the page image
                    if os.path.exists(page_path):
                        os.remove(page_path)
            else:
                # Process the image with our comprehensive pipeline
                processed_versions = comprehensive_image_processing(temp_path, unique_id)
                
                if processed_versions:
                    # Extract text from all processed versions
                    text, confidence, method = extract_best_text(processed_versions, language)
                    all_text.append(text)
                    processing_details.append(f"Used {method} with confidence {confidence:.2f}")
            
            # Combine all extracted text
            extracted_text = "\n".join(all_text)
            processing_info = "\n".join(processing_details)
            
            # Generate audio if text was extracted
            audio_url = None
            if extracted_text.strip():
                audio_path = os.path.join(AUDIO_FOLDER, f"{unique_id}.mp3")
                tts = gTTS(text=extracted_text, lang='en', slow=False)
                tts.save(audio_path)
                audio_url = url_for('get_audio_file', filename=f"{unique_id}.mp3")
            
            # Clean up original uploaded file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            # Provide result to user
            return render_template('result.html',
                                  text=extracted_text,
                                  processing_info=processing_info,
                                  audio_file=audio_url,
                                  has_audio=bool(audio_url))
        
        except Exception as e:
            logger.exception("Error in conversion process")
            return render_template('index.html', error=f"Error during processing: {str(e)}")
    
    return render_template('index.html', error='Invalid file type')

@app.route('/audio/<filename>')
def get_audio_file(filename):
    return send_file(os.path.join(AUDIO_FOLDER, filename), mimetype='audio/mpeg')

@app.route('/cleanup', methods=['POST'])
def cleanup():
    try:
        # Remove files from processed folder
        for filename in os.listdir(PROCESSED_FOLDER):
            file_path = os.path.join(PROCESSED_FOLDER, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        # Only log the cleanup action (don't remove uploads and audio as they might be in use)
        logger.info("Cleaned up processed files")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)