import logging
import sys
import time
import RPi.GPIO as GPIO
from pygame import mixer
from Adafruit_BNO055 import BNO055
import subprocess

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

mixer.pre_init()
mixer.init()
mixer.set_num_channels(24)

#Directories to the notes
A = mixer.Sound('/home/pi/Desktop/gizmo/Scripts/A.wav')
B = mixer.Sound('/home/pi/Desktop/gizmo/Scripts/B.wav')
C = mixer.Sound('/home/pi/Desktop/gizmo/Scripts/C.wav')
D = mixer.Sound('/home/pi/Desktop/gizmo/Scripts/D.wav')

#Initial calibration values
moving_check = 0
calibration_angle = 0

bno = BNO055.BNO055(serial_port='/dev/serial0', rst=5)

# Enable verbose debug logging if -v is passed as a parameter.
if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
    logging.basicConfig(level=logging.DEBUG)

# Initialize the BNO055 and stop if something went wrong.
if not bno.begin():
    raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')

# Print system status and self test result.
status, self_test, error = bno.get_system_status()
print('System status: {0}'.format(status))
print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
# Print out an error if system status is in error mode.
if status == 0x01:
    print('System error: {0}'.format(error))
    print('See datasheet section 4.3.59 for the meaning.')

# Print BNO055 software revision and other diagnostic data.
sw, bl, accel, mag, gyro = bno.get_revision()
print('Software version:   {0}'.format(sw))
print('Bootloader version: {0}'.format(bl))
print('Accelerometer ID:   0x{0:02X}'.format(accel))
print('Magnetometer ID:    0x{0:02X}'.format(mag))
print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))

print('Welcome to the Disco Stick! press Ctrl-C to quit...')

while True:    

    if GPIO.input(23) == False: #If Calibration button, reset calibration constants
        calibration_angle, roll, pitch = bno.read_euler()
 
    if GPIO.input(3) == False: #If power button, shutdown
        subprocess.call(['shutdown', '-h', 'now'], shell=False)
    
    ax,ay,az = bno.read_linear_acceleration() #Store raw acceleration values at each instant minus gravity

    if az > -6: # If acceleration peak has subsided, flag ready to play new note
        moving_check = 0
    
    if moving_check == 0:
        if az < -8: #Note if acceleration exceeds 8 ms^2 + gravity
            
            heading, roll, pitch = bno.read_euler() 
            aux = heading - calibration_angle # Angle with respect to the observer 
            if aux < -180: # turn reading into +- 180 degrees (- is left, + right)
                aux += 360
            elif aux > 180:
                aux -= 360
            
            
                
            if aux < -45: # determine and play appropriate note
                A.set_volume(((-az)-8)/10)
                A.play()
            elif aux < 0:
                B.set_volume(((-az)-8)/10)
                B.play()
            elif aux < 45:
                C.set_volume(((-az)-8)/10)
                C.play()
            elif aux < 90:
                D.set_volume(((-az)-8)/10)
                D.play()
            
            moving_check = 1 # prevents repeated notes per acceleration peak
        

    time.sleep(0.005)


