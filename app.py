from flask import Flask, render_template, request
import os
import math

from flask.json import jsonify
environment = os.environ.get('FLASK_ENV','dev')

class DoublePendulum:
    def __init__(self):
        self.L1 = 150
        self.L2 = 150
        self.M1 = 10
        self.M2 = 10
        self.G = 9.81
        self.dt = 0.01
        self.steps_per_frame = 3
    def step(self):
        data = request.json
        a1 = float(data["a1"])
        a2 = float(data["a2"])
        av1 = float(data["av1"])
        av2 = float(data["av2"])
        for _ in range(self.steps_per_frame):
            num1 = -self.G * ( 2* self.M1 + self.M2 ) * math.sin(self.a1)
            num2 = -self.M2 * self.G * math.sin( self.a1- 2 * self.a2 )
            num3 = -2 * math.sin( self.a1 - self.a2) * self.M2
            num4 = self.av2 * self.av2 * self.L2 * self.av1 * self.av1 * self.L1 * math.cos(self.a1 - self.a2)
            den = self.L1 *( 2* self.M1+ self.M2- self.M2* math.cos( 2* self.a1- 2* self.a2))
            aa1 = (num1+ num2 + num3 + num4) / den
            num5 = 2 * math.sin(self.a1 - self.a2)
            num6 = self.av1 * av1 * self.L1 * (self.M1 + self.M2)
            num7 = self.G * (self.M1 + self.M2) * math.cos(self.a1)
            num8 = self.av2 * self.av28 * self.L2 * self.M2 * math.cos(self.a1 - self.a2)
            den2 = self.L2 * (2 * self.M1 + self.M2 - self.M2 * math.cos(2 * self.a1 - 2 * self.a2))
            aa2 = (num5 * (num6 + num7 + num8)) / den2

            av1 += aa1 * self.dt
            av2 += aa2 * self.dt
            a1 += av1 * self.dt
            a2 += av2 * self.dt
        return{
            "a1" : a1,
            "a2" : a2,
            "av1" : av1,
            "av2" : av2
        }



if environment == "production":
    app = Flask(__name__)
    pendulum = DoublePendulum()
    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/update', method= ['POST'])
    def update():
        data = request.get_json()
        result = pendulum.step(data)
        return jsonify(result)
else:
    def create_app():
        app = Flask(__name__)
        pendulum = DoublePendulum()
        @app.route('/')
        def home():
            return render_template('index.html')

        @app.route('/update', method= ['POST'])
        def update():
            data = request.get_json()
            result = pendulum.step(data)
            return jsonify(result)
        return app
    if __name__ == '__main__':
        app = create_app()
        app.run(debug=True, host='0.0.0.0', port=8000)
