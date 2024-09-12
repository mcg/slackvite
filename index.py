from flask import Flask, request, render_template_string
from wsgiref.handlers import CGIHandler

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

@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        reason = request.form['reason']
        return f'Name: {name}, Email: {email}, Reason: {reason}'
    return render_template_string(form_html)

if __name__ == "__main__":
    import os
    os.environ['FLASK_ENV'] = 'development'
    CGIHandler().run(app)
    # app.run(debug=True)