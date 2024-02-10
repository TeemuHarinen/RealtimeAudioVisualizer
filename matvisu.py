import numpy as np
import time
import pyaudio

# Parameters for audio stream
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 40000
CHUNK = 1024
MAX_HEIGHT = 20

# ANSI color codes for console visualization
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RESET = "\033[0m"

# Index for BlackHole
DEVICE_INDEX = 5

def normalize_audio_data(audio_data):
    """Normalize the audio data to 0-1 range, ensuring no division by zero."""
    audio_data = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
    min_val = np.min(audio_data)
    max_val = np.max(audio_data)
    # Avoid division by zero by adding a small value to the denominator
    normalized_data = (audio_data - min_val) / (max_val - min_val + 1e-10)
    return normalized_data

def create_visualization_data(normalized_data, num_bars=8):
    """Create visualization data from the normalized audio data."""
    bars = np.array_split(normalized_data, num_bars)
    bar_heights = [np.mean(bar) for bar in bars]
    return bar_heights

def display_in_console(bar_heights, max_height=10):
    """Display the bar heights in the console with dynamic scaling, visual enhancements, and NaN protection."""
    # Filter out NaN values, replacing them with 0, and ensure there's no division by zero
    clean_bar_heights = [0 if np.isnan(height) else height for height in bar_heights]
    max_bar_height = max(clean_bar_heights) if clean_bar_heights else 1
    max_bar_height = max(1, max_bar_height)  # Ensure max_bar_height is never 0 to avoid division by zero
    
    scaled_heights = [int((height / max_bar_height) * max_height) for height in clean_bar_heights]

    # Clear the console for a cleaner display
    print('\033[H\033[J', end='')  # This sequence clears the screen and moves the cursor to the top
    
    # Enhanced visual representation with NaN protection
    for height in scaled_heights:
        bar = '*' * height
        print(f"{bar}".ljust(max_height))

def audio_callback(in_data, frame_count, time_info, status):
    if not in_data:
        return (None, pyaudio.paContinue)  # Early return if no data
    
    normalized_data = normalize_audio_data(in_data)
    if np.isnan(normalized_data).any():
        print(f"{RED}NaN detected!{RESET}")
        return (None, pyaudio.paContinue)  # Early return if NaN is detected
    
    bar_heights = create_visualization_data(normalized_data)
    display_in_console(bar_heights, MAX_HEIGHT)
    return (None, pyaudio.paContinue)

def main():
    # Create audio stream
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=False,
                    frames_per_buffer=CHUNK,
                    input_device_index=DEVICE_INDEX,
                    stream_callback=audio_callback)
    
    print(f"{YELLOW}Audio stream started!{RESET}")
    stream.start_stream()
    
    try:
        while stream.is_active():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print(f"{RED}Audio stream stopped!{RESET}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()


