"""
A curses-based text user interface for Boggle.

The player types words into the window and presses enter to submit them.
Feedback is presented to the player in the following ways:
  - The player is told whether the word is invalid, is not on the board,
    is found successfully, or was found already.
  - The point value of the word is displayed, if applicable.
  - The path formed by the word is displayed on the board, if applicable.
  - The set of found words is displayed.

The player can display the list of all words on the board and optionally
start a new game by pressing `CTRL + D`.

The player can completely exit the game by pressing `CTRL + C`.
"""

import argparse
import curses
import enum
import logging
import sys
import textwrap
import copy
from typing import Any, Dict, List, NamedTuple, Optional, Set, Tuple, Type, TypeVar

from py_boggle import game_dictionary, game_manager  # noqa: F401
from py_boggle.boggle_dictionary import BoggleDictionary
from py_boggle.boggle_game import BoggleGame

"""The `curses.window` type isn't available before Python 3.8

To avoid runtime issues with `curses.window` being undefined in 3.6 and 3.7,
we use the `CursesWindow` type defined here in type hints.
"""
if sys.version_info < (3, 8):
    CursesWindow = Any
else:
    CursesWindow = curses.window


_BaseType = TypeVar("_BaseType")


def construct_subclass_of(base: Type[_BaseType]) -> _BaseType:
    """Construct an instance of a subclass of the `base` type.

    Args:
        base: A base class type (not an instance). The constructor
        of the subclass must not accept parameters.

    Returns:
        An instance of a subclass of the `base` type.

    Raises:
        RuntimeError: No subclass exists in the module scope.
        TypeError: The constructor of the subclass requires at least
            one argument.
    """
    subclasses = base.__subclasses__()

    if len(subclasses) == 0:
        errmsg = f"Could not find any subclasses of {base.__name__}"
        logging.critical(errmsg)
        raise RuntimeError(errmsg)
    else:
        try:
            return subclasses[0]()
        except TypeError as err:
            errmsg = f"The constructor of {base.__name__} must not accept parameters."
            logging.critical(errmsg)
            raise err


