// Open and close settings menu
document.addEventListener('DOMContentLoaded', function () {
    const settingsMenu = document.getElementById('settings-menu');
    const closeSettingsButton = document.getElementById('close-settings');
    const startSpeechButton = document.getElementById('start-speech');
    const pauseSpeechButton = document.getElementById('pause-speech');
    const stopSpeechButton = document.getElementById('stop-speech');
    const textSizeSlider = document.getElementById('text-size-slider');
    const fontSelector = document.getElementById('font-selector');
    const textToRead = document.getElementById('textToRead');
    const currentSizeLabel = document.getElementById('current-size');
    const voiceSelector = document.getElementById('voice-selector');

    // Function to toggle settings menu visibility
    function toggleSettingsMenu() {
        settingsMenu.style.display = settingsMenu.style.display === 'none' ? 'block' : 'none';
    }

    // Event listeners for opening and closing settings menu
    document.getElementById('settingsButton').addEventListener('click', toggleSettingsMenu);
    closeSettingsButton.addEventListener('click', toggleSettingsMenu);


    
    document.getElementById('settingsButton2').addEventListener('click', toggleSettingsMenu);
    closeSettingsButton.addEventListener('click', toggleSettingsMenu);


    // Adjust text size
    textSizeSlider.addEventListener('input', function () {
        const newSize = `${textSizeSlider.value}px`;
        textToRead.style.fontSize = newSize;
        currentSizeLabel.textContent = textSizeSlider.value;
    });

    // Change font
    fontSelector.addEventListener('change', function () {
        textToRead.style.fontFamily = fontSelector.value;
    });

    // Text-to-speech functionality
    let speechSynthesis = window.speechSynthesis;
    let speechUtterance = new SpeechSynthesisUtterance();

    // Populate voice selector with available voices
    function populateVoiceList() {
        const voices = speechSynthesis.getVoices();
        voiceSelector.innerHTML = '';
        voices.forEach((voice, index) => {
            const option = document.createElement('option');
            option.textContent = `${voice.name} (${voice.lang})`;
            option.value = index;
            voiceSelector.appendChild(option);
        });
    }

    populateVoiceList();
    if (speechSynthesis.onvoiceschanged !== undefined) {
        speechSynthesis.onvoiceschanged = populateVoiceList;
    }

    startSpeechButton.addEventListener('click', function () {
        if (!speechSynthesis.speaking) {
            speechUtterance.text = textToRead.innerText || textToRead.textContent;
            const selectedVoiceIndex = voiceSelector.value;
            speechUtterance.voice = speechSynthesis.getVoices()[selectedVoiceIndex];
            speechSynthesis.speak(speechUtterance);
        } else if (speechSynthesis.paused) {
            speechSynthesis.resume();
        }
    });

    pauseSpeechButton.addEventListener('click', function () {
        if (speechSynthesis.speaking) {
            speechSynthesis.pause();
        }
    });

    stopSpeechButton.addEventListener('click', function () {
        if (speechSynthesis.speaking) {
            speechSynthesis.cancel();
        }
    });
});
