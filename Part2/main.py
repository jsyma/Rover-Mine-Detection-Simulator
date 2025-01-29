import requests
import json
import copy
import os 
from time import perf_counter 
from hashlib import sha256
from threading import Thread, Lock
from multiprocessing import Process

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
    with open(map_file_name, 'r') as fmap:
        map_info = fmap.readline().split()
        rows = int(map_info[0])
        cols = int(map_info[1])
        map = [[0] * cols for _ in range(rows)]
        for row, line in enumerate(fmap.readlines()):
            cells = line.split()
            for col, value in enumerate(cells):
                map[row][col] = 1 if value == "1" else 0

    return map_info, map

def write_rover_path_to_file(rover_id, rover_map, output_folder):
    '''
    Writes the rover's path/updated map to a .txt file.

    Args: 
        rover_id (int): The unique ID of the rover (0-indexed).
        rover_map (list): A 2D list representing the rover's path/map, with each cell being '0', '1' or '*'. 
    '''
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    file_name = os.path.join(output_folder, f'path_{rover_id + 1}.txt')
    with open(file_name, 'w') as f:
        for row in rover_map:
            f.write(" ".join([str(cell) for cell in row]) + "\n")

def rover_movement(rover_id, commands, info, starter_map, mine_serial_mapping):
    '''
    Simulates a rover's movement on the map based on a sequence of commands, 
    updating the map as the rover moves and handles interaction with mines. 

    Args:
        rover_id (int): The unique ID of the rover (0-indexed).
        commands (list): A list of command sequences for all rovers.
        map_info (list): A list containing the dimensions of the map [rows, columns].
        map (list): A 2D list of the map, with each cell being either '0' or '1'.
        mine_serial_mapping (dict): A mapping of mine locations to serial numbers.
    
    Returns:
        list: The updated map after processing the rover's movement and interactions.
    '''
    map = starter_map
    number_of_rows = int(info[0])
    number_of_cols = int(info[1]) - 1
    rover_row_pos = 0
    rover_col_pos = 0
    current_direction = "SOUTH"
    disarm = False
    mine_locations = get_location_of_mines(map, info)

    for move in commands[rover_id]:
        if move == 'L' or move == 'R':
            current_direction = rotate_rover(current_direction, move)
        elif move == 'M':
            update = False
            prev_row = rover_row_pos
            prev_col = rover_col_pos
            if current_direction == "SOUTH" and rover_row_pos + 1 < number_of_rows:
                rover_row_pos += 1
                update = True
            elif current_direction == "NORTH" and rover_row_pos - 1 >= 0:
                rover_row_pos -= 1
                update = True
            elif current_direction == "WEST" and rover_col_pos - 1 >= 0:
                rover_col_pos -= 1
                update = True
            elif current_direction == "EAST" and rover_col_pos + 1 <= number_of_cols:
                rover_col_pos += 1
                update = True
            if update: 
                # Used in threading
                with lock:   
                    if not disarm and ((prev_row, prev_col) in mine_locations):
                        print(f"Rover {rover_id + 1} hit a mine at ({prev_row}, {prev_col})!")
                        # Stop processing the rest of the commands and Mark as Exploded
                        map[prev_row][prev_col] = "X"
                        break
                disarm = False
                map[rover_row_pos][rover_col_pos] = "*"
        elif move == 'D':
            disarm = True
            if (rover_row_pos, rover_col_pos) in mine_locations:
                serial_number = mine_serial_mapping[(rover_id + 1)]
                print(f"Rover {rover_id + 1} is disarming mine at ({rover_row_pos}, {rover_col_pos}) with serial number: {serial_number}")
                # Used in threading
                with lock:
                    pin, hash_value = disarm_mine(serial_number)
                    print(f"Mine {serial_number} disarmed. PIN: {pin}, Hash: {hash_value}")
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

def generate_rover_path(rover_id, commands, map_info, map, mine_serial_mapping, output_folder):
    '''
    Processes a rover's command sequence, updates the map with its traversed path and generates the updated map to a .txt file.

    Args: 
        rover_id (int): The unique ID of the rover (0-indexed).
        commands (list): A list of command sequences for all rovers.
        map_info (list): A list containing the dimensions of the map [rows, columns].
        map (list): A 2D list of the map, with each cell being either '0' or '1'.
        mine_serial_mapping (dict): A mapping of mine locations to serial numbers.
    '''
    map_copy = copy.deepcopy(map)
    updated_map = rover_movement(rover_id, commands, map_info, map_copy, mine_serial_mapping)
    with lock:
        write_rover_path_to_file(rover_id, updated_map, output_folder)

def get_location_of_mines(map,map_info):
    '''
    Extracts the locations of mines from the map.

    Args:
        map (list): A 2D list of the map, with each cell being either '0' or '1'.    
        map_info (list): A list containing the dimensions of the map [rows, columns].

    Returns:
        list: A list of tuples representing (row, col) position of a mine. 
    '''
    mine_location_list = []
    rows = (int)(map_info[0])
    cols = (int)(map_info[1])
    for row in range(rows):
        for col in range(cols):
            if map[row][col] == 1:
                mine_location_list.append((row, col))
    return mine_location_list

