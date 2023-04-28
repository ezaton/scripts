#!/usr/bin/env python3

'''
This script is meant to allow capturing the PPPoE credentials used by locked home routers.
Locked routers are a very common case in Spain, and in order to replace the ISP-provided router
with a natural router, you will have to get the login information.
You can follow up on the procedure of doing it in here (requires Spanish or translation software):
https://www.frikidelto.com/tutorial/como-conseguir-el-usuario-y-contrasena-pppoe-para-instalar-un-router-neutro/

This script is derived by the original script created by FRIKIdelTo, and then rewritten
in English, with some structure changes, however - the idea remains the same.

The original text by FRIKIdelTo:
Creado por FRIKIdelTO (https://www.frikidelto.com)
Este script fue desarrollado siguiendo el excelente tutorial que BocaDePez (usuario anónimo) publicó en:
https://bandaancha.eu/foros/sustituir-router-digi-fibra-router-1732730/2#r1lf3a
todo el mérito es de él. Gracias crack, seas quién seas ;-)

Muchas gracias a Manel (@VillaArtista en Telegram) por avisarme de dicho tutorial
y por aclararme dudas durante el desarrollo de este script.
'''

import subprocess
import netifaces
from pathlib import Path as path
import re
import os
import sys
import time
import datetime

# CONSTANTS
# 
NAME = "GETpppoe"
VERSION = NAME + " 1.0"
ORIG_NAME = "FRIKIpppoe"
ORIG_VERSION = ORIG_NAME + " 21.05.03 by FRIKIdelTO.com"


configuration = """\
ms-dns 8.8.8.8 asyncmap 0
noauth
crtscts
lock
hide-password
modem
debug
proxyarp
lcp-echo-interval 10
lcp-echo-failure 2
noipx
plugin /etc/ppp/plugins/rp-pppoe.so
require-pap
ktune
nobsdcomp
noccp
novj
"""
# operators and their vlan
operators = (
["DiGi", 20],
["Movistar/Tuenti/O2", 6],
["Vodafone/Lowi", 100],
["NEBA: Vodafone/Lowi", 24],
["Jazztel", 1074],
["MasMovil/PepePhone/Yoigo", 20],
["Orange/Amena", 832],
["Adamo", 603]
)

# Terminate all processes
def kill_proceses():
    print_save("Performing process cleanup")
    subprocess.run(['sudo', 'killall', '-q', '-w', 'tshark'])
    subprocess.run(['sudo', 'killall', '-q', '-w', 'pppoe-server'])


# A function to test Internet connection
def check_internet():
    internet = False
    format = 0
    while internet == False:
        try:
            subprocess.check_output(['ping', '-c', '2', '8.8.8.8'], stderr=subprocess.STDOUT, universal_newlines=True)
            internet = True
        except subprocess.CalledProcessError:
            print("Waiting for Internet connection... \n")
            time.sleep(1)


# Show how much time passed since starting the capture
def show_time(begin):
    minutes = 0
    seconds = (datetime.datetime.now() - begin).seconds # How many seconds passed since the beginning
    if seconds > 0:
        print("Completed in " + str(seconds) + " seconds")
    return seconds


# Saves into log file
def save_log(message):
    time = datetime.datetime.now().strftime("%d/%m/%Y_%H:%M:%S")
    archive = open(ARCHIVE_LOG, "a", encoding="utf-8")
    if message == "\n":
        archive.write("\n")
    else:
        archive.write(time + "  " + str(message) + "\n")
    archive.close()


# Prints on screen and saves to log file
def print_save(message):
    save_log(message)
    print(message + "\n")


# Shows the contents of the log
def show_log():
    print("Records saved:")
    archive = open(ARCHIVE_LOG, "r", encoding="utf-8")
    for line in archive:
        print(line.replace('\n',''))
    archive.close()


# Document how many packets were saved
def calculate_packets_captured():
    archive = open(str(path.home()) + "/" + NAME + "/capture.txt", "r", encoding="utf-8")
    counter = len(archive.read().split('\n'))
    archive.close()
    save_log('Captured Packets: ' + str(counter-1))


# Create log directory
def create_path():
    os.chdir(str(path.home()))
    try:
        os.mkdir(NAME)
    except:
        pass


