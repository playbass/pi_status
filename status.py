#!/usr/bin/python
# File Name :
# Creation Date :
# Last Modified : Fri 05 Feb 2016 03:16:45 PM MST
# Created By : originally created by /u/TheLadDothCallMe
#              major mods by Nathan Gilbert
'''
Simple Raspberry Pi Web Status Page
'''
# DISCLAIMER: I won't be held accountable for what you do with
# this script. Use it however you choose, and let me know
# if you create something cool with it!
#
# This script collects various infos about the Pi
# and then inserts them into an HTML template before
# printing it to the screen.
# It is meant to be used by calling the script from the
# command line and outputting the result to an file
# on a web server.
#
# Example usage: "python status.py > /var/wwww/html/status.html"
#
# As it is HTML, the whole look and feel can be modified in the
# template below if you know a little CSS. Additional information
# can be added by adding the output of a shell command to a variable
# and enclosing it within a DIV of class "detailItem" in the template.

import psutil # Only used pretty much for getting the RAM values
import time
from subprocess import check_output

# This has the main HTML template that is used every time the script is run.
# If you have issue after modifying it, make sure you have your quotes in
# the right places. Notepad++ is great for syntax highlighting it.
def printHtml():
    """prints out the html file"""
    print '''<html>
	<head>
		<title>Raspberry Pi Status</title>
		<link href='https://fonts.googleapis.com/css?family=Oswald' rel='stylesheet' type='text/css'>
		<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1" />
		<style>
			body {
			background-color: #1C1C1C;
			font-family: 'Oswald', sans-serif;
			}
			#container {
			width: 100%;
			max-width: 600px;
			margin: 20px auto;
			padding-top: 10px;
			background-color: #585858;
			}
			#details {
			display:block;
			padding:10px;
			}
			#logo {
			background-image: url("rpi.png");
			background-size: auto 150px;
			background-repeat: no-repeat;
			height: 150px;
			width: 125px;
			margin: 0px auto;
			}
			.detailItem {
			padding: 5px;
			margin: 10px;
			background-color: #A4A4A4;
			vertical-align:middle;
			}
			#ramBar {
			width:100%;
			height: 20px;
			background-color:#75a928;
			}
			#diskBar {
			width:100%;
			height: 20px;
			background-color:#75a928;
			}
			#ramFill {
			float:left;
			width: ''' + ram_percent + '''%;
			height:100%;
			background-color:#bc1142;
			}
                        #diskFill {
			float:left;
			width: ''' + disk_percent + '''%;
			height:100%;
			background-color:#bc1142;
                        }
		</style>
	</head>
	<body>
		<div id="container">
			<div id="logo"></div>
			<div id="details">
                            <div class="detailItem">Hostname: ''' + hostname + '''</div>
                            <div class="detailItem">Uptime: ''' + uptime + '''</div>
                            <div class="detailItem">CPU Temp: ''' + temp_c\
                            + ''' &deg;C (''' + temp_f + ''' &deg;F)</div>
                            <div class="detailItem">RAM: ''' + ram_used +\
                                    ''' MB used of ''' + ram_total + '''\
                                    MB, ''' + ram_free + ''' MB free
                                    <div id="ramBar">
                                        <div id="ramFill" />
                                        </div>
                                    </div>
                            </div>
                            <div class="detailItem">Disk: ''' + disk_used +\
                                    ''' MB (''' + disk_percent + '''%) used of ''' + disk_total + '''\
                                    MB, ''' + disk_free + ''' MB free
                                    <div id="diskBar">
                                        <div id="diskFill" /></div>
                                    </div>
                            </div>

                            <div class="detailItem">Google Ping: ''' + ping + ''' \
                            ms -- Avg: ''' + avg_ping + ''' ms</div>
                            <div class="detailItem">Banned SSH IPs today: ''' +\
                            str(banned_ips) + '''</div>
                            <div class="detailItem">Last Updated: ''' + updated + '''</div>
			</div>
		</div>
	</body>
</html>'''
#<div class="detailItem">DNS Queries Today: ''' + dns + '''</div>
    return

def save_ping(ping_value):
    """Saves the ping value out to a file"""
    with open("/var/www/html/ping_history.txt", 'a') as ping_file:
        ping_file.writelines(ping_value + "\n")

def read_ping():
    """Read in the ping history and return an avg value"""
    lines = []
    with open("/var/www/html/ping_history.txt", 'r') as ping_file:
        lines = ping_file.readlines()

    #grab the last 5 lines
    total = sum(map(lambda x: float(x.strip()), lines))
    return str(total / len(lines))

# Just shows the hostname command. Note the .split() function to get rid of any new lines from the shell.
hostname = check_output(["hostname"]).strip()
# The calculations here are just lazy and round to the nearest integer.
ram_total = str(psutil.virtual_memory().total / 1024 / 1024)
ram_used = str((psutil.virtual_memory().total - psutil.virtual_memory().available) / 1024 / 1024)
ram_free = str(psutil.virtual_memory().available / 1024 / 1024)
ram_percent = str(psutil.virtual_memory().percent)

# Shows the uptime from the shell with the pretty option
uptime = check_output(["uptime", "-p"]).strip()
#dns = check_output(["cat /var/log/dnsmasq.log | grep \"$(date \"+%b %e\")\" | grep \"query\" | wc -l"],shell=True).strip() # This isn't needed if you are not running DNSmasq

# The last time the script was run
updated = time.strftime("%I:%M:%S %p %m/%d/%Y %Z")

# Reads the CPU temp in milligrade
temp_c = str(round(float(check_output(["cat","/sys/class/thermal/thermal_zone0/temp"])) / 1000,1))
temp_f = str(float(temp_c) * 1.8 + 32)

# Pings Google DNS 5 times and awks the average ping time
ping = check_output(["ping -c 5 8.8.8.8 | tail -1| awk -F '/' '{print $5}'"],shell=True).strip()
save_ping(ping)
avg_ping = read_ping()

# get the storage space used
disk_space = check_output(["df", "-m"])
disk_percent = "0"
disk_used = "0"
disk_free = "0"
disk_total = "0"
lines = disk_space.split("\n")
for line in lines:
    #print line
    if line.startswith("/dev/root"):
        tokens = line.split()
        disk_used = str(int(tokens[2]))
        disk_free = str(int(tokens[3]))
        disk_total = str(int(tokens[1]))
        disk_percent = str(float(tokens[4].replace("%", "")))
        break

lines = []
with open("/var/log/fail2ban.log", 'r') as inFile:
    lines = inFile.readlines()
today = time.strftime("%Y-%m-%d")
banned_ips = 0
for line in lines:
    if line.startswith(today):
        if line.find("Ban") > -1:
            banned_ips += 1

printHtml() # Calls the function and puts everything together