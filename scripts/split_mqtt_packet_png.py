from PIL import Image

# Load the image
image_path = "scripts/mqtt_packet_structure.png"
image = Image.open(image_path)

# Dimensions of the image
width, height = image.size

# Split point (just after the Client ID, around the middle of the image)
split_point = width // 2

# Crop the image into two parts
left_image = image.crop((0, 0, split_point, height))
right_image = image.crop((split_point, 0, width, height))

# Create a new image to stack the two parts vertically
new_image = Image.new('RGB', (split_point, height * 2))

# Paste the two parts into the new image
new_image.paste(left_image, (0, 0))
new_image.paste(right_image, (0, height))

# Save the new image
output_path = "scripts/mqtt_packet_structure_split.png"
new_image.save(output_path)

# Show the new image
new_image.show()
