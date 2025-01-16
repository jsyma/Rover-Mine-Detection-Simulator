import requests
import json


def get_rover_commands(rover_count):
    """
    Gets the rover commands from the provided api
    @param rover_count  The number of Rovers to get commands from
    @return The Rover commands in JSON format
    """
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
    maxR = (int)(info[0])
    maxC = (int)(info[1])-1
    r = 0
    c = 0
    current_direction = "SOUTH"
    for move in commands[rover_id]:
        if move == 'L' or move == 'R':
            current_direction = rotate_rover(current_direction, move)
        elif move == 'M':
            if current_direction == "SOUTH":
                if r+1 < maxR :
                    r+=1
            if current_direction == "NORTH":
                if  r - 1 >= 0:
                    r -=1
            if current_direction == "WEST":
                if  c-1 >= 0:
                    c-=1
            if current_direction == "EAST":
                if c+1 <= maxC:
                    c +=1
            #print(r,c)
            map[r][c] = "*"
    return map 

def generate_rover_path(rover_id, commands, map_info):
    
    dig = False
    current_row = 1
    current_col = 0
    current_direction = "SOUTH"
    max_rows = map_info[0]
    max_cols = map_info[1]

    # Need an Update Rover Path Function 
    total_time = 0
    for move in commands[rover_id]:
        if move == 'L' or move == 'R':
            current_direction = rotate_rover(current_direction, move)
            

        elif move == 'M':
            
            if current_direction == "SOUTH":
                if current_row < max_rows:
                    current_row += 1
            elif current_direction == "WEST":
                if current_col >= 2:
                    current_col -= 2
            elif current_direction == "NORTH":
                if current_row > 1:
                    current_row -= 1
            elif current_direction == "EAST":
                if current_col < ((3 - 1) * 2):
                    current_col += 2

        elif move == 'D':
            dig = True
            # Need a Check for Mine 
    
    print(f'Total time took: {total_time} seconds.')

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
    fmap = open(map_file_name, 'r')
    info = fmap.readline().split()
    rows = (int)(info[0])
    cols = (int)(info[1])

    map = [[0 for i in range(cols)] for j in range(rows)]

    r = 0
    c = 0

    for line in fmap.readlines():
       c = 0
       for x in line.split():
           if x == "1":
               map[r][c] = 1
           c+=1
       r+=1 

    fmap.close()    
    return info, map


def main():
    info,map = build_map("map1.txt")

    commands = get_rover_commands(10)
    print(info)
    for x in map:
        print(x)

    print("...")

#def rover_movement(rover_id, commands, info, starter_map):
    new_map = rover_movement(0, commands, info, map)
    for x in new_map:
        print(x)
    #generate_rover_path(1, commands, map)
    #print(commands)
    # TODO ---------
    # print path.txt
    # add mine handling

if __name__ == "__main__":
    main()