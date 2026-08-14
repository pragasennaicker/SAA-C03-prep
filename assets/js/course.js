const TOTAL = 17;
const PROGRESS_KEY = 'saaC03VisualProgress';
const THEME_KEY = 'saaC03Theme';

function getDone() {
  try {
    const raw = JSON.parse(localStorage.getItem(PROGRESS_KEY) || '[]');
    return Array.isArray(raw) ? raw.map(Number).filter((n) => n >= 1 && n <= TOTAL) : [];
  } catch (e) {
    return [];
  }
}

function setDone(done) {
  localStorage.setItem(PROGRESS_KEY, JSON.stringify([...new Set(done)].sort((a, b) => a - b)));
}

function updateProgressUI() {
  const done = getDone();
  const bar = document.getElementById('progBar');
  const text = document.getElementById('progText');
  if (bar) bar.style.width = (done.length / TOTAL * 100) + '%';
  if (text) text.textContent = done.length + ' / ' + TOTAL + ' complete';
  for (let i = 1; i <= TOTAL; i++) {
    const dot = document.getElementById('dot-' + i);
    if (dot) dot.classList.toggle('done', done.includes(i));
  }
  document.querySelectorAll('.complete-check').forEach((el) => {
    el.checked = done.includes(Number(el.dataset.lesson));
  });
}

function saveProgressFromCheckbox(el) {
  const lesson = Number(el.dataset.lesson);
  let done = getDone();
  if (el.checked) {
    if (!done.includes(lesson)) done.push(lesson);
  } else {
    done = done.filter((n) => n !== lesson);
  }
  setDone(done);
  updateProgressUI();
}

function resetProgress() {
  if (confirm('Reset all course progress?')) {
    localStorage.removeItem(PROGRESS_KEY);
    updateProgressUI();
  }
}

function filterLessons() {
  const input = document.getElementById('search');
  if (!input) return;
  const q = input.value.toLowerCase().trim();
  document.querySelectorAll('.lesson-card').forEach((c) => {
    c.classList.toggle('hidden', Boolean(q) && !(c.dataset.search || '').includes(q));
  });
}

function showScenario(lesson, i, btn) {
  const section = btn.closest('.lesson-section');
  section.querySelectorAll('.scenario-tab').forEach((x) => x.classList.remove('active'));
  btn.classList.add('active');
  section.querySelectorAll('.scenario-panel').forEach((x) => x.classList.remove('active'));
  const panel = document.getElementById('sc-' + lesson + '-' + i);
  if (panel) panel.classList.add('active');
}

function answer(el, correct, id) {
  const card = el.closest('.quiz-card');
  card.querySelectorAll('.option').forEach((x) => { x.disabled = true; });
  el.classList.add(correct ? 'correct' : 'wrong');
  if (!correct) {
    card.querySelectorAll('.option').forEach((x) => {
      if ((x.getAttribute('onclick') || '').includes(',true,')) x.classList.add('correct');
    });
  }
  const fb = document.getElementById(id);
  if (fb) fb.style.display = 'block';
}

function systemTheme() {
  try {
    return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  } catch (e) {
    return 'dark';
  }
}

function getTheme() {
  const saved = localStorage.getItem(THEME_KEY);
  if (saved === 'light' || saved === 'dark') return saved;
  return systemTheme();
}

function applyTheme(theme) {
  const next = theme === 'light' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem(THEME_KEY, next);
  const btn = document.getElementById('themeToggle');
  if (!btn) return;
  const isLight = next === 'light';
  btn.setAttribute('aria-pressed', String(isLight));
  btn.setAttribute('aria-label', isLight ? 'Switch to dark colour scheme' : 'Switch to light colour scheme');
  btn.title = isLight ? 'Switch to dark' : 'Switch to light';
  btn.innerHTML = isLight
    ? '<span class="theme-icon" aria-hidden="true">☾</span><span>Dark</span>'
    : '<span class="theme-icon" aria-hidden="true">☀</span><span>Light</span>';
}

