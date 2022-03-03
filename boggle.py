#! /usr/bin/env python3

"""
Main module for the Boggle UI.

The program will fail to run if the implementations for `GameDictionary`
or `GameManager` are incomplete.

Windows users need to install the `windows-curses` package:
```
py -m pip install --user windows-curses
```

To run the script, navigate to the top-level directory of this project
in a terminal window and execute:
    Unix:
        python3 boggle.py

    Windows:
        py boggle.py

You can view the full list of command-line arguments by adding `-h` to
the end of the command. e.g:
    python3 boggle.py -h
"""

import argparse
import curses
import logging
import os
from typing import List, Optional

import py_boggle.ui.tui as tui


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--log", action="store_true", help="Enable logging.")
    parser.add_argument(
        "-w", "--words", type=str, default="words.txt", help="Path to the words file."
    )
    parser.add_argument(
        "-c", "--cubes", type=str, default="cubes.txt", help="Path to the cubes file."
    )
    parser.add_argument(
        "-b", "--board", type=str, default="", help="Use the board in this file."
    )

    return parser.parse_args()


if __name__ == "__main__":
    cfg = parse_args()

    if cfg.log:
        logfile = "boggle-tui.log"
    else:
        logfile = os.devnull
    logfmt = "[%(name)s::%(funcName)s]: %(levelname)s: %(message)s"
    logging.basicConfig(filename=logfile, level=logging.DEBUG, format=logfmt)

    custom_board: Optional[List[List[str]]] = None
    if cfg.board:
        try:
            with open(cfg.board, "r") as fin:
                lines = fin.readlines()
                lines = [line.strip() for line in lines]
                lines = [line for line in lines if line]
                custom_board = [list(line) for line in lines]

                board_size = len(custom_board)
                for row in custom_board:
                    if len(row) != board_size:
                        logging.error("custom board is not square.")
                        custom_board = None
                        break
        except OSError:
            logging.error(f"custom board file '{cfg.board}' could not be read.")

    curses.wrapper(tui.entry, cfg, custom_board=custom_board)
