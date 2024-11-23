import os
from flask import Flask, request, redirect, url_for, render_template, flash, send_from_directory
import cloudconvert
from werkzeug.utils import secure_filename
from flask_cors import CORS

API_KEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiYmViNTNjMjg4NzcxZGFjMDc5ZTQxZDA2YzE3ZGQ3MzVhZGVjNmNmY2Y3ODBmNGEwYTI0ZWI4YmRhOTQwOTQ0NzBkODc5ZDJhNjhhZjM3YTYiLCJpYXQiOjE3MzIyODQyNzguNjYyNDE1LCJuYmYiOjE3MzIyODQyNzguNjYyNDE2LCJleHAiOjQ4ODc5NTc4NzguNjU3MzUxLCJzdWIiOiI3MDI4NDYxOSIsInNjb3BlcyI6WyJ1c2VyLnJlYWQiLCJ1c2VyLndyaXRlIiwidGFzay53cml0ZSIsInRhc2sucmVhZCIsIndlYmhvb2sucmVhZCIsIndlYmhvb2sud3JpdGUiLCJwcmVzZXQud3JpdGUiLCJwcmVzZXQucmVhZCJdfQ.SQRRO1y-YuNnmGi-se9bxa9g0dGW9wTb9DO38FMb27q95jO6qsVfZN71H2niW53lrJW9M7KHd3RoG3B2IIxdhK8AVa07xMPfT67_JDzcREaazp1GqD-a53geHoWFZ3r3ne8dgsrWOrQA7oUGipRZ6Jd0Ns4gleKWgD02sANit9mjl-CwB5BjJjWVXEbqFRC9gMFJ5N7N73nWixSmC_Atn7Jk55Gy5BJh4tSghY82FcRTJBlyHYdVIFCNSYsR1AJN7bcj7yfMNvnY0pObaMoKPUETzn93YOPiTcIAvxBeQf-4sQ-y3yFaKnESCR-WlWRl8HnZbm5xNYaKsgwBSC4C4aJNnr306SWPjvafDQ8EgY3XXWL_hy0l4aR_zVoVNCDAYtYzHeUH9rZ9Dg5ck6fvHENlsWtZ2gsj5s2fWYSBbxnH5prDzLd4Fmpu8i1I21CrCr8LmHl-rSDhDVf1HYiEEuEdlKCku-pkYc_ON2YmJCIfwq_9HGVPezuGmdI1JgvXTvml7Sghy_81B9KDbVdS7UsQPzaZSnt-rqfiSYOej30y9lhDJTh7BXUmUCcJan_n1Nh7r4DIInVIM7_k615V5CmCld3-1z5NiH0eQcDn2IYMRX3RU_Kx2s9vYQa7LwYtiiAypq_XjuzuC6oSXLZMe9DFoe65NhoUciEhdc-ItbU'
cloudconvert.configure(api_key = API_KEY, sandbox = False)

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Directory to save uploaded files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, 'downloads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

CORS(app, resources={r"/uploads/*": {"origins": "https://cloudconvert.com/"}})

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part in the request', 'error')
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        flash('No file selected for uploading', 'error')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        flash(f'File {filename} uploaded successfully!', 'success')
        print(f'http://crazydave.pythonanywhere.com/uploads/{ filename }')
        job = cloudconvert.Job.create(payload={
             "tasks": {
                 'import': {
                      'operation': 'import/url',
                      'url': f'https://crazydave.pythonanywhere.com/uploads/{ filename }'
                 },
                 'convert': {
                     'operation': 'convert',
                     'input': 'import',
                     'output_format': 'pdf'
                 },
                 'export': {
                     'operation': 'export/url',
                     'input': 'convert'
                 }
             }
        })

        return redirect(url_for('index'))
    else:
        flash('File type not allowed', 'error')
        return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def download_raw(filename):
    """Serve a file from the uploads directory."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/downloads/<filename>')
def download_finished(filename):
    """Serve a file from the downloads directory."""
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/complete')
def conversion_complete():
    print(request.get_json())
    return '', 200

if __name__ == "__main__":
    app.run(debug=True)
