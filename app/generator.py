import os
import uuid
import subprocess
from flask import request, Response

# Chemins de dossiers
GENERATOR_FOLDER = r'../brainrot'
FILES_FOLDER = r'files'

def getOutputFileName():
    """Ensure the output folder exists and return a unique output file path."""
    if not os.path.exists(FILES_FOLDER):
        os.makedirs(FILES_FOLDER)
    filename = uuid.uuid4()
    return filename, os.path.join(FILES_FOLDER, f"{filename}.mp4")

def generateFromScript():
    """Generate video output from a provided script."""
    script = request.args.get('script')
    if not script:
        return Response('No script provided', status=400)

    scriptPath = os.path.join(GENERATOR_FOLDER, 'script.txt')
    with open(scriptPath, 'w') as scriptFile:
        scriptFile.write(script)

    filename, outputPath = getOutputFileName()
    command = ['python', '-u', os.path.join(GENERATOR_FOLDER, "main.py"), '-s', scriptPath, '-o', outputPath]

    return streamOutput(command, scriptPath, filename)

def generateFromPrompt():
    """Generate video output from a provided prompt."""
    prompt = request.args.get('prompt')
    if not prompt:
        return Response('No prompt provided', status=400)

    filename, outputPath = getOutputFileName()
    command = ['python', '-u', os.path.join(GENERATOR_FOLDER, "main.py"), '-p', prompt, '-o', outputPath]

    return streamOutput(command, None, filename)

def streamOutput(command, scriptPath, fileUUID):
    """Launch the command and stream the output using Server-Sent Events (SSE)."""
    def generator():
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in process.stdout:
            yield f"data: {line}\n\n"
        process.stdout.close()
        process.wait()

        if scriptPath:
            os.remove(scriptPath)

        yield f"data: [FILE] {fileUUID}\n\n"

    return Response(generator(), mimetype='text/event-stream')
