#!/usr/bin/env -S uv --cache-dir ./.cache run 

from flask import Flask, request, render_template_string
from wsgiref.handlers import CGIHandler
import requests
import os

app = Flask(__name__)

form_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Form</title>
</head>
<body>
    <h2>Input Form</h2>
    <form method="POST">
        Name: <input type="text" name="name"><br>
        Email: <input type="email" name="email"><br>
        Reason: <input type="text" name="reason"><br>
        <input type="submit" value="Submit">
    </form>
</body>
</html>
'''

def post_to_slack(name, email, reason):
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook_url:
        raise ValueError("SLACK_WEBHOOK_URL environment variable not set")
    
    payload = {
        "text": f"Name: {name}\nEmail: {email}\nReason: {reason}"
    }
    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()

def post_to_slack(name, email, reason):
    webhook_url = os.getenv('InviteWebhook')
    if not webhook_url:
        raise ValueError("SLACK_WEBHOOK_URL environment variable not set")
    
    payload = {
        "text": f"Name: {name}\nEmail: {email}\nReason: {reason}"
    }
    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()

@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        reason = request.form['reason']
        post_to_slack(name, email, reason)
        return f'Name: {name}, Email: {email}, Reason: {reason}'
    return render_template_string(form_html)

if __name__ == "__main__":
    os.environ['FLASK_ENV'] = 'development'
    CGIHandler().run(app)
    # app.run(debug=True)