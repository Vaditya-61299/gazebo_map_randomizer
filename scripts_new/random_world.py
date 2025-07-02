import xml.etree.ElementTree as ET

def extract_includes(filepath, include_type):
    """
    include_type: 'base' or 'obstacle'
    """
    tree = ET.parse(filepath)
    root = tree.getroot()

    # Find the <world> tag
    world_elem = root.find('world')
    if world_elem is None and root.tag == 'world':
        world_elem = root
    if world_elem is None:
        raise Exception(f"No <world> element found in {filepath}")

    includes = []
    for include in world_elem.findall('include'):
        uri_elem = include.find('uri')
        if uri_elem is not None:
            uri_text = uri_elem.text.lower()
            is_obstacle = 'obstacle' in uri_text
            if include_type == 'obstacle' and is_obstacle:
                includes.append(include)
            elif include_type == 'base' and not is_obstacle:
                includes.append(include)

    return includes

def create_random_world(base_path, world_path, output_path):
    # Extract relevant includes
    base_includes = extract_includes(base_path, 'base')
    obstacle_includes = extract_includes(world_path, 'obstacle')

    # Create new SDF structure
    sdf_elem = ET.Element('sdf', version="1.6")
    world_elem = ET.SubElement(sdf_elem, 'world', name="default")

    for inc in base_includes + obstacle_includes:
        world_elem.append(inc)

    # Write to file
    tree = ET.ElementTree(sdf_elem)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f"✅ random_world.world successfully created at: {output_path}")

if __name__ == "__main__":
    create_random_world(
        base_path='world/room_world.world',
        world_path='world/obstacle_world.world',
        output_path='world/random_world.world'
    )
