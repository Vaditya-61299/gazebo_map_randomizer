import os
import random
import shutil

MAP_BOUNDS = (-10, 10)

def generate_random_rooms(num_rooms):
    rooms = []
    for i in range(num_rooms):
        center_x = round(random.uniform(-8, 8), 2)
        center_y = round(random.uniform(-8, 8), 2)
        length = round(random.uniform(3.0, 6.0), 2)
        width = round(random.uniform(3.0, 6.0), 2)

        x_min = center_x - length / 2
        x_max = center_x + length / 2
        y_min = center_y - width / 2
        y_max = center_y + width / 2

        rooms.append({
            "name": f"room_{i}",
            "center": (center_x, center_y),
            "size": (length, width),
            "bounds": [(x_min, y_min), (x_max, y_max)],
        })

    return rooms

'''def create_wall_model(name, size, pose, model_dir):
    model_path = os.path.join(model_dir, name)
    os.makedirs(os.path.join(model_path, "meshes"), exist_ok=True)

    sdf = f"""<?xml version='1.0'?>
<sdf version='1.6'>
  <model name='{name}'>
    <static>true</static>
    <link name='link'>
      
      <collision name='collision'>
        <geometry>
          <box><size>{' '.join(map(str, size))}</size></box>
        </geometry>
      </collision>
      <visual name='visual'>
        <geometry>
          <box><size>{' '.join(map(str, size))}</size></box>
        </geometry>
      </visual>
    </link>
  </model>
</sdf>
"""
    config = f"""<?xml version='1.0'?>
<model>
  <name>{name}</name>
  <version>1.0</version>
  <sdf version='1.6'>model.sdf</sdf>
</model>
"""
    with open(os.path.join(model_path, "model.sdf"), 'w') as f:
        f.write(sdf)
    with open(os.path.join(model_path, "model.config"), 'w') as f:
        f.write(config)'''

def create_wall_model(name, size, pose, model_dir):
    model_path = os.path.join(model_dir, name)
    os.makedirs(os.path.join(model_path, "meshes"), exist_ok=True)

    # Note: No <pose> inside <model>; it's specified in world file
    sdf = f"""<?xml version='1.0'?>
<sdf version='1.6'>
  <model name='{name}'>
    <static>true</static>
    <link name='link'>
      <collision name='collision'>
        <pose>0 0 0 0 0 0</pose>
        <geometry>
          <box>
            <size>{size[0]} {size[1]} {size[2]}</size>
          </box>
        </geometry>
      </collision>
      <visual name='visual'>
        <pose>0 0 0 0 0 0</pose>
        <geometry>
          <box>
            <size>{size[0]} {size[1]} {size[2]}</size>
          </box>
        </geometry>
      </visual>
    </link>
  </model>
</sdf>
"""

    config = f"""<?xml version='1.0'?>
<model>
  <name>{name}</name>
  <version>1.0</version>
  <sdf version='1.6'>model.sdf</sdf>
  <author></author>
  <description>Auto-generated wall model</description>
</model>
"""

    with open(os.path.join(model_path, "model.sdf"), 'w') as f:
        f.write(sdf)
    with open(os.path.join(model_path, "model.config"), 'w') as f:
        f.write(config)


def generate_walls(rooms, model_dir):
    h = 1.0  # ✅ fixed height
    t = 0.2  # wall thickness
    pose_z = 0.0  # ✅ fixed pose z

    walls = []
    for room in rooms:
        x, y = room["center"]
        l, w = room["size"]

        wall_data = [
            ("top",     [l, t, h],   [x, y + w / 2, pose_z]),
            ("bottom",  [l, t, h],   [x, y - w / 2, pose_z]),
            ("left",    [t, w, h],   [x - l / 2, y, pose_z]),
            ("right",   [t, w, h],   [x + l / 2, y, pose_z]),
        ]

        doorway_wall = random.choice(["top", "bottom", "left", "right"])

        for name, size, pose in wall_data:
            if name == doorway_wall:
                continue

            wall_model_name = f"{room['name']}_wall_{name}"
            create_wall_model(wall_model_name, size, pose, model_dir)

            x_min = pose[0] - size[0] / 2
            x_max = pose[0] + size[0] / 2
            y_min = pose[1] - size[1] / 2
            y_max = pose[1] + size[1] / 2

            walls.append({
                "name": wall_model_name,
                "pose": pose,
                "bounds": [(x_min, y_min), (x_max, y_max)],
            })

    return walls

