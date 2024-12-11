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
    const opacitySlider = document.getElementById('opacity-slider');
    const currentOpacityLabel = document.getElementById('current-opacity');

    // Load settings from localStorage
    function loadSettings() {
        const textSize = localStorage.getItem('textSize');
        const font = localStorage.getItem('font');
        const opacity = localStorage.getItem('opacity');

        if (textSize) {
            textToRead.style.fontSize = `${textSize}px`;
            textSizeSlider.value = textSize;
            currentSizeLabel.textContent = textSize;
        }
        if (font) {
            textToRead.style.fontFamily = font;
            fontSelector.value = font;
        }
        if (opacity) {
            textToRead.style.opacity = opacity;
            opacitySlider.value = opacity;
            currentOpacityLabel.textContent = opacity;
        }
    }

    // Save settings to localStorage
    function saveSettings() {
        localStorage.setItem('textSize', textSizeSlider.value);
        localStorage.setItem('font', fontSelector.value);
        localStorage.setItem('opacity', opacitySlider.value);
    }

    window.onload = function() {
        var features = document.querySelectorAll('.feature');
        var maxHeight = 0;
        features.forEach(function(feature) {
            if (feature.offsetHeight > maxHeight) {
                maxHeight = feature.offsetHeight;
            }
        });
        features.forEach(function(feature) {
            feature.style.minHeight = maxHeight + 'px';
        });
    };

    // Function to toggle settings menu visibility
    function toggleSettingsMenu() {
        if (settingsMenu.style.display === 'block') {
            settingsMenu.style.display = 'none';
            document.removeEventListener('click', handleOutsideClick, true);
        } else {
            settingsMenu.style.display = 'block';
            // Delay adding the event listener to avoid the immediate click event that triggers the menu to open
            setTimeout(() => {
                document.addEventListener('click', handleOutsideClick, true);
            }, 0);
        }
    }

    function handleOutsideClick(event) {
        if (!settingsMenu.contains(event.target) && event.target.id !== 'settingsButton' && event.target.id !== 'settingsButton2') {
            toggleSettingsMenu();
        }
    }

    // Event listeners for opening and closing settings menu
    document.getElementById('settingsButton').addEventListener('click', toggleSettingsMenu);
    closeSettingsButton.addEventListener('click', toggleSettingsMenu);

    document.getElementById('settingsButton2').addEventListener('click', toggleSettingsMenu);
    closeSettingsButton.addEventListener('click', toggleSettingsMenu);

    // Adjust text size and save
    textSizeSlider.addEventListener('input', function () {
        const newSize = `${textSizeSlider.value}px`;
        textToRead.style.fontSize = newSize;
        currentSizeLabel.textContent = textSizeSlider.value;
        saveSettings();
    });

    // Change font and save
    fontSelector.addEventListener('change', function () {
        textToRead.style.fontFamily = fontSelector.value;
        saveSettings();
    });

    // Adjust text opacity and save
    opacitySlider.addEventListener('input', function () {
        const newOpacity = opacitySlider.value;
        textToRead.style.opacity = newOpacity;
        currentOpacityLabel.textContent = newOpacity;
        saveSettings();
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

    // Load settings on page load
    loadSettings();
});

function showPromptlightNovelPubDotVip() {
    const novelLink = prompt("Enter the link for your novel:", "Link");
    if (novelLink) {
        alert("Processing...");
        fetch('/lightNovelPubDotVip', { // Bit to change
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ novelLink: novelLink })
        })
    } else {
        alert("Prompt cancelled.");
    }
}

function showPromptreaderNovel() {
    const novelLink = prompt("Enter the link for your novel:", "Link");
    if (novelLink) {
        alert("Processing...");
        fetch('/readerNovel', { // Bit to change
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ novelLink: novelLink })
        })
    } else {
        alert("Prompt cancelled.");
    }
}

function showPromptreadWebNovel() {
    const novelLink = prompt("Enter the link for your novel:", "Link");
    if (novelLink) {
        alert("Processing...");
        fetch('/readWebNovel', { // Bit to change
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ novelLink: novelLink })
        })
    } else {
        alert("Prompt cancelled.");
    }
}

function showPromptwebNovelDotCom() {
    const novelLink = prompt("Enter the link for your novel:", "Link");
    if (novelLink) {
        alert("Processing...");
        fetch('/webNovelDotCom', { // Bit to change
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ novelLink: novelLink })
        })
    } else {
        alert("Prompt cancelled.");
    }
}


document.addEventListener('DOMContentLoaded', () => {
    const button = document.getElementById('randomDirButton');

    button.addEventListener('click', () => {
        fetch('/random_directory')
            .then(response => response.json())
            .then(data => {
                console.log(data.directory);
                if (data.directory !== 'No directories found') {
                    const newHref = `/novels_chapters?n=${data.directory}`;
                    window.location.href = newHref;
                } else {
                    alert('No directories found');
                }
            })
            .catch(error => console.error('Error:', error));
    });
});


