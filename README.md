# PyQt Maze Editor

A simple maze editor for micromouse mazes.

__Note that this is a work in progress and some functions may not yet be implemented__

### Requirements

As a Python application, this should run on any platform so long as the requirements are met.

To run this application you will need Python >= 3.8 and the PyQt5 and numpy modules.

To install Python, visit python.org. On Windows, unless you have a particular reason not to, look for the option to 
add Python to your path and make sure it is selected. 

With Python 3 installed on your computer, add the dependencies with:

```pip install PyQt5 numpy``` or ```pip3 install PyQt5 numpy```

Then run with ``` python main.py``` or ```python3 ./main.py```

depending on how your python is installed

### Operation

Maze files are listed to the right of the window. Simply select one to see it and make changes. Alternatively, the 
usual file open/save options are available to edit a maze anywhere in your filesystem.

To toggle walls, click with the left mouse button near any wall. the outer walls are protected.

Goal cells are highlighted in green. To toggle a goal cell shift-click anywhere in the cell. note that goal cells 
normally form a rectangular block of cells. This program does not enforce that.

Zoom in and out with the mouse wheel.

Pan a zoomed maze by moving the mouse while pressing the middle mouse button or both buttons simultaneously

Show or hide costs for the currently selected flooding method with the checkbox in the options section.

_Not Yet Implemented_
 - change flooding method and options
 - select size when creating new maze
 - enable multiple, simultaneous flood/path options
 - file history

### Maze Files

A comprehensive set of maze files is included, all in text format. These are taken from two github repositories:

- [Micromouseonline](https://github.com/micromouseonline/mazefiles)

- [Kerikun11](https://github.com/kerikun11/micromouse-maze-data)

These text files are easy to view in any editor, even without this application. 

### Acknowledgements

Some of the code relating to the maze and the flooder is modified from original work by Ryotaro Onuki in his 
micromouse maze library

https://github.com/kerikun11/micromouse-maze-library


