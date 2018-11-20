![Science Project By Johnny Sprada](/images/sp_screenshot.png)

# Science Project Pi

## Objectives
### Primary
Create a Raspberry Pi that will monitor four temperature sensors and log the results at a specified frequency.  MY primary use for this is to test the Mpemba effect for a school science project.

### Secondary
Add a simple dashboard that will allow web-based remote monitoring.

##Methods
This software system consists of two scripts, and a log file.   One script polls sensors and logs the results to a log file.  The other script scrapes the log file, graphs the results on a chart and serves it up as a web page (Dash/Flask).  I used three cron jobs, one to start the web interface, one to check sensor script each minute, and one that will use `rsync` to make a backup of the log file each hour.


#### This system is set up under the assumption that it will be run as user `pi`.
There are hard-coded links to files that will be created in the pi user directory. If there's enough demand to use this tool, I'd be happy to make it work for use under any user.   


## Notes
It should be noted that this device/web interface is not intended to be deployed or routed (NAT) with a public facing interface.  Absolutley zero effort has been put into creating this as a secure device.  It could very well be a good place to start developing a platform that others can use on the open Internet in the future.  For now, just keep in mind that if you deploy an unsecured Raspberry Pi on the open internet, it will get pwned in no time flat, and could be used as a jump-off point into your network.  My efforts on *this* project have been solely to build a quick tool that I can use to complete my project.  

Additionally, I am not a software engineer, and these tools were quickly knocked out for a project.  I did not include robust error checking or automated tests.  If there's interest in the project, and people want to use it for their own purposes, I'd consider building a more robust system. 

### Assumptions

It's assumed that the end user knows a little about Linux already, or is at least comfortable working in terminal emulators.   

It's also assumed that there are four sensors connected.   If you use more or less, the software will need to be adapted.  If there's enough demand, I'll consider making it auto-detect and adapt as necessary.


## Requirements

