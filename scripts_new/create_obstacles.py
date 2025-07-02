import os
import shutil
import random
import math



def gen_obstacle_sdf(name_obst, scale, pose, name_real, dae_extension=False):
    ext = "dae" if dae_extension else "obj"

    sdf = f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <model name="{name_obst}">
    <static>true</static>
    <link name="link">
      <!-- No pose here, world file handles model pose -->

      <collision name="collision">
        <pose>0 0 0 0 0 0</pose>  <!-- Offset if mesh is misaligned -->
        <geometry>
          <mesh>
            <scale>{scale[0]} {scale[1]} {scale[2]}</scale>
            <uri>model://{name_obst}/meshes/{name_real}.{ext}</uri>
          </mesh>
        </geometry>
      </collision>

      <visual name="visual">
        <pose>0 0 0 0 0 0</pose>  <!-- Offset if mesh is misaligned -->
        <geometry>
          <mesh>
            <scale>{scale[0]} {scale[1]} {scale[2]}</scale>
            <uri>model://{name_obst}/meshes/{name_real}.{ext}</uri>
          </mesh>
        </geometry>
      </visual>
    </link>
  </model>
</sdf>
"""
    return sdf



def gen_obstacle_config(name_obst, name_real):
    config = f"""<?xml version="1.0"?>
<model>
  <name>{name_obst}</name>
  <version>1.0</version>
  <sdf version="1.6">model.sdf</sdf>
  <author></author>
  <description>Auto-generated model for obstacle</description>
</model>
"""
    return config


def get_object_pool():
    home = os.path.expanduser("~")
    gazebo_models_path = os.path.join(home, ".gazebo", "models")

    possible_models = ["construction_cone", "cinder_block", "arm_part"]
    random.shuffle(possible_models)  # Shuffle once for variety

    valid_objects = []

    for selected_model in possible_models:
        source_model_path = os.path.join(gazebo_models_path, selected_model)
        source_meshes = os.path.join(source_model_path, "meshes")

        if not os.path.exists(source_meshes):
            continue

        mesh_files = os.listdir(source_meshes)
        for file in mesh_files:
            if file.endswith(".dae") or file.endswith(".obj"):
                mesh_name, extension = os.path.splitext(file)
                extension = extension[1:].lower()
                valid_objects.append((selected_model, mesh_name, extension))
                break  # use only the first mesh found

    if not valid_objects:
        raise Exception("❌ No valid models with .dae or .obj files found.")

    return valid_objects


def get_scale():
    return [
        round(random.uniform(0.5, 1.5), 2),
        round(random.uniform(0.5, 1.5), 2),
        round(random.uniform(0.5, 1.5), 2)
    ]


def get_pose():
    x = round(random.uniform(-8, 8), 2)
    y = round(random.uniform(-8, 8), 2)
    z = 0.0
    roll, pitch = 0.0, 0.0
    yaw = round(random.uniform(0, 2 * math.pi), 3)
    return [x, y, z, roll, pitch, yaw]



def create_obstacle(num_obst):
    root_folder = os.getcwd()
    model_folder = os.path.join(root_folder, "models")
    os.makedirs(model_folder, exist_ok=True)

    object_pool = get_object_pool()
    if not object_pool:
        raise Exception("❌ No valid models found in the object pool.")

    obstacles = []

    # Randomly choose num_obst obstacles (with replacement)
    selected_obstacles = [random.choice(object_pool) for _ in range(num_obst)]

    for i, (selected_model, mesh_name, extension) in enumerate(selected_obstacles):
        _name = f"obstacle_{i}"
        scale = get_scale()
        pose = get_pose()

        print(f"🎲 Creating obstacle {_name} from model '{selected_model}'")

        obstacle_folder = os.path.join(model_folder, _name)
        os.makedirs(obstacle_folder, exist_ok=True)

        # Copy mesh
        source_model_path = os.path.join(os.path.expanduser("~"), ".gazebo", "models", selected_model)
        shutil.copytree(os.path.join(source_model_path, "meshes"), os.path.join(obstacle_folder, "meshes"), dirs_exist_ok=True)

        # Copy materials if exist
        source_materials = os.path.join(source_model_path, "materials")
        if os.path.exists(source_materials):
            shutil.copytree(source_materials, os.path.join(obstacle_folder, "materials"), dirs_exist_ok=True)

        # Write SDF
        is_dae = extension == "dae"
        with open(os.path.join(obstacle_folder, "model.sdf"), 'w') as sdf_file:
            sdf_file.write(gen_obstacle_sdf(name_obst=_name, scale=scale, pose=pose, name_real=mesh_name, dae_extension=is_dae))

        # Write config
        with open(os.path.join(obstacle_folder, "model.config"), 'w') as config_file:
            config_file.write(gen_obstacle_config(name_obst=_name, name_real=mesh_name))

        obstacles.append((_name, pose))

    return obstacles



def get_world(obstacles, root_folder):
    world_template = """<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="default">

    <!-- Basic ground plane -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <!-- Light -->
    <include>
      <uri>model://sun</uri>
    </include>
"""

    for name, pose in obstacles:
        pose_str = " ".join(str(p) for p in pose)
        world_template += f"""
    <include>
      <uri>model://{name}</uri>
      <pose>{pose_str}</pose>
    </include>"""

    world_template += """
  </world>
</sdf>
"""

    world_folder = os.path.join(root_folder, "world")
    os.makedirs(world_folder, exist_ok=True)
    with open(os.path.join(world_folder, "obstacle_world.world"), 'w') as f:
        f.write(world_template)


# ---------- MAIN ----------
if __name__ == "__main__":
    num_obstacles = 25
    obstacles = create_obstacle(num_obst=num_obstacles)
    get_world(obstacles, root_folder=os.getcwd())
