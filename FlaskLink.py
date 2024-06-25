from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
import subprocess

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/welcomePage')
def welcome_page():
    return render_template('welcomePage.html')


@app.route('/nutrition')
def nutrition():
    return render_template('dashboard.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        image = request.files['image']
        image_path = os.path.join('assets/Unknown', image.filename)
        image.save(image_path)

        # Execute imageClassifierTest.py and capture its output
        output = subprocess.check_output(['python', 'imageClassifierTest.py'])
        output_str = output.decode('utf-8').strip()  # Convert bytes to string

        # Create a JSON response with the output
        response_data = {'output': output_str}
        return jsonify(response_data)


if __name__ == '__main__':
    app.run()
