#!/bin/sh
# Install

upgrade_system()
{
sudo apt-get update
sudo apt-get -y dist-upgrade
}

install_packages()
{
sudo apt-get install -y $(cat packages.txt) --no-install-recommends
}

install_requirements()
{
sudo pip install -r requirements.txt
echo "dtoverlay=w1-gpio" | sudo tee -a /boot/config.txt
}

install_files()
{
mkdir /home/pi/sp
cp temps.py /home/pi/sp/temps.py
cp app.py /home/pi/sp/app.py
}

setup_cron()
{
echo "@reboot pi /usr/bin/python /home/pi/sp/app.py" | sudo tee /etc/cron.d/sp_on_reboot
echo "* * * * * pi /usr/bin/python /home/pi/sp/temps.py >> /dev/null 2>&1" | sudo tee /etc/cron.d/sp_per_minute
echo "0 * * * * pi /usr/bin/rsync /home/pi/sp/temps_log /home/pi/sp/temps_log_backup" | sudo tee /etc/cron.d/sp_per_hour
echo "Please reboot now"
}

upgrade_system
install_packages
install_requirements
install_files
setup_cron
