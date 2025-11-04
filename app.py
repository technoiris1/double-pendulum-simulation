from flask import Flask, render_template
import os
import math
import time
environment = os.environ.get('FLASK_ENV','dev')

if environment=='production':
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return render_template('index.html')

elif environment == 'dev':
    def create_app():
        app = Flask(__name__)
        class DoublePendulum:
            def __init__(self):
                self.L1 = 150
                self.L2 = 150
                self.M1 = 10
                self.M2 = 10
                self.G = 9.81
                self.dt = 0.01
                self.a1 = math.pi/2
                self.a2 = math.pi/2
                self.av1 = 0
                self.av2 = 0
                self.last_update = time.time()
            def step(self):
                num1 = -self.G * ( 2* self.M1 + self.M2 ) * math.sin(self.a1)
                num2 = -self.M2 * self.G * math.sin( self.a1- 2 * self.a2 )
                num3 = -2 * math.sin( self.a1 - self.a2) * self.M2
                num4 = self.av2 * self.av2 * self.L2 * self.av1 * self.av1 * self.L1 * math.cos(self.a1 - self.a2)
                den = self.L1 *( 2* self.M1+ self.M2- self.M2* math.cos( 2* self.a1- 2* self.a2))
                aa1 = (num1+ num2 + num3 + num4) / den
                num5 = 2 * math.sin(self.a1 - self.a2)
                num6 = self.av1 * self.av1 * self.L1 * (self.M1 + self.M2)
                num7 = self.G * (self.M1 + self.M2) * math.cos(self.a1)
                num8 = self.av2 * self.av28 * self.L2 * self.M2 * math.cos(self.a1 - self.a2)
                den2 = self.L2 * (2 * self.M1 + self.M2 - self.M2 * math.cos(2 * self.a1 - 2 * self.a2))
        @app.route('/')
        def home():
            return render_template('index.html')

        return app

    if __name__ == '__main__':
        app = create_app()
        app.run(debug=True, host='0.0.0.0', port=8000)