class Coordinate(NamedTuple):
    row: int
    col: int

    def __add__(self, other):
        """Add two coordinates.

        Args:
            other (Coordinate): The addend.

        Returns:
            Coordinate: The sum of this Coordinate and `other`.
        """
        return Coordinate(self.row + other.row, self.col + other.col)

    def __sub__(self, other):
        """Subtract two coordinates."""
        return Coordinate(self.row - other.row, self.col - other.col)

    def div(self, divisor: int):
        """Divide each element of a coordinate by an integer.

        Returns a new coordinate.
        """
        return Coordinate(self.row // divisor, self.col // divisor)

    # TODO: refactor: move this to the TUI class?
    def to_board_coords(self):
        """Return a Coordinate scaled to the board subwindow."""
        return Coordinate(self.row * TUI.BOARD_Y_SCALE, self.col * TUI.BOARD_X_SCALE)

    def __tuple__(self) -> Tuple[int, int]:
        """Convert this object into a standard Tuple.

        Returns:
            A row-major tuple representation of this coordinate.
        """
        return (self.row, self.col)


"""Type alias to convey intent."""
CoordinateDelta = Coordinate


class Ordinal(enum.Enum):
    """A Coordinate delta representation of ordinal directions."""

    NORTH = CoordinateDelta(-1, 0)
    NORTHEAST = CoordinateDelta(-1, 1)
    EAST = CoordinateDelta(0, 1)
    SOUTHEAST = CoordinateDelta(1, 1)
    SOUTH = CoordinateDelta(1, 0)
    SOUTHWEST = CoordinateDelta(1, -1)
    WEST = CoordinateDelta(0, -1)
    NORTHWEST = CoordinateDelta(-1, -1)

    # Special cross-cases
    NE_NW_CROSS = CoordinateDelta(-2, 0)
    NE_SE_CROSS = CoordinateDelta(0, 2)
    SE_SW_CROSS = CoordinateDelta(2, 0)
    SW_NW_CROSS = CoordinateDelta(0, -2)


arrows = {
    Ordinal.NORTH: "↑",
    Ordinal.NORTHEAST: "↗",
    Ordinal.EAST: "→",
    Ordinal.SOUTHEAST: "↘",
    Ordinal.SOUTH: "↓",
    Ordinal.SOUTHWEST: "↙",
    Ordinal.WEST: "←",
    Ordinal.NORTHWEST: "↖",
    # Special cross-cases
    Ordinal.NE_NW_CROSS: "⤧",
    Ordinal.NE_SE_CROSS: "⤨",
    Ordinal.SE_SW_CROSS: "⤩",
    Ordinal.SW_NW_CROSS: "⤪",
}


class TUI:
    """Encapsulates a TUI.

    Attributes:
        log: logging interface
        dict: BoggleDictionary instance
        cubes: cubes file for the BoggleGame
        custom_board: custom board for the BoggleGame
        game: BoggleGame instance
        input_buf: Input buffer for keyboard entry
        input_feedback: Feedback to the player about the previous input.
        last_word_coords: The coordinates of the last added word.
        found_words: set of words found so far
        scr: main curses window
        subwins: curses subwindows
            subwins["board"]: curses subwindow for the board
            subwins["input"]: curses subwindow for the input area
            subwins["info"]: curses subwindow for misc. game info (scores)
            subwins["words"]: curses subwindow for found words
    """

    BOARD_SIZE = 4
    BOARD_Y_SCALE = 2
    BOARD_X_SCALE = 4

    def __init__(
        self,
        scr: CursesWindow,
        words: str,
        cubes: str,
        custom_board: Optional[List[List[str]]],
    ):
        """Create a new TUI.

        Initialize game elements to their default values.

        Args:
            scr: curses screen object
            words: path to words file
            cubes: path to cubes file
        """
        self.log = logging.getLogger("tui")
        self.log.info("-" * 20)
        self.log.info("Creating new TUI")

        """(type: ignore): Type[T] expects a concrete class.
        Although mypy is told to ignore the error, it still seems to
        infer the type of the instance variables correctly.
        """
        self.dict = construct_subclass_of(BoggleDictionary)  # type: ignore
        self.game = construct_subclass_of(BoggleGame)  # type: ignore
        self.custom_board = custom_board
        try:
            self.log.info(f"words file: {words}")
            self.dict.load_dictionary(words)
            self.log.info(f"cubes file: {cubes}")
            self.cubes = cubes
            self.game.new_game(self.BOARD_SIZE, 1, cubes, self.dict)
        except OSError as err:
            self.log.critical(err)
            raise err

        if self.custom_board:
            self.game.set_game(self.custom_board)
        self.check_board_size()

        self.input_buf: List[str] = []
        self.input_feedback = ""
        self.found_words: Set[str] = set()
        self.last_word_coords: List[Coordinate] = []

        self.scr = scr
        self.subwins: Dict[str, CursesWindow] = {}
        self.allocate_subwins()

        self.draw_all()

    def allocate_subwins(self):
        """Allocate space in the curses screen for subwindows.

        Raises:
            Runtime: The subwindows overlap each other badly enough
                for curses.window.subwin to raise a curses.error
        """

        self.log.info("Allocating subwindows")
        MAX_Y, MAX_X = self.scr.getmaxyx()
        self.log.info(f"screen size (x, y): {MAX_X} x {MAX_Y}")

        try:
            # Since terminal characters typically aren't square, put one space
            # between vertical indices and three spaces between horizontal indices.
            # Curses does not allow you to write to the lower right corner of a window.
            BOARD_ORIGIN_X = 1
            BOARD_ORIGIN_Y = 1
            BOARD_LEN_X = (self.BOARD_SIZE - 1) * self.BOARD_X_SCALE + 1
            BOARD_LEN_Y = self.BOARD_SIZE * self.BOARD_Y_SCALE
            self.subwins["board"] = self.scr.subwin(
                BOARD_LEN_Y,
                BOARD_LEN_X,
                BOARD_ORIGIN_Y,
                BOARD_ORIGIN_X,
            )

            INPUT_LEN_X = MAX_X - 2
            INPUT_LEN_Y = 6
            INPUT_ORIGIN_X = 1
            INPUT_ORIGIN_Y = MAX_Y - INPUT_LEN_Y - 1
            self.subwins["input"] = self.scr.subwin(
                INPUT_LEN_Y, INPUT_LEN_X, INPUT_ORIGIN_Y, INPUT_ORIGIN_X
            )

            INFO_ORIGIN_X = 1
            INFO_ORIGIN_Y = BOARD_ORIGIN_Y + BOARD_LEN_Y
            INFO_LEN_X = BOARD_LEN_X
            INFO_LEN_Y = INPUT_ORIGIN_Y - INFO_ORIGIN_Y
            self.subwins["info"] = self.scr.subwin(
                INFO_LEN_Y, INFO_LEN_X, INFO_ORIGIN_Y, INFO_ORIGIN_X
            )

            FOUND_WORDS_ORIGIN_X = BOARD_ORIGIN_X + BOARD_LEN_X + 1
            FOUND_WORDS_ORIGIN_Y = 1
            FOUND_WORDS_LEN_X = MAX_X - FOUND_WORDS_ORIGIN_X - 1
            FOUND_WORDS_LEN_Y = INPUT_ORIGIN_Y - FOUND_WORDS_ORIGIN_Y
            self.subwins["words"] = self.scr.subwin(
                FOUND_WORDS_LEN_Y,
                FOUND_WORDS_LEN_X,
                FOUND_WORDS_ORIGIN_Y,
                FOUND_WORDS_ORIGIN_X,
            )
        except curses.error:
            errmsg = "The terminal window is too small to allocate subwindows."
            self.log.fatal(errmsg)
            raise RuntimeError(errmsg)

        for (key, val) in self.subwins.items():
            # misusing the Coordinate type
            origin = Coordinate(*val.getbegyx())
            size = Coordinate(*val.getmaxyx())
            bottom_right = origin + size
            self.log.info(
                f"Created subwin {key}:"
                + f"{origin.__tuple__()} -> {bottom_right.__tuple__()}"
            )

            val.border("*", "*", "*", "*", "*", "*", "*", "*")

        self.scr.border()
        self.scr.refresh()

    def check_board_size(self):
        """Check if the board is square.

        Issues a warning in the log if the board is not square.
        """
        board = copy.deepcopy(self.game.get_board())
        size = len(board)
        for row in board:
            if len(row) != size:
                self.log.warning("board is not square; continuing anyway")
                break

    def new_game(self):
        """Initialize a new game.

        Uses the custom board if it's set.
        """
        self.game.new_game(self.BOARD_SIZE, 1, self.cubes, self.dict)
        if self.custom_board:
            self.game.set_game(self.custom_board)
        self.check_board_size()

        self.input_buf.clear()
        self.input_feedback = ""
        self.found_words.clear()
        self.last_word_coords.clear()

        self.draw_all()

    def draw_all(self):
        """A convenience function to draw all subwindows."""
        self.draw_board()
        self.draw_info()
        self.draw_found_words()
        self.draw_input_area()

    def draw_board(self):
        """Draw the Boggle board and the path of the last added word,
        if it exists.
        """
        subwin = self.subwins["board"]
        subwin.clear()
        board = copy.deepcopy(self.game.get_board())
        size = len(board)

        for row in range(size):
            for col in range(size):
                subwin.addch(row * 2, col * 4, board[row][col])

        if self.last_word_coords:
            # delay drawing just in case there's an error
            to_draw: Dict[Coordinate, CoordinateDelta] = {}

            if len(self.last_word_coords) < 2:
                self.log.warning("'last_word_coords' shorter than 2, skipping")
            else:
                for i in range(1, len(self.last_word_coords)):
                    prev = self.last_word_coords[i - 1]
                    cur = self.last_word_coords[i]
                    self.log.debug(f"{prev} -> {cur}")

                    try:
                        prev_bc = prev.to_board_coords()
                        cur_bc = cur.to_board_coords()
                        mid_bc = (cur_bc + prev_bc).div(2)
                        if mid_bc not in to_draw:
                            diff = cur - prev
                            dir = Ordinal(diff)
                            to_draw[mid_bc] = dir
                        else:
                            self.log.info("direction cross")
                            existing_dir = to_draw[mid_bc]
                            self.log.debug(f"existing dir: {existing_dir}")
                            diff = cur - prev
                            self.log.debug(f"diff: {diff}")
                            diff = existing_dir.value + diff
                            dir = Ordinal(diff)
                            self.log.debug(f"new dir: {dir}")
                            to_draw[mid_bc] = dir
                    except ValueError:
                        self.log.warning(
                            f"invalid coordinate delta {cur}-{prev}={diff}"
                        )
                        to_draw = {}
                        break
            if to_draw:
                for board_coord, dir in to_draw.items():
                    subwin.addch(board_coord.row, board_coord.col, arrows[dir])

        subwin.refresh()

    def draw_info(self):
        """Draw the info panel."""
        subwin = self.subwins["info"]
        subwin.clear()
        subwin.move(0, 0)

        scores = copy.deepcopy(self.game.get_scores())
        for (i, score) in enumerate(scores):
            subwin.move(i, 0)
            subwin.addstr(f"Player {i}: {score}")

        subwin.refresh()

    def draw_found_words(self, all_words=False):
        """Draw the found_words panel."""
        subwin = self.subwins["words"]
        subwin.clear()

        if not all_words:
            subwin.addstr(0, 1, "Words found so far:")
            words = ", ".join(self.found_words)
        else:
            words = set(self.game.get_all_words()).difference(self.found_words)
            computer_score = 0
            for word in words:
                computer_score += len(word) - 3

            plural = "s" if computer_score != 1 else ""
            subwin.addstr(
                0, 1, f"The computer scored {computer_score} point{plural} with:"
            )
            words = ", ".join(words)

        lines = textwrap.wrap(words, width=subwin.getmaxyx()[1] - 1)
        for i, line in enumerate(lines):
            try:
                subwin.addstr(i + 1, 1, line)
            except curses.error:
                # writing past the subwindow boundaries
                break

        subwin.refresh()

    def draw_input_area(self):
        """Draws (or redraws) the input area.

        Clears the input subwindow and draws all input elements.
        While this approach is not very efficient when handling
        entry and deletion of individual characters, it greatly
        simplifies the code.
        """
        subwin = self.subwins["input"]
        subwin.clear()
        max_y, max_x = subwin.getmaxyx()

        subwin.addstr(
            max_y - 2,
            0,
            "Press `CTRL + D` to finish this game and `CTRL + C` to exit the program.",
        )

        subwin.move(0, 0)
        if self.input_feedback:
            subwin.addstr(self.input_feedback)
            subwin.move(1, 0)
        bufstr = "".join(self.input_buf)
        subwin.addstr(f">>> {bufstr}")
        subwin.move(*subwin.getyx())
        subwin.refresh()

    def process_word(self, input: str):
        """Process a word from user input.

        This should generally be called only after the enter key is
        pressed.

        Args:
            input: Input string
        """
        self.log.info(f"raw input: '{input}'")
        input = input.strip().lower()
        if not input:
            return

        if len(input) < 4:
            self.input_feedback = f"'{input}' is too short."
        elif not self.dict.contains(input):
            self.input_feedback = f"'{input}' is not a legal word."
        else:
            points = self.game.add_word(input, 0)
            plural = "s" if points != 1 else ""

            if points == 0:
                if input in self.found_words:
                    self.input_feedback = f"'{input}' has already been found."
                else:
                    self.input_feedback = f"'{input}' is not on the board."
            else:
                self.input_feedback = f"'{input}': {points} point{plural}!"
                self.found_words.add(input)
                last_word_points = self.game.get_last_added_word()
                if last_word_points:
                    self.last_word_coords = [Coordinate(*t) for t in last_word_points]
                    self.draw_info()
                    self.draw_board()
                    self.draw_found_words()

        self.log.debug(self.input_feedback)
        self.draw_input_area()

    def wait_for_input(self) -> str:
        """Return an input string from the user.

        Returns:
            When the user presses the enter key, the contents of the
            input buffer are concatenated and returned.

        Raises:
            KeyboardInterrupt: `CTRL + C` is pressed
            EOFError: `CTRL + D` is pressed
        """
        ETX = b"\x03"
        EOT = b"\x04"
        BACKSPACE_KEYS = (
            b"KEY_BACKSPACE",
            b"\x7f",  # ascii `DEL`
            b"\x08",  # ascii `BS`
        )

        while True:
            try:
                s = self.scr.getkey()  # raises KeyboardInterrupt, curses.error
            except curses.error as err:
                # a "no input" error often occurs when the terminal is resized
                self.log.warning(f"[wait_for_input->getkey()] curses.error: {err}")
                continue
            b = bytes(s, encoding="utf-8")

            self.log.debug(f"raw char entry: {b}")  # type: ignore

            if b == ETX:
                # CTRL + C if not caught automatically
                raise KeyboardInterrupt
            elif b == EOT:
                # CTRL + D
                raise EOFError
            elif b in BACKSPACE_KEYS:
                if self.input_buf:
                    self.input_buf.pop()
            elif b == b"KEY_RESIZE":
                self.allocate_subwins()
                self.draw_all()
            elif s == "\n":
                retval = "".join(self.input_buf)
                self.input_buf.clear()
                return retval
            elif len(s) == 1:
                self.input_buf.append(s)
            else:
                self.log.warning(f"Unrecognized input: {b}")  # type: ignore

            # Update the addition and deletion of keys.
            # It is the caller's responsibility to update the screen
            # if an error was raised or the enter key was pressed.
            self.draw_input_area()

    def input_loop(self):
        """Continuously process user input."""
        run = True
        reprompt = False

        while run:
            try:
                user_input = self.wait_for_input()

                if not reprompt:
                    self.process_word(user_input)
                else:
                    if user_input.lower().startswith("y"):
                        self.new_game()
                        reprompt = False
                    else:
                        run = False
            except EOFError:
                reprompt = True
                self.draw_found_words(True)
                self.input_feedback = "new game? [yes/no]"
                self.draw_input_area()
            except KeyboardInterrupt:
                run = False


def entry(screen: CursesWindow, cfg: argparse.Namespace, **kwargs):
    """Entry function to the TUI.

    This function should not be called directly. It should be passed
    as a parameter to `curses.wrapper`.

    Args:
        screen: curses.window object passed by curses.wrapper
        cfg: command line options

    Keyword Args:
        custom_board: List[List[str]]: custom board to use
    """
    screen.clear()
    tui = TUI(screen, cfg.words, cfg.cubes, kwargs.get("custom_board"))

    tui.input_loop()
