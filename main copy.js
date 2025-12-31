let player;
let videos = []; // Will be populated later

// Load YouTube IFrame API immediately on page load
document.addEventListener('DOMContentLoaded', function() {
    const tag = document.createElement('script');
    tag.src = "https://www.youtube.com/iframe_api";
    const firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

    // Initialize player once API is ready
    window.onYouTubeIframeAPIReady = function() {
        player = new YT.Player('youtubePlayer', {
            events: {
                'onReady': onPlayerReady
            }
        });

        // Load a random video on page load
        loadVideo();
    };

    // Get DOM elements
    const playBtn = document.getElementById('playBtn');
    const counterElement = document.getElementById('counterValue');

    // Button click handler
    playBtn.addEventListener('click', function() {
        loadVideo();
    });

    // Fetch videos from external JSON with caching
    const CACHE_KEY = 'videoListCache';
    const CACHE_TTL_MS = 60 * 60 * 1000; // 1 hour

    function getVideoListFromCache() {
        const cache = sessionStorage.getItem(CACHE_KEY);
        if (!cache) return null;

        const cacheData = JSON.parse(cache);
        const now = Date.now();
        if (now - cacheData.timestamp > CACHE_TTL_MS) {
            localStorage.removeItem(CACHE_KEY);
            return null;
        }
        return cacheData.videos;
    }

    function saveVideoListToCache(videos) {
        const cacheData = {
            videos: videos,
            timestamp: Date.now()
        };
        sessionStorage.setItem(CACHE_KEY, JSON.stringify(cacheData));
    }

    // Try to get from cache first
    const cachedVideos = getVideoListFromCache();
    if (cachedVideos) {
        videos = cachedVideos;
        // Initialize player and load video if ready
        if (player) {
            loadVideo();
        } else {
            window.onYouTubeIframeAPIReady = function() {
                loadVideo();
            };
        }
    } else {
        // Fetch from server
        fetch('http://127.0.0.1:5500/db.json')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to load video list');
                }
                return response.json();
            })
            .then(data => {
                videos = data;
                saveVideoListToCache(data); // Cache it
                // Initialize player and load video if ready
                if (player) {
                    loadVideo();
                } else {
                    window.onYouTubeIframeAPIReady = function() {
                        loadVideo();
                    };
                }
            })
            .catch(error => {
                console.error('Error loading video list:', error);
                // Fallback: use empty array or show error
                videos = [];
            });
    }

    // Load video function (unchanged, but now uses `videos` array)
    function loadVideo() {
        let played = getPlayedVideos();

        const availableVideos = videos.filter(video => !played.includes(video.videoID));

        if (availableVideos.length === 0) {
            if (!confirm("All videos have been viewed, reset history ?")) {
                return;
            }
            played = [];
            setPlayedVideos(played);
            availableVideos.push(...videos);
        }

        const randomVideo = availableVideos[Math.floor(Math.random() * availableVideos.length)];

        const newPlayed = [...played, randomVideo.videoID];
        setPlayedVideos(newPlayed);

        const videoId = randomVideo.videoID;
        const playerUrl = `https://www.youtube.com/embed/${videoId}?autoplay=0&controls=1&modestbranding=1&rel=0`;
        document.getElementById('youtubePlayer').src = playerUrl;

        if (player) {
            player.loadVideoById(videoId);
        }

        // 📌 Update counter
        updateCounter(availableVideos.length);
    }

    function onPlayerReady(event) {
        // Player is ready — you can add extra logic here if needed
        updateCounter(videos.length); // Optional: show total at start
    }

    function updateCounter(remaining) {
        const counterElement = document.getElementById('counterValue');
        counterElement.textContent = remaining;
    }

    function getPlayedVideos() {
        const cookie = document.cookie
            .split(';')
            .find(row => row.trim().startsWith('playedVideos='));

        if (!cookie) {
            return [];
        }

        try {
            return JSON.parse(cookie.split('=')[1]);
        } catch (e) {
            return [];
        }
    }

    function setPlayedVideos(played) {
        document.cookie = `playedVideos=${JSON.stringify(played)}; path=/; max-age=31536000; SameSite=Strict; Secure`;
    }
});
