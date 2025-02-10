To Run Part 1 - Drawing the path of the Rovers:
- cd Part1 
- python main.py

In this part, a program gets the commands of each rover and draws the path of the map, and if it hits a mine, 
without a 'D' command, the rest of the commands are ignored. Both the sequential and threading approaches will 
draw the new map based on the rover commands and the final computation times are printed and compared. 

To Run Part 2 - Digging Mines:
- cd Part2
- python main.py

In this part, the rover disarms any mine it comes across upon receiving the 'D' command. If it successfully 
disarms a mine, it continues with its commands. Both the sequential and threading approaches will disarm mines
and draw the new map based on the rover commands. The final computation times are printed and compared. 
