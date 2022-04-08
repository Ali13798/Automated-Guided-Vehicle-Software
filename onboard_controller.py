import math

from agv_tools import AgvTools as agvt


def main():
    freq = agvt.calc_pulse_freq()
    print(freq)


if __name__ == "__main__":
    main()
