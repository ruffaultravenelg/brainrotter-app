# app.py
from flask import Flask, request, send_from_directory, render_template, Response
import subprocess
import os
import uuid

# Initialize the Flask app
app = Flask(__name__)

# Route pour une page web (retourne du HTML)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate')
def generatePage():
    prompt = request.args.get('prompt')
    return render_template('generate.html', prompt=prompt)

@app.route('/files/<filename>')
def downloadFile(filename):
    """
    Serve a file from the 'files' folder.
    Reject filenames that might lead to directory traversal.
    """
    if '..' in filename or filename.startswith('/'):
        return Response('Invalid filename', status=400)
    return send_from_directory('files', filename)

# Constants (in camelCase)
generatorFolder = r'../brainrot'
filesFolder = r'files'

def getOutputFileName():
    """
    Ensure the output folder exists and return a unique output file path.
    """
    if not os.path.exists(filesFolder):
        os.makedirs(filesFolder)
    return os.path.join(filesFolder, f"{uuid.uuid4()}.mp4")

def generateFromScript():
    """
    Generate video output from a provided script.
    The script is passed as a query parameter and written to a temporary file.
    """
    script = request.args.get('script')
    if not script:
        return Response('No script provided', status=400)
    
    # Write the script content to a temporary file
    scriptPath = os.path.join(generatorFolder, 'script.txt')
    with open(scriptPath, 'w') as scriptFile:
        scriptFile.write(script)
    
    # Generate a unique output file path
    outputPath = getOutputFileName()
    
    # Define the command to run the generator script
    command = [
        'python', '-u', os.path.join(generatorFolder, "main.py"),
        '-s', scriptPath,
        '-o', outputPath
    ]
    
    def streamOutput():
        """
        Launch the command in unbuffered mode and stream each output line 
        to the client using Server-Sent Events (SSE).
        """
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # Read line by line
        )
        for line in process.stdout:
            yield f"data: {line}\n\n"
        process.stdout.close()
        process.wait()
        
        # Remove the temporary script file
        os.remove(scriptPath)
        
        # Signal that generation is complete and provide the output file path
        yield f"data: [FILE] {outputPath}\n\n"
    
    return Response(streamOutput(), mimetype='text/event-stream')

def generateFromPrompt():
    """
    Generate video output from a provided prompt.
    The prompt is passed as a query parameter.
    """
    prompt = request.args.get('prompt')
    if not prompt:
        return Response('No prompt provided', status=400)
    
    # Generate a unique output file path
    outputPath = getOutputFileName()
    
    # Define the command to run the generator script using the prompt
    command = [
        'python', '-u', os.path.join(generatorFolder, "main.py"),
        '-p', prompt,
        '-o', outputPath
    ]
    
    def streamOutput():
        """
        Launch the command in unbuffered mode and stream each output line 
        to the client using Server-Sent Events (SSE).
        """
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # Read line by line
        )
        for line in process.stdout:
            yield f"data: {line}\n\n"
        process.stdout.close()
        process.wait()
        
        # Signal that generation is complete and provide the output file path
        yield f"data: [FILE] {outputPath}\n\n"
    
    return Response(streamOutput(), mimetype='text/event-stream')

@app.route('/api/generate', methods=['GET'])
def generate():
    """
    API endpoint to generate video output.
    Accepts either a 'script' or 'prompt' query parameter.
    """
    script = request.args.get('script')
    if script:
        return generateFromScript()
    
    prompt = request.args.get('prompt')
    if prompt:
        return generateFromPrompt()
    
    return Response('No script or prompt provided', status=400)

if __name__ == '__main__':
    # Run the Flask app in debug mode with threaded support for streaming
    app.run(debug=True, threaded=True)
