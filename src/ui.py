from getpass import getpass
import socket


COLORS = {"green" : "\33[92m",
          "red"   : "\33[91m",
          "yellow" : "\33[93m",
          "endc"    : "\33[0m" }


def print_green(msg):
    """Prints msg in green text."""
    print("{0}{1}{2}".format(COLORS["green"], msg, COLORS["endc"]))


def print_yellow(msg):
    """Prints msg in yellow text."""
    print("{0}{1}{2}".format(COLORS["yellow"], msg, COLORS["endc"]))


def print_red(msg):
    """Prints msg in red text."""
    print("{0}{1}{2}".format(COLORS["red"], msg, COLORS["endc"]))


def input_handled(prompt):
    """Wrapper for input() that handles KeyboardInterrupts."""
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print_red("\nAborting...")
        exit()


def getpass_handled(prompt):
    """Wrapper for getpass() that handles KeyboardInterrupts."""
    try:
        return getpass(prompt)
    except KeyboardInterrupt:
        print_red("\nAborting...")
        exit()


def confirm(prompt):
    """Displays the prompt, only returns true with input 'Y' or 'y'."""
    confirmation = input_handled(COLORS["yellow"] + prompt + COLORS["endc"]).lower()
    return confirmation == "y"


def input_default(prompt, default):
    """Displays the prompt, returns input (default if user enters nothing)."""
    response = input_handled("{} [{}]: ".format(prompt, default))
    return response if response else default


def get_ip():
    """Prompts the user for and returns a valid IP address string."""
    while True:
        ip = input_handled("IP: ")

        # Check if the ip has 3 "."s. inet_aton does not verify this
        if len(ip.split(".")) != 4:
            print_red("\nInvalid IP address. Please try again.")
            continue

        # Check if input creates a valid ip
        try:
            socket.inet_aton(ip)
        except socket.error:
            print_red("\nInvalid IP address. Please try again.")
            continue

        return ip


def get_command(commands):
    """Prompts for a command, and returns when the user has chosen a valid one."""
    while True:
        command = input_handled("> ").lower()

        if command in commands:
            return command
        else:
            print_red("Invalid command. Please try again.")

