from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import os
from PIL import Image
import piexif

app = Flask(__name__, static_url_path='/static')

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed extensions for file uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # file.save(filepath)
        
        # Process the image and print EXIF data
        exif_data = process_image(filepath)
        return render_template('upload.html', exif_data=exif_data)

    return redirect(request.url)

def process_image(filepath):
    try:
        image = Image.open(filepath)
        exif_data = image._getexif()

        if exif_data is not None:
            exif_dict = piexif.load(image.info["exif"])
            datetime_1 = exif_dict['Exif'][36867]
            device = exif_dict['Exif'][42036]
            exif = {"datetime": datetime_1,
            "device": device}
            # exif = {
            #     piexif.TAGS[key]["name"]: exif_data[key]
            #     for key in exif_data
            #     if key in piexif.TAGS
            # }
            # for key, val in exif.items():
            #     print(f"{key}: {val}")

            return exif
        else:
            print("No EXIF data found")
            return "No EXIF data found"
    except Exception as e:
        print(f"Error processing image: {e}")
        return str(e)

if __name__ == "__main__":
    app.run(debug=True)
