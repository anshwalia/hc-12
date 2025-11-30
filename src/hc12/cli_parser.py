"""Argument Parser Module"""

from argparse import ArgumentParser

cli_parser = ArgumentParser(
    prog="HC-12 CLI",
    description="Command line interface for HC-12 serial wireless module",
)

# CLI Arguments
cli_parser.add_argument(
    "-p", "--port", type=str, help="HC-12 serial port", required=True
)
cli_parser.add_argument(
    "-b", "--baud-rate", type=int, default=9600, help="HC-12 serial baudrate"
)
cli_parser.add_argument(
    "-d", "--debug", type=bool, default=False, help="HC-12 debug mode"
)
