/* The game publishes a JSON snapshot after every change. Render the same snapshot
   for native file sharing and PNG download; never rely on a WebGL screenshot. */
(function (root) {
  'use strict';
  const palette = { background: '#2b335f', corridor: '#395c98', node: '#19959c',
    bonus: '#d38441', goal: '#e9c35b', text: '#eeeeee' };

  function renderCard(canvas, state) {
    canvas.width = 900;
    canvas.height = 1120;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = palette.background;
    ctx.fillRect(0, 0, 900, 1120);
    ctx.textAlign = 'center';
    ctx.fillStyle = '#97e8bd';
    ctx.font = '18px sans-serif';
    ctx.fillText('DAILY ROUTE PUZZLE', 450, 56);
    ctx.fillStyle = palette.text;
    ctx.font = 'bold 44px sans-serif';
    ctx.fillText('Three Notes Quest', 450, 114);
    ctx.font = '24px sans-serif';
    ctx.fillText(`MAP ${state.mapId}`, 450, 158);
    ctx.fillStyle = palette.goal;
    ctx.font = 'bold 60px sans-serif';
    ctx.fillText(`SCORE ${state.score}`, 450, 239);
    ctx.fillStyle = palette.text;
    ctx.font = '24px sans-serif';
    ctx.fillText(state.maximum == null ? 'DAILY CHALLENGE' : `BEST POSSIBLE ${state.maximum}`, 450, 282);
    const n = state.board.length;
    const cell = 720 / n;
    const left = 90;
    const top = 320;
    const center = (x, y) => [left + (x + .5) * cell, top + (y + .5) * cell];
    state.board.forEach((row, y) => row.forEach((tile, x) => {
      if (tile !== 'wall') {
        ctx.fillStyle = palette.corridor;
        ctx.fillRect(left + x * cell, top + y * cell, cell, cell);
      }
    }));
    state.board.forEach((row, y) => row.forEach((tile, x) => {
      if (!(x % 2 && y % 2) || tile === 'wall') return;
      const [cx, cy] = center(x, y);
      const special = tile === 'x2' || tile === 'x3';
      ctx.fillStyle = tile === 'goal' ? palette.goal : special ? palette.bonus : palette.node;
      ctx.fillRect(cx - cell * .4, cy - cell * .4, cell * .8, cell * .8);
      ctx.fillStyle = special || tile === 'goal' ? palette.background : palette.text;
      ctx.font = `bold ${Math.floor(cell * .34)}px monospace`;
      ctx.fillText(tile === 'start' ? 'S' : tile === 'goal' ? 'G' : String(tile), cx, cy + cell * .12);
    }));
    const labels = { perfect: 'PERFECT — THEORETICAL MAXIMUM!', clear: 'CLEARED', stuck: 'TRY ANOTHER ROUTE', playing: 'ROUTE IN PROGRESS' };
    ctx.fillStyle = palette.goal;
    ctx.font = 'bold 24px sans-serif';
    ctx.fillText(labels[state.status], 450, 1040);
    ctx.fillStyle = palette.text;
    ctx.font = '20px sans-serif';
    ctx.fillText('#ThreeNotesQuest  ·  threen.netlify.app', 450, 1086);
    return canvas;
  }

  function imageFile(canvas, mapId) {
    const data = atob(canvas.toDataURL('image/png').split(',')[1]);
    const bytes = Uint8Array.from(data, c => c.charCodeAt(0));
    return new File([bytes], `ThreeNotesQuest-${mapId}.png`, { type: 'image/png' });
  }

  root.renderShareCard = renderCard;
  root.pendingGameAction = '';
  let state = null;
  let canvas = null;
  let celebrationTimer = null;
  root.reducedMotion = typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (typeof matchMedia === 'function') {
    matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', event => {
      root.reducedMotion = event.matches;
    });
  }
  root.updateGameState = function (json) {
    state = JSON.parse(json);
    // Only public result data reaches the PNG renderer; route details stay in play.
    const publicState = { mapId: state.mapId, board: state.board, score: state.score,
      maximum: state.maximumRevealed ? state.maximum : null, status: state.status };
    canvas = renderCard(document.createElement('canvas'), publicState);
    const labels = { perfect: '理論最高点でクリア！ PERFECT', clear: 'クリア！ 戻って別の経路も試せます',
      stuck: '行き止まり。「1手戻す」で再挑戦できます', playing: '数字と倍率をつないで高得点を狙おう' };
    document.getElementById('result').textContent = labels[state.status];
    document.getElementById('scoreValue').textContent = String(state.score);
    document.getElementById('maximumValue').textContent = state.maximumRevealed ? String(state.maximum) : '?';
    document.getElementById('maximumButton').disabled = !!state.maximumRevealed;
    document.getElementById('maximumButton').textContent = state.maximumRevealed ? '理論最高点' : '理論最高点を見る';
    const feedback = state.feedback || {action: 'reset', delta: 0, milestone: 0};
    if (feedback.action !== 'sync') {
      document.getElementById('scoreDelta').textContent = feedback.action === 'reset' ? '—' :
        `${feedback.action === 'undo' ? '↶ ' : ''}${feedback.delta > 0 ? '+' : ''}${feedback.delta}`;
    }
    const celebration = document.getElementById('milestoneMessage');
    if (feedback.action === 'undo' || feedback.action === 'reset') {
      clearTimeout(celebrationTimer);
      celebration.textContent = '';
      celebration.removeAttribute('data-tier');
    } else if (feedback.milestone) {
      clearTimeout(celebrationTimer);
      celebration.dataset.tier = String(feedback.milestone);
      celebration.textContent = feedback.milestone === 200 ? '200点到達！すばらしいルート！' : '100点到達！いい調子！';
      celebrationTimer = setTimeout(() => {
        celebration.textContent = '';
        celebration.removeAttribute('data-tier');
      }, 3000);
    }
    const directionLabels = {up: '上へ', down: '下へ', left: '左へ', right: '右へ'};
    Object.entries(directionLabels).forEach(([name, label]) => {
      const button = document.querySelector(`[data-action="${name}"]`);
      const kind = (state.actions || {})[name];
      button.disabled = !kind;
      button.dataset.kind = kind || 'blocked';
      button.setAttribute('aria-label', label + (kind === 'undo' ? '（1手戻す）' : ''));
    });
    document.getElementById('undoButton').disabled = state.moves === 0;
    document.getElementById('shareButton').disabled = false;
  };
  root.setSoundEnabled = function (enabled) {
    const button = document.getElementById('soundButton');
    button.textContent = enabled ? '音 ON' : '音 OFF';
    button.setAttribute('aria-pressed', String(enabled));
  };

  if (typeof document === 'undefined') return;
  document.querySelectorAll('[data-action]').forEach(button => {
    button.addEventListener('click', () => { root.pendingGameAction = button.dataset.action; });
  });
  document.getElementById('shareButton').addEventListener('click', async () => {
    if (!state || !canvas) return;
    const status = document.getElementById('shareStatus');
    const button = document.getElementById('shareButton');
    button.disabled = true;
    try {
      // Build the file synchronously to preserve the tap's user activation on iOS.
      const file = imageFile(canvas, state.mapId);
      if (navigator.canShare && navigator.canShare({ files: [file] })) {
        await navigator.share({ files: [file], title: 'ThreeNotesQuest',
          text: `Score: ${state.score}${state.maximumRevealed ? ` / ${state.maximum}` : ''} MAP ${state.mapId} #ThreeNotesQuest https://threen.netlify.app/` });
        status.textContent = '画像を共有しました';
      } else {
        download(file);
        status.textContent = 'PNG画像を保存しました';
      }
    } catch (error) {
      status.textContent = error.name === 'AbortError' ? '共有をキャンセルしました' : '共有できませんでした。下のリンクから画像を保存できます。';
      if (error.name !== 'AbortError') {
        const link = document.createElement('a');
        link.href = canvas.toDataURL('image/png');
        link.download = `ThreeNotesQuest-${state.mapId}.png`;
        link.textContent = 'PNGを保存';
        status.appendChild(link);
      }
    } finally {
      button.disabled = false;
    }
  });

  function download(file) {
    const url = URL.createObjectURL(file);
    const link = document.createElement('a');
    link.href = url;
    link.download = file.name;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10000);
  }
})(typeof window === 'undefined' ? globalThis : window);