# Identify which Linux distro
def what_distro():
    # If Ubuntu/Debian - run required installation components. If RH/OEL/Centos/Fedora - run different actions
    # Not sure in Python 3.8 distro.id() is used. In earlier versions - platform.linux_distribution() which is already deprecated
    try:
        import distro
        dist = distro.id()
    except AttributeError:
        import platform
        dist = platform.linux_distribution()[0]

    # Check what type of Linux we are using
    if any(name in dist.lower() for name in ["oracle", "redhat", "fedora", "centos", "alma", "rocky"]):
        distro = "rhel"
        print_save("Distro is " + distro)
    elif any(name in dist.lower() for name in ["ubuntu", "debian", "mint"]):
        distro = "ubuntu"
        print_save("Distro is " + distro)
    else:
        print_save("Distro is unknown. Skipping software installation")
        distro = "unknown"
    return distro


# Install software on Ubuntu
def software_ubuntu(software_list):
    archive = open("/etc/apt/sources.list", "r", encoding="utf-8")
    content = archive.read()
    archive.close()
    command = "apt"
    if 'universe' not in content:
        print_save('Adding the "universe" respository')
        subprocess.run(["sudo", "add-apt-repository", "universe"])
    else:
        print_save('The "universe" respository is defined')

    for software in software_list:
        if software == "tshark":
            subprocess.run(["echo", '"wireshark-common wireshark-common/install-setuid boolean true"', "|", "sudo",  "debconf-set-selections"])
        try:
            print_save("Installing " + software)
            subprocess.run(["sudo", "DEBIAN_FRONTEND=noninteractive", "apt-get", "install",  software, "--yes"])
        except:
            print_save("Failed to install " + software + ". Continuing anyhow")
            pass


# Install software on RHEL family
def software_rhel(software_list,rhel_group_software_list):
    for software in software_list:
        try:
            subprocess.run(["sudo", "dnf", "install",  "-y", software])
        except:
            print_save("Failed to install " + software + ". Continuing anyhow")
            pass
    for software in rhel_group_software_list:
        try:
            # Handle package groups
            subprocess.run(["sudo", "dnf", "groupinstall",  "-y", software])
        except:
            print_save("Failed to install group " + software + ". Continuing anyhow")
            pass


# Checks a list of software components. If missing - they will be installed
def check_software():
    minimal_software_list = [
        "tshark",
        "ppp",
        "pppoe-server",
        "wget",
        "tar"
    ]  
    missing_software = []
    distro = what_distro()
    for software in minimal_software_list:
        try:
            subprocess.check_output(["which", software])
            print_save(software + "is installed")
        except:
            # Populate a list of missing software
            missing_software.append(software)

    # Python modules
    try:
        import requests
    except:
        missing_software.append("python3-requests")

    # Do we have any missing software?    
    if missing_software:
        # We need to go through adding/installing said components
        
        print("The following missing software is \n")
        print(missing_software, end=" ")
        save_log(missing_software)
        install_software(distro,missing_software)


# Install the required software.
def install_software(distro,missing_software):
    additional_ubuntu_software_list = [
        "ppp-dev",
        "pppoeconf",
        "build-essentials"
    ]
    additional_rhel_software_list = [
        "make",
        "pppd-dev"
    ]
    rhel_group_software_list = [
        "Development Tools"
    ]
    print_save("Need to verify that Internet connection works")
    check_internet()
    pppoe_server = False
    # Special care needs to be taken for pppoe-server
    if "pppoe-server" in missing_software:
        pppoe_server = True
        missing_software.remove("pppoe-server")
        if distro == "ubuntu":
            missing_software = additional_ubuntu_software_list + missing_software
        elif distro == "rhel":
            missing_software = additional_rhel_software_list + missing_software
    # Do we have any missing software?
    if missing_software:
        if distro == "ubuntu":
            software_ubuntu(missing_software)
        elif distro == "rhel":
            software_rhel(missing_software,rhel_group_software_list)
        else:
            print_save("Missing software. Install manually or modify the script to handle your own Linux distribution!")
    if pppoe_server:
        get_and_compile_pppoe()
    # Now that we have all software installed, we need to configure PPPoE
    configure_pppoe()