function toggleTheme() {
  applyTheme(getTheme() === 'light' ? 'dark' : 'light');
}

function wireThemeToggle() {
  const btn = document.getElementById('themeToggle');
  if (!btn || btn.dataset.wired === '1') return;
  btn.dataset.wired = '1';
  btn.addEventListener('click', toggleTheme);
}

function wireKeywords() {
  const root = document.querySelector('.keywords');
  if (!root || root.dataset.wired === '1') return;
  root.dataset.wired = '1';
  const panel = root.querySelector('.keyword-def');
  const chips = [...root.querySelectorAll('.keyword-chip')];
  if (!panel || !chips.length) return;

  function closeAll() {
    chips.forEach((c) => c.setAttribute('aria-expanded', 'false'));
    panel.hidden = true;
    panel.textContent = '';
  }

  function openChip(chip) {
    chips.forEach((c) => c.setAttribute('aria-expanded', String(c === chip)));
    panel.textContent = chip.getAttribute('data-def') || '';
    panel.hidden = false;
  }

  chips.forEach((chip) => {
    chip.addEventListener('click', (e) => {
      e.stopPropagation();
      if (chip.getAttribute('aria-expanded') === 'true') closeAll();
      else openChip(chip);
    });
  });

  document.addEventListener('click', (e) => {
    if (!root.contains(e.target)) closeAll();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeAll();
  });
}

function wireArchBuild() {
  document.querySelectorAll('[data-arch-build]').forEach((root) => {
    if (root.dataset.wired === '1') return;
    root.dataset.wired = '1';
    const buttons = [...root.querySelectorAll('[data-arch-layer]')];
    const layers = [...root.querySelectorAll('.arch-layer')];
    const caption = root.querySelector('[data-arch-caption]');
    const empty = root.querySelector('[data-arch-empty]');
    const captions = {};
    root.querySelectorAll('[data-arch-copy]').forEach((el) => {
      captions[el.getAttribute('data-arch-copy')] = el.innerHTML;
    });
    const needs = {};
    buttons.forEach((btn) => {
      needs[btn.dataset.archLayer] = (btn.getAttribute('data-arch-needs') || '')
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean);
    });
    const names = buttons.map((b) => b.dataset.archLayer);
    const dependents = {};
    names.forEach((name) => { dependents[name] = []; });
    names.forEach((name) => {
      (needs[name] || []).forEach((req) => {
        if (dependents[req]) dependents[req].push(name);
      });
    });

    const active = new Set();

    function requiredFor(name, seen = new Set()) {
      if (seen.has(name)) return seen;
      seen.add(name);
      (needs[name] || []).forEach((req) => requiredFor(req, seen));
      return seen;
    }

    function removeWithDependents(name, seen = new Set()) {
      if (seen.has(name)) return seen;
      seen.add(name);
      (dependents[name] || []).forEach((dep) => removeWithDependents(dep, seen));
      return seen;
    }

    function render(focus) {
      buttons.forEach((btn) => {
        const on = active.has(btn.dataset.archLayer);
        btn.classList.toggle('active', on);
        btn.setAttribute('aria-pressed', String(on));
      });
      layers.forEach((g) => {
        const required = (g.getAttribute('data-arch-need') || '')
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean);
        const on = required.length > 0 && required.every((name) => active.has(name));
        g.classList.toggle('is-on', on);
      });
      if (empty) empty.hidden = active.size > 0;
      if (caption) {
        if (focus && active.has(focus) && captions[focus]) {
          caption.innerHTML = captions[focus];
        } else if (active.size === 0) {
          caption.innerHTML = '<p class="arch-build-empty">Click a chip to add that piece to the drawing. Click it again to remove it and anything that depends on it.</p>';
        }
      }
    }

    buttons.forEach((btn) => {
      btn.addEventListener('click', () => {
        const name = btn.dataset.archLayer;
        if (active.has(name)) {
          removeWithDependents(name).forEach((n) => active.delete(n));
          render(null);
        } else {
          requiredFor(name).forEach((n) => active.add(n));
          render(name);
        }
      });
    });

    const showAll = root.querySelector('[data-arch-all]');
    const reset = root.querySelector('[data-arch-reset]');
    if (showAll) {
      showAll.addEventListener('click', () => {
        names.forEach((n) => active.add(n));
        render(null);
        if (caption && captions.all) caption.innerHTML = captions.all;
      });
    }
    if (reset) {
      reset.addEventListener('click', () => {
        active.clear();
        render(null);
      });
    }

    wireArchViewport(root);
    render(null);
  });
}

