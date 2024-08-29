file_path = '../mqtt_aflnet_stdout.log'

lines_to_skip = 9095

with open(file_path, 'r') as file:
    lines = file.readlines()[lines_to_skip:]

with open(file_path, 'w') as file:
    file.writelines(lines)

print(f"The first {lines_to_skip} lines have been removed.")
