import requests
import json
import copy

def get_rover_commands(rover_count):
    '''
    Gets the rover commands from the provided api

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
            #print(rover_row_pos, rover_col_pos)
            map[rover_row_pos][rover_col_pos] = "*"

    return map

# def generate_rover_path(rover_id, commands, map_info):
    
#     dig = False
#     current_row = 1
#     current_col = 0
#     current_direction = "SOUTH"
#     max_rows = map_info[0]
#     max_cols = map_info[1]

#     # Need an Update Rover Path Function 
#     total_time = 0
#     for move in commands[rover_id]:
#         if move == 'L' or move == 'R':
#             current_direction = rotate_rover(current_direction, move)
            

#         elif move == 'M':
            
#             if current_direction == "SOUTH":
#                 if current_row < max_rows:
#                     current_row += 1
#             elif current_direction == "WEST":
#                 if current_col >= 2:
#                     current_col -= 2
#             elif current_direction == "NORTH":
#                 if current_row > 1:
#                     current_row -= 1
#             elif current_direction == "EAST":
#                 if current_col < ((3 - 1) * 2):
#                     current_col += 2

#         elif move == 'D':
#             dig = True
#             # Need a Check for Mine 
    
#     print(f'Total time took: {total_time} seconds.')

def rotate_rover(current_direction, move) -> str:
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
            - map_info (list): A list of two integers, first one being the number of rows and second one is the number of columns.
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
    file_name = f'path_{rover_id + 1}.txt'
    print(f"Writing to {file_name}")
    with open(file_name, 'w') as f:
        for row in rover_map:
            f.write(" ".join([str(cell) for cell in row]) + "\n")


def main():
    map_info, map = build_map("map1.txt")
    commands = get_rover_commands(10)
    for rover_id in range(10):
        map_copy = copy.deepcopy(map)
        updated_map = rover_movement(rover_id, commands, map_info, map_copy)
        write_rover_path_to_file(rover_id, updated_map)
    # TODO ---------
    # add mine handling

   

if __name__ == "__main__":
    main()