* Raspberry Pi using a Raspbian/Debian Linux operating system with wifi configured.
* (4) DS18B20 1-Wire Temperature Sensor Probes (https://datasheets.maximintegrated.com/en/ds/DS18B20.pdf)
* (1) 4.7k resistor
* (4) 100 ohm resistors
* (Optional) Srew terminal break-out board for Raspberry Pi (makes it easy to connect devices)
* (optional) UPS battery backup (LifePO4weredPi+) (Rad piece of hardware with excellent software - https://github.com/xorbit/LiFePO4wered-Pi)
* Misc: PCB hole board, breakout board, small gage wire, heat shrink, hot glue, etc.


## Prepare Hardware

Getting a single DS18B20 sensor working on the Raspberry Pi is rather simple.   It requires only three connections to the Pi: 3.3v, ground, and the 1-Wire signal.   To reduce noise, a 4.7k resistor should be connected between the 3.3v power and the 1-Wire signal.

These sensors are designed to work over a very long (up to 200 meters) connection, and in parallel with other sensors like, using a single signal wire.  For this project, we are connecting several sensors within close range of each other (about a meter apart).  Because of this, there's a likely potential that the signals from these devices will interfere with each other.  To accommodate for this, we need to make a minor adjustment to how we connect the sensors to the Pi.   By adding a single 150 ohm resistor between the 1-Wire signal and the GPIO on the Pi, all of the sensors will work well with each other on the 1-Wire network.


Pardon the hand-drawn image, but it's a simple enough circuit and it would take me longer to learn how to draw this in a drawing program for the time being.

![DS18B20 Sensor Wiring Diagram](/images/sensor_wiring_diagram.jpg)

Here's an image of two DS18B20 sensors.  One in the water-proof probe type package, with wiring harness, and the smaller piece is the same sensor in a different, TOS type package.    Both sensors work identically, and have the same three connections (Voltage, Ground, 1-Wire signal) they are simply delivered in different physical formats for different uses.  In my particular project, I've configured 3x probe types for testing water temeperatures and 1x TOS type for ambient air temps.

![DS18B20 Sensors](/images/sensors.jpg)


After wiring the sensors together, and connecting them to the Raspberry Pi, you'll need to prepare the Pi to read the sensors.

Connect your sensor array to a Raspberry Pi 3.3v pin, ground, and the 1Wire signal to Pin #7 (GPIO#4) on the raspberry Pi.  

Here's a photo of mine, completed with shrink wrap around the PC board where all the resistors and sensors are connected.   I also hot-glued (hacker's duct tape!) any wires that are soldered to the board to releive stress when bending and handling.  I used sticky backed velcro on both the pi and the circuit board to mount into a very high-tech cardboard box.  The box is indeed high tech because it was used to ship my new TI Nspire CX calculator.  

![Science Project By Johnny Sprada](/images/sp_complete.jpg)


## Software
Start with a base system configuarion of Raspbian.  I created a guide  to do just that:

https://github.com/jsprada/Raspberry_Pi/blob/master/RPi_Install_Raspbian_Lite_Headless.md

### Enable 1-Wire

1-Wire is a technology/protocol for connecting, reading and controlling sensor networks.  It's the protocol we'll use to read the DS18B20 sensors.   Thanfully, this functionality it built into the Linux kernel.  All we have to do is enable it on our device and we can start using it.  

 To enable the 1-Wire functionality of the Raspberry Pi, append `dtoverlay=w1-gpio`  to the end of  `/boot/config.txt`

 The following commands will append the correct text to the end of the file, without having to open an editor.  If you prefer to edit the file manually, feel free to.

    echo "dtoverlay=w1-gpio" | sudo tee -a /boot/config.txt

Note that this will automatically enable 1-Wire on pin #7 (GPIO#4).


Now reboot the Raspberry Pi, to start using 1-Wire devices.


## Check 1-Wire devices

After building your sensor array, and enabling 1-wire in the steps prior, it's time to test the sensors.   One cool feature of this interface is that each sensor is mounted to the Linux filetree, as nodes that are treated just like files.   This means we can use builtin Linux tools such as `ls` and `cat` to read the sensor inputs.

    $ cd /sys/bus/w1/devices
    $ ls
    28-0017984322bc  28-002498430404  28-00ff98431313  28-0114301b957a  w1_bus_master1

Notice there are 5 directories.   `w1_bus_master1` contains information about the 1-Wire master device (your Raspberry Pi) and the other four directories are named after the unique identifier of each of the sensors (1-Wire slave devices)

It should be noted that each device is assigned a hardware address at the factory, and is unique.  So no matter how many sensors you add, your existing sensors will always keep their name.

Let's read a sensor.  Change directory into one of your sensor directories.  Your names are different than mine, so you'll have to pick one for yourself.

    $ cd 28-0017984322bc
    $ ls
    driver  hwmon  id  name  power  subsystem  uevent  w1_slave
    $ cat w1_slave
    f9 ff 64 05 7f 00 00 ff 82 : crc=82 YES
    f9 ff 64 05 7f 00 00 ff 82 t=-437


My sensor, at the time of writing this, happens to be in the freezer at the moment, so it's giving a -.437 degrees.  Notice a string of hex numbers, repeated twice, and a CRC check.   The sensors will internally detect the temp, then report it, and the two results are verified against each other to ensure they weren't changed.   This is beyond the scope of this document, but you can read about it in the spec sheet which was linked to in the parts list section.   The value we are after is the number that comes after "t="  Out of the box these have a 3 digit accuracy, or measure to the thousandth of a degree.  So the resulting -437 value shown is -0.437C.  If the number showed 22750, it would be 22.750C.   For my use, I built a Python script to scrape these numbers, divide by 1000  which converts the integer to a float, then average to the nearest tenth or hundredth of a degree as needed.  Maybe your application will make use of the higher resolution, but mine doesn't for now.


## Automate it!

To keep things simple, I've split the duties of this device into two separate functions, each has it's own Python script.  The first function is  collecting temps from the probes at a certain frequency and writing them to a log file.   The second function is reading that log file, graphing and displaying the information on a simple web web page.   Both of these functions are controlled by the old-trusty crontab.  One cron job per task.   One cron job will start the web service when the device boots, and the other will run the temp scraping script once per minute in perpetuity.

Before that will work, you'll need to install a couple packages for your operating system, and some python libraries that the scripts make use of.  I've created an installation script called `install.sh` that will install the OS packages, Python modules, copy scripts into `/home/pi/sp/`, and add the two cron jobs.     All you have to do is restart the device and it will begin logging.

    $ install.sh

    After it's complete, reboot the pi and point a web browser from another computer on the network to the IP address of the Raspberry Pi, on port 8050 similar to this, but using your own IP address: `http://192./168.1.176:8050`

### Collect temps and write to a Log
In `/home/pi/sp/temps.py` script called `temps.py` that will look at the 1-wire directory (`/sys/bus/w1/devices`) and read all the directories within it, then traversing each of those directories, and grabbing the temp from each probe.   Then the script will check to see if a log file has been created yet, or not and create it (adding a header row) or append the temps to it once and end.

You can envoke this manually, to see how it works:

    $ python temps.py


### Display temps over a web page      
In `/home/py/sp/temps.py` there's another script called app.py.  This uses  a Flask/Dash framework to serve up the results in a web page.   You can access this by pointing a web browser (from your local network) the Pi IP address, on port 8050.   For instance `http://192./168.1.176:8050`  Here's a screen shot of an actual test I'm performing, using this device.


![DS18B20 Sensors](/images/mpemba_screenshot.png)











## (Optional - if you have supporting hardware) Enable UPS Battery Backup

I have some LiFePO4wered Raspberry Pi batter backup/UPS devices that I ordered from Crowd Supply, which are fantastic for adding power redundancy on important data gathering devices.   While this isn't required, it adds a bit of insurance that your precious data that you've gathered won't be interrupted while collecting.  

I will enable I2C for a battery backup device that I'm adding, you may not use this.

    $  echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
    $ sudo apt-get -y install build-essential git
    $ git clone https://github.com/xorbit/LiFePO4wered-Pi.git
    $ cd LiFePO4wered-Pi/
    $ ./build.py
    $ sudo ./INSTALL.sh

Connect hardware device, reboot.





## Get Science Project Code

Log in to the Pi via SSH over
    $ git clone https://github.com/jsprada/science_project
    $ cd science_project
    $ sh install.sh
