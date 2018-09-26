# System


# User
import led_blink
import pwm_led
import interrupts
from lab2 import Lab2
from machine import Timer

# Main
def main():
    #Checkpoint 1
    #led_blink.blink_LED_PWM()
    
    #Checkpoint 2
    #pwm_led.init_all()
    
    #Checkpoint 3
    #interrupts.setup_switch()
    
    #Alternate
    devices = [True, True, True, True] #[test_led, led, piezo, als]
    lab2 = Lab2(devices)
    
    return

main()
