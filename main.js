let player;
let videos = [];

// Load YouTube IFrame API on page load
document.addEventListener('DOMContentLoaded', function() {
    const tag = document.createElement('script');
    tag.src = "https://www.youtube.com/iframe_api";
    const firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

    window.onYouTubeIframeAPIReady = function() {
        player = new YT.Player('youtubePlayer', {
            events: {
                'onReady': onPlayerReady
            }
        });

        loadVideo();
    };

    const playBtn = document.getElementById('playBtn');

    playBtn.addEventListener('click', function() {
        loadVideo();
    });

    // Fetch videos from external JSON with caching
    const CACHE_KEY = 'videoListCache';
    const CACHE_TTL_MS = 60 * 60 * 1000;

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
        fetch('http://127.0.0.1:5500/db.txt')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load video list');
            }
            return response.text();
        })
        .then(text => {
            // Split by lines and filter out empty lines
            const videoIds = text.trim().split('\n').filter(id => id.trim() !== '');

            // Create array of objects with videoID
            videos = videoIds.map(id => ({ videoID: id }));

            saveVideoListToCache(videos);
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
            videos = [];
        });
    }

    function loadVideo() {
        let played = getPlayedVideos();

        // If no videos have been played yet, skip the reset prompt
        if (played.length === 0) {
            const availableVideos = videos;
            const randomVideo = availableVideos[Math.floor(Math.random() * availableVideos.length)];

            const newPlayed = [...played, randomVideo.videoID];
            setPlayedVideos(newPlayed);

            const videoId = randomVideo.videoID;
            const playerUrl = `https://www.youtube.com/embed/${videoId}?autoplay=0&controls=1&modestbranding=1&rel=0`;
            document.getElementById('youtubePlayer').src = playerUrl;

            if (player) {
                player.loadVideoById(videoId);
            }

            updateCounter(availableVideos.length);
            return;
        }

        // If there are played videos, filter to get available ones
        const availableVideos = videos.filter(video => !played.includes(video.videoID));

        // If no videos left, show reset popup
        if (availableVideos.length === 0) {
            if (!confirm("All videos have been viewed, reset history?")) {
                return;
            }
            played = [];
            setPlayedVideos(played);
            availableVideos.push(...videos);
        }

        // Pick a random video from available
        const randomVideo = availableVideos[Math.floor(Math.random() * availableVideos.length)];

        const newPlayed = [...played, randomVideo.videoID];
        setPlayedVideos(newPlayed);

        const videoId = randomVideo.videoID;
        const playerUrl = `https://www.youtube.com/embed/${videoId}?autoplay=0&controls=1&modestbranding=1&rel=0`;
        document.getElementById('youtubePlayer').src = playerUrl;

        if (player) {
            player.loadVideoById(videoId);
        }

        updateCounter(availableVideos.length);
    }

    function onPlayerReady(event) {
        updateCounter(videos.length);
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
