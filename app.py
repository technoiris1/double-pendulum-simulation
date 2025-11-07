from flask import Flask, render_template, request, jsonify
import os
import math
import time
environment = os.environ.get('FLASK_ENV', 'dev')


class DoublePendulum:
    def __init__(self):
        self.L1 = 150
        self.L2 = 150
        self.M1 = 10
        self.M2 = 10
        self.G = 9.81
        self.dt = 0.01
        self.steps_per_frame = 3

    def step(self, data):
        a1 = float(data["a1"])
        a2 = float(data["a2"])
        av1 = float(data["av1"])
        av2 = float(data["av2"])

        for _ in range(self.steps_per_frame):
            num1 = -self.G * (2 * self.M1 + self.M2) * math.sin(a1)
            num2 = -self.M2 * self.G * math.sin(a1 - 2 * a2)
            num3 = -2 * math.sin(a1 - a2) * self.M2
            num4 = av2 * av2 * self.L2 + av1 * av1 * self.L1 * math.cos(a1 - a2)
            den = self.L1 * (2 * self.M1 + self.M2 - self.M2 * math.cos(2 * a1 - 2 * a2))
            aa1 = (num1 + num2 + num3 * num4) / den

            num5 = 2 * math.sin(a1 - a2)
            num6 = av1 * av1 * self.L1 * (self.M1 + self.M2)
            num7 = self.G * (self.M1 + self.M2) * math.cos(a1)
            num8 = av2 * av2 * self.L2 * self.M2 * math.cos(a1 - a2)
            den2 = self.L2 * (2 * self.M1 + self.M2 - self.M2 * math.cos(2 * a1 - 2 * a2))
            aa2 = (num5 * (num6 + num7 + num8)) / den2

            av1 += aa1 * self.dt
            av2 += aa2 * self.dt
            a1 += av1 * self.dt
            a2 += av2 * self.dt

        return {
            "a1": a1,
            "a2": a2,
            "av1": av1,
            "av2": av2,
            "L1" : self.L1,
            "L2" : self.L2,
            "M1" : self.M1,
            "M2" : self.M2
        }

if environment == "production":
    app = Flask(__name__)
    pendulum = DoublePendulum()

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/update', methods=['POST'])
    def update():
        data = request.get_json(force=True)
        result = pendulum.step(data)
        return jsonify(result)

else:
    def create_app():
        app = Flask(__name__)
        pendulum = DoublePendulum()
        def run_simulation():
            while True:
                pendulum.step()
                time.sleep(0.03)
        threading.Thread(target=run_simulation, daemon = True).start()
        @app.route('/')
        def home():
            return render_template('index.html')

        @app.route('/coords')
        def coords():
            return jsonify({
                "a1": pendulum.a1,
                "a2" : pendulum.a2,
                "x1" : pendulum.L1 * math.sin(pendulum.a1),
                "y1": pendulum.L1 * math.cos(pendulum.a1),
                "x2": pendulum.L1 * math.sin(pendulum.a1) +
                        pendulum.L2 * math.sin(pendulum.a2),
                "y2" : pendulum.L1 * math.sin(pendulum.a1)+
                        pendulum.L2 * math.cos(pendulum.a2)
            })

    if __name__ == '__main__':
        app = create_app()
        app.run(debug=True, host='0.0.0.0', port=5051)