function wireArchViewport(root) {
  const canvas = root.querySelector('.arch-build-canvas');
  const svg = canvas && canvas.querySelector('svg');
  if (!canvas || !svg || canvas.dataset.zoomWired === '1') return;
  canvas.dataset.zoomWired = '1';

  const stage = document.createElement('div');
  stage.className = 'arch-build-stage';
  svg.parentNode.insertBefore(stage, svg);
  stage.appendChild(svg);
  svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');

  const zoomGroup = document.createElement('div');
  zoomGroup.className = 'arch-build-zoom';
  zoomGroup.setAttribute('role', 'group');
  zoomGroup.setAttribute('aria-label', 'Zoom drawing');
  zoomGroup.innerHTML =
    '<button type="button" class="scenario-tab" data-arch-zoom-out aria-label="Zoom out">\u2212</button>' +
    '<span class="arch-build-zoom-label" data-arch-zoom-label>100%</span>' +
    '<button type="button" class="scenario-tab" data-arch-zoom-in aria-label="Zoom in">+</button>' +
    '<button type="button" class="scenario-tab" data-arch-zoom-fit>Fit</button>';
  const actions = root.querySelector('.arch-build-actions');
  if (actions) actions.insertBefore(zoomGroup, actions.firstChild);
  else canvas.parentNode.insertBefore(zoomGroup, canvas);

  const btnIn = zoomGroup.querySelector('[data-arch-zoom-in]');
  const btnOut = zoomGroup.querySelector('[data-arch-zoom-out]');
  const btnFit = zoomGroup.querySelector('[data-arch-zoom-fit]');
  const label = zoomGroup.querySelector('[data-arch-zoom-label]');

  const MIN = 1;
  const MAX = 4;
  const STEP = 1.25;
  let scale = 1;
  let tx = 0;
  let ty = 0;

  function clampPan() {
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    if (scale <= MIN + 0.001) {
      tx = 0;
      ty = 0;
      return;
    }
    const maxX = w * (scale - 1);
    const maxY = h * (scale - 1);
    tx = Math.min(0, Math.max(-maxX, tx));
    ty = Math.min(0, Math.max(-maxY, ty));
  }

  function apply() {
    clampPan();
    stage.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + scale + ')';
    const isFit = scale <= MIN + 0.01;
    label.textContent = Math.round(scale * 100) + '%';
    btnOut.disabled = isFit;
    btnIn.disabled = scale >= MAX - 0.01;
    canvas.classList.toggle('is-zoomed', !isFit);
  }

  function zoomAt(clientX, clientY, next) {
    next = Math.min(MAX, Math.max(MIN, next));
    const rect = canvas.getBoundingClientRect();
    const px = clientX - rect.left;
    const py = clientY - rect.top;
    const wx = (px - tx) / scale;
    const wy = (py - ty) / scale;
    scale = next;
    tx = px - wx * scale;
    ty = py - wy * scale;
    apply();
  }

  function zoomTowardCenter(factor) {
    const rect = canvas.getBoundingClientRect();
    zoomAt(rect.left + rect.width / 2, rect.top + rect.height / 2, scale * factor);
  }

  function fit() {
    scale = MIN;
    tx = 0;
    ty = 0;
    apply();
  }

  btnIn.addEventListener('click', () => zoomTowardCenter(STEP));
  btnOut.addEventListener('click', () => zoomTowardCenter(1 / STEP));
  btnFit.addEventListener('click', fit);

  canvas.tabIndex = 0;
  canvas.setAttribute(
    'aria-label',
    'Architecture drawing. Drag to pan. Ctrl plus scroll or pinch to zoom.'
  );
  canvas.title = 'Ctrl + scroll or pinch to zoom · drag to pan';

  canvas.addEventListener('wheel', (e) => {
    if (!(e.ctrlKey || e.metaKey)) return;
    e.preventDefault();
    const factor = Math.exp(-e.deltaY * 0.01);
    zoomAt(e.clientX, e.clientY, scale * factor);
  }, { passive: false });

  const pointers = new Map();
  let dragging = false;
  let lastX = 0;
  let lastY = 0;
  let pinchDist = 0;
  let pinchScale = 1;
  let pinchTx = 0;
  let pinchTy = 0;

  canvas.addEventListener('pointerdown', (e) => {
    if (e.target.closest('button')) return;
    canvas.setPointerCapture(e.pointerId);
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pointers.size === 2) {
      const pts = [...pointers.values()];
      const dx = pts[0].x - pts[1].x;
      const dy = pts[0].y - pts[1].y;
      pinchDist = Math.hypot(dx, dy) || 1;
      pinchScale = scale;
      pinchTx = tx;
      pinchTy = ty;
      dragging = false;
      canvas.classList.remove('is-panning');
    } else if (scale > MIN) {
      dragging = true;
      lastX = e.clientX;
      lastY = e.clientY;
      canvas.classList.add('is-panning');
    }
  });

  canvas.addEventListener('pointermove', (e) => {
    if (!pointers.has(e.pointerId)) return;
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pointers.size === 2 && pinchDist) {
      const pts = [...pointers.values()];
      const dx = pts[0].x - pts[1].x;
      const dy = pts[0].y - pts[1].y;
      const dist = Math.hypot(dx, dy) || 1;
      const midX = (pts[0].x + pts[1].x) / 2;
      const midY = (pts[0].y + pts[1].y) / 2;
      const rect = canvas.getBoundingClientRect();
      const px = midX - rect.left;
      const py = midY - rect.top;
      const next = Math.min(MAX, Math.max(MIN, pinchScale * (dist / pinchDist)));
      const wx = (px - pinchTx) / pinchScale;
      const wy = (py - pinchTy) / pinchScale;
      scale = next;
      tx = px - wx * scale;
      ty = py - wy * scale;
      apply();
    } else if (dragging && scale > MIN) {
      tx += e.clientX - lastX;
      ty += e.clientY - lastY;
      lastX = e.clientX;
      lastY = e.clientY;
      apply();
    }
  });

  function endPointer(e) {
    pointers.delete(e.pointerId);
    if (pointers.size < 2) pinchDist = 0;
    if (pointers.size === 0) {
      dragging = false;
      canvas.classList.remove('is-panning');
    }
  }
  canvas.addEventListener('pointerup', endPointer);
  canvas.addEventListener('pointercancel', endPointer);

  canvas.addEventListener('dblclick', (e) => {
    if (e.target.closest('button')) return;
    if (scale >= MAX - 0.01) fit();
    else zoomAt(e.clientX, e.clientY, Math.min(MAX, scale * STEP));
  });

  canvas.addEventListener('keydown', (e) => {
    if (e.key === '+' || e.key === '=') {
      e.preventDefault();
      zoomTowardCenter(STEP);
    } else if (e.key === '-' || e.key === '_') {
      e.preventDefault();
      zoomTowardCenter(1 / STEP);
    } else if (e.key === '0') {
      e.preventDefault();
      fit();
    }
  });

  apply();
}

document.addEventListener('DOMContentLoaded', () => {
  applyTheme(getTheme());
  wireThemeToggle();
  wireKeywords();
  wireArchBuild();
  updateProgressUI();
  document.querySelectorAll('.complete-check').forEach((el) => {
    el.addEventListener('change', () => saveProgressFromCheckbox(el));
  });
});
