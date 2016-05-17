__author__ = 'Gaston C. Hillar'


from wiringx86 import GPIOGalileoGen2 as GPIO
import time


class Board:
    gpio = GPIO(debug=False)


class AnalogLed:
    def __init__(self, pin, name):
        self.pin = pin
        self.name = name
        self.gpio = Board.gpio
        self.gpio.pinMode(pin, self.gpio.PWM)
        self.brightness_value = 0
        self.set_brightness(0)

    def set_brightness(self, value):
        brightness_value = value
        if brightness_value > 255:
            brightness_value = 255
        elif brightness_value < 0:
            brightness_value = 0
        self.gpio.analogWrite(self.pin, brightness_value)
        self.brightness_value = brightness_value
        print("{0} LED connected to PWM Pin #{1} set to brightness {2}.".format(self.name, self.pin, brightness_value))


class VoltageInput:
    initial_analog_pin_number = 14

    def __init__(self, analog_pin):
        self.analog_pin = analog_pin
        self.gpio = Board.gpio
        self.gpio.pinMode(
            analog_pin + self.__class__.initial_analog_pin_number,
            self.gpio.ANALOG_INPUT)

    @property
    def voltage(self):
        raw_value = self.gpio.analogRead(
            self.analog_pin +
            self.__class__.initial_analog_pin_number)
        return raw_value / 1023.0 * 5.0


class DarknessSensor:
    # Light level descriptions
    light_extremely_dark = "extremely dark"
    light_very_dark = "very dark"
    light_dark = "just dark"
    light_no_need_for_a_flashlight = \
        "there is no need for a flashlight"
    # Maximum voltages that determine the light level
    extremely_dark_max_voltage = 2.0
    very_dark_max_voltage = 3.0
    dark_max_voltage = 4.0

    def __init__(self, analog_pin):
        self.voltage_input = VoltageInput(analog_pin)
        self.voltage = 0.0
        self.ambient_light = self.__class__.light_extremely_dark
        self.measure_light()

    def measure_light(self):
        self.voltage = self.voltage_input.voltage
        if self.voltage < \
                self.__class__.extremely_dark_max_voltage:
            self.ambient_light = self.__class__.light_extremely_dark
        elif self.voltage < \
                self.__class__.very_dark_max_voltage:
            self.ambient_light = self.__class__.light_very_dark
        elif self.voltage < \
                self.__class__.dark_max_voltage:
            self.ambient_light = self.__class__.light_dark
        else:
            self.ambient_light = self.__class__.light_no_need_for_a_flashlight


class BoardInteraction:
    # The photoresistor included in the voltage divider
    # is connected to analog PIN A0
    darkness_sensor = DarknessSensor(0)
    # The Red LED is connected to GPIO pin ~6
    red_led = AnalogLed(6, 'Red')
    # The Green LED is connected to GPIO Pin ~5
    green_led = AnalogLed(5, 'Green')
    # The Blue LED is connected to GPIO Pin ~3
    blue_led = AnalogLed(3, 'Blue')

    @classmethod
    def set_rgb_led_brightness(cls, brightness_level):
        cls.red_led.set_brightness(brightness_level)
        cls.green_led.set_brightness(brightness_level)
        cls.blue_led.set_brightness(brightness_level)

    @classmethod
    def update_leds_brightness(cls):
        if cls.darkness_sensor.ambient_light == DarknessSensor.light_extremely_dark:
            cls.set_rgb_led_brightness(255)
        elif cls.darkness_sensor.ambient_light == DarknessSensor.light_very_dark:
            cls.set_rgb_led_brightness(128)
        elif cls.darkness_sensor.ambient_light == DarknessSensor.light_dark:
            cls.set_rgb_led_brightness(64)
        else:
            cls.set_rgb_led_brightness(0)


if __name__ == "__main__":
    last_ambient_light = ""
    while True:
        BoardInteraction.darkness_sensor.measure_light()
        new_ambient_light = BoardInteraction.darkness_sensor.ambient_light
        if new_ambient_light != last_ambient_light:
            # The ambient light value changed
            last_ambient_light = new_ambient_light
            print("Darkness level: {0}".format(new_ambient_light))
            BoardInteraction.update_leds_brightness()
        # Sleep 2 seconds
        time.sleep(2)
