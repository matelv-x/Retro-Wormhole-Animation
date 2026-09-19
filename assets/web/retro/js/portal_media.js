(function () {
  'use strict';

  const API = '/stargate/get/portal_media';
  let lastSignature = '';

  function isVideo(filename) {
    return /\.(?:mp4|webm)$/i.test(filename || '');
  }

  function ensureVideoLayer(ring, type) {
    let layer = ring.querySelector('.portal-' + type + '-video');
    if (layer) return layer.querySelector('video');
    layer = document.createElement('div');
    layer.className = 'portal-media-video portal-' + type + '-video';
    const video = document.createElement('video');
    video.className = 'portal-' + type + '-video-element';
    video.muted = true;
    video.autoplay = true;
    video.loop = true;
    video.playsInline = true;
    video.preload = 'auto';
    layer.appendChild(video);
    ring.insertBefore(layer, ring.firstChild);
    return video;
  }

  function updateImage(image, filename, scale) {
    if (!image) return;
    const source = 'images/' + encodeURIComponent(filename);
    image.setAttribute('href', source);
    image.setAttributeNS('http://www.w3.org/1999/xlink', 'href', source);
    image.setAttribute('x', String(337 - (616 * scale / 2)));
    image.setAttribute('y', String(335 - (616 * scale / 2)));
    image.setAttribute('width', String(616 * scale));
    image.setAttribute('height', String(616 * scale));
    image.setAttribute('preserveAspectRatio', 'xMidYMid slice');
  }

  function updateVideo(video, filename, enabled) {
    if (!video) return;
    if (enabled) {
      const source = 'images/' + encodeURIComponent(filename);
      if (video.getAttribute('src') !== source) {
        video.setAttribute('src', source);
        video.load();
      }
      const attempt = video.play();
      if (attempt) attempt.catch(function () {});
    } else if (video.hasAttribute('src')) {
      video.pause();
      video.removeAttribute('src');
      video.load();
    }
  }

  function apply(config) {
    if (!config || !config.wormhole || !config.blackhole) return;
    const signature = JSON.stringify(config);
    if (signature === lastSignature) return;
    lastSignature = signature;

    const wormhole = config.wormhole;
    const blackhole = config.blackhole;
    const wormholeScale = Math.max(50, Math.min(250, Number(wormhole.scale) || 100)) / 100;
    const blackholeScale = Math.max(50, Math.min(250, Number(blackhole.scale) || 100)) / 100;
    document.documentElement.style.setProperty('--portal-wormhole-scale', String(wormholeScale));
    document.documentElement.style.setProperty('--portal-blackhole-scale', String(blackholeScale));

    document.querySelectorAll('.ring-1').forEach(function (ring) {
      updateImage(ring.querySelector('.wormhole-gif'), wormhole.selected, wormholeScale);
      updateImage(ring.querySelector('.blackhole-gif'), blackhole.selected, blackholeScale);
      updateVideo(ensureVideoLayer(ring, 'wormhole'), wormhole.selected, isVideo(wormhole.selected));
      updateVideo(ensureVideoLayer(ring, 'blackhole'), blackhole.selected, isVideo(blackhole.selected));
    });

    document.body.classList.toggle('portal-wormhole-video-selected', isVideo(wormhole.selected));
    document.body.classList.toggle('portal-blackhole-video-selected', isVideo(blackhole.selected));
  }

  function refresh() {
    fetch(API, {cache: 'no-store'})
      .then(function (response) {
        if (!response.ok) throw new Error('Portal media request failed');
        return response.json();
      })
      .then(apply)
      .catch(function () {});
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', refresh);
  } else {
    refresh();
  }
  window.setInterval(refresh, 3000);
})();
