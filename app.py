from flask import Flask, render_template, jsonify, request
import math, threading,os, json

environment = os.environ.get('FLASK_ENV', 'dev')


class Double_Pendulum():
    def __init__(self, data, origin_x: float=300, origin_y: float=300,theta_1: float=math.pi/2, theta_2: float=math.pi/2,
                      omega_1: float=0.0, omega_2: float=0.0):
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.length_rod_1 = data.get("length_rod_1")
        self.length_rod_2 = data.get("length_rod_2")
        self.mass_bob_1 = data.get("mass_bob_1")
        self.mass_bob_2 = data.get("mass_bob_2")
        self.g = data.get("g")
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


stop_event = threading.Event()
simulation_thread = None
standard_config = '{"length_rod_1":150, "length_rod_2":120, "mass_bob_1" : 50, "mass_bob_2":10, "g":9.81}'
standard_data = json.loads(standard_config)
double_pendulum = Double_Pendulum(standard_data)
def run_simulation():
    while not stop_event.is_set():
        double_pendulum.step()
        threading.Event().wait(0.03)

def start_simulation():
    global simulation_thread, stop_event, double_pendulum
    stop_event.clear()
    simulation_thread = threading.Thread(target=run_simulation, daemon=True)
    simulation_thread.start()

start_simulation()
app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html', origin_x=double_pendulum.origin_x, origin_y=double_pendulum.origin_y)

@app.route('/coords')
def coords():
    return jsonify(double_pendulum.get_coords())

@app.route('/restart', methods=['POST'])
def restart():
    global stop_event, double_pendulum
    stop_event.set()

    threading.Event().wait(0.05)
    double_pendulum = Double_Pendulum()

    start_simulation()
    return jsonify({"status": "restarted"})

@app.route('/update', methods = ['POST'])
def update():
    if request.is_json:
        data = request.get_json()

        global stop_event, double_pendulum
        stop_event.set()
        threading.Event().wait(0.05)
        double_pendulum = Double_Pendulum(data)
        start_simulation()
        return jsonify({"success": "updated"})
    else:
        return jsonify({"error": "400"})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5051)