def create_mine_serial_mapping(mine_file_name, rover_id):
    '''
    Creates a dictionary mapping rover_id and their corresponding mine serial numbers. 

    Args:
        map (list): A 2D list of the map, with each cell being either '0' or '1'.
        map_info (list): A list containing the dimensions of the map [rows, columns].
        mine_file_name (str): The name of the file containing the list of mine serial numbers.
        rover_id (int): The unique ID of the rover (1-indexed).
    Returns:
        dict: A dictionary where the keys are tuples representing mine coordinates (row, col),
              and the values are the corresponding serial numbers for those mines.
    '''
    with open(mine_file_name, "r") as f:
        serial_numbers = f.read().splitlines()
    selected_serial_number = serial_numbers[rover_id - 1]
    print(f"Mapping Rover {rover_id} to Mine Serial Numbers: {selected_serial_number}")

    mine_serial_mapping = {rover_id: selected_serial_number}
    return mine_serial_mapping

def disarm_mine(serial_number):
    '''
    Disarms a mine based on its serial number by iterating through potential PIN values and hashing the combination of serial 
    number and PIN until a hash is found that starts with '000000'. Simulates finding a correct PIN to disarm the mine. 

    Args: 
        serial_number (str): The serial number of the mine to be disarmed.
    
    Returns: 
        tuple: A tuple containing:
            - pin (int): The correct PIN to disarm the mine.
            - hash_value (str): The SHA-256 hash value of the serial number and PIN, starts with '00000'. 
    '''
    pin = 0 
    while True:
        temporary_mine_key = f"{serial_number}{pin}".encode()
        hash_value = sha256(temporary_mine_key).hexdigest()
        if hash_value.startswith("00000"):
            return pin, hash_value
        pin += 1

def run_rovers_sequentially(commands, map_info, map, mine_serial_mapping, output_folder):
    '''
    Runs the rover commands sequentially, processing one rover's path at a time. 

    Args:
        commands (list): A list of command sequences for all rovers.
        map_info (list): A list containing the dimensions of the map [rows, columns].
        map (list): A 2D list of the map, with each cell being either '0' or '1'.
        mine_serial_mapping (dict): A mapping of mine locations to serial numbers.

    Returns:
        float: The time taken to process all rovers sequentially, in seconds.
    '''
    start_time = perf_counter()

    for rover_id in range(10):
        generate_rover_path(rover_id, commands, map_info, map, mine_serial_mapping, output_folder)

    end_time = perf_counter()
    return end_time - start_time

def run_rovers_in_threads(commands, map_info, map, mine_serial_mapping, output_folder): 
    '''
    Runs the rover commands concurrently using multiple threads. 

    Args:
        commands (list): A list of command sequences for all rovers.
        map_info (list): A list containing the dimensions of the map [rows, columns].
        map (list): A 2D list of the map, with each cell being either '0' or '1'.
        mine_serial_mapping (dict): A mapping of mine locations to serial numbers.

    Returns:
        float: The time taken to process all rovers using threading, in seconds.
    '''
    threads = []
    start_time = perf_counter()
    for rover_id in range(0, 10):
        thread = Thread(target=generate_rover_path, args=(rover_id, commands, map_info, map, mine_serial_mapping, output_folder))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    end_time = perf_counter()
    return end_time - start_time

def run_rovers_in_processes(commands, map_info, map, mine_serial_mapping, output_folder): 
    '''
    Runs the rover commands concurrently using multiple processes.

    Args:
        commands (list): A list of command sequences for all rovers.
        map_info (list): A list containing the dimensions of the map [rows, columns].
        map (list): A 2D list of the map, with each cell being either '0' or '1'.
        mine_serial_mapping (dict): A mapping of mine locations to serial numbers.

    Returns:
        float: The time taken to process all rovers using multiprocessing, in seconds.
    '''
    processes = []
    start_time = perf_counter()
    for rover_id in range(0, 10):
        process = Process(target=generate_rover_path, args=(rover_id, commands, map_info, map, mine_serial_mapping, output_folder))
        processes.append(process)

    for process in processes:
        process.start()

    for process in processes: 
        process.join()

    end_time = perf_counter()
    return end_time - start_time

def main():
    '''
    The main entry point of the program. 
    - Loads the map and rover commands.
    - Creates a mapping of rover_id to mine serial numbers.
    - Runs the rovers sequentially and in parallel (using threading or multiprocessing).
    - Compares the performance times of sequential vs. parallel processing. 
    - Prints out the execution time for each approach and the difference in time. 
    '''
    map_info, map = build_map("../map1.txt")
    commands = get_rover_commands(10)
    mine_serial_mapping = {}
    for i in range(10):
        mine_serial_mapping.update(create_mine_serial_mapping("../mines.txt", rover_id = i + 1))

    # Sequential Execution
    sequential_output_folder = 'output_sequential_paths'
    sequential_time = run_rovers_sequentially(commands, map_info, map, mine_serial_mapping, sequential_output_folder)
    
    # Parallel Execution Using Threading
    threading_output_folder = 'output_threading_paths'
    threading_time = run_rovers_in_threads(commands, map_info, map, mine_serial_mapping, threading_output_folder)
    
    # Parallel Execution Using Multiple Processes
    multiprocessing_output_folder = 'output_multiprocessing_paths'
    multiprocessing_time = run_rovers_in_processes(commands, map_info, map, mine_serial_mapping, multiprocessing_output_folder)

    print(f"Sequential processing time: {sequential_time:.2f} seconds.")
    print(f"Parallel processing time (Threading): {threading_time:.2f} seconds.")
    print(f"Parallel processing time (Multiprocessing): {multiprocessing_time:.2f} seconds.")

    # Difference between sequential vs parallel
    print(f"Time difference (Sequential - Threading): {sequential_time - threading_time:.2f} seconds.")
    print(f"Time difference (Sequential - Multiprocessing): {sequential_time - multiprocessing_time:.2f} seconds.")

if __name__ == "__main__":
    main()