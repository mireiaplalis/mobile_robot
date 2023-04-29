from picarx import Picarx
import time

def main():
    try:
        px = Picarx()
        px.forward(5)
        angle = -15

        while True:
            distance = px.ultrasonic.read()
            if distance > 0 and distance < 300:
                print("Distance:", distance)
                if distance > 35:
                    px.set_dir_servo_angle(0)
                else:
                    print("Starting to go around it")
                    break
        
        px.set_dir_servo_angle(angle)
        px.forward(20)
        time.sleep(0.8)
        px.set_dir_servo_angle(-angle)
        time.sleep(2)
        px.set_dir_servo_angle(angle)
        time.sleep(0.8)
        px.set_dir_servo_angle(0)
        time.sleep(4)
        #while True and angle <= 77:
        #    print("Incrementing angle: ", angle)
        #    angle += 3
        #    px.set_dir_servo_angle(angle)
        #    time.sleep(0.05)
        #px.set_dir_servo_angle(0)
        #time.sleep(2)
    finally:
        px.forward(0)

if __name__ == "__main__":
    main()

