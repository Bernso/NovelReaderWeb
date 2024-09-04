import customtkinter as ctk
from tkinter import filedialog, END, Listbox
import vlc
import threading
import os
import time

# Create the main application window
app = ctk.CTk()
app.title("CustomTkinter Music Player")
app.geometry("850x470")

# Global variables
playlist = []
current_index = 0
player = vlc.MediaPlayer()
is_paused = False
is_playing = False

# Function to load songs into the playlist
def load_songs():
    global playlist
    song_paths = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3 *.wav")])
    if song_paths:
        for song in song_paths:
            playlist.append(song)
            song_listbox.insert(END, os.path.basename(song))

# Function to play the selected song
def play_song():
    global current_index, player, is_paused, is_playing
    if playlist:
        if is_paused:
            player.play()
            is_paused = False
        else:
            stop_song()
            song = playlist[current_index]
            player = vlc.MediaPlayer(song)
            player.play()
            is_playing = True
            update_song_info()
            track_progress()

# Function to pause the song
def pause_song():
    global is_paused
    if is_playing:
        player.pause()
        is_paused = True

# Function to stop the song
def stop_song():
    global is_playing
    if is_playing:
        player.stop()
        is_playing = False
        progress_slider.set(0)
        song_time_label.configure(text="00:00 / 00:00")

# Function to play the next song
def next_song():
    global current_index
    stop_song()
    if current_index < len(playlist) - 1:
        current_index += 1
    else:
        current_index = 0
    play_song()

# Function to play the previous song
def previous_song():
    global current_index
    stop_song()
    if current_index > 0:
        current_index -= 1
    else:
        current_index = len(playlist) - 1
    play_song()

# Function to set the volume
def set_volume(val):
    volume = float(val) / 100
    player.audio_set_volume(int(volume * 100))

# Function to update song info like title and duration
def update_song_info():
    song = playlist[current_index]
    song_title_label.configure(text=os.path.basename(song))
    song_length = player.get_length() / 1000  # Length in seconds
    song_time_label.configure(text=f"00:00 / {time.strftime('%M:%S', time.gmtime(song_length))}")

# Function to update the track progress
def track_progress():
    def progress():
        while is_playing:
            current_time = player.get_time() / 1000  # Current time in seconds
            song_length = player.get_length() / 1000  # Total length in seconds
            if song_length > 0:
                progress_slider.set((current_time / song_length) * 100)
                song_time_label.configure(text=f"{time.strftime('%M:%S', time.gmtime(current_time))} / {time.strftime('%M:%S', time.gmtime(song_length))}")
            time.sleep(1)
    threading.Thread(target=progress).start()

# Function to handle playlist selection
def on_select(evt):
    global current_index
    w = evt.widget
    current_index = int(w.curselection()[0])
    stop_song()
    play_song()

# Create the UI elements
song_listbox = Listbox(app, bg="#222222", fg="white", height=10)
song_listbox.pack(pady=10, fill="x")
song_listbox.bind('<<ListboxSelect>>', on_select)

load_button = ctk.CTkButton(app, text="Load Songs", command=load_songs)
load_button.pack(pady=10)

song_title_label = ctk.CTkLabel(app, text="No Song Playing", font=("Arial", 18))
song_title_label.pack(pady=5)

song_time_label = ctk.CTkLabel(app, text="00:00 / 00:00", font=("Arial", 12))
song_time_label.pack()

progress_slider = ctk.CTkSlider(app, from_=0, to=100)
progress_slider.pack(pady=10, fill="x")

control_frame = ctk.CTkFrame(app)
control_frame.pack(pady=20)

previous_button = ctk.CTkButton(control_frame, text="Previous", command=previous_song)
previous_button.grid(row=0, column=0, padx=10)

play_button = ctk.CTkButton(control_frame, text="Play", command=play_song)
play_button.grid(row=0, column=1, padx=10)

pause_button = ctk.CTkButton(control_frame, text="Pause", command=pause_song)
pause_button.grid(row=0, column=2, padx=10)

stop_button = ctk.CTkButton(control_frame, text="Stop", command=stop_song)
stop_button.grid(row=0, column=3, padx=10)

next_button = ctk.CTkButton(control_frame, text="Next", command=next_song)
next_button.grid(row=0, column=4, padx=10)

volume_label = ctk.CTkLabel(app, text="Volume", font=("Arial", 12))
volume_label.pack()

volume_slider = ctk.CTkSlider(app, from_=0, to=100, command=set_volume)
volume_slider.set(100)  # Set the default volume to 100%
volume_slider.pack(pady=5, fill="x")

# Run the main event loop
app.mainloop()
