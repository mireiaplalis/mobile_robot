from picarx import Picarx

def main():
    try:
        px = Picarx()
        prev_distance = px.ultrasonic.read()
        searching = True
        angle = 0

        while True:
            distance = px.ultrasonic.read()
            if searching:
                #print("Distance", distance, "Previous", prev_distance)
                if distance < 250 and prev_distance - distance > 50: # TODO: find effective thresholds for this check
                    print("Distance changed by a lot and is within bounds, so we have likely found the object")
                    searching = False
                    angle = 0
                    px.set_dir_servo_angle(angle)
                    
                else:
                    angle = 10
                    px.set_dir_servo_angle(angle)
                    px.forward(0.1)
                    # TODO: verify that this is an appropriate angle/speed
            else:
                print("distance", distance)
                if distance < 6: # TODO: check if this threshold lets the robot bump into the object
                    break
                    
            
    finally:
       px.forward(0)

if __name__ == "__main__":
    main()


