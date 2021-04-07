import RPi.GPIO as GPIO          
from time import sleep
import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt_client
import json

class MYDMove:
    # can have common data here
    min_speed = 30
    max_speed = 100
    pwm = 100
    ramp_seconds = 0.3
    ramp_seconds_turn = 0.1
    ramp_increments = 100
    
    def __init__(self):
        
        # left rear wheel
        self.Lin1 = 18
        self.Lin2 = 17
        self.LenA = 4
        
        # left front wheel
        self.Lin3 = 24
        self.Lin4 = 25
        self.LenB = 5

        # right front wheel
        self.Rin1 = 6
        self.Rin2 = 12
        self.RenA = 13
                
        # right rear wheel
        self.Rin3 = 27
        self.Rin4 = 23
        self.RenB = 22

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.Lin1,GPIO.OUT)
        GPIO.setup(self.Lin2,GPIO.OUT)
        GPIO.setup(self.LenA,GPIO.OUT)
        GPIO.setup(self.Lin3,GPIO.OUT)
        GPIO.setup(self.Lin4,GPIO.OUT)
        GPIO.setup(self.LenB,GPIO.OUT)
        GPIO.setup(self.Rin1,GPIO.OUT)
        GPIO.setup(self.Rin2,GPIO.OUT)
        GPIO.setup(self.RenA,GPIO.OUT)
        GPIO.setup(self.Rin3,GPIO.OUT)
        GPIO.setup(self.Rin4,GPIO.OUT)
        GPIO.setup(self.RenB,GPIO.OUT)
        
        GPIO.output(self.Lin1,GPIO.LOW)
        GPIO.output(self.Lin2,GPIO.LOW)
        GPIO.output(self.Lin3,GPIO.LOW)
        GPIO.output(self.Lin4,GPIO.LOW)
        GPIO.output(self.Rin1,GPIO.LOW)
        GPIO.output(self.Rin2,GPIO.LOW)
        GPIO.output(self.Rin3,GPIO.LOW)
        GPIO.output(self.Rin4,GPIO.LOW)
        self.lr=GPIO.PWM(self.LenA,self.pwm)
        self.lf=GPIO.PWM(self.LenB,self.pwm)
        self.rf=GPIO.PWM(self.RenA,self.pwm)
        self.rr=GPIO.PWM(self.RenB,self.pwm)
        self.lr.start(self.min_speed)
        self.lf.start(self.min_speed)
        self.rf.start(self.min_speed)
        self.rr.start(self.min_speed)
        
    def set_status_forward(self, speed):
        self.lr.ChangeDutyCycle(speed)
        self.lf.ChangeDutyCycle(speed)
        self.rf.ChangeDutyCycle(speed)
        self.rr.ChangeDutyCycle(speed)
        GPIO.output(self.Lin1,GPIO.HIGH)
        GPIO.output(self.Lin2,GPIO.LOW)
        GPIO.output(self.Lin3,GPIO.HIGH)
        GPIO.output(self.Lin4,GPIO.LOW)
        GPIO.output(self.Rin1,GPIO.HIGH)
        GPIO.output(self.Rin2,GPIO.LOW)
        GPIO.output(self.Rin3,GPIO.HIGH)
        GPIO.output(self.Rin4,GPIO.LOW)
        
    def set_status_back(self, speed):
        self.lr.ChangeDutyCycle(speed)
        self.lf.ChangeDutyCycle(speed)
        self.rf.ChangeDutyCycle(speed)
        self.rr.ChangeDutyCycle(speed)
        GPIO.output(self.Lin1,GPIO.LOW)
        GPIO.output(self.Lin2,GPIO.HIGH)
        GPIO.output(self.Lin3,GPIO.LOW)
        GPIO.output(self.Lin4,GPIO.HIGH)
        GPIO.output(self.Rin1,GPIO.LOW)
        GPIO.output(self.Rin2,GPIO.HIGH)
        GPIO.output(self.Rin3,GPIO.LOW)
        GPIO.output(self.Rin4,GPIO.HIGH)
        
        
    def set_status_right(self, speed):
        self.lr.ChangeDutyCycle(speed)
        self.lf.ChangeDutyCycle(speed)
        self.rf.ChangeDutyCycle(speed)
        self.rr.ChangeDutyCycle(speed)
        GPIO.output(self.Lin1,GPIO.HIGH)
        GPIO.output(self.Lin2,GPIO.LOW)
        GPIO.output(self.Lin3,GPIO.HIGH)
        GPIO.output(self.Lin4,GPIO.LOW)
        GPIO.output(self.Rin1,GPIO.LOW)
        GPIO.output(self.Rin2,GPIO.HIGH)
        GPIO.output(self.Rin3,GPIO.LOW)
        GPIO.output(self.Rin4,GPIO.HIGH)
        
    def set_status_left(self, speed):
        self.lr.ChangeDutyCycle(speed)
        self.lf.ChangeDutyCycle(speed)
        self.rf.ChangeDutyCycle(speed)
        self.rr.ChangeDutyCycle(speed)
        GPIO.output(self.Lin1,GPIO.LOW)
        GPIO.output(self.Lin2,GPIO.HIGH)
        GPIO.output(self.Lin3,GPIO.LOW)
        GPIO.output(self.Lin4,GPIO.HIGH)
        GPIO.output(self.Rin1,GPIO.HIGH)
        GPIO.output(self.Rin2,GPIO.LOW)
        GPIO.output(self.Rin3,GPIO.HIGH)
        GPIO.output(self.Rin4,GPIO.LOW)
        
    def set_status_stop(self):
        GPIO.output(self.Lin1,GPIO.LOW)
        GPIO.output(self.Lin2,GPIO.LOW)
        GPIO.output(self.Lin3,GPIO.LOW)
        GPIO.output(self.Lin4,GPIO.LOW)
        GPIO.output(self.Rin1,GPIO.LOW)
        GPIO.output(self.Rin2,GPIO.LOW)
        GPIO.output(self.Rin3,GPIO.LOW)
        GPIO.output(self.Rin4,GPIO.LOW)
        
    def forward(self, seconds):
        # move forward for the defined number of seconds
        # includes a ramp on the motors
        
        if seconds <= self.ramp_seconds:
            print("Forward / back commands need to be greater than ", self.ramp_seconds)
            exit(0)
            
        ramp_speed_increment = (self.max_speed - self.min_speed) / self.ramp_increments
        ramp_time_increment = self.ramp_seconds / self.ramp_increments
        speed = self.min_speed
        time = 0.0
        
        while (time <= self.ramp_seconds):
            self.set_status_forward(speed)
            time = time + ramp_time_increment
            speed = speed + ramp_speed_increment
            sleep(ramp_time_increment)
    
        sleep(seconds - self.ramp_seconds)
            
        self.set_status_stop()
        
    def back(self, seconds):
        # move back for the defined number of seconds
        # includes a ramp on the motors
        
        if seconds <= self.ramp_seconds:
            print("Forward / back commands need to be greater than ", self.ramp_seconds)
            exit(0)
        
        ramp_speed_increment = (self.max_speed - self.min_speed) / self.ramp_increments
        ramp_time_increment = self.ramp_seconds / self.ramp_increments
        speed = self.min_speed
        time = 0.0
        
        while (time <= self.ramp_seconds):
            self.set_status_back(speed)
            time = time + ramp_time_increment
            speed = speed + ramp_speed_increment
            sleep(ramp_time_increment)
            
        sleep(seconds - self.ramp_seconds)
            
        self.set_status_stop()
         
    def right(self, seconds):
        # move right for the defined number of seconds
        # includes a ramp on the motors
        
        if seconds <= self.ramp_seconds_turn:
            print("Turn commands need to be greater than ", self.ramp_seconds_turn)
            exit(0)
        
        ramp_speed_increment = (self.max_speed - self.min_speed) / self.ramp_increments
        ramp_time_increment = self.ramp_seconds_turn / self.ramp_increments
        speed = self.min_speed
        time = 0.0
        
        while (time <= self.ramp_seconds_turn):
            self.set_status_right(speed)
            time = time + ramp_time_increment
            speed = speed + ramp_speed_increment
            sleep(ramp_time_increment)
            
        sleep(seconds - self.ramp_seconds_turn)
            
        self.set_status_stop()
        
    def left(self, seconds):
        # move right for the defined number of seconds
        # includes a ramp on the motors
        
        if seconds <= self.ramp_seconds_turn:
            print("Turn commands need to be greater than ", self.ramp_seconds_turn)
            exit(0)
        
        ramp_speed_increment = (self.max_speed - self.min_speed) / self.ramp_increments
        ramp_time_increment = self.ramp_seconds_turn / self.ramp_increments
        speed = self.min_speed
        time = 0.0
        
        while (time <= self.ramp_seconds_turn):
            self.set_status_left(speed)
            time = time + ramp_time_increment
            speed = speed + ramp_speed_increment
            sleep(ramp_time_increment)
            
        sleep(seconds - self.ramp_seconds_turn)
            
        self.set_status_stop()
        
