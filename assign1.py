import RPi.GPIO as GPIO
import random
import os
import time 
import datetime

rooms = [
		{
			'room_number':'B509',
			'light':21,
			'ac':17
		},
		{
			'room_number':'B512',
			'light':20,
			'ac':16
		},
		{
			'room_number':'B516',
			'light':19,
			'ac': 13
		},
		{
			'room_number':'B517',
			'light':18,
			'ac':12
		}
]


shared_space = ['corridor', 'washrooms']

#random probabilities in %
P_WORK_DAYTIME = 80
P_WORK_IN_EVENING = 50
P_WORK_AT_NIGHT = 10
P_FORGET_SWITCH_OFF_OFFICE_LIGHT = 5
P_FORGET_SWITCH_OFF_CORRIDOR_LIGHT = 50

room_states = []

def is_dark(hour):
	return 1 if 0 <= hour <=6 or 18 <= hour <= 23 else 0

def is_cool(hour):
	return 0 if 12 <= hour <= 17 else 1 

def occupant_in(hour):
	choices = []
	if 18 <= hour <= 21:
		choices = [1] * P_WORK_IN_EVENING + [0] * (100  - P_WORK_IN_EVENING) 
	elif hour >= 22 or hour <= 6:
		choices = [0] * (100 - P_WORK_AT_NIGHT) + [1] * P_WORK_AT_NIGHT
	else:
		choices = [1] * P_WORK_DAYTIME + [0] * (100 - P_WORK_DAYTIME)
		
	return random.choice(choices)

def office_light_on(hour, forget_probability):
	is_occupant_in = occupant_in(hour)
        light_on_auto = is_dark(hour) and is_occupant_in
        light_on_manual = light_on_auto


	#check wither lights should be on
	if not light_on_manual:
		light_on_manual = random.choice([1] * forget_probability + [0] * (100 - forget_probability))
	return {'auto': light_on_auto, 'manual': light_on_manual}

if __name__ == "__main__":
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(6,GPIO.OUT)
	GPIO.setup(12,GPIO.OUT)
	GPIO.setup(13,GPIO.OUT)
	GPIO.setup(16,GPIO.OUT)
	GPIO.setup(17,GPIO.OUT)
	GPIO.setup(18,GPIO.OUT)
	GPIO.setup(19,GPIO.OUT)
	GPIO.setup(20,GPIO.OUT)
	GPIO.setup(21,GPIO.OUT)

	file_name = "report_%s.csv" % datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S')
	file = open(file_name, "a")
	if os.stat(file_name).st_size == 0:        
		file.write("Day,Hour,Room,Dark,Cool,OccupantIn,OfficeLightOnAuto,OfficeLightOnManuel,CorridorLightOnAuto,CorridorLightOnManual, AC \n")
	day = 1

	# Light the LED on and off in a random manner
	for day in range(365):
	    print "Day %i" % (day + 1)
	    for hour in range(24):
			atleast_one_occupant = 0
			for room in rooms:
			    is_occupant_in = occupant_in(hour)
			    light_on = office_light_on(hour, P_FORGET_SWITCH_OFF_OFFICE_LIGHT)

			    office_light_on_manual = light_on['manual']
			    office_light_on_auto = light_on['auto']

                            ac_on = not is_cool(hour) and is_occupant_in

			    #office lights
			    if office_light_on_auto:
			    	GPIO.output(room['light'],GPIO.HIGH)
			    else:
			    	GPIO.output(room['light'],GPIO.LOW)

		            #corridor light
			    atleast_one_occupant = atleast_one_occupant or is_occupant_in 
			    corridor_light_on_auto = atleast_one_occupant and is_dark(hour)
			    #forget factor
			    corridor_light_on_manual = corridor_light_on_auto
			    if not corridor_light_on_manual:
			    	corridor_light_on_manual = random.choice([1] * P_FORGET_SWITCH_OFF_CORRIDOR_LIGHT + [0] * (100 -  P_FORGET_SWITCH_OFF_CORRIDOR_LIGHT))
			    
			    
			    if corridor_light_on_auto:
			    	GPIO.output(6,GPIO.HIGH)
			    else:
			    	GPIO.output(6,GPIO.LOW)


			    #office AC 
			    if ac_on:
			    	GPIO.output(room['ac'],GPIO.HIGH)
			    else:
			    	GPIO.output(room['ac'],GPIO.LOW)

			    #write to csv file
			    file.write("%i,%i,%s,%s,%s,%s,%s,%s,%s,%s,%s \n" % (day,hour,room['room_number'],str(is_dark(hour)), str(is_cool(hour)), str(occupant_in(hour)),str(office_light_on_auto),str(office_light_on_manual), str(corridor_light_on_auto),str(corridor_light_on_manual),str(ac_on)))
			    file.flush() 

			    #display results
			    print "Room Number %s Occupant is %s Light: %s and AC: %s" % (room['room_number'], "In" if is_occupant_in else "Out", "On" if office_light_on_auto else "Off", "ON" if ac_on else "OFF")
	    		print "Time: %i:00 It is %s and %s" % (hour, "dark" if is_dark(hour) else "bright", "cool" if is_cool(hour) else "hot") 
			time.sleep(1)

