import requests
import json
import copy
import os 
import time 
from threading import Thread, Lock

lock = Lock()

def get_rover_commands(rover_count):
    '''
    Gets the rover commands from the provided api.

    Args: 
        rover_count (int): The number of rovers to get commands from.
    
    Returns: 
        list: A list of Rover commands, each element in the list is a list of commands
              for a specific rover.
    '''
    commands = []
    api = 'https://coe892.reev.dev/lab1/rover'
    for rover_id in range(1, rover_count + 1):
        r = requests.get(f'{api}/{rover_id}')
        if r.ok:
            content = json.loads(r.content)
            commands.append(content['data']['moves'])
        else:
            raise Exception(f"Failed to fetch API for rover {rover_id}")
    return commands

def rover_movement(rover_id, commands, info, starter_map):
    map = starter_map
    number_of_rows = int(info[0])
    number_of_cols = int(info[1]) - 1
    rover_row_pos = 0
    rover_col_pos = 0
    current_direction = "SOUTH"

    for move in commands[rover_id]:
        if move == 'L' or move == 'R':
            current_direction = rotate_rover(current_direction, move)
        elif move == 'M':
            if current_direction == "SOUTH" and rover_row_pos + 1 < number_of_rows:
                rover_row_pos += 1
            elif current_direction == "NORTH" and rover_row_pos - 1 >= 0:
                rover_row_pos -= 1
            elif current_direction == "WEST" and rover_col_pos - 1 >= 0:
                rover_col_pos -= 1
            elif current_direction == "EAST" and rover_col_pos + 1 <= number_of_cols:
                rover_col_pos += 1
            if map[rover_row_pos][rover_col_pos] == 1:
                print(f"Rover {rover_id + 1} hit a mine at ({rover_row_pos}, {rover_col_pos})!")
                # Stop processing the rest of the commands
                return map
            map[rover_row_pos][rover_col_pos] = "*"
        elif move == 'D':
            # Need a mine_check function to see if can disarm and continue with the commands
            continue
    return map

def rotate_rover(current_direction, move) -> str:
    '''
    Rotate the rover's direction based on the given movement command using a predefined sequence of directions.

    Args:
        current_direction (str): The current direction of the rover. Valid options: "NORTH", "EAST", "SOUTH", "WEST".
        move (str): The rotation command. Valid options: "L", "R".

    Returns:
        str: The new direction of the rover after the rotation. 
    '''
    directions = ["NORTH", "EAST", "SOUTH", "WEST"]
    idx = directions.index(current_direction)
    
    if move == "L":
        return directions[(idx - 1) % 4]
    elif move == "R":
        return directions[(idx + 1) % 4]
    else:
        raise ValueError("Invalid move. Use 'L' for left or 'R' for right.")


def build_map(map_file_name):
    '''
    Reads a map file and builds a grid representation of the map. 

    Args: 
        map_file_name (str): The name of the file containing the map data.
    
    Returns:
        tuple: A tuple containing:
            - map_info (list): A list containing the dimensions of the map [rows, columns].
            - map (list): A 2D list of the map, with each cell being either '0' or '1'.
    '''
    fmap = open(map_file_name, 'r')
    map_info = fmap.readline().split()
    rows = (int)(map_info[0])
    cols = (int)(map_info[1])

    map = [[0 for i in range(cols)] for j in range(rows)]

    for row, line in enumerate(fmap.readlines()):
        cells = line.split()
        for col, value in enumerate(cells):
            if value == "1":
                map[row][col] = 1
    fmap.close()    

    return map_info, map

def write_rover_path_to_file(rover_id, rover_map):
    '''
    Writes the rover's path/updated map to a .txt file.

    Args: 
        rover_id (int): The rover ID.
        rover_map (list): A 2D list representing the rover's path/map, with each cell being '0', '1' or '*'. 
    '''
    directory = 'output_rover_paths'
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_name = os.path.join(directory, f'path_{rover_id + 1}.txt')
    with open(file_name, 'w') as f:
        for row in rover_map:
            f.write(" ".join([str(cell) for cell in row]) + "\n")

def generate_rover_path(rover_id, commands, map_info, map):
    '''
    Processes a rover's command sequence, updates the map with its traversed path and generates the updated map to a .txt file.

    Args: 
        rover_id (int): The unique ID of the rover (0-indexed).
        commands (list): A list of command sequences for all rovers.
        map_info (list): A list containing the dimensions of the map [rows, columns].
        map (list): A 2D list of the map, with each cell being either '0' or '1'.
    '''
    map_copy = copy.deepcopy(map)
    updated_map = rover_movement(rover_id, commands, map_info, map_copy)
    write_rover_path_to_file(rover_id, updated_map)

def main():
    # Sequential Execution  
    start_time = time.time()
    map_info, map = build_map("map1.txt")
    commands = get_rover_commands(10)
    for rover_id in range(10):
        generate_rover_path(rover_id, commands, map_info, map)
    sequential_time = time.time() - start_time
    print(f"Sequential processing time: {sequential_time:.2f} seconds.")
   
   # Parallel execution using threading
    start_time = time.time()
    threads = []
    for rover_id in range(10):
        thread = Thread(target=generate_rover_path, args=(rover_id, commands, map_info, map))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    parallel_time = time.time() - start_time
    print(f"Parallel processing time: {parallel_time:.2f} seconds.")

    # Difference between sequential vs parallel
    print(f"Time difference: {sequential_time -  parallel_time:.2f} seconds.")
   
    # TODO ---------
    # add mine handling

if __name__ == "__main__":
    main()