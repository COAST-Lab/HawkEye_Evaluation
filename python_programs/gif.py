from PIL import Image, ImageSequence

def combine_gif_with_colorbar(gif_path, color_bar_path, output_path):
    # Open the GIF and the color bar image
    gif = Image.open(gif_path)
    color_bar = Image.open(color_bar_path)

    # List to hold the new frames
    new_frames = []

    # Process each frame in the GIF
    for frame in ImageSequence.Iterator(gif):
        # This ensures the frame is in RGBA mode (necessary for compositing images with alpha)
        frame = frame.convert("RGBA")

        # Create a new frame with height of the original frame plus color bar
        new_frame = Image.new('RGBA', (gif.width, frame.height + color_bar.height))

        # Paste the original frame
        new_frame.paste(frame, (0, 0))

        # Calculate the position to center the color bar horizontally
        x_position = (gif.width - color_bar.width) // 2

        # Paste the color bar at the bottom and center it horizontally
        new_frame.paste(color_bar, (x_position, frame.height), color_bar)  # Using color_bar as a mask for itself

        # Append the new frame to the list
        new_frames.append(new_frame)

    # Save the frames as a new GIF
    new_frames[0].save(output_path, save_all=True, append_images=new_frames[1:], optimize=False, loop=0, duration=gif.info['duration'])

# Paths to the files
gif_path = '/Users/mitchtork/Thesis/HawkEye_Evaluation/visualization/contour_plots/wb/chlor_a/3D_plots/chlor_a_gradient.gif'
color_bar_path = '/Users/mitchtork/Thesis/HawkEye_Evaluation/local_processing_resources/chlor_a_horizontal.png'
output_path = '/Users/mitchtork/Thesis/HawkEye_Evaluation/visualization/contour_plots/wb/chlor_a/3D_plots/chlor_a_with_color_bar.gif'

# Call the function
combine_gif_with_colorbar(gif_path, color_bar_path, output_path)