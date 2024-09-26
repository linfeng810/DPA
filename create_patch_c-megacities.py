"""this script applies to 8-bit images which can be read by PIL"""

import os
from PIL import Image
import numpy as np


def crop_image_and_label(image_path, tile_size=(512, 512), stride=(512, 512), output_dir='output_tiles_target'):
    """
    Crops an image and its corresponding label into tiles of specified size and saves them with the original filename as prefix.

    Parameters:
        image_path (str): Path to the high-resolution image.
        tile_size (tuple): Size of each tile (width, height).
        stride (tuple): Stride of the sliding window (default: (512, 512)).
        output_dir (str): Directory to save the cropped tiles.

    Returns:
        None
    """
    # Open the image and label
    img = Image.open(image_path)

    img_width, img_height = img.size

    # Get the original file name without extension
    base_filename = os.path.splitext(os.path.basename(image_path))[0]

    # resize PlanetScope images
    if base_filename.startswith('2019'):
        new_width, new_height = img_width * 3 // 4, img_height * 3 // 4
        img = img.resize((new_width, new_height), Image.LANCZOS)
        img_width, img_height = img.size

    # Create output directories for images and labels
    output_img_dir = os.path.join(output_dir, "images")

    if not os.path.exists(output_img_dir):
        os.makedirs(output_img_dir)

    tile_count = 0

    # Loop over the image using a sliding window to crop the tiles
    for y in range(0, img_height, stride[1]):
        for x in range(0, img_width, stride[0]):
            # Crop the image and label tile
            img_tile = img.crop((x, y, x + tile_size[0], y + tile_size[1]))

            # Ensure the tile is exactly the tile_size
            if img_tile.size == tile_size:
                # Save the image tile
                img_tile_filename = f"{base_filename}_tile_{tile_count}.tif"
                img_tile.save(os.path.join(output_img_dir, img_tile_filename))

                tile_count += 1

    print(f"Total tiles saved for {base_filename}: {tile_count}")


def process_all_images_and_labels(image_folder, tile_size=(512, 512), stride=(512, 512),
                                  output_dir='output_tiles_target'):
    """
    Process all images and their corresponding labels in a folder by cropping them into tiles and saving them with original filename as prefix.

    Parameters:
        image_folder (str): Folder containing the high-resolution images.
        tile_size (tuple): Size of each tile (width, height).
        stride (tuple): Stride of the sliding window.
        output_dir (str): Directory to save the cropped tiles.

    Returns:
        None
    """
    # List all image files in the input folder
    for filename in os.listdir(image_folder):
        if filename.endswith('.png') or filename.endswith('.tif'):  # Add other formats as needed
            image_path = os.path.join(image_folder, filename)

            crop_image_and_label(image_path, tile_size, stride, output_dir)


# Example usage:
image_folder = '/data/linfeng/landuse/DPA_data/c-megacities/Image__8bit_NirRGB/'  # Path to the folder with high-res images (7000x7000)
process_all_images_and_labels(image_folder,
                              tile_size=(512, 512), stride=(512, 512),
                              output_dir='output_tiles_target')
