from flask import Flask, render_template, jsonify
import math, threading,os

environment = os.environ.get('FLASK_ENV', 'dev')


class Double_Pendulum:
    def __init__(self, origin_x: float=300, origin_y: float=300, length_rod_1: float=120,
                  length_rod_2: float=120, mass_bob_1: float=50, mass_bob_2: float=10,
                    g: float=9.81, theta_1: float=math.pi/2, theta_2: float=math.pi/2,
                      omega_1: float=0.0, omega_2: float=0.0):
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.length_rod_1 = length_rod_1
        self.length_rod_2 = length_rod_2
        self.mass_bob_1 = mass_bob_1
        self.mass_bob_2 = mass_bob_2
        self.g = g
        self.theta_1 = theta_1 # angle of bob from verticle plane
        self.theta_2 = theta_2
        self.omega_1 = omega_1 # angular velocity of bob from vertical plane
        self.omega_2 = omega_2
        self.x_1 = self.origin_x + self.length_rod_1 * math.sin(self.theta_1)
        self.y_1 = self.origin_y + self.length_rod_1 * math.cos(self.theta_1)
        self.x_2 = self.x_1 + self.length_rod_2 * math.sin(self.theta_2)
        self.y_2 = self.y_1 + self.length_rod_2 * math.cos(self.theta_2)

    def step(self, dt: float=0.06):
        delta = self.theta_2 - self.theta_1
        denominator_1 = (self.mass_bob_1 + self.mass_bob_2) * self.length_rod_1 - self.mass_bob_2 * self.length_rod_1 * math.cos(delta) ** 2
        denominator_2 = (self.length_rod_2 / self.length_rod_1) * denominator_1

        acceleration_1 = (self.mass_bob_2 * self.length_rod_1 * self.omega_1 ** 2 * math.sin(delta) * math.cos(delta) +
              self.mass_bob_2 * self.g * math.sin(self.theta_2) * math.cos(delta) +
              self.mass_bob_2 * self.length_rod_2 * self.omega_2 ** 2 * math.sin(delta) -
              (self.mass_bob_1 + self.mass_bob_2) * self.g * math.sin(self.theta_1)) / denominator_1

        acceleration_2 = (-self.mass_bob_2 * self.length_rod_2 * self.omega_2 ** 2 * math.sin(delta) * math.cos(delta) +
              (self.mass_bob_1 + self.mass_bob_2) * self.g * math.sin(self.theta_1) * math.cos(delta) -
              (self.mass_bob_1 + self.mass_bob_2) * self.length_rod_1 * self.omega_1 ** 2 * math.sin(delta) -
              (self.mass_bob_1 + self.mass_bob_2) * self.g * math.sin(self.theta_2)) / denominator_2

        self.omega_1 += acceleration_1 * dt
        self.omega_2 += acceleration_2 * dt
        self.theta_1 += self.omega_1 * dt
        self.theta_2 += self.omega_2 * dt

        self.x_1 = self.origin_x + self.length_rod_1 * math.sin(self.theta_1)
        self.y_1 = self.origin_y + self.length_rod_1 * math.cos(self.theta_1)
        self.x_2 = self.x_1 + self.length_rod_2 * math.sin(self.theta_2)
        self.y_2 = self.y_1 + self.length_rod_2 * math.cos(self.theta_2)
    def get_coords(self):
        return [
            {'x': self.x_1, 'y': self.y_1},
            {'x': self.x_2, 'y': self.y_2},
            {'m1': self.mass_bob_1, 'm2' : self.mass_bob_2}
        ]

double_pendulum = Double_Pendulum()

def run_simulation():
    while True:
        double_pendulum.step()
        threading.Event().wait(0.03)

threading.Thread(target=run_simulation, daemon=True).start()

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html', origin_x=double_pendulum.origin_x, origin_y=double_pendulum.origin_y)

@app.route('/coords')
def coords():
    return jsonify(double_pendulum.get_coords())



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5051)
