    def user_location(data):
        global stove_turned_on_timestamp, user_in_kitchen, user_in_other_room, last_motion_value, last_time_sensor_check, motion_value, illu_diff, illuminance_array, last_illu

        illu_diff = abs(last_illu - data["illuminance"])

        motion_value = motion_value + illu_diff
        
        illuminance_array.append(data["illuminance"])

        last_illu = data["illuminance"]

        if time.time() >= last_time_sensor_check + 10:
            #motion_value = Average(illuminance_array)
            
            #if last_motion_value == 0:
                #last_motion_value = motion_value
            print(illuminance_array)
            print(motion_value)
            illuminance_array.clear()
            if motion_value > MOTION_ILLUMINANCE_THRESHOLD:
                user_in_kitchen = False
                user_in_other_room = True
                print("User in other room")
            else:
                user_in_other_room = False
                user_in_kitchen = True
                print("User in kitchen ")
                stove_turned_on_timestamp = time.time()
            last_time_sensor_check = time.time()
            #last_motion_value = motion_value 
            motion_value = 0   