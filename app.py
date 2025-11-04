import os
from flask import Flask, render_template

def create_app():
    app = Flask(__name__)

    app.config['DEVELOPMENT'] = os.environ.get('FLASK_ENV') == 'development'

    @app.route('/')
    def hello_world():
        return render_template('index.html')

    return app
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8000)