document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const nav = document.querySelector('.nav');
    
    mobileMenuButton.addEventListener('click', function() {
        nav.classList.toggle('active');
        
        // Toggle aria-expanded
        const isExpanded = nav.classList.contains('active');
        this.setAttribute('aria-expanded', isExpanded);
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
        const isClickInsideNav = nav.contains(event.target);
        const isClickOnButton = mobileMenuButton.contains(event.target);
        
        if (!isClickInsideNav && !isClickOnButton && nav.classList.contains('active')) {
            nav.classList.remove('active');
            mobileMenuButton.setAttribute('aria-expanded', 'false');
        }
    });

    // Close menu when window is resized above mobile breakpoint
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768 && nav.classList.contains('active')) {
            nav.classList.remove('active');
            mobileMenuButton.setAttribute('aria-expanded', 'false');
        }
    });
});



function showReplyForm(commentId) {
    // Create reply form if it doesn't exist
    let replyForm = document.getElementById(`reply-form-${commentId}`);
    if (!replyForm) {
        const comment = document.querySelector(`[data-comment-id="${commentId}"]`);
        replyForm = document.createElement('div');
        replyForm.id = `reply-form-${commentId}`;
        replyForm.className = 'reply-form';
        replyForm.innerHTML = `
            <input type="text" id="reply-username-${commentId}" placeholder="Your username">
            <textarea id="reply-content-${commentId}" placeholder="Write your reply..."></textarea>
            <div class="reply-actions">
                <button onclick="submitReply(${commentId})">Reply</button>
                <button onclick="hideReplyForm(${commentId})">Cancel</button>
            </div>
        `;
        comment.appendChild(replyForm);
    }
    replyForm.style.display = 'block';
}

function hideReplyForm(commentId) {
    const replyForm = document.getElementById(`reply-form-${commentId}`);
    if (replyForm) {
        replyForm.style.display = 'none';
    }
}

function submitReply(parentId) {
    const username = document.getElementById(`reply-username-${parentId}`).value;
    const content = document.getElementById(`reply-content-${parentId}`).value;
    const novelName = document.getElementById('novel-title').textContent;
    const chapterNumber = document.getElementById('chapter-number').textContent;
    
    if (!username || !content) {
        alert('Please fill in all fields');
        return;
    }
    
    fetch('/api/comments', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            novel_name: novelName,
            chapter_number: chapterNumber,
            username: username,
            content: content,
            parent_id: parentId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            hideReplyForm(parentId);
            loadComments(); // Reload all comments to show the new reply
        } else {
            alert('Error posting reply');
        }
    });
}

// Load comments when page loads
document.addEventListener('DOMContentLoaded', loadComments);

function submitComment() {
    // Get the input values
    const username = document.getElementById('comment-username').value;
    const content = document.getElementById('comment-content').value;
    const novelName = document.getElementById('novel-title').textContent;
    const chapterNumber = document.getElementById('chapter-number').textContent;
    
    // Validate inputs
    if (!username || !content) {
        alert('Please fill in both username and comment');
        return;
    }
    
    // Send the comment to the server
    fetch('/api/comments', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            novel_name: novelName,
            chapter_number: chapterNumber,
            username: username,
            content: content
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Clear the form
            document.getElementById('comment-username').value = '';
            document.getElementById('comment-content').value = '';
            
            // Reload comments to show the new one
            loadComments();
        } else {
            alert('Error posting comment: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error posting comment. Please try again.');
    });
}

function loadComments() {
    const novelName = document.getElementById('novel-title').textContent;
    const chapterNumber = document.getElementById('chapter-number').textContent;
    
    fetch(`/api/comments/${encodeURIComponent(novelName)}/${chapterNumber}`)
        .then(response => response.json())
        .then(comments => {
            const container = document.getElementById('comments-container');
            container.innerHTML = comments.map(comment => `
                <div class="comment ${comment.pinned ? 'pinned' : ''}" data-comment-id="${comment.id}">
                    ${comment.pinned ? '<div class="pin-indicator">📌 Pinned</div>' : ''}
                    <div class="comment-header">
                        <span class="username">${comment.username}</span>
                        <span class="timestamp">${comment.timestamp}</span>
                    </div>
                    <div class="comment-content">${comment.content}</div>
                    ${comment.replies.length > 0 ? `
                        <div class="replies">
                            ${comment.replies.map(reply => `
                                <div class="comment" data-comment-id="${reply.id}">
                                    <div class="comment-header">
                                        <span class="username">${reply.username}</span>
                                        <span class="timestamp">${reply.timestamp}</span>
                                    </div>
                                    <div class="comment-content">${reply.content}</div>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                    <button onclick="showReplyForm(${comment.id})" class="reply-button">Reply</button>
                </div>
            `).join('');
        })
        .catch(error => {
            console.error('Error loading comments:', error);
            document.getElementById('comments-container').innerHTML = 
                '<p class="error">Error loading comments. Please refresh the page.</p>';
        });
}

function togglePin(commentId) {
    // Add CSRF token if you're using Flask's CSRF protection
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    fetch(`/api/comments/${commentId}/toggle_pin`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        credentials: 'same-origin' // This is important for cookies/session
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Reload comments to show updated pin status
            loadComments();
        } else {
            alert('Error toggling pin status: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error toggling pin status. Please try again.');
    });
}

