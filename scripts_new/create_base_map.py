import os
import random

GRID_LIMIT = 10
WALL_HEIGHT = 1.0
WALL_THICKNESS = 0.2
POSE_Z = 0.0
DOOR_WIDTH = 1.0
NUM_ROOMS = 5  # 👈 User-defined number of rooms

def create_wall_model(name, size, pose, model_dir):
    path = os.path.join(model_dir, name)
    os.makedirs(os.path.join(path, "meshes"), exist_ok=True)
    sdf = f"""<?xml version='1.0'?>
<sdf version='1.6'>
  <model name='{name}'>
    <static>true</static>
    <link name='link'>
      <collision name='collision'>
        <geometry><box><size>{size[0]} {size[1]} {size[2]}</size></box></geometry>
      </collision>
      <visual name='visual'>
        <geometry><box><size>{size[0]} {size[1]} {size[2]}</size></box></geometry>
      </visual>
    </link>
  </model>
</sdf>"""
    config = f"""<?xml version='1.0'?>
<model><name>{name}</name><version>1.0</version><sdf version='1.6'>model.sdf</sdf></model>"""
    with open(os.path.join(path, "model.sdf"), 'w') as f: f.write(sdf)
    with open(os.path.join(path, "model.config"), 'w') as f: f.write(config)

def generate_perimeter_walls(model_dir):
    h = WALL_HEIGHT
    t = WALL_THICKNESS
    size = GRID_LIMIT * 2
    half = size / 2
    perimeter = [
        ("outer_top",    [size, t, h],  [0,  half + t/2, POSE_Z]),
        ("outer_bottom", [size, t, h],  [0, -half - t/2, POSE_Z]),
        ("outer_left",   [t, size, h],  [-half - t/2, 0, POSE_Z]),
        ("outer_right",  [t, size, h],  [ half + t/2, 0, POSE_Z]),
    ]
    walls = []
    for name, size, pose in perimeter:
        create_wall_model(name, size, pose, model_dir)
        walls.append({"name": name, "pose": pose})
    return walls

def generate_room(room_index, model_dir):
    wall_entities = []

    # Step 1: Random perimeter wall
    side = random.choice(["top", "bottom", "left", "right"])
    length1 = random.randint(3, GRID_LIMIT // 2)

    if side in ["top", "bottom"]:
        x = random.randint(-GRID_LIMIT + 1, GRID_LIMIT - 1)
        y = GRID_LIMIT if side == "top" else -GRID_LIMIT
        dir_y = -1 if side == "top" else 1
        mid_y = y + dir_y * (length1 / 2)

        pose1 = [x, mid_y, POSE_Z]
        size1 = [WALL_THICKNESS, length1, WALL_HEIGHT]
        start = (x, y)
        end1 = (x, y + dir_y * length1)
        axis1 = "Y"

    else:
        y = random.randint(-GRID_LIMIT + 1, GRID_LIMIT - 1)
        x = -GRID_LIMIT if side == "left" else GRID_LIMIT
        dir_x = 1 if side == "left" else -1
        mid_x = x + dir_x * (length1 / 2)

        pose1 = [mid_x, y, POSE_Z]
        size1 = [length1, WALL_THICKNESS, WALL_HEIGHT]
        start = (x, y)
        end1 = (x + dir_x * length1, y)
        axis1 = "X"

    name1 = f"room{room_index}_wall1"
    create_wall_model(name1, size1, pose1, model_dir)
    wall_entities.append({"name": name1, "pose": pose1})
    print(f"🏠 Room {room_index} - Wall 1: {side} -> {axis1}, from {start} to {end1}")

    # Step 2: Perpendicular wall with door gap
    x1, y1 = end1
    axis2 = "X" if axis1 == "Y" else "Y"
    direction = random.choice(["+X", "-X"] if axis2 == "X" else ["+Y", "-Y"])

    if direction == "+X":
        x_start = x1 + DOOR_WIDTH
        length2 = GRID_LIMIT - x_start
        center = (x_start + length2 / 2, y1)
        size2 = [length2, WALL_THICKNESS, WALL_HEIGHT]

    elif direction == "-X":
        x_start = x1 - DOOR_WIDTH
        length2 = x_start + GRID_LIMIT
        center = (x_start - length2 / 2, y1)
        size2 = [length2, WALL_THICKNESS, WALL_HEIGHT]

    elif direction == "+Y":
        y_start = y1 + DOOR_WIDTH
        length2 = GRID_LIMIT - y_start
        center = (x1, y_start + length2 / 2)
        size2 = [WALL_THICKNESS, length2, WALL_HEIGHT]

    elif direction == "-Y":
        y_start = y1 - DOOR_WIDTH
        length2 = y_start + GRID_LIMIT
        center = (x1, y_start - length2 / 2)
        size2 = [WALL_THICKNESS, length2, WALL_HEIGHT]

    pose2 = [center[0], center[1], POSE_Z]
    name2 = f"room{room_index}_wall2"
    create_wall_model(name2, size2, pose2, model_dir)
    wall_entities.append({"name": name2, "pose": pose2})
    print(f"🏠 Room {room_index} - Wall 2: {direction}, center: {center}")

    return wall_entities

def generate_world(all_walls, out_path):
    world = """<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="default">
    <include><uri>model://ground_plane</uri></include>
    <include><uri>model://sun</uri></include>
"""
    for wall in all_walls:
        pose = " ".join(map(str, wall["pose"]))
        world += f"""    <include>
      <uri>model://{wall["name"]}</uri>
      <pose>{pose}</pose>
    </include>
"""
    world += "  </world>\n</sdf>"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f: f.write(world)

if __name__ == "__main__":
    root = os.getcwd()
    model_dir = os.path.join(root, "models")
    world_file = os.path.join(root, "world", "room_world.world")

    all_walls = generate_perimeter_walls(model_dir)

    for i in range(NUM_ROOMS):
        walls = generate_room(i + 1, model_dir)
        all_walls.extend(walls)

    generate_world(all_walls, world_file)
    print(f"✅ Generated {NUM_ROOMS} rooms in {world_file}")
