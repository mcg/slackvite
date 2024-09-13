#!/usr/bin/env -S uv --cache-dir ./.cache run 

from flask import Flask, request, render_template, render_template_string, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_wtf.csrf import CSRFProtect
from wsgiref.handlers import CGIHandler
import requests
import os

app = Flask(__name__)

app.config['TURNSTILE_SECRET_KEY'] = os.getenv('TURNSTILE_SECRET_KEY')
app.secret_key = os.getenv('FLASK_CSRF_KEY')
if not app.secret_key:
    raise ValueError("FLASK_CSRF_KEY environment variable not set")

csrf = CSRFProtect(app)

class InputForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    reason = StringField('Reason', validators=[DataRequired()])
    submit = SubmitField('Submit')

form_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Invite Me</title>
    <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
</head>
<body>
    <h2>Slack Invite</h2>
    <form method="POST">
        {{ form.hidden_tag() }}
        Name: {{ form.name }}<br>
        Email: {{ form.email }}<br>
        Reason: {{ form.reason }}<br>
        <div class="cf-turnstile" data-sitekey="{{ turnstile_site_key }}"></div><br>
        {{ form.submit }}
    </form>
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            <ul>
            {% for message in messages %}
                <li>{{ message }}</li>
            {% endfor %}
            </ul>
        {% endif %}
    {% endwith %}
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

def verify_turnstile(response):
    secret_key = app.config['TURNSTILE_SECRET_KEY']
    verify_url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    payload = {
        'secret': secret_key,
        'response': response
    }
    r = requests.post(verify_url, data=payload)
    return r.json().get('success', False)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = InputForm()
    if form.validate_on_submit():
        turnstile_response = request.form.get('cf-turnstile-response')
        if not verify_turnstile(turnstile_response):
            flash("Turnstile verification failed. Please try again.")
            return redirect(url_for('index'))

        post_to_slack(form.name.data, form.email.data, form.reason.data)
        flash("Form submitted successfully!")
        return redirect(url_for('success'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}")
    return render_template_string(form_html, form=form, turnstile_site_key=os.getenv('TURNSTILE_SITE_KEY'))

app.route('/success')
def success():
    return render_template('success.html')

if __name__ == "__main__":
    os.environ['FLASK_ENV'] = 'development'
    CGIHandler().run(app)
    # app.run(debug=True)