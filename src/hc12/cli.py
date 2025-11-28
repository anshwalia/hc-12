"""Command Line Module For HC-12"""

from .wrapper import HC12


def main():
    port = input("HC-12 Port: ")
    hc12_module = HC12(port)
    print("Type 'EXIT' to quit!")
    while True:
        user_input = input("HC-12 => ")
        if user_input == "EXIT":
            break
        hc12_module.send(user_input.encode())
