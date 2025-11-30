"""Command Line Module For HC-12"""

from threading import Thread, Event

from .cli_parser import cli_parser
from .wrapper import HC12


def recv_loop(hc12: HC12, stop: Event) -> None:
    """HC-12 receive loop function"""
    while not stop.is_set():
        if hc12.readable():
            encoded_msg = hc12.readline()
            if len(encoded_msg):
                decoded_msg = encoded_msg.decode(hc12.encoding).strip()
                print(f"\nHC-12 [RECV MSG]: {decoded_msg}")


def main():
    args = cli_parser.parse_args()
    hc12 = HC12(port=args.port, baudrate=args.baud_rate, debug=args.debug)

    print("\nType 'EXIT' to quit!\n")

    stop_event = Event()
    recv_loop_thread = Thread(
        name="HC-12-RECV",
        target=recv_loop,
        args=(
            hc12,
            stop_event,
        ),
    )
    recv_loop_thread.start()

    while True:
        msg = input("HC-12 [SEND MSG]: ")
        if msg.upper() == "EXIT":
            stop_event.set()
            recv_loop_thread.join()
            hc12.close()
            break
        if hc12.writable():
            hc12.write(bytes(f"{msg}\n", hc12.encoding))
