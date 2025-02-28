from flask import Blueprint, render_template, request, send_from_directory, Response
from app.generator import generateFromScript, generateFromPrompt
main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/generate')
def generatePage():
    prompt = request.args.get('prompt')
    return render_template('generate.html', prompt=prompt)

@main.route('/api/download/<fileid>')
def downloadFile(fileid):
    """Serve a file from the 'files' folder, with basic security checks."""
    if '..' in fileid or fileid.startswith('/'):
        return Response('Invalid filename', status=400)
    return send_from_directory('../files', fileid + '.mp4')

@main.route('/api/generate', methods=['GET'])
def generate():
    """API endpoint to generate video output."""
    script = request.args.get('script')
    if script:
        return generateFromScript()

    prompt = request.args.get('prompt')
    if prompt:
        return generateFromPrompt()

    return Response('No script or prompt provided', status=400)
