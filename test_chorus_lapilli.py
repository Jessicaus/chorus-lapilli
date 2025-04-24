#!/usr/bin/env python3
'''Simple test harness for Chorus Lapilli.

Extend the TestChorusLapilli class to add your own tests.
'''
import os
import sys
import argparse
import subprocess
import unittest
import urllib.request


class TestChorusLapilli(unittest.TestCase):
    '''Integration testing for Chorus Lapilli

    This class handles the entire react start up, testing, and take down
    process. Feel free to modify it to suit your needs.
    '''

    # ========================== [USEFUL CONSTANTS] ===========================

    # React default startup address
    REACT_HOST_ADDR = 'http://localhost:3000'

    # XPATH query used to find Chorus Lapilli board tiles
    BOARD_TILE_XPATH = '//button[contains(@class, \'square\')]'

    # Sets of symbol classes - each string contains all valid characters
    # for that particular symbol
    SYMBOL_BLANK = ''
    SYMBOL_X = 'Xx'
    SYMBOL_O = '0Oo'

    # ======================== [SETUP/TEARDOWN HOOKS] =========================

    @classmethod
    def setUpClass(cls):
        '''This function runs before testing occurs.

        Bring up the web app and configure Selenium
        '''

        env = dict(os.environ)
        env.update({
            # Prevent React from starting its own browser window
            'BROWSER': 'none',
            # Disable SSL warnings for Legacy NodeJS
            'NODE_OPTIONS': '--openssl-legacy-provider'
        })

        # if npm install has never been run, install dependencies
        if not os.path.isfile('package-lock.json'):
            subprocess.run(['npm', 'install'],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL,
                           env=env,
                           check=True)

        # Await Webserver Start
        cls.react = subprocess.Popen(['node',
                                      'node_modules/react-scripts/scripts/'
                                      'start.js'],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.DEVNULL,
                                     env=env)
        for _ in cls.react.stdout:
            try:
                with urllib.request.urlopen(cls.REACT_HOST_ADDR):
                    break

            except IOError:
                pass

            # Ensure React does not terminate early
            if cls.react.poll() is not None:
                raise OSError('React terminated before test')

        # Configure the Selenium webdriver
        cls.driver = Browser()
        cls.driver.get(cls.REACT_HOST_ADDR)
        cls.driver.implicitly_wait(0.5)

    @classmethod
    def tearDownClass(cls):
        '''This function runs after all testing have run.

        Terminate React and take down the Selenium webdriver.
        '''
        cls.react.terminate()
        cls.react.wait()
        cls.driver.quit()

    def setUp(self):
        '''This function runs before every test.

        Refresh the browser so we get a new board.
        '''
        self.driver.refresh()

    def tearDown(self):
        '''This function runs after every test.

        Not needed, but feel free to add stuff here.
        '''

    # ========================== [HELPER FUNCTIONS] ===========================

    def assertBoardEmpty(self, tiles):
        '''Checks if all board tiles are empty.

        Arguments:
          tiles: List[WebElement] - a board consisting of 9 buttons elements
        Raises:
          AssertionError - if board is not empty
        '''
        if len(tiles) != 9:
            raise AssertionError('tiles is not a 3x3 grid')
        for i, tile in enumerate(tiles):
            if tile.text.strip():
                raise AssertionError(f'tile {i} is not empty: '
                                     f'\'{tile.text}\'')

    def assertTileIs(self, tile, symbol_set):
        '''Checks if all board tiles are empty.

        Arguments:
          tile: WebElement - the button element to check
          symbol_set: str - a string containing all the valid symbols
        Raises:
          AssertionError - if tile is not in the symbol set
        '''
        if symbol_set is None:
            return
        if symbol_set == self.SYMBOL_BLANK:
            name = 'BLANK'
        elif symbol_set == self.SYMBOL_X:
            name = 'X'
        elif symbol_set == self.SYMBOL_O:
            name = 'O'
        else:
            name = 'in symbol_set'
        text = tile.text.strip()
        if ((symbol_set == self.SYMBOL_BLANK and text)
                or (symbol_set != self.SYMBOL_BLANK and not text)
                or text not in symbol_set):
            raise AssertionError(f'tile is not {name}: \'{tile.text}\'')
    
    def assertBoardState(self, tiles, expected_symbols):
        '''Asserts that all tiles match the expected 3x3 board layout.

        Arguments:
        tiles: List[WebElement] - the 9 tile elements
        expected_symbols: List[str] - list of 9 strings: 'X', 'O', or '' (empty)
    
        Raises:
        AssertionError - if any tile's text does not match the expected symbol
        '''
        if len(expected_symbols) != 9:
            raise ValueError("Expected exactly 9 symbols for a 3x3 board.")

        for i in range(9):
            actual = tiles[i].text.strip()
            expected = expected_symbols[i]
            if actual != expected:
                raise AssertionError(
                    f"Mismatch at tile {i}: expected '{expected}', found '{actual}'"
                )