'''def generate_perimeter_walls(model_dir):
    h = 1.0
    t = 0.2
    pose_z = 0.0
    size = 20.0

    half_size = size / 2
    half_t = t / 2

    perimeter = [
        ("outer_top",    [size, t, h],  [0.0,  half_size - half_t, pose_z]),
        ("outer_bottom", [size, t, h],  [0.0, -half_size + half_t, pose_z]),
        ("outer_left",   [t, size, h],  [-half_size + half_t, 0.0, pose_z]),
        ("outer_right",  [t, size, h],  [ half_size - half_t, 0.0, pose_z]),
    ]

    walls = []
    for name, wall_size, pose in perimeter:
        create_wall_model(name, wall_size, pose, model_dir)
        x_min = pose[0] - wall_size[0] / 2
        x_max = pose[0] + wall_size[0] / 2
        y_min = pose[1] - wall_size[1] / 2
        y_max = pose[1] + wall_size[1] / 2
        walls.append({
            "name": name,
            "pose": pose,
            "bounds": [(x_min, y_min), (x_max, y_max)],
        })

    return walls'''

def generate_perimeter_walls(model_dir):
    h = 1.0       # Wall height
    t = 0.2       # Wall thickness
    size = 20.0   # Grid size (from -10 to +10)
    pose_z = 0.0  # So bottom is at z=0 and top at z=1

    half_size = size / 2

    perimeter = [
        # Horizontal walls (top/bottom)
        ("outer_top",    [size, t, h],  [0.0,  half_size + t / 2, pose_z]),
        ("outer_bottom", [size, t, h],  [0.0, -half_size - t / 2, pose_z]),

        # Vertical walls (left/right)
        ("outer_left",   [t, size, h],  [-half_size - t / 2, 0.0, pose_z]),
        ("outer_right",  [t, size, h],  [ half_size + t / 2, 0.0, pose_z]),
    ]

    walls = []
    for name, wall_size, pose in perimeter:
        create_wall_model(name, wall_size, pose, model_dir)
        x_min = pose[0] - wall_size[0] / 2
        x_max = pose[0] + wall_size[0] / 2
        y_min = pose[1] - wall_size[1] / 2
        y_max = pose[1] + wall_size[1] / 2
        walls.append({
            "name": name,
            "pose": pose,
            "bounds": [(x_min, y_min), (x_max, y_max)],
        })

    return walls




def generate_world(walls, out_path):
    world = """<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="default">
    <include><uri>model://ground_plane</uri></include>
    <include><uri>model://sun</uri></include>
"""

    for wall in walls:
        pose_str = " ".join(map(str, wall["pose"]))
        world += f"""    <include>
      <uri>model://{wall["name"]}</uri>
      <pose>{pose_str}</pose>
    </include>
"""

    world += """  </world>\n</sdf>"""

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(world)

if __name__ == "__main__":
    num_rooms = random.randint(4, 6)
    print(f"🛖 Generating {num_rooms} random rooms...")

    root = os.getcwd()
    model_dir = os.path.join(root, "models")
    world_file = os.path.join(root, "world", "base_world.world")

    rooms = generate_random_rooms(num_rooms)
    perimeter_walls = generate_perimeter_walls(model_dir)
    room_walls = generate_walls(rooms, model_dir)
    all_walls = perimeter_walls + room_walls

    generate_world(all_walls, world_file)

    print(f"✅ World with rooms and walls generated at {world_file}")
