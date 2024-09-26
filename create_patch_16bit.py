import os
from osgeo import gdal
import numpy as np

def crop_image_and_label(image_path, label_path, tile_size=(512, 512), stride=(512, 512), output_dir='output_tiles'):
    """
    Crops a 16-bit satellite image and its corresponding label into tiles of specified size and saves them.

    Parameters:
        image_path (str): Path to the high-resolution image.
        label_path (str): Path to the corresponding label image.
        tile_size (tuple): Size of each tile (width, height).
        stride (tuple): Stride of the sliding window (default: (512, 512)).
        output_dir (str): Directory to save the cropped tiles.

    Returns:
        None
    """
    # Open the image and label using GDAL
    img_ds = gdal.Open(image_path)
    label_ds = gdal.Open(label_path)

    img_width = img_ds.RasterXSize
    img_height = img_ds.RasterYSize

    # # Ensure the image and label dimensions match
    # if not (img_width == label_ds.RasterXSize and img_height == label_ds.RasterYSize):
    #     print("Image and label sizes do not match. \n"
    #           "Path: "+image_path+label_path+"\n"
    #           "Image size: "+str(img_width)+","+str(img_height)+"\n"
    #           "Label size: "+str(label_ds.RasterXSize)+","+str(label_ds.RasterYSize))

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
            # Skip tiles that are smaller than a certain threshold (e.g., too small to be useful)
            if img_width - x < tile_size[0] or img_height - y <= tile_size[1]:
                continue

            # Crop the image and label tile
            img_tile = img_ds.ReadAsArray(x, y, tile_size[0], tile_size[1])
            label_tile = label_ds.ReadAsArray(x, y, tile_size[0], tile_size[1])

            # Ensure that the tile is not empty
            if img_tile is None or label_tile is None:
                continue

            # Ensure the tile is exactly the tile_size
            if img_tile.shape[1] == tile_size[1] and img_tile.shape[2] == tile_size[0]:  # For multi-band images
                # Convert the label tile to NumPy array if it's not already
                label_np = np.array(label_tile)

                # Find the number of unique categories in the label tile
                unique_categories = np.unique(label_np)

                # Check if more than 50% of pixels are labeled
                labeled_percentage = np.count_nonzero(label_np) / (tile_size[0] * tile_size[1])

                # Check if the tile contains two or more categories
                if len(unique_categories) >= 2 and labeled_percentage >= 0.5:
                    # Save the image tile using GDAL
                    img_tile_filename = f"{base_filename}_tile_{tile_count}.tif"
                    img_tile_path = os.path.join(output_img_dir, img_tile_filename)

                    # Create a new GeoTIFF file for the image tile
                    driver = gdal.GetDriverByName('GTiff')
                    img_tile_ds = driver.Create(img_tile_path, tile_size[0], tile_size[1], img_ds.RasterCount, gdal.GDT_UInt16)
                    img_tile_ds.WriteRaster(0, 0, tile_size[0], tile_size[1], img_tile.tobytes())
                    img_tile_ds.FlushCache()
                    img_tile_ds = None  # Close the file

                    # Save the label tile using GDAL
                    label_tile_filename = f"{base_filename}_tile_{tile_count}_24label.tif"
                    label_tile_path = os.path.join(output_label_dir, label_tile_filename)

                    # Create a new GeoTIFF file for the label tile
                    label_tile_ds = driver.Create(label_tile_path, tile_size[0], tile_size[1], 1, gdal.GDT_Byte)
                    label_tile_ds.WriteRaster(0, 0, tile_size[0], tile_size[1], label_tile.tobytes())
                    label_tile_ds.FlushCache()
                    label_tile_ds = None  # Close the file

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
        if filename.endswith('.tiff'):  # Assuming satellite images are in GeoTIFF format
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
image_folder = '/data/linfeng/landuse/DPA_data/source_dir/image/'  # Path to the folder with high-res images (7000x7000)
label_folder = '/data/linfeng/landuse/DPA_data/source_dir/label/'  # Path to the folder with corresponding labels
process_all_images_and_labels(image_folder, label_folder,
                              tile_size=(512, 512), stride=(256, 256),
                              output_dir='output_tiles')
