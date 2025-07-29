# app.py

from flask import Flask, request, render_template_string
import boto3
import config

app = Flask(__name__)

# Initialize S3 client using IAM role (no keys needed)
s3 = boto3.client('s3', region_name=config.AWS_REGION)

# Simple HTML form (inlined for now)
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Upload to S3</title>
</head>
<body>
    <h1>Upload File to S3</h1>
    <form method="POST" action="/upload" enctype="multipart/form-data">
        <input type="file" name="file" required>
        <input type="submit" value="Upload">
    </form>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part in the request', 400

    file = request.files['file']

    if file.filename == '':
        return 'No file selected', 400

    try:
        # Upload the file to the specified S3 bucket
        s3.upload_fileobj(
            file,
            config.S3_BUCKET_NAME,
            file.filename,
            ExtraArgs={'ACL': 'public-read'}  # Optional: make file publicly accessible
        )

        file_url = f"https://{config.S3_BUCKET_NAME}.s3.{config.AWS_REGION}.amazonaws.com/{file.filename}"
        return f'File uploaded successfully! <br><a href="{file_url}">View File</a>'

    except Exception as e:
        return f"File upload failed: {str(e)}", 500

if __name__ == '__main__':
    # Run on port 80 so that ALB can access it
    app.run(host='0.0.0.0', port=80)