# Download and install PPPoE Server
# Happens the same on all platforms
def get_and_compile_pppoe():
    print_save("Grabbing latest version of rp-pppoe sources")
    import requests
    result = requests.get('https://dianne.skoll.ca/projects/rp-pppoe/download/').content
    links = re.findall(r'<a href=[\"]?([^\" >]+)', str(result))
    found = False
    for link in links:
        if "tar.gz" in link and ".sig" not in link:
            url = 'https://dianne.skoll.ca/projects/rp-pppoe/download/' + link
            archive = link
            print_save("Grabbing: " + str(archive))
            found = True
    if found == False:
        print_save("ERROR: Cannot find link to rp-pppoe on the Internet. Try installing it manually")
        print_save("Aborting")
        sys.exit()
    else:
        save_log('Found link: ' + str(url))
    
    if path(archive).is_file() == True:
        print_save("File already downloaded")
    else:
        check_internet()
        subprocess.run(["wget", url])
        print_save('Download done')
    file = archive.replace('.tar.gz','') + "/src"
    if path(file).is_dir() == True:
        print_save("File already extracted")
    else:
        subprocess.run(["tar", "xvf", archive])
        print_save('Extracted source file')

    os.chdir(file)
    try:
        print_save("Configuring source")
        subprocess.run(["./configure", '--enable-plugin'])
        print_save("Done")
        print_save("Compiling")
        subprocess.run(["make"])
        print_save("Done")
        print_save("Compiling rp-pppoe.so")
        subprocess.run(["make", "rp-pppoe.so"])
        print_save("Done")
        print_save("Installing")
        subprocess.run(["sudo", "make", "install"])
        print_save("Done")
    except:
        print_save("Failed to compile package. Either missing dependencies or an unknown Linux. Try manually to compoile rp-pppoe, and when done - re-run this script")
        sys.exit()


# Configure PPPoE
def configure_pppoe():
    print_save("Creating /etc/ppp/options")
    try:
        archive = open("/etc/ppp/options", "w", encoding="utf-8")
        archive.write(configuration)
        archive.close()
    except:
        print_save("ERROR: Failed to create /etc/ppp/options")
        sys.exit()
    print_save("Creating /etc/ppp/pap-secrets")
    line = '"Username"' + '\t' + '*' + '\t' + '"p4ssw0rd"' + '\t' + '*' + '\n'
    try:
        archive = open("/etc/ppp/pap-secrets", "r", encoding="utf-8")
        content = archive.read()
        archive.close()
        if line not in content: # File has not been previously modified
            archive = open("/etc/ppp/pap-secrets", "a", encoding="utf-8")
            archive.write(line)
            archive.close()
            print_save("Done")
        else:
            print_save("Our fake credentials are already set in")
        print_save("Done")
    except Exception as e:
        print_save("Failed to save PPP credentials")
        sys.exit()


# Detects the required network interface
def detect_interface():
    interface = ""
    all_nics = netifaces.interfaces()
    print_save("All detected interfaces are " + str(all_nics))
    for item in all_nics:
        if item[:3] == "eth" or item[:2] == "en":
            interface = item
            break
    if interface == "":
        print_save("Could not detect the correct Ethernet interface")
        print_save("ERROR: Aborting")
        sys.exit()
    else:
        print_save("Detected interface " + interface)
    return(interface)


# Provides a list of Internet providers, and asks for relevant VLAN ID
def select_isp():
    print_save("List of Operators:")
    print("==================\n")
    n = 1
    total = len(operators)
    for operator in operators:
        name = operator[0]
        vlan = operator[1]
        print("[ " + str[n] + " ] " + name + " (vlan: " + str(vlan) + ")\n")
        n = n + 1 
    print("[ " + str[n] + " ] " + "Enter VLAN manually\n")
    print()
    save_log("Asking for VLAN")
    option = ""
    while True:
        try:
            option = int(input("Select your Operator: "))
            if option > 0 and option <= n:
                break
            else:
                print("Invalid option\n")
                time.sleep(1)
                print()
        except KeyboardInterrupt:
            print()
            print()
            print()
            print_save("Operation Interrupted by User")
            sys.exit()
        except:
            print("Invalid option: You must enter a number")
            time.sleep(1)
    vlan = 0
    if option == n:
        print_save("The user has selected to enter VLAN manually")
        while True:
            try:
                vlan = int(input("Enter a VLAN: "))
                break
            except KeyboardInterrupt:
                print()
                print()
                print()
                print_save("Operation Interrupted by User")
                sys.exit()
            except:
                print("Invalid option: You must enter a number\n")
                time.sleep(1)
    else:
        vlan = operators[option-1][1]
    print_save("Selected VLAN " + vlan)
    return(vlan)


# Cleans up all interfaces
def cleanup_interfaces():
    all_nics = netifaces.interfaces()
    for item in all_nics:
        if "." in item:
            print_save("Cleaning up interface " + item)
            subprocess.run(["sudo", "ip", "link", "delete", item])
            print_save("Cleaned up " + item)


