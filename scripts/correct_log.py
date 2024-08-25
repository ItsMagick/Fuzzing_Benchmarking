# Specify the path to your log file
file_path = '../mqtt_aflnet_stdout.log'

# Number of lines to skip
lines_to_skip = 9095

# Read the file and skip the first 9095 lines
with open(file_path, 'r') as file:
    lines = file.readlines()[lines_to_skip:]

# Write the remaining lines back to the file
with open(file_path, 'w') as file:
    file.writelines(lines)

print(f"The first {lines_to_skip} lines have been removed.")
