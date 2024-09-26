"""this script applies to 8-bit images which can be read by PIL"""

import os
from PIL import Image
import numpy as np


def crop_image_and_label(image_path, label_path, tile_size=(512, 512), stride=(512, 512), output_dir='output_tiles'):
    """
    Crops an image and its corresponding label into tiles of specified size and saves them with the original filename as prefix.

    Parameters:
        image_path (str): Path to the high-resolution image.
        label_path (str): Path to the corresponding label image.
        tile_size (tuple): Size of each tile (width, height).
        stride (tuple): Stride of the sliding window (default: (512, 512)).
        output_dir (str): Directory to save the cropped tiles.

    Returns:
        None
    """
    # Open the image and label
    img = Image.open(image_path)
    label = Image.open(label_path)

    img_width, img_height = img.size

    # Ensure the image and label dimensions match
    assert img.size == label.size, "Image and label sizes do not match."

    # Get the original file name without extension
    base_filename = os.path.splitext(os.path.basename(image_path))[0]

    # Create output directories for images and labels
    output_img_dir = os.path.join(output_dir, "images")
    output_label_dir = os.path.join(output_dir, "labels")

    if not os.path.exists(output_img_dir):
        os.makedirs(output_img_dir)
    if not os.path.exists(output_label_dir):
        os.makedirs(output_label_dir)

    tile_count = 0

    # Loop over the image using a sliding window to crop the tiles
    for y in range(0, img_height, stride[1]):
        for x in range(0, img_width, stride[0]):
            # Crop the image and label tile
            img_tile = img.crop((x, y, x + tile_size[0], y + tile_size[1]))
            label_tile = label.crop((x, y, x + tile_size[0], y + tile_size[1]))

            # Ensure the tile is exactly the tile_size
            if img_tile.size == tile_size and label_tile.size == tile_size:
                # Convert images to NumPy arrays
                image_np = np.array(img_tile)
                label_np = np.array(label_tile)
                # Find the number of unique categories in the label tile
                unique_categories = np.unique(label_tile)

                # Check if more than 50% of pixels are labeled
                labeled_percentage = np.count_nonzero(label_tile) / (tile_size[0] * tile_size[1])

                # Check if the tile contains two or more categories
                if len(unique_categories) >= 2 and labeled_percentage >= 0.5:
                    # Save the image tile
                    img_tile_filename = f"{base_filename}_{tile_size[0]}tile_{tile_count}.tif"
                    if tile_size != (512, 512):  # resize
                        img_tile = img_tile.resize((512, 512), Image.LANCZOS)
                        label_tile = label_tile.resize((512, 512), Image.NEAREST)
                    img_tile.save(os.path.join(output_img_dir, img_tile_filename))

                    # Save the label tile
                    label_tile_filename = f"{base_filename}_{tile_size[0]}tile_{tile_count}_24label.tif"
                    label_tile.save(os.path.join(output_label_dir, label_tile_filename))

                    tile_count += 1

    print(f"Total tiles saved for {base_filename}: {tile_count}")


def process_all_images_and_labels(image_folder, label_folder, tile_size=(512, 512), stride=(512, 512),
                                  output_dir='output_tiles'):
    """
    Process all images and their corresponding labels in a folder by cropping them into tiles and saving them with original filename as prefix.

    Parameters:
        image_folder (str): Folder containing the high-resolution images.
        label_folder (str): Folder containing the corresponding label files.
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

            # Construct the corresponding label file path
            label_filename = os.path.splitext(filename)[0] + '_24label.png'
            label_path = os.path.join(label_folder, label_filename)

            # Check if the corresponding label file exists
            if os.path.exists(label_path):
                crop_image_and_label(image_path, label_path, tile_size, stride, output_dir)
            else:
                print(f"Label file not found for {filename}")


# Example usage:
image_folder = '/data/linfeng/landuse/DPA_data/five-billion-pixels/Image__8bit_NirRGB/'  # Path to the folder with high-res images (7000x7000)
label_folder = '/data/linfeng/landuse/DPA_data/source_dir/label/'  # Path to the folder with corresponding labels
process_all_images_and_labels(image_folder, label_folder,
                              tile_size=(512, 512), stride=(512, 512),
                              output_dir='output_tiles_8bit')
