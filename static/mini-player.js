// Initialize the miniPlayer object globally right away
window.miniPlayer = {
    // Placeholder methods will be replaced when DOM is ready
    play: function() { console.warn('Player not yet initialized'); },
    pause: function() { console.warn('Player not yet initialized'); },
    next: function() { console.warn('Player not yet initialized'); },
    prev: function() { console.warn('Player not yet initialized'); },
    setVolume: function() { console.warn('Player not yet initialized'); },
    toggle: function() { console.warn('Player not yet initialized'); },
    loadSongs: function() { console.warn('Player not yet initialized'); },
    playSongByIndex: function() { console.warn('Player not yet initialized'); },
    isInitialized: false
};

// Cache for preloaded audio files
const audioCache = new Map();

// Function to preload audio files
function preloadAudio(url) {
    return new Promise((resolve, reject) => {
        // Check if already in cache
        if (audioCache.has(url)) {
            resolve(audioCache.get(url));
            return;
        }

        // Create a new audio element
        const audio = new Audio();
        
        // Set up event listeners
        audio.addEventListener('canplaythrough', () => {
            // Store in cache
            audioCache.set(url, audio);
            resolve(audio);
        }, { once: true });
        
        audio.addEventListener('error', (e) => {
            console.error(`Error preloading audio: ${url}`, e);
            reject(new Error(`Failed to preload audio: ${url}`));
        }, { once: true });
        
        // Set source and start loading
        audio.preload = 'auto';
        audio.src = url;
    });
}

// Function to preload all songs
async function preloadAllSongs(songUrls) {
    console.log('Starting to preload all songs...');
    const preloadPromises = songUrls.map(url => preloadAudio(url));
    
    try {
        await Promise.all(preloadPromises);
        console.log('All songs preloaded successfully');
    } catch (error) {
        console.error('Error preloading songs:', error);
    }
}

// Function to parse M3U8 playlist
async function parseM3U8Playlist(url) {
    try {
        const response = await fetch(url);
        const text = await response.text();
        
        const lines = text.split('\n');
        const songs = [];
        const titles = [];
        let currentTitle = '';
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            if (line.startsWith('#EXTINF:')) {
                // Extract title from EXTINF line
                const titleMatch = line.match(/,(.+)$/);
                if (titleMatch && titleMatch[1]) {
                    currentTitle = titleMatch[1];
                }
            } else if (line && !line.startsWith('#')) {
                // This is a URL line
                songs.push(line);
                titles.push(currentTitle || `Song ${songs.length}`);
                currentTitle = '';
            }
        }
        
        return { songs, titles };
    } catch (error) {
        console.error('Error parsing M3U8 playlist:', error);
        return { songs: [], titles: [] };
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const miniPlayer = document.getElementById('miniPlayer');
    const toggleExpandBtn = document.getElementById('toggleExpand');
    const audioPlayer = document.getElementById('audioPlayer');
    const progressBar = document.getElementById('progressBar');
    const progressContainer = document.getElementById('progressContainer');
    const currentTimeDisplay = document.getElementById('currentTime');
    const durationDisplay = document.getElementById('duration');
    const playBtn = document.getElementById('playBtn');
    const playIcon = document.getElementById('playIcon');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const volumeSlider = document.getElementById('volumeSlider');
    const volumeIcon = document.getElementById('volumeIcon');
    //const nowPlaying = document.getElementById('nowPlaying');
    const shuffleBtn = document.getElementById('shuffleBtn');
    const loopBtn = document.getElementById('loopBtn');
    const closeBtn = document.getElementById('closeBtn');
    const songSelect = document.getElementById('songSelect');

    // Check if all required elements are present
    if (!miniPlayer || !audioPlayer || !progressBar || !progressContainer ||
        !playBtn || !prevBtn || !nextBtn || !shuffleBtn || !loopBtn || !songSelect) {
        console.error('Mini player: Required DOM elements not found');
        return; // Exit initialization if elements are missing
    }

    // Start with the player minimized
    miniPlayer.classList.add('collapsed');
    toggleExpandBtn.innerHTML = '<i class="fas fa-expand"></i>';

    // State management
    let songs = [];
    let songTitles = [];
    let currentSongIndex = -1;
    let isShuffleOn = false;
    let isLoopOn = false;
    let originalSongOrder = [];
    let shuffledSongs = [];
    let originalIndexMap = [];

    // Toggle expand/collapse
    toggleExpandBtn.addEventListener('click', () => {
        miniPlayer.classList.toggle('collapsed');
        toggleExpandBtn.innerHTML = miniPlayer.classList.contains('collapsed')
            ? '<i class="fas fa-expand"></i>'
            : '<i class="fas fa-compress"></i>';
    });

    // Close mini player
    closeBtn.addEventListener('click', () => {
        audioPlayer.pause();
        miniPlayer.style.display = 'none';
    });

    // Song selection
    songSelect.addEventListener('change', (e) => {
        const selectedUrl = e.target.value;
        const selectedIndex = songs.indexOf(selectedUrl);
        if (selectedIndex !== -1) {
            playSong(selectedIndex);
        }
    });

    // Utility Functions
    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

    function updateNowPlaying(index) {
        if (index >= 0 && index < songTitles.length) {
            //nowPlaying.textContent = songTitles[index];
            // Also update the dropdown selection
            if (songSelect) {
                songSelect.value = songs[index];
            }
        } else {
            //nowPlaying.textContent = 'Select a song to play';
        }
    }

    // Fixed shuffle functionality
    function shuffleArray(array) {
        const indices = Array.from(array.keys());
        const shuffled = [];
        const indexMap = [];

        // Create shuffled indices
        while (indices.length > 0) {
            const randomIndex = Math.floor(Math.random() * indices.length);
            const originalIndex = indices.splice(randomIndex, 1)[0];
            shuffled.push(array[originalIndex]);
            indexMap.push(originalIndex);
        }

        originalIndexMap = indexMap;
        return shuffled;
    }

    function toggleShuffle() {
        isShuffleOn = !isShuffleOn;
        shuffleBtn.classList.toggle('active');

        if (isShuffleOn) {
            // Save current song
            const currentSong = currentSongIndex !== -1 ? songs[currentSongIndex] : null;

            // Shuffle all songs
            shuffledSongs = shuffleArray([...songs]);

            // Make sure current song is first in the shuffled list if playing
            if (currentSong && !audioPlayer.paused) {
                const currentIndex = shuffledSongs.indexOf(currentSong);
                if (currentIndex !== -1) {
                    shuffledSongs.splice(currentIndex, 1);
                    shuffledSongs.unshift(currentSong);
                    // Update the index map
                    const originalIndex = originalIndexMap.splice(currentIndex, 1)[0];
                    originalIndexMap.unshift(originalIndex);
                }
            }

            songs = shuffledSongs;
            if (currentSong && !audioPlayer.paused) {
                currentSongIndex = 0;
            } else {
                currentSongIndex = -1; // Reset selection when shuffling without playback
            }
        } else {
            // Save current song
            const currentSong = currentSongIndex !== -1 ? songs[currentSongIndex] : null;

            // Restore original order
            songs = [...originalSongOrder];

            // Find the index of current song in original order
            if (currentSong) {
                currentSongIndex = originalSongOrder.indexOf(currentSong);
                if (currentSongIndex === -1) currentSongIndex = 0;
            } else {
                currentSongIndex = -1;
            }
        }
    }

    // Loop functionality
    function toggleLoop() {
        isLoopOn = !isLoopOn;
        loopBtn.classList.toggle('active');
        audioPlayer.loop = isLoopOn;
    }

    // Playback functions
    function playSong(index) {
        if (index < 0 || index >= songs.length) return;

        const songPath = songs[index];
        currentSongIndex = index;

        // Calculate the title index based on whether we're in shuffle mode
        let titleIndex;
        if (isShuffleOn) {
            titleIndex = originalIndexMap[index];
        } else {
            titleIndex = index;
        }

        // Update UI
        updateNowPlaying(titleIndex);

        // Check if the song is in cache
        if (audioCache.has(songPath)) {
            // Use cached audio
            const cachedAudio = audioCache.get(songPath);
            audioPlayer.src = cachedAudio.src;
            audioPlayer.load(); // Ensure the audio is loaded
            
            // Copy properties from cached audio
            audioPlayer.currentTime = 0;
            
            // Play the audio
            audioPlayer.play()
                .then(() => {
                    playIcon.classList.remove('fa-play');
                    playIcon.classList.add('fa-pause');
                })
                .catch(error => {
                    console.error('Playback failed:', error);
                });
        } else {
            // Fallback to direct loading if not in cache
            audioPlayer.src = songPath;
            audioPlayer.play()
                .then(() => {
                    playIcon.classList.remove('fa-play');
                    playIcon.classList.add('fa-pause');
                })
                .catch(error => {
                    console.error('Playback failed:', error);
                });
        }
    }

    function togglePlay() {
        if (audioPlayer.paused) {
            if (audioPlayer.src) {
                audioPlayer.play()
                    .then(() => {
                        playIcon.classList.remove('fa-play');
                        playIcon.classList.add('fa-pause');
                    });
            } else if (songs.length > 0) {
                playSong(0);
            }
        } else {
            audioPlayer.pause();
            playIcon.classList.remove('fa-pause');
            playIcon.classList.add('fa-play');
        }
    }

    function playPrevious() {
        if (songs.length === 0) return;

        if (audioPlayer.currentTime > 3) {
            // If current time is more than 3 seconds, restart the current song
            audioPlayer.currentTime = 0;
            return;
        }

        const newIndex = currentSongIndex <= 0 ? songs.length - 1 : currentSongIndex - 1;
        playSong(newIndex);
    }

    function playNext() {
        if (songs.length === 0) return;

        if (isLoopOn) {
            // If loop is on, replay the current song
            audioPlayer.currentTime = 0;
            audioPlayer.play();
            return;
        }

        const newIndex = (currentSongIndex + 1) % songs.length;
        playSong(newIndex);
    }

    // Player controls event listeners
    playBtn.addEventListener('click', togglePlay);
    prevBtn.addEventListener('click', playPrevious);
    nextBtn.addEventListener('click', playNext);
    shuffleBtn.addEventListener('click', toggleShuffle);
    loopBtn.addEventListener('click', toggleLoop);

    // Handle song ending
    audioPlayer.addEventListener('ended', () => {
        if (isLoopOn) {
            audioPlayer.play();
        } else {
            playNext();
        }
    });

    // Progress bar update
    audioPlayer.addEventListener('timeupdate', () => {
        if (isNaN(audioPlayer.duration)) return;
        const progress = (audioPlayer.currentTime / audioPlayer.duration) * 100;
        progressBar.style.width = `${progress}%`;
        currentTimeDisplay.textContent = formatTime(audioPlayer.currentTime);
    });

    audioPlayer.addEventListener('loadedmetadata', () => {
        durationDisplay.textContent = formatTime(audioPlayer.duration);
    });

    // Volume control
    volumeSlider.addEventListener('input', (e) => {
        const volume = e.target.value / 100;
        audioPlayer.volume = volume;
        updateVolumeIcon(volume);
    });

    function updateVolumeIcon(volume) {
        volumeIcon.className = 'fas';
        if (volume === 0) {
            volumeIcon.classList.add('fa-volume-mute');
        } else if (volume < 0.5) {
            volumeIcon.classList.add('fa-volume-down');
        } else {
            volumeIcon.classList.add('fa-volume-up');
        }
    }

    // Progress bar interaction
    let isProgressBarDragging = false;

    progressContainer.addEventListener('mousedown', startDragging);
    progressContainer.addEventListener('touchstart', startDragging);

    document.addEventListener('mousemove', updateDragging);
    document.addEventListener('touchmove', updateDragging);

    document.addEventListener('mouseup', stopDragging);
    document.addEventListener('touchend', stopDragging);

    function startDragging(e) {
        isProgressBarDragging = true;
        updateProgress(e);
    }

    function updateDragging(e) {
        if (!isProgressBarDragging) return;
        updateProgress(e);
        e.preventDefault();
    }

    function stopDragging() {
        isProgressBarDragging = false;
    }

    function updateProgress(e) {
        const rect = progressContainer.getBoundingClientRect();
        const clientX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
        let clickPosition = (clientX - rect.left) / rect.width;
        clickPosition = Math.max(0, Math.min(1, clickPosition));

        if (audioPlayer.duration) {
            // If we're clicking on the progress bar and a song is already loaded
            if (audioPlayer.src) {
                // If we're clicking on the very end of the progress bar (last 5%)
                if (clickPosition > 0.95) {
                    // Play the next song
                    playNext();
                } 
                // If we're clicking on the very beginning of the progress bar (first 5%)
                else if (clickPosition < 0.05) {
                    // Play the previous song
                    playPrevious();
                } 
                // Otherwise, seek within the current song
                else {
                    audioPlayer.currentTime = clickPosition * audioPlayer.duration;
                }
            } 
            // If no song is loaded yet, load the first song
            else if (songs.length > 0) {
                playSong(0);
            }
        }
    }

    // Update the global miniPlayer object with the actual functions
    window.miniPlayer = {
        play: () => {
            if (audioPlayer.paused && songs.length > 0) {
                if (!audioPlayer.src) {
                    playSong(0);
                } else {
                    togglePlay();
                }
            }
        },
        pause: () => {
            if (!audioPlayer.paused) {
                togglePlay();
            }
        },
        next: playNext,
        prev: playPrevious,
        setVolume: (level) => {
            const vol = Math.max(0, Math.min(1, level));
            audioPlayer.volume = vol;
            volumeSlider.value = vol * 100;
            updateVolumeIcon(vol);
        },
        toggle: () => {
            miniPlayer.classList.toggle('collapsed');
            toggleExpandBtn.innerHTML = miniPlayer.classList.contains('collapsed')
                ? '<i class="fas fa-expand"></i>'
                : '<i class="fas fa-compress"></i>';
        },
        loadSongs: async (playlistUrl = '/static/music/playlist.m3u8') => {
            try {
                // Parse the M3U8 playlist
                const { songs: songArray, titles: titleArray } = await parseM3U8Playlist(playlistUrl);
                
                if (!Array.isArray(songArray) || songArray.length === 0) {
                    console.error('Mini player: Invalid song array from playlist');
                    return;
                }

                songs = songArray;
                originalSongOrder = [...songs];

                // Handle song titles
                if (Array.isArray(titleArray) && titleArray.length === songArray.length) {
                    songTitles = titleArray;
                } else {
                    // Generate titles from song paths if not provided
                    songTitles = songArray.map(path => {
                        try {
                            // Extract filename from path without extension
                            return path.split('/').pop().replace(/\.[^/.]+$/, "");
                        } catch (e) {
                            return "Unknown Song";
                        }
                    });
                }

                // Populate song select dropdown
                if (songSelect) {
                    // Clear existing options except the first one
                    while (songSelect.options.length > 1) {
                        songSelect.remove(1);
                    }

                    // Add new options
                    songArray.forEach((path, index) => {
                        const option = document.createElement('option');
                        option.value = path;
                        option.textContent = songTitles[index];
                        songSelect.appendChild(option);
                    });
                }

                currentSongIndex = -1;
                updateNowPlaying(-1);
                
                // Preload all songs into cache
                preloadAllSongs(songArray);
                
                console.log(`Loaded ${songArray.length} songs from playlist`);
            } catch (error) {
                console.error('Error loading playlist:', error);
            }
        },
        playSongByIndex: (index) => {
            if (index >= 0 && index < songs.length) {
                playSong(index);
            }
        },
        isInitialized: true
    };

    console.log('Mini player initialized successfully');
});