# =========================== [ADD YOUR TESTS HERE] ===========================

    def test_new_board_empty(self):
        '''Check if a new game always starts with an empty board.'''
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)
        self.assertBoardEmpty(tiles)

    def test_button_click(self):
        '''Check if clicking the top-left button adds an X.'''
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)
        self.assertTileIs(tiles[0], self.SYMBOL_BLANK)
        tiles[0].click()
        self.assertTileIs(tiles[0], self.SYMBOL_X)
    
    def test_alternate_button_click(self):
        '''Check if clicking the top-left button adds an X.'''
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)
        self.assertTileIs(tiles[0], self.SYMBOL_BLANK)
        tiles[0].click()
        self.assertTileIs(tiles[0], self.SYMBOL_X)
        tiles[1].click()
        self.assertTileIs(tiles[1], self.SYMBOL_O)
    
    def test_player_win(self):
        '''Check if player can still move after one Player has won the game.'''
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)
        tiles[0].click() # X
        tiles[1].click() # O
        tiles[4].click() # X
        tiles[3].click() # O
        tiles[8].click() # X won
        tiles[2].click()
        expected = [
            'X', 'O', '',
            'O', 'X', '',
            '', '', 'X'
        ]
        self.assertBoardState(tiles, expected)
    
    def test_valid_adjacent_move(self):
        '''After 3 pieces placed, player can move one piece to an adjacent empty tile.'''
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)

        # X and O take turns placing 3 each
        tiles[0].click()  # X
        tiles[1].click()  # O
        tiles[3].click()  # X
        tiles[2].click()  # O
        tiles[8].click()  # X (X now has 3)
        tiles[5].click()  # O (O now has 3)

        # X moves piece from 8 → 7
        tiles[8].click()  # select piece
        tiles[7].click()  # move to adjacent empty square

        expected = [
            'X', 'O', 'O',
            'X', '', 'O',
            '', 'X', ''
        ]
        self.assertBoardState(tiles, expected)
    
    def test_center_cannot_move(self):
        '''Player cannot move any other tile because their center tile is still occupied and next move is not a winning move.'''
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)
        tiles[3].click()  # X
        tiles[1].click() # O
        tiles[4].click() # x
        tiles[5].click() # O
        tiles[8].click() # x
        tiles[0].click() # O

        tiles[8].click()  # select piece
        tiles[7].click()  # failed to move to adjacent empty square

        expected = [
            'O', 'O', '',
            'X', 'X', 'O',
            '', '', 'X'
        ]
        self.assertBoardState(tiles, expected)

        tiles[4].click()  # select center piece
        tiles[3].click() # select another piece
        tiles[6].click() # failed to move to adjacent empty square
        expected = [
            'O', 'O', '',
            'X', 'X', 'O',
            '', '', 'X'
        ]
        self.assertBoardState(tiles, expected)

        tiles[4].click()
        tiles[2].click() # moved successfully
        expected = [
            'O', 'O', 'X',
            'X', '', 'O',
            '', '', 'X'
        ]
        self.assertBoardState(tiles, expected)

        tiles[4].click() # nothing happens
        tiles[0].click()
        tiles[4].click() # move to center
        expected = [
            '', 'O', 'X',
            'X', 'O', 'O',
            '', '', 'X'
        ]
        self.assertBoardState(tiles, expected)

        tiles[8].click()
        tiles[7].click()
        expected = [
            '', 'O', 'X',
            'X', 'O', 'O',
            '', 'X', ''
        ]
        self.assertBoardState(tiles, expected)

        tiles[5].click()
        tiles[6].click() #nothing happens
        tiles[5].click()
        tiles[8].click() #nothing happens
        expected = [
            '', 'O', 'X',
            'X', 'O', 'O',
            '', 'X', ''
        ]
        self.assertBoardState(tiles, expected)
        
        tiles[4].click()
        tiles[0].click()
        expected = [
            'O', 'O', 'X',
            'X', '', 'O',
            '', 'X', ''
        ]
        self.assertBoardState(tiles, expected)

    def test_can_win_from_center(self):
        '''Player may keep center if their move completes a win.'''
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)

        # X at 0, 4 (center), and moves 8 → 7 to win via 0-4-7 (diagonal down-left)
        tiles[1].click()  # X
        tiles[3].click()  # O
        tiles[5].click()  # X (center)
        tiles[4].click()  # O
        tiles[2].click()  # X
        tiles[7].click()  # O

        # X moves 1 → 0 and wins
        tiles[1].click()
        tiles[0].click()

        expected = [
            'X', '', 'X',
            'O', 'O', 'X',
            '', 'O', ''
        ]
        self.assertBoardState(tiles, expected)

        tiles[3].click() # not selecting center
        tiles[1].click() # completes win
        expected = [
            'X', 'O', 'X',
            '', 'O', 'X',
            '', 'O', ''
        ]
        self.assertBoardState(tiles, expected)

