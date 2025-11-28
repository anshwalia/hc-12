from .wrapper import HC12


def main():
    port = input("HC-12 Port: ")
    hc12_module = HC12(port)
    print(hc12_module.get_current_settings())
