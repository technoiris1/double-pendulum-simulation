from flask import Flask, render_template, jsonify
import math, threading, time, os

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
        self.a1 = math.pi / 2
        self.a2 = math.pi / 2
        self.av1 = 0
        self.av2 = 0

    def step(self):
        a1, a2, av1, av2 = self.a1, self.a2, self.av1, self.av2

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
        self.a1, self.a2, self.av1, self.av2 = a1, a2, av1, av2

    def get_coords(self):
        x1 = self.L1 * math.sin(self.a1)
        y1 = self.L1 * math.cos(self.a1)
        x2 = x1 + self.L2 * math.sin(self.a2)
        y2 = y1 + self.L2 * math.cos(self.a2)
        return {"x1": x1, "y1": y1, "x2": x2, "y2": y2}


if environment == "production":
    app = Flask(__name__)
    pendulum = DoublePendulum()

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/coords')
    def coords():
        return jsonify(pendulum.get_coords())


else:
    def create_app():
        app = Flask(__name__)
        pendulum = DoublePendulum()
        def run_simulation():
            while True:
                pendulum.step()
                time.sleep(0.03)
        threading.Thread(target=run_simulation, daemon=True).start()

        @app.route('/')
        def home():
            return render_template('index.html')

        @app.route('/coords')
        def coords():
            return jsonify(pendulum.get_coords())

        return app

    if __name__ == '__main__':
        app = create_app()
        app.run(debug=True, host='0.0.0.0', port=5051)