# Sets up the network interface with the correct VLAN
def setup_interface(interface,vlan,interface_vlan):
    print_save("Creating a VLAN interface " + interface + " with VLAN " + str(vlan))
    try:
        subprocess.run(["sudo", "ip", "link", "add", "link", interface, "name", interface_vlan, "type", "vlan", "id", str(vlan)])
        print_save("Interface " + interface_vlan + " created")
    except Exception as e:
        print_save("Cannot create VLAN interface")
        print_save("Message: " + str(e))
        sys.exit()
    define_ip(interface_vlan)
    bring_up(interface_vlan)


# Defines IP
def define_ip(interface_vlan):
    print_save("Setting up temporary IP address")
    try:
        subprocess.run(["sudo", "ip", "addr", "flush", "dev", interface_vlan])
        subprocess.run(["sudo", "ip", "addr", "add", "10.0.0.1/16", "dev", interface_vlan])
        print_save("Done")
    except Exception as e:
        print_save("Cannot flush and set IP address to interface")
        print_save("Message: " + str(e))
        sys.exit()


# Brings interface up
def bring_up(interface_vlan):
    print_save("Activating interface " + str(interface_vlan))
    try:
        subprocess.run(["sudo", "ip", "link", "set", interface_vlan, "up"])
        print_save("Done")
    except Exception as e:
        print_save("Cannot bring interface up")
        print_save("Message: " + str(e))
        sys.exit()


# Message the user and ask for Enter to start:
def text_message():
    print("Everything is ready to start capturing the packets from the router. \n")
    print("It is not necessary to remain connected to the Internet anymore. \n")
    print("-----------------------------------------------------------------\n")
    print("Connect the WAN port of the router to the configured computer network interface\n")
    print("-----------------------------------------------------------------\n")
    input("Press on ENTER when ready\n")


# Starts PPPoE Server
def start_pppoe(interface_vlan):
    kill_proceses()
    print_save("Starting PPPoE Service")
    try:
        subprocess.run(["sudo", "pppoe-server", "-C", "ftth", "-I", interface_vlan, "-N", "256", "-O", "/etc/ppp/options"])
        print_save("Done")
    except Exception as e:
        print_save("Cannot start pppoe")
        print_save("Message: " + str(e))
        sys.exit()


# Capture packets
def capture_packets(interface_vlan):
    print_save("Starting packet capturing")
    try:
        subprocess.Popen(["sudo", "tshark", "-i", interface_vlan, "-T", "text"], stdout=open(str(path.home()) + "/" + NAME + "/capture.txt", "wb"), stderr=open(os.devnull, 'w'))
        print_save("Done")
    except Exception as e:
        print_save("Cannot capture")
        print_save("Message: " + str(e))
        sys.exit()


# Grabs the credentials from the dump file
def grab_creds():
    print_save("Grabbing credentials from capture file")
    username = ""
    password = ""
    initial = datetime.datetime.now()
    while username == "" and password == "":
        try:
            print_save("Please wait. It may take a while")
            archive = open(str(path.home()) + "/" + NAME + "/capture.txt", "r", encoding="utf-8")
            for line in archive:
                if 'Authenticate-Request' in line:
                    try:
                        username = re.search(r'Peer-ID=\'([\@A-Za-z0-9_\./\\-]*)\'', line).group(1)
                    except:
                        pass
                    try:
                        password = re.search(r'Password=\'([\@A-Za-z0-9_\./\\-]*)\'', line).group(1)
                    except:
                        pass
                    if username != "" and password != "":
                        print_save("PPPoE Credentials detected")
                        print_save("Username: " + str(username))
                        print_save("Password: " + str(password))
                        show_time(initial)
                        calculate_packets_captured()
                        break
            archive(close)
        except KeyboardInterrupt:
            print_save("Interrupted by user")
            calculate_packets_captured()
            show_log()
            sys.exit()
        except:
            pass


### MAIN ###
if __name__ == '__main__':
    # Clean the shell
    os.system("clear")

    # Make sure it runs as root or sudo
    if os.geteuid() != 0:
        subprocess.run(['sudo', 'python3', *sys.argv])
        sys.exit(0)

    # Cleanup
    kill_proceses()

    os.chdir(NAME)
    ARCHIVE_LOG = str(path.home()) + "/" + NAME + "/" + NAME + ".log"
    save_log('\n')
    save_log('Starting the script')
    os.system("clear")
    print(VERSION)
    # Check what is installed and add the missing packages
    check_software()
    interface = detect_interface()
    vlan = select_isp()
    interface_vlan = "sniffer." + str(vlan)
    cleanup_interfaces()
    setup_interface(interface,vlan,interface_vlan)
    text_message()
    start_pppoe(interface_vlan)
    capture_packets(interface_vlan)
    grab_creds()
    print_save("Operation done")
    sys.exit()