# Minesweeper Solver

> A Minesweeper solver using Xlib. This solver is designed to solve the "Mines" Minesweeper game on Ubuntu. It currently supports a game grid size of 30x16. The solver automates the gameplay by analyzing the screen using Xlib and making strategic moves to uncover safe tiles.

> New Version using Xlib ( 3 seconds )

> Old Version using only PyAutoGui ( 47 seconds )
> [example.webm](https://github.com/mateogon/minesweeper_solver/assets/21253519/1c4628ae-80f5-410b-9a10-e3f0a6547a40)

## Key Features

- Automatically solves the "Mines" Minesweeper game on Ubuntu.
- Supports a game grid size of 30x16.
- Utilizes Xlib to analyze the screen and make strategic moves.
- Press "{" to start the solver and "}" to stop it.

## Requirements

- Python 3.x
- Xlib
- PyAutoGUI
- playsound
- keyboard
- matplotlib
- opencv-python
- numpy

## Installation

1. Clone the repository:

git clone https://github.com/mateogon/minesweeper_solver.git

2. Navigate to the project directory:

cd minesweeper_solver

3. Install the dependencies:

pip install -r requirements.txt

## Usage

1. Make sure you have the Minesweeper game window open on your Ubuntu system.
2. Run the `minesweeper.py` script using Python:

python minesweeper.py

3. Press "{" to start the solver and let it solve the Minesweeper game.
4. Press "}" to stop the solver.

## Disclaimer

This project was created in a couple of hours and may have limitations or bugs. It currently supports a specific game grid size and is designed for Ubuntu. Use it at your own risk and feel free to modify or enhance it to suit your needs.
