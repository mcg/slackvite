#!/usr/bin/env -S uv --cache-dir ./.cache run 

from flask import Flask, request, render_template_string
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_wtf.csrf import CSRFProtect
from wsgiref.handlers import CGIHandler
import requests
import os

app = Flask(__name__)
csrf = CSRFProtect(app)

class InputForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    reason = StringField('Reason', validators=[DataRequired()])
    captcha = StringField('Captcha', validators=[DataRequired()])
    submit = SubmitField('Submit')

form_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Invite Me</title>
</head>
<body>
    <h2>Slack Invite</h2>
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
    form = InputForm()
    if form.validate_on_submit():
        post_to_slack(form.name.data, form.email.data, form.reason.data)
        return f'Name: {form.name.data}, Email: {form.email.data}, Reason: {form.reason.data}'

    return render_template_string(form_html, form=form, captcha=captcha)

if __name__ == "__main__":
    os.environ['FLASK_ENV'] = 'development'
    CGIHandler().run(app)
    # app.run(debug=True)