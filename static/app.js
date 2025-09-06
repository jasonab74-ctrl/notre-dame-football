(function () {
  const playBtn = document.getElementById('fight-song');
  const audio = document.getElementById('audio');
  const refreshBtn = document.getElementById('refresh');

  if (playBtn && audio) {
    playBtn.addEventListener('click', async () => {
      try {
        if (audio.paused) {
          await audio.play();
          playBtn.setAttribute('aria-pressed', 'true');
          playBtn.classList.remove('pill--hollow');
        } else {
          audio.pause();
          playBtn.setAttribute('aria-pressed', 'false');
          playBtn.classList.add('pill--hollow');
        }
      } catch (e) {
        // ignore autoplay issues
      }
    });

    // Stop jumpiness when audio ends
    audio.addEventListener('ended', () => {
      playBtn.setAttribute('aria-pressed', 'false');
      playBtn.classList.add('pill--hollow');
    });
  }

  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => {
      // simple, reliable: full reload (prevents DOM jumps)
      location.replace(location.pathname + '?t=' + Date.now());
    });
  }
})();