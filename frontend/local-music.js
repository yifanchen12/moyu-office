(() => {
  const style = document.createElement('style');
  style.textContent = `
    #room-music{position:absolute;z-index:1200;transform-origin:top left;display:flex;align-items:center;gap:8px;
      height:32px;padding:4px 9px;width:260px;border:2px solid #906244;background:#342923ed;color:#fff0c8;
      box-shadow:0 3px 0 #1e1816;pointer-events:none;font:12px/20px "Microsoft YaHei",sans-serif}
    #room-music .music-window{overflow:hidden;flex:1;min-width:0;white-space:nowrap}
    #room-music .music-track{display:flex;width:max-content;animation:room-song 22s linear infinite}
    #room-music .music-track span{padding-right:34px;min-width:240px}
    #room-music[data-available=false] .music-track{animation:none;color:#c6b69b}
    @keyframes room-song{to{transform:translateX(-50%)}}
    @media(prefers-reduced-motion:reduce){#room-music .music-track{animation:none}}
  `;
  document.head.append(style);
  const bar = document.createElement('div');
  bar.id = 'room-music';
  bar.dataset.available = 'false';
  bar.innerHTML = '<span class="music-symbol" aria-hidden="true">♫</span><div class="music-window"><div class="music-track"><span></span><span aria-hidden="true"></span></div></div>';
  bar.setAttribute('role', 'status');
  const container = document.querySelector('#game-container');
  container.style.position = 'relative';
  container.append(bar);
  function position() {
    const canvas = container.querySelector('canvas');
    if (!canvas) {bar.style.visibility='hidden';return}
    const rect = canvas.getBoundingClientRect(), parent = container.getBoundingClientRect();
    const scale = rect.width / 1280;
    bar.style.visibility = 'visible';
    bar.style.left = (rect.left-parent.left+535*scale)+'px';
    bar.style.top = (rect.top-parent.top+100*scale)+'px';
    bar.style.transform = 'scale('+scale+')';
  }
  let previous = '';
  function show(info) {
    const available = !!(info && info.available && info.title);
    const text = available ? info.title+(info.artist?' · '+info.artist:'') : '网易云音乐 · 等待歌曲';
    if (text !== previous) {
      bar.querySelectorAll('.music-track span').forEach(span => span.textContent=text);
      previous=text;
    }
    bar.dataset.available=String(available);
    bar.setAttribute('aria-label', text);
    bar.title=available ? info.source : '尚未读到网易云歌曲信息';
  }
  async function refresh() {
    try {
      const response=await fetch('/local/status',{cache:'no-store'});
      if (!response.ok) throw Error();
      show((await response.json()).music);
    } catch {show(null)}
  }
  show(null);refresh();position();
  setInterval(refresh,5000);
  const resize=new ResizeObserver(position);resize.observe(container);
  new MutationObserver(position).observe(container,{childList:true});
  window.addEventListener('resize',position);
})();
