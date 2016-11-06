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
PROBABILITY_WORK_AT_NIGHT = 0.1
PROBABILITY_LIGHT_DAY_TIME = 0.1
PROBABILITY_FORGET_SWITCH_OFF_LIGHT = 0.05
room_states = []


def is_dark(hour):
	return True if 0 <= hour <=6 or 18 <= hour <= 23 else False

def is_cool(hour):
	return False if 12 <= hour <= 17 else True 

def occupant_in(hour):
	choices = []
	if 18 <= hour <= 21:
		choices = [True] * 50 + [False] * 50
	elif hour >= 22 or hour <= 6:
		choices = [False] * 90 + [True] * 10
	else:
		choices = [True] * 80 + [False] * 20
		
	return random.choice(choices)


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
		file.write("Day,Hour,Room,Dark,Cool,OccupantIn,LightOn,CorridorLightOn, AC \n")
	day = 1

	# Light the LED on and off in a random manner
	for day in range(365):
	    print "Day %i" % (day + 1)
	    for hour in range(24):
			atleast_one_occupant = False
			for room in rooms:
			    is_occupant_in = occupant_in(hour)
                            light_on = is_dark(hour) and is_occupant_in
                            ac_on = not is_cool(hour) and is_occupant_in
			    atleast_one_occupant = atleast_one_occupant or is_occupant_in 

			    #office lights
			    if light_on:
			    	GPIO.output(room['light'],GPIO.HIGH)
			    else:
			    	GPIO.output(room['light'],GPIO.LOW)

		            #corridor light
			    if atleast_one_occupant and is_dark(hour):
			    	GPIO.output(6,GPIO.HIGH)
			    else:
			    	GPIO.output(6,GPIO.LOW)


			    #office AC 
			    if ac_on:
			    	GPIO.output(room['ac'],GPIO.HIGH)
			    else:
			    	GPIO.output(room['ac'],GPIO.LOW)

			    #write to csv file
			    file.write("%i,%i,%s,%s,%s,%s,%s,%s,%s \n" % (day,hour,room['room_number'],str(is_dark(hour)), str(is_cool(hour)), str(occupant_in(hour)),str(light_on), str(atleast_one_occupant),str(ac_on)))
			    file.flush() 

			    #display results
			    print "Room Number %s Occupant is %s Light: %s and AC: %s" % (room['room_number'], "In" if is_occupant_in else "Out", "On" if light_on else "Off", "ON" if ac_on else "OFF")
	    		print "Time: %i:00 It is %s and %s" % (hour, "dark" if is_dark(hour) else "bright", "cool" if is_cool(hour) else "hot") 
			time.sleep(1)

