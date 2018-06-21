import numpy as np
import gclib
import matplotlib.pyplot as plt
import time

'''

All user settings are set here; the rest of the script should not need modification.
Undesired plots can be commented out at the end of the script.

'''

#select axis to tune ('A', 'B', 'C', or 'D')
axis = 'B' #must be string

#select speed in encoder ticks per second
speed = '4200' #must be string

#select movement distace in encoder ticks
distance = '8000' #must be string, can be positive or negative

#select number of samples to take, which will set the duration of data acquisition
samplenumber = 1000 #must be float/integer

#select PID tuning parameters (must be strings)
Kp = '15' #proportional constant
Kd = '110' #derivative constant
lowpass = '0.85' #low pass filter
FV = '0' #velocity feedforward
FA = '0' #acceleration feedforward
IL = '7' #integrator limit
Ki = '3' #integration constant

#choose whether or not to save settings into Galil
savesettings = False










global g
#make an instance of the gclib python class
g = gclib.py()

#connect to network
g.GOpen('192.168.1.201 --direct -s ALL')

#used for galil commands
c = g.GCommand


c('AB') #abort motion and program
c('MO') #turn off all motors

#set PID parameters
c('KP' + axis + '=' + Kp)
c('KD' + axis + '=' + Kd)
c('PL' + axis + '=' + lowpass)
c('FV' + axis + '=' + FV)
c('FA' + axis + '=' + FA)
c('IL' + axis + '=' + IL)
c('KI' + axis + '=' + Ki)

if savesettings == True:
    c('BN')

c('SH' + axis) #servo on

c('JG' + axis + '=' + speed) #set new speed


#tell motor to wait for python to start aquisition and move
c('WT 1000')
c('PR' + axis + '=' + distance)
c('BG' + axis)


#acquire data
error = []
velocity = []
position = []
seconds = []

while len(velocity)<samplenumber:
    error.append(float(c('MG _TE' + axis)))
    velocity.append(float(c('MG _TV' + axis)))
    position.append(float(c('MG _TP' + axis)))
    seconds.append(float(time.clock()))



#turn off in case things get out of hand
c('AB')
c('MO')

print('motion done')



g.GClose()


#compute fourier transforms
velocityfft = np.abs(np.fft.fft(velocity))**2
velocityfft = np.split(velocityfft,2)[0]
positionfft = np.abs(np.fft.fft(position))**2
positionfft = np.split(positionfft,2)[0]
errorfft = np.abs(np.fft.fft(error))**2
errorfft = np.split(errorfft,2)[0]



dt = seconds[2]-seconds[1]
hz = 1/dt
bin = len(velocity)
hertz = []
for i in range(0,int(len(velocity)/2)):
    hertz.append(i*hz/bin)


#plot results
plt.plot(seconds,velocity)
plt.xlabel('Time (s)')
plt.ylabel('Velocity (counts/s)')
plt.title('Velocity Profile')
plt.show()

plt.loglog(hertz,velocityfft)
plt.xlabel('Frequency (Hz)')
plt.ylabel('(counts/s)^2/Hz')
plt.title('Velocity Power Spectrum')
plt.show()

plt.plot(seconds,position)
plt.xlabel('Time (s)')
plt.ylabel('Position (counts)')
plt.title('Position Profile')
plt.show()

plt.loglog(hertz,positionfft)
plt.xlabel('Frequency (Hz)')
plt.ylabel('counts^2/Hz')
plt.title('Position Power Spectrum')
plt.show()

plt.plot(seconds,error)
plt.xlabel('Time (s)')
plt.ylabel('Position Error (counts)')
plt.title('Position Error Profile')
plt.show()

plt.plot(hertz,errorfft)
plt.xlabel('Frequency (Hz)')
plt.ylabel('counts^2/Hz')
plt.title('Position Error Power Spectrum')
plt.show()