mydMove = MYDMove()


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() - if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("mydaemon/move")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

    # Check that the message is in the right format
    message_text = msg.payload.decode('utf-8')
    try:
        message_json = json.loads(message_text)
    except Exception as e:
        print("Couldn't parse raw data: %s" % message_text, e)
    else:
        print("JSON received : ", message_json)
    
    if message_json["command"]=='back':
            mydMove.back(message_json["distance"])
    elif message_json["command"]=='forward':
        mydMove.forward(message_json["distance"])
    elif message_json["command"]=='right':
        mydMove.right(message_json["distance"])
    elif message_json["command"]=='left':
        mydMove.left(message_json["distance"])
    elif message_text=='exit':
        GPIO.cleanup()
        #break
    else:
        print("The move callback did not understand that command")
    
        
def main():
    
    # test 
    #mydMove.forward(1)
    #mydMove.back(1)
    #mydMove.right(0.3)
    #mydMove.left(0.5)
    #exit(0)
    
    
    
    local_mqtt_client = mqtt_client.Client()
    local_mqtt_client.on_connect = on_connect
    local_mqtt_client.on_message = on_message
    local_mqtt_client.connect("test.mosquitto.org", 1883, 60)

    while True:
        local_mqtt_client.loop_forever()
    
    
if __name__ == '__main__':
    main()
    