// Get references to elements
const openModalButton = document.getElementById('openModal');
const openModalButton2 = document.getElementById('openModal2');
const modal = document.getElementById('settingsModal');
const closeModalButton = document.getElementById('closeModal');
const slider = document.getElementById('fontSizeSlider');
const textContent = document.querySelector('.content');
const fontSizeValue = document.getElementById('fontSizeValue');
const modalContent = document.getElementById('modalContent');
const voiceSelect = document.getElementById('voiceSelect');

// Function to open the modal
openModalButton.onclick = () => {
    modal.style.display = "block";
};

openModalButton2.onclick = () => {
    modal.style.display = "block";
};

// Function to close the modal
closeModalButton.onclick = () => {
    modal.style.display = "none";
};

// Close the modal if the user clicks outside of it
window.onclick = (event) => {
    if (event.target == modal) {
        modal.style.display = "none";
    }
};

// Add an event listener to the slider to update the font size
slider.addEventListener('input', () => {
    const fontSize = slider.value;
    textContent.style.fontSize = fontSize + 'px';
    fontSizeValue.textContent = fontSize;
});



// Text-to-Speech functionality
if ('speechSynthesis' in window) {
    const synth = window.speechSynthesis;
    let voices = [];

    // Load voices
    const loadVoices = () => {
        voices = synth.getVoices().filter(voice => voice.name.includes('Microsoft') || voice.name.includes('Google'));
        voiceSelect.innerHTML = ''; // Clear existing options
        if (voices.length > 0) {
            voices.forEach(voice => {
                const option = document.createElement('option');
                option.textContent = `${voice.name} (${voice.lang})`;
                option.value = voice.name;
                voiceSelect.appendChild(option);
            });
        } else {
            const noVoiceOption = document.createElement('option');
            noVoiceOption.textContent = 'No voices available';
            noVoiceOption.disabled = true;
            voiceSelect.appendChild(noVoiceOption);
        }
    };

    loadVoices(); // Initial load

    if (typeof synth.onvoiceschanged !== "undefined") {
        synth.onvoiceschanged = loadVoices; // Reload voices when they change
    }

    // Play TTS
    document.getElementById('playTTS').addEventListener('click', () => {
        if (synth.paused) {
            synth.resume();
        } else {
            if (synth.speaking) {
                synth.cancel();
            }
            const textToSpeak = document.getElementById('textToRead').innerText;
            const utterance = new SpeechSynthesisUtterance(textToSpeak);
            const selectedVoice = voices.find(voice => voice.name === voiceSelect.value);
            utterance.voice = selectedVoice || voices[0];
            utterance.rate = 1;
            utterance.pitch = 1;
            utterance.lang = selectedVoice ? selectedVoice.lang : 'en-US';
            utterance.onend = () => {
                console.log('Speech has finished.');
            };
            utterance.onerror = (e) => {
                console.error('An error occurred during speech synthesis:', e);
            };
            synth.speak(utterance);
        }
    });

    // Pause TTS
    document.getElementById('pauseTTS').addEventListener('click', () => {
        if (synth.speaking) {
            synth.pause();
        }
    });

    // Stop TTS
    document.getElementById('stopTTS').addEventListener('click', () => {
        synth.cancel();
    });

} else {
    alert('Sorry, your browser does not support text-to-speech.');
}
