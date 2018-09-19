# System


# User
import led_blink
import pwm_led

# Main
def main():
    #led_blink.blink_LED()
    #led_blink.SOS_LED()

    led_blink.blink_LED_PWM()
    pwm_led.init_all()

    return

main()
