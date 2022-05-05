from time import sleep

import pigpio

from tools.agv_tools import AgvTools

MOTOR = 23

# Connect to pigpiod daemon
pi = pigpio.pi()

# Set up pins as an output
pi.set_mode(MOTOR, pigpio.OUTPUT)

cb_counter = pi.callback(user_gpio=MOTOR)

dist = 10
ramp = AgvTools.create_ramp_inputs(inches=dist)
print(ramp)

AgvTools.generate_ramp(pi=pi, ramp=ramp, motor_pin=MOTOR, clear_waves=True)

t = 0.050
c = 1
while c < 200:
    print(f"Count at {c * t} seconds is {cb_counter.tally()}")
    c += 1
    sleep(t)

sleep(10)
print(
    f"final count is {cb_counter.tally()}\nExpected {AgvTools.calc_pulse_num_from_dist(inches=dist)}"
)

print("resetting tally...")
cb_counter.reset_tally()
print(f"new talley is {cb_counter.tally()}")
