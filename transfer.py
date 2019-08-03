#!/usr/bin/env python3
"""Code file transferrer for KIPR Wallaby's. Requires Python 3.6 or higher."""

# Wallaby Code File Transferrer
# Copyright (C) 2019 "0xCBA" & James "thavoss06" Espericueta
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


# CREDITS
# Thank you Leland from Dead Robot Society for the original bash/batch scripts ("pycharm-wallaby-tools")
# that inspired the creation of this program

# pycharm-wallaby-tools is licensed under the MIT license.
#
# Copyright (c) 2019 Dead Robot Society
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# The subprocess module allows us to spawn host OS processes
from subprocess import check_call, CalledProcessError
# The sys module allows us to access key variables and functions used by the Python interpreter
# We use it to parse command-line arguments, terminate the program early, and determine specific host OS names
from sys import argv, exit, platform
# The os module allows us to interface with the host OS
# We use it to determine more general host OS names
from os import name

# The fabric module is a third-party module that allows us to create SSH connections
from fabric import Connection

# All of these evaluate to booleans
WINDOWS = platform in {"win32", "cygwin", "msys"}
MACOS = platform == "darwin"
OTHER_UNIX = name == "posix"  # Should cover at least Linux and *BSD

# Don't know of any OS that isn't going to be supported here
WIFI_SWITCHING_AVAILABLE = WINDOWS or MACOS or OTHER_UNIX

# --- CONFIG ---
# TODO: Maybe put all of this into a config file
# The following two variables act as a whitelist which determines how hostnames passed into the program
# should be treated
# Both whitelists affect what the upcoming hostname shorthands resolve to
# A prompt will occur whenever you pass a hostname that's part of a whitelist containing multiple hostnames
WIRED_HOSTNAME_WHITELIST = {"192.168.124.1", }
WIFI_HOTSPOT_HOSTNAME_WHITELIST = {"192.168.125.1", }  # This whitelist tells the program to switch Wi-Fi networks
# Hostname shorthands
# "wired" resolves to hostnames specified in WIRED_HOSTNAMES
# "hotspot" resolves to hostnames specified in WIFI_HOTSPOT_HOSTNAMES
# "prompt" will prompt for a hostname at runtime, accepting previous shorthands as input
# Anything else is not a shorthand and will parsed as an exact hostname
ACCEPT_HOSTNAME_SHORTHANDS = True  # Set to False to only allow an exact hostname passed as a command-line argument
APPEND_TO_FOUR_NUM_WALLABY_SSID = True  # Appends "-wallaby" to input for the SSID prompt if it contains 4 numbers
WINDOWS_WIFI_INTERFACE = "wlan"
MACOS_WIFI_INTERFACE = ""  # TODO: Determine this since this seems to vary
OTHER_UNIX_WIFI_INTERFACE = "wlan0"


def main(argc):
    """The main subroutine for this program.

    Tentative exit code meanings:
    Code 0: Success
    Code 1: General Error
    Code 2: Unsupported OS
    Code 3: Not Implemented
    """
    if argc < 5:
        print("You are missing command line arguments! Please include them")  # TODO: append "and read the README..."
        exit(1)

    # argv[0] is the program name; normally given automatically (unless you go out of your way to make it not)
    # COMMAND LINE ARGUMENTS ORDER SUBJECT TO CHANGE
    wallaby_hostname = argv[1]  # Hostname to connect to using SSH
    wallaby_user_name = argv[2].rstrip("/")
    wallaby_project_name = argv[3].rstrip("/")
    programming_language = argv[4].lower()  # Only "python" is accepted for now

    # No account password by default
    wallaby_linux_pass = None
    if argc > 5:
        wallaby_linux_pass = argv[5]

    switch_wifi_networks = False
    if WIFI_HOTSPOT_HOSTNAME_WHITELIST is not None and wallaby_hostname in WIFI_HOTSPOT_HOSTNAME_WHITELIST:
        if not WIFI_SWITCHING_AVAILABLE:
            print("Unfortunately, your OS is not supported for connecting to a Wallaby Wi-Fi hotspot...\n"
                  "You may use wired communication, or if your Wallaby acts as a client to a LAN,\n"
                  "you can specify its IP address or hostname")
            exit(2)
        switch_wifi_networks = True

    if switch_wifi_networks:
        wifi_ssid = input("Please specify the SSID of the Wallaby you wish to connect to: ")

        if APPEND_TO_FOUR_NUM_WALLABY_SSID and len(wifi_ssid) == 4:
            try:
                wifi_ssid = int(wifi_ssid)
                print("NOTICE: Appending \"-wallaby\" to inputted SSID")
                wifi_ssid = str(wifi_ssid) + "-wallaby"
            except ValueError:
                pass

        # Begin the OS-specific wifi-switching code
        # TODO: Finish all of this
        # In the end, this code should first probe the current SSID, save it to a variable, connect to a Wallaby,
        # and then connect back to the saved SSID
        if WINDOWS:
            try:
                check_call(["netsh", "wlan", "connect", f"name=\"{wifi_ssid}\""])
            except CalledProcessError:
                # TODO: Create xml profile for connecting to new network
                print("Creation of netsh xml profiles not implemented yet! Exiting...")
                exit(3)
        elif MACOS:
            print("Connecting to Wi-Fi in macOS is not implemented yet! Exiting...")
            exit(3)
        elif OTHER_UNIX:
            print("Connecting to Wi-Fi in UNIX-like OS's is not implemented yet! Exiting...")
            exit(3)

    # TODO: Add C support
    if programming_language != "python":
        print("Only Python is supported currently! Exiting...")
        exit(3)

    print("Connecting to Wallaby...")
    ssh = Connection(wallaby_hostname, user="root", connect_kwargs={"password": wallaby_linux_pass})

    ssh_wd = f"/home/root/Documents/KISS/{wallaby_user_name}/{wallaby_project_name}"

    print("Interacting with Wallaby...")
    print("Creating a backup directory...")
    ssh.run(f"cp -a {ssh_wd}/. {ssh_wd}-tmp/")

    print("Creating file & directory structure...")
    ssh.run(f"rm -rf {ssh_wd}/")
    ssh.run(f"mkdir -p {ssh_wd}/bin/ {ssh_wd}/src/ {ssh_wd}/data/ {ssh_wd}/include/")
    ssh.run(f'echo {{"language": "Python", "user": "{wallaby_user_name}"}} > {ssh_wd}/project.manifest')

    print("Transferring files...")
    ssh.put(f"{wallaby_project_name}", remote=f"{ssh_wd}/src")

    print("Creating necessary support files...")
    ssh.run(f"ln -s {ssh_wd}/bin/main.py {ssh_wd}/bin/botball_user_program")
    ssh.run(f"chmod +x {ssh_wd}/bin/main.py")

    # TODO: Add this functionality
    if switch_wifi_networks:
        print("Connecting back to previous Wi-Fi networks is not implemented! Exiting...")
        exit(3)

    # TODO: Automatically download libwallaby (this program is becoming very complex)


# Runs main() only if not imported as a module
if __name__ == "__main__":
    main(len(argv))
