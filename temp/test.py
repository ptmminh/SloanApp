from flask import Flask, request

app = Flask(__name__)

@app.route('/test', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print(request.form.getlist('hello'))

    return '''<form method="post">
<input type="checkbox" name="hello" value="world war 2" checked>
<input type="checkbox" name="hello" value="davidism 3" checked>
<input type="submit">
</form>'''

app.run()