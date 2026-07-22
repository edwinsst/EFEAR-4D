import sys
import subprocess
import rosbag
import os

# Usage: python3 convert_ros2mcap_to_rosbag.py /path/to/mcap/folder/ /output/bag/name.bag
# Play converted bag with: "rosbag play /path/to/your/bag.bag /imaging_radar1:=/oculii_radar/point_cloud --clock"

if len(sys.argv) < 3:
    print("Usage: python3 prep_bag.py <input.mcap_folder> <output_efear.bag>")
    sys.exit(1)

input_mcap = sys.argv[1]
final_bag = sys.argv[2]
temp_bag = "temp_converted.bag"

# 1. Clean up any broken files from previous failed runs
if os.path.exists(temp_bag):
    print(f"Removing old {temp_bag}...")
    os.remove(temp_bag)

# 2. Convert MCAP to ROS 1 Bag (Skipping unknown types)
print(f"Converting {input_mcap} to ROS 1...")

subprocess.run([
    "rosbags-convert", input_mcap, 
    "--dst", temp_bag, 
    "--exclude-topic", "/connected_clients",
    "--exclude-topic", "/client_count",
    "--exclude-topic", "/events/write_split"
], check=True)

# 3. Fix PointCloud2 fields for EFEAR-4D
print("Fixing PointCloud2 fields for EFEAR-4D...")
with rosbag.Bag(final_bag, 'w') as outbag:
    for topic, msg, t in rosbag.Bag(temp_bag).read_messages():
        if topic == '/imaging_radar1':
            # Strictly map only the two exact fields EFEAR needs
            for field in msg.fields:
                if field.name == 'snr':
                    field.name = 'power'
                elif field.name == 'velocity':
                    field.name = 'doppler'
        outbag.write(topic, msg, t)

# 4. Clean up the temporary ROS 1 bag
os.remove(temp_bag)
print(f"Success! Ready to play: {final_bag}")
