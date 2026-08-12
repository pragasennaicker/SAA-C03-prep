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

document.addEventListener('DOMContentLoaded', () => {
  applyTheme(getTheme());
  wireThemeToggle();
  wireKeywords();
  updateProgressUI();
  document.querySelectorAll('.complete-check').forEach((el) => {
    el.addEventListener('change', () => saveProgressFromCheckbox(el));
  });
});
