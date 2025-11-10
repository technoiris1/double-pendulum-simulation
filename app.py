from flask import Flask, render_template, jsonify, request
import math, threading, os, json

environment = os.environ.get('FLASK_ENV', 'dev')

class Double_Pendulum:
    def __init__(self, data, origin_x=300, origin_y=300, theta_1=math.pi/2, theta_2=math.pi/2,
                 omega_1=0.0, omega_2=0.0):
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.length_rod_1 = float(data.get("length_rod_1", 150))
        self.length_rod_2 = float(data.get("length_rod_2", 120))
        self.mass_bob_1 = float(data.get("mass_bob_1", 50))
        self.mass_bob_2 = float(data.get("mass_bob_2", 10))
        self.g = float(data.get("g", 9.81))
        self.theta_1 = theta_1
        self.theta_2 = theta_2
        self.omega_1 = omega_1
        self.omega_2 = omega_2
        self.update_positions()

    def update_positions(self):
        self.x_1 = self.origin_x + self.length_rod_1 * math.sin(self.theta_1)
        self.y_1 = self.origin_y + self.length_rod_1 * math.cos(self.theta_1)
        self.x_2 = self.x_1 + self.length_rod_2 * math.sin(self.theta_2)
        self.y_2 = self.y_1 + self.length_rod_2 * math.cos(self.theta_2)

    def step(self, dt=0.06):
        delta = self.theta_2 - self.theta_1
        denom1 = (self.mass_bob_1 + self.mass_bob_2) * self.length_rod_1 - self.mass_bob_2 * self.length_rod_1 * math.cos(delta) ** 2
        denom2 = (self.length_rod_2 / self.length_rod_1) * denom1

        a1 = (self.mass_bob_2 * self.length_rod_1 * self.omega_1 ** 2 * math.sin(delta) * math.cos(delta)
              + self.mass_bob_2 * self.g * math.sin(self.theta_2) * math.cos(delta)
              + self.mass_bob_2 * self.length_rod_2 * self.omega_2 ** 2 * math.sin(delta)
              - (self.mass_bob_1 + self.mass_bob_2) * self.g * math.sin(self.theta_1)) / denom1

        a2 = (-self.mass_bob_2 * self.length_rod_2 * self.omega_2 ** 2 * math.sin(delta) * math.cos(delta)
              + (self.mass_bob_1 + self.mass_bob_2) * self.g * math.sin(self.theta_1) * math.cos(delta)
              - (self.mass_bob_1 + self.mass_bob_2) * self.length_rod_1 * self.omega_1 ** 2 * math.sin(delta)
              - (self.mass_bob_1 + self.mass_bob_2) * self.g * math.sin(self.theta_2)) / denom2

        self.omega_1 += a1 * dt
        self.omega_2 += a2 * dt
        self.theta_1 += self.omega_1 * dt
        self.theta_2 += self.omega_2 * dt
        self.update_positions()

    def get_coords(self):
        return [
            {'x': self.x_1, 'y': self.y_1},
            {'x': self.x_2, 'y': self.y_2},
            {'m1': self.mass_bob_1, 'm2': self.mass_bob_2}
        ]


stop_event = threading.Event()
simulation_thread = None
standard_data = json.loads('{"length_rod_1":150, "length_rod_2":120, "mass_bob_1":50, "mass_bob_2":10, "g":9.81}')
double_pendulum = Double_Pendulum(standard_data)

def run_simulation():
    while not stop_event.is_set():
        double_pendulum.step()
        threading.Event().wait(0.03)

def start_simulation():
    global simulation_thread
    stop_event.clear()
    simulation_thread = threading.Thread(target=run_simulation, daemon=True)
    simulation_thread.start()

def restart_simulation(data=None):
    global stop_event, double_pendulum
    stop_event.set()
    threading.Event().wait(0.05)
    double_pendulum = Double_Pendulum(data or standard_data)
    start_simulation()

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
    restart_simulation()
    return jsonify({"status": "restarted"})

@app.route('/update', methods=['POST'])
def update():
    if not request.is_json:
        return jsonify({"error": "invalid json"}), 400
    data = request.get_json()
    restart_simulation(data)
    return jsonify({"status": "updated"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5051)
