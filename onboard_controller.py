import math

from agv_tools import AgvTools as agv_tools


def main():
    print(agv_tools.calc_pulse_freq(velocity=2.25))

    dist = 10
    print(agv_tools.calc_pulse_num(dist))


if __name__ == "__main__":
    main()