# ================= [DO NOT MAKE ANY CHANGES BELOW THIS LINE] =================

if __name__ != '__main__':
    from selenium.webdriver import Firefox as Browser
    from selenium.webdriver.common.by import By
else:
    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='Chorus Lapilli Tester')
    parser.add_argument('-b',
                        '--browser',
                        action='store',
                        metavar='name',
                        choices=['firefox', 'chrome', 'safari'],
                        default='firefox',
                        help='the browser to run tests with')
    parser.add_argument('-c',
                        '--change-dir',
                        action='store',
                        metavar='dir',
                        default=None,
                        help=('change the working directory before running '
                              'tests'))

    # Change the working directory
    options = parser.parse_args(sys.argv[1:])
    # Import different browser drivers based on user selection
    try:
        if options.browser == 'firefox':
            from selenium.webdriver import Firefox as Browser
        elif options.browser == 'chrome':
            from selenium.webdriver import Chrome as Browser
        else:
            from selenium.webdriver import Safari as Browser
        from selenium.webdriver.common.by import By
    except ImportError as err:
        print('[Error]',
              err, '\n\n'
              'Please refer to the Selenium documentation on installing the '
              'webdriver:\n'
              'https://www.selenium.dev/documentation/webdriver/'
              'getting_started/',
              file=sys.stderr)
        sys.exit(1)

    if options.change_dir:
        try:
            os.chdir(options.change_dir)
        except OSError as err:
            print(err, file=sys.stderr)
            sys.exit(1)

    if not os.path.isfile('package.json'):
        print('Invalid directory: cannot find \'package.json\'',
              file=sys.stderr)
        sys.exit(1)

    tests = unittest.defaultTestLoader.loadTestsFromTestCase(TestChorusLapilli)
    unittest.TextTestRunner().run(tests)
