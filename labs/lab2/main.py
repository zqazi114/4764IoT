# System


# User
import led_blink
import pwm_led
import interrupts

# Main
def main():
    #led_blink.blink_LED()
    #led_blink.SOS_LED()
    led_blink.blink_LED_PWM()
    
    #pwm_led.led_test()
    #pwm_led.init_timer()
    #pwm_led.timer_cb(1)
    #pwm_led.init_all()
    
    interrupts.setup_switch()
    
    return

main()
