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


def generate_rover_path(rover_id, commands):
    
    dig = False
    current_row = 1
    current_col = 0
    current_direction = "SOUTH"
    # Need an Update Rover Path Function 
    total_time = 0
    for move in commands[rover_id]:
        if move == 'L' or move == 'R':
            current_direction = move_rover(current_direction, move)
            

        elif move == 'M':
            
            if current_direction == "SOUTH":
                if current_row < 4:
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

def move_rover(current_direction, move) -> str:
    directions = ["NORTH", "EAST", "SOUTH", "WEST"]
    idx = directions.index(current_direction)
    
    if move == "L":
        return directions[(idx - 1) % 4]
    elif move == "R":
        return directions[(idx + 1) % 4]
    else:
        raise ValueError("Invalid move. Use 'L' for left or 'R' for right.")
    
def main():
    commands = get_rover_commands(10)
    generate_rover_path(1, commands)
    print(commands)
    # TODO ---------

if __name__ == "__main__":
    main()