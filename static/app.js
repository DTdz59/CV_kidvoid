'use strict';

// ── State ─────────────────────────────────────────────────────────────────────
let ALL_OBJECTS = {};
let cameraStream = null;
let lastResult   = null;
let currentDetailId = null;
let facingMode   = 'environment';
let scanMode     = 'imagenet';

const CATEGORY_LABEL = {
  fruit:   { label: '🍎 Trái cây',     color: '#4CAF82' },
  animal:  { label: '🐾 Động vật',     color: '#FF9800' },
  food:    { label: '🍕 Đồ ăn',        color: '#FF5252' },
  vehicle: { label: '🚗 Phương tiện',  color: '#42A5F5' },
  object:  { label: '📦 Đồ vật',       color: '#9B5DE5' },
  nature:  { label: '🌿 Thiên nhiên',  color: '#66BB6A' },
};

const CATEGORY_EMOJI = {
  fruit: '🍎',
  animal: '🐾',
  food: '🍽️',
  vehicle: '🚗',
  object: '📦',
  nature: '🌿',
};

const EMOJI_KEYWORDS = [
  [['apple'], '🍎'], [['banana'], '🍌'], [['orange', 'lemon', 'lime'], '🍊'],
  [['grape', 'raisin'], '🍇'], [['strawberry'], '🍓'], [['pineapple'], '🍍'],
  [['pomegranate'], '🍒'], [['fig'], '🫒'], [['mushroom'], '🍄'],

  [['dog', 'puppy', 'retriever', 'poodle', 'terrier', 'husky', 'beagle'], '🐶'],
  [['cat', 'kitten', 'tabby', 'siamese', 'persian'], '🐱'],
  [['bird', 'robin', 'sparrow', 'parrot', 'macaw'], '🐦'],
  [['fish', 'goldfish'], '🐟'], [['shark'], '🦈'], [['turtle', 'tortoise'], '🐢'],
  [['frog', 'toad'], '🐸'], [['snake', 'cobra', 'python'], '🐍'],
  [['horse', 'zebra'], '🐴'], [['cow', 'ox', 'bull'], '🐮'],
  [['pig', 'boar'], '🐷'], [['sheep', 'goat'], '🐑'],
  [['elephant'], '🐘'], [['lion'], '🦁'], [['tiger'], '🐯'],
  [['bear', 'panda'], '🐻'], [['monkey', 'ape', 'gorilla'], '🐵'],
  [['rabbit', 'hare'], '🐰'], [['chicken', 'hen', 'rooster'], '🐔'],
  [['duck', 'goose'], '🦆'], [['butterfly'], '🦋'], [['bee'], '🐝'],

  [['pizza'], '🍕'], [['hamburger', 'cheeseburger'], '🍔'],
  [['hot dog'], '🌭'], [['ice cream'], '🍦'], [['cake', 'cupcake'], '🎂'],
  [['bread', 'bagel', 'baguette'], '🍞'], [['cookie', 'biscuit'], '🍪'],
  [['coffee', 'espresso'], '☕'], [['egg'], '🥚'], [['soup'], '🍲'],
  [['sandwich'], '🥪'], [['taco'], '🌮'], [['burrito'], '🌯'],
  [['spaghetti', 'pasta'], '🍝'], [['sushi'], '🍣'], [['cheese'], '🧀'],

  [['car', 'automobile', 'taxi', 'jeep'], '🚗'], [['bus'], '🚌'],
  [['train', 'locomotive'], '🚆'], [['airliner', 'airplane', 'warplane'], '✈️'],
  [['bicycle'], '🚲'], [['motorcycle', 'scooter'], '🏍️'],
  [['boat', 'canoe', 'kayak'], '⛵'], [['truck', 'pickup'], '🚚'],
  [['ambulance'], '🚑'], [['fire engine'], '🚒'], [['tractor'], '🚜'],

  [['backpack', 'rucksack'], '🎒'], [['book', 'comic'], '📚'],
  [['laptop', 'computer', 'notebook'], '💻'], [['phone', 'cellular'], '📱'],
  [['television', 'monitor', 'screen'], '📺'], [['camera'], '📷'],
  [['clock', 'watch', 'stopwatch'], '🕒'], [['umbrella'], '☂️'],
  [['ball', 'soccer', 'basketball', 'baseball', 'tennis'], '⚽'],
  [['teddy'], '🧸'], [['guitar', 'banjo'], '🎸'], [['piano'], '🎹'],
  [['drum'], '🥁'], [['microphone'], '🎤'], [['violin'], '🎻'],
  [['chair', 'stool'], '🪑'], [['cup', 'mug'], '☕'], [['bottle'], '🍶'],
  [['pencil', 'pen'], '✏️'], [['key'], '🔑'], [['lock'], '🔒'],
  [['hammer'], '🔨'], [['wrench'], '🔧'], [['knife'], '🔪'],
  [['lamp'], '💡'], [['envelope', 'mailbox'], '✉️'], [['balloon'], '🎈'],
  [['sunglasses'], '🕶️'], [['hat'], '🎩'], [['shoe', 'sneaker', 'boot'], '👟'],
  [['shirt', 'jersey', 'sweatshirt'], '👕'], [['toilet'], '🚽'],

  [['tree', 'oak', 'pine', 'palm'], '🌳'], [['flower', 'rose', 'daisy'], '🌸'],
  [['sunflower'], '🌻'], [['cactus'], '🌵'], [['mountain', 'cliff'], '⛰️'],
  [['volcano'], '🌋'], [['fountain', 'geyser'], '⛲'],
];

const VISUAL_QUERY_ALIASES = {
  apple: 'apple fruit',
  orange: 'orange fruit',
  fig: 'fig fruit',
  notebook: 'laptop computer',
  monitor: 'computer monitor',
  cellular_telephone: 'mobile phone',
  mobile_phone: 'mobile phone',
  soccer_ball: 'football ball',
  book_jacket: 'book',
  espresso: 'coffee cup',
  pickup: 'pickup truck',
  fire_engine: 'fire truck',
  airliner: 'airplane',
};

const visualCache = new Map();
let visualObserver = null;

// Quiz state
const quiz = { questions:[], index:0, score:0, streak:0, answered:false };
// Pronunciation state
const pron = { index:0, keys:[], listening:false, recognition:null };
// Audio context (lazy init)
let audioCtx = null;

// ── Boot ──────────────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', async () => {
  ALL_OBJECTS = await fetch('/api/all-objects').then(r => r.json());
  pron.keys   = Object.keys(ALL_OBJECTS);
  updateHomeStats();
  await new Promise(r => setTimeout(r, 1800));
  showScreen('home');
  buildDict();
});

function updateHomeStats() {
  const totalEl = $('stat-total-objects');
  const categoryEl = $('stat-total-categories');
  if (!totalEl || !categoryEl) return;

  const objects = Object.values(ALL_OBJECTS);
  totalEl.textContent = objects.length.toLocaleString('vi-VN') + '+';
  categoryEl.textContent = new Set(objects.map(o => o.category || 'object')).size;
}

// ── Navigation ────────────────────────────────────────────────────────────────
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  if (id === 'scan')          initScan();
  if (id === 'quiz')          startQuiz();
  if (id === 'dict')          filterDict();
  if (id === 'pronunciation') initPron();
  if (id !== 'scan')          stopCamera();
}

function setScanMode(mode) {
  scanMode = mode === 'fruit' ? 'fruit' : 'imagenet';
  document.querySelectorAll('.mode-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.mode === scanMode);
  });
  const hint = $('scan-hint');
  if (hint) {
    hint.textContent = scanMode === 'fruit'
      ? 'Che do trai cay: apple, banana, grape, orange, pomegranate'
      : 'Che do vat dung: nhan dien do vat hang ngay bang ImageNet';
  }
}

// ── AUDIO ─────────────────────────────────────────────────────────────────────
function getAudio() {
  if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  return audioCtx;
}

function playSound(type) {
  try {
    const ctx  = getAudio();
    const osc  = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain); gain.connect(ctx.destination);
    const now = ctx.currentTime;

    if (type === 'correct') {
      osc.type = 'sine';
      osc.frequency.setValueAtTime(523, now);
      osc.frequency.setValueAtTime(659, now + .12);
      osc.frequency.setValueAtTime(784, now + .24);
      gain.gain.setValueAtTime(.25, now);
      gain.gain.exponentialRampToValueAtTime(.001, now + .5);
      osc.start(now); osc.stop(now + .5);
    } else if (type === 'wrong') {
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(220, now);
      osc.frequency.linearRampToValueAtTime(150, now + .25);
      gain.gain.setValueAtTime(.2, now);
      gain.gain.exponentialRampToValueAtTime(.001, now + .3);
      osc.start(now); osc.stop(now + .3);
    } else if (type === 'win') {
      [523,659,784,1047].forEach((f,i) => {
        const o2 = ctx.createOscillator(), g2 = ctx.createGain();
        o2.connect(g2); g2.connect(ctx.destination);
        o2.type = 'sine'; o2.frequency.value = f;
        g2.gain.setValueAtTime(.2, now + i*.1);
        g2.gain.exponentialRampToValueAtTime(.001, now + i*.1 + .3);
        o2.start(now + i*.1); o2.stop(now + i*.1 + .3);
      });
    } else if (type === 'star') {
      osc.type = 'sine';
      osc.frequency.setValueAtTime(880, now);
      gain.gain.setValueAtTime(.15, now);
      gain.gain.exponentialRampToValueAtTime(.001, now + .2);
      osc.start(now); osc.stop(now + .2);
    }
  } catch {}
}

// ── CONFETTI ──────────────────────────────────────────────────────────────────
function launchConfetti() {
  const colors = ['#FF7043','#9B5DE5','#4CAF82','#FFD54F','#FF6B9D','#42A5F5'];
  for (let i = 0; i < 120; i++) {
    const el = document.createElement('div');
    el.className = 'confetti-piece';
    const size = 6 + Math.random() * 8;
    el.style.cssText = `
      left:${Math.random()*100}vw;
      width:${size}px; height:${size}px;
      background:${colors[i % colors.length]};
      border-radius:${Math.random()>.5?'50%':'2px'};
      animation-delay:${Math.random()*1.5}s;
      animation-duration:${2+Math.random()*2}s;
    `;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 5000);
  }
}

// ── OBJECT HELPER ─────────────────────────────────────────────────────────────
function getObj(label) {
  if (!label) return null;
  if (ALL_OBJECTS[label]) return enhanceObject(label, ALL_OBJECTS[label]);
  // Fallback for unmapped labels
  const name = label.replace(/_/g,' ').replace(/\b\w/g, c => c.toUpperCase());
  return enhanceObject(label, {
    nameEn:name, nameVn:name, emoji:'📦', phonetic:'',
    color:'#78909C', category:'object', funFact:`This is a ${name}!`
  });
}

function enhanceObject(id, obj) {
  return { ...obj, emoji: resolveEmoji(id, obj) };
}

function resolveEmoji(id, obj) {
  const haystack = [
    id,
    obj.nameEn,
    obj.nameVn,
    ...(obj.keywords || []),
  ].filter(Boolean).join(' ').toLowerCase().replace(/[_-]/g, ' ');

  for (const [keywords, emoji] of EMOJI_KEYWORDS) {
    if (keywords.some(kw => haystack.includes(kw))) return emoji;
  }

  return obj.emoji || CATEGORY_EMOJI[obj.category] || CATEGORY_EMOJI.object;
}

function visualFallbackHtml(obj) {
  return `<span class="visual-fallback">${obj?.emoji || '📦'}</span>`;
}

function getVisualQuery(id, obj) {
  const key = (id || '').toLowerCase();
  if (VISUAL_QUERY_ALIASES[key]) return VISUAL_QUERY_ALIASES[key];

  const base = (obj?.keywords?.[0] || obj?.nameEn || id || '')
    .replace(/_/g, ' ')
    .split(',')[0]
    .trim();

  if (!base) return '';
  if (obj?.category === 'fruit') return `${base} fruit`;
  if (obj?.category === 'animal') return `${base} animal`;
  if (obj?.category === 'food') return `${base} food`;
  if (obj?.category === 'vehicle') return `${base} vehicle`;
  if (obj?.category === 'nature') return `${base} nature`;
  return base;
}

async function fetchWikiThumb(query) {
  if (!query) return null;
  const cacheKey = `wiki-thumb:${query.toLowerCase()}`;

  if (visualCache.has(cacheKey)) return visualCache.get(cacheKey);
  try {
    const cached = localStorage.getItem(cacheKey);
    if (cached) {
      const parsed = JSON.parse(cached);
      visualCache.set(cacheKey, parsed);
      return parsed;
    }
  } catch {}

  const url = 'https://en.wikipedia.org/w/api.php?' + new URLSearchParams({
    action: 'query',
    generator: 'search',
    gsrsearch: query,
    gsrlimit: '1',
    prop: 'pageimages',
    pithumbsize: '320',
    format: 'json',
    origin: '*',
  });

  try {
    const data = await fetch(url).then(r => r.ok ? r.json() : null);
    const page = data?.query?.pages && Object.values(data.query.pages)[0];
    const thumb = page?.thumbnail?.source
      ? { src: page.thumbnail.source, title: page.title || query }
      : null;
    visualCache.set(cacheKey, thumb);
    try { localStorage.setItem(cacheKey, JSON.stringify(thumb)); } catch {}
    return thumb;
  } catch {
    visualCache.set(cacheKey, null);
    return null;
  }
}

function setObjectVisual(el, id, obj, className = 'object-photo') {
  if (!el || !obj) return;
  const enhanced = enhanceObject(id, obj);
  const query = getVisualQuery(id, enhanced);
  el.dataset.visualId = id || enhanced.nameEn || '';
  el.innerHTML = visualFallbackHtml(enhanced);

  fetchWikiThumb(query).then(thumb => {
    if (!thumb || el.dataset.visualId !== (id || enhanced.nameEn || '')) return;
    el.innerHTML = `<img class="${className}" src="${thumb.src}" alt="${enhanced.nameEn}" loading="lazy">`;
  });
}

function visualHtml(id, obj) {
  const enhanced = enhanceObject(id, obj);
  const query = getVisualQuery(id, enhanced).replace(/"/g, '&quot;');
  return `<span class="object-visual lazy-visual" data-id="${id}" data-query="${query}" data-name="${enhanced.nameEn.replace(/"/g, '&quot;')}">${visualFallbackHtml(enhanced)}</span>`;
}

function hydrateVisuals(root = document) {
  if (!visualObserver) {
    visualObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        visualObserver.unobserve(el);
        fetchWikiThumb(el.dataset.query).then(thumb => {
          if (!thumb) return;
          el.innerHTML = `<img class="object-photo" src="${thumb.src}" alt="${el.dataset.name || ''}" loading="lazy">`;
        });
      });
    }, { rootMargin: '200px' });
  }

  root.querySelectorAll('.lazy-visual').forEach(el => visualObserver.observe(el));
}

// ── SCAN ──────────────────────────────────────────────────────────────────────
async function initScan() { hideResult(); await startCamera(); }

async function startCamera() {
  if (cameraStream) stopCamera();
  const configs = [
    { video:{ facingMode, width:{ideal:1280}, height:{ideal:720} } },
    { video:{ width:{ideal:1280}, height:{ideal:720} } },
    { video: true },
  ];
  for (const cfg of configs) {
    try {
      cameraStream = await navigator.mediaDevices.getUserMedia(cfg);
      $('camera-video').srcObject = cameraStream;
      $('scan-placeholder').classList.add('hidden');
      $('scan-hint').textContent = 'Đặt vật thể vào khung rồi bấm quét';
      return;
    } catch (e) { window._camErr = e; }
  }
  const err = window._camErr;
  $('scan-placeholder').classList.remove('hidden');
  $('scan-placeholder').innerHTML = err?.name === 'NotAllowedError'
    ? `<span>🔒</span><p style="text-align:center;padding:0 20px">Chưa cho phép camera.<br>Bấm <b>🔒</b> trên thanh địa chỉ → Allow → Tải lại trang.</p>
       <button class="btn-hero" onclick="location.reload()">🔄 Tải lại</button>`
    : `<span>📷</span><p>Không tìm thấy camera</p>
       <button class="btn-hero" onclick="openGallery()">🖼️ Chọn ảnh</button>`;
}

function stopCamera() { cameraStream?.getTracks().forEach(t=>t.stop()); cameraStream=null; }
async function switchCamera() { facingMode = facingMode==='environment'?'user':'environment'; await startCamera(); }

function capturePhoto() {
  const video = $('camera-video');
  if (!cameraStream || video.readyState < 2) { openGallery(); return; }
  $('scan-frame').classList.add('flash');
  setTimeout(() => $('scan-frame').classList.remove('flash'), 300);
  $('scan-hint').textContent = 'Đang nhận diện...';
  const canvas = $('camera-canvas');
  canvas.width = video.videoWidth; canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  canvas.toBlob(blob => sendToPredict(blob), 'image/jpeg', .9);
}

function openGallery() { $('gallery-input').click(); }
function handleGallery(e) { const f=e.target.files[0]; if(f) sendToPredict(f); e.target.value=''; }

async function sendToPredict(blob) {
  hideResult();
  $('scan-loading').classList.remove('hidden');
  try {
    const fd = new FormData();
    fd.append('file', blob, 'photo.jpg');
    fd.append('mode', scanMode);
    const data = await fetch('/api/predict',{method:'POST',body:fd}).then(r=>r.json());
    if (data.detail) throw new Error(data.detail);
    if (!data.results?.length) throw new Error();
    showScanResult(data);
  } catch {
    $('scan-hint').textContent = 'Không nhận diện được, thử lại nhé! 😊';
    setTimeout(() => { $('scan-hint').textContent = 'Đặt vật thể vào khung rồi bấm quét'; }, 2500);
  } finally { $('scan-loading').classList.add('hidden'); }
}

function showScanResult(data) {
  const top = data.results[0];
  const obj = getObj(top.label);
  if (!obj) return;
  lastResult = top.label;
  const cat  = CATEGORY_LABEL[obj.category] || CATEGORY_LABEL.object;

  setObjectVisual($('result-emoji'), top.label, obj);
  $('result-name-en').textContent  = obj.nameEn;
  $('result-name-en').style.color  = obj.color;
  $('result-name-vn').textContent  = obj.nameVn;
  $('result-phonetic').textContent = obj.phonetic;
  $('result-phonetic').style.cssText = `background:${obj.color}20;color:${obj.color}`;
  $('btn-detail').style.background = obj.color;
  $('result-confidence').innerHTML = renderPredictionMeta(data, cat);

  $('scan-result').classList.remove('hidden');
  speak(obj.nameEn);
  // Animate emoji
  const el = $('result-emoji');
  el.style.transform = 'scale(0)';
  requestAnimationFrame(() => { el.style.transition='transform .5s cubic-bezier(.34,1.56,.64,1)'; el.style.transform='scale(1)'; });
}

function renderPredictionMeta(data, cat) {
  const top = data.results[0];
  const confidence = top?.confidence || 0;
  const quality = data.quality || {};
  const issueMap = {
    dark: 'ảnh hơi tối',
    too_bright: 'ảnh quá sáng',
    low_contrast: 'ít tương phản',
    blurry: 'ảnh hơi mờ',
  };
  const issues = (quality.issues || []).map(i => issueMap[i] || i);
  const uncertain = !data.demo_mode && confidence < 0.35;
  const modeLabel = data.source === 'fruit' ? 'Fruit model' : 'ImageNet';

  const predictionRows = (data.results || []).slice(0, 3).map((r, idx) => {
    const item = getObj(r.label);
    const pct = Math.round((r.confidence || 0) * 100);
    return `
      <div class="prediction-row">
        <span>${idx + 1}. ${item?.nameEn || r.label}</span>
        <strong>${pct}%</strong>
      </div>`;
  }).join('');

  return `
    <div class="result-meta-line">
      <span class="cat-badge" style="background:${cat.color}18;color:${cat.color}">${cat.label}</span>
      <span class="mode-pill">${modeLabel}</span>
      <span>${data.demo_mode ? '⚠️ Demo' : `✨ ${(confidence * 100).toFixed(1)}%`}</span>
    </div>
    ${uncertain ? '<div class="scan-warning">Độ tin cậy thấp, nên quét lại gần hơn hoặc đổi góc chụp.</div>' : ''}
    ${issues.length ? `<div class="scan-warning">Chất lượng ảnh: ${issues.join(', ')}.</div>` : ''}
    ${predictionRows ? `<div class="prediction-list">${predictionRows}</div>` : ''}
  `;
}

function hideResult() { $('scan-result').classList.add('hidden'); }
function speakResult() { if(lastResult) speak(getObj(lastResult)?.nameEn); }
function openDetail()  { hideResult(); openDetailModal(lastResult); }

// ── QUIZ ──────────────────────────────────────────────────────────────────────
function startQuiz() {
  const keys = Object.keys(ALL_OBJECTS);
  quiz.questions = shuffle(keys).slice(0,10).map(correct => ({
    correct, options: shuffle([correct, ...shuffle(keys.filter(k=>k!==correct)).slice(0,3)])
  }));
  quiz.index=0; quiz.score=0; quiz.streak=0; quiz.answered=false;
  $('quiz-playing').style.display='flex';
  $('quiz-result').classList.add('hidden');
  renderQuestion();
}

function renderQuestion() {
  const q   = quiz.questions[quiz.index];
  const obj = getObj(q.correct);
  const cat = CATEGORY_LABEL[obj?.category] || CATEGORY_LABEL.object;
  quiz.answered = false;

  $('quiz-counter').textContent  = `Câu ${quiz.index+1}/${quiz.questions.length}`;
  $('quiz-score').textContent    = quiz.score;
  $('quiz-progress').style.width = `${((quiz.index+1)/quiz.questions.length)*100}%`;
  setObjectVisual($('quiz-emoji'), q.correct, obj);
  $('quiz-emoji').classList.remove('bounce');
  $('btn-next').classList.add('hidden');

  // Streak badge
  const sb = $('streak-badge');
  if (quiz.streak >= 2) { sb.textContent=`🔥${quiz.streak}`; sb.style.display='inline-block'; }
  else sb.style.display='none';

  // Category badge
  ensureCatBadge('quiz-cat-badge', $('quiz-emoji'), 'beforebegin', cat);

  const container = $('quiz-options');
  container.innerHTML = '';
  q.options.forEach((key, i) => {
    const f = getObj(key);
    const btn = document.createElement('button');
    btn.className='quiz-option';
    btn.innerHTML=`<span class="opt-emoji">${visualHtml(key, f)}</span><span>${f?.nameEn}</span><span class="opt-check"></span>`;
    btn.onclick=()=>selectAnswer(i);
    container.appendChild(btn);
  });
  hydrateVisuals(container);
}

function selectAnswer(i) {
  if (quiz.answered) return;
  quiz.answered=true;
  const q=quiz.questions[quiz.index];
  const isCorrect = q.options[i]===q.correct;
  if (isCorrect) { quiz.score++; quiz.streak++; } else { quiz.streak=0; }

  document.querySelectorAll('.quiz-option').forEach((btn,idx)=>{
    const key=q.options[idx];
    if (key===q.correct)  { btn.classList.add('correct'); btn.querySelector('.opt-check').textContent='✓'; }
    else if (idx===i)      { btn.classList.add('wrong');   btn.querySelector('.opt-check').textContent='✗'; }
    else                   btn.classList.add('dim');
    btn.disabled=true;
  });

  if (isCorrect) {
    $('quiz-emoji').classList.add('bounce');
    playSound('correct');
    speak(`Correct! ${getObj(q.correct)?.nameEn}`);
    // Show streak toast
    if (quiz.streak>=3) showStreakToast(quiz.streak);
  } else {
    playSound('wrong');
    speak(getObj(q.correct)?.nameEn);
  }

  $('btn-next').textContent = quiz.index<quiz.questions.length-1 ? 'Tiếp theo →' : 'Xem kết quả 🎉';
  $('btn-next').classList.remove('hidden');
}

function nextQuestion() {
  if (quiz.index < quiz.questions.length-1) { quiz.index++; renderQuestion(); }
  else showQuizResult();
}

function showStreakToast(n) {
  const msgs=['','','','🔥 On fire!','⚡ Super!','💥 Incredible!','🏆 Unstoppable!'];
  const toast=document.createElement('div');
  toast.className='streak-toast';
  toast.textContent = msgs[Math.min(n,msgs.length-1)] || `🔥×${n}`;
  document.body.appendChild(toast);
  setTimeout(()=>toast.remove(),1800);
}

function showQuizResult() {
  $('quiz-playing').style.display='none';
  $('quiz-result').classList.remove('hidden');
  const pct=quiz.score/quiz.questions.length;
  const [emoji,msg]=pct>=.9?['🏆','Xuất sắc! Em giỏi lắm!']
    :pct>=.7?['🌟','Rất tốt! Cố gắng thêm nhé!']
    :pct>=.5?['😊','Khá tốt! Ôn lại nhé!']
    :['💪','Cố lên! Thử lại nhé!'];

  $('quiz-result-emoji').textContent=emoji;
  $('quiz-result-msg').textContent=msg;
  $('quiz-final-score').textContent=`${quiz.score}/${quiz.questions.length}`;
  $('quiz-final-bar').style.width=`${pct*100}%`;
  $('quiz-final-pct').textContent=`${Math.round(pct*100)}%`;

  // Streak record
  const streakEl=$('quiz-max-streak');
  if(streakEl) streakEl.textContent=`Streak cao nhất: 🔥${quiz.streak}`;

  if (pct>=.8) { launchConfetti(); playSound('win'); }
}

// ── DICTIONARY ────────────────────────────────────────────────────────────────
let dictFilter = 'all';

function setFilter(cat, btn) {
  dictFilter = cat;
  document.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  buildDict();
}

function filterDict() { buildDict(); }

function buildDict() {
  const grid=$('dict-grid');
  const q=($('dict-search')?.value||'').toLowerCase();

  const entries=Object.entries(ALL_OBJECTS).filter(([,f])=>{
    const mQ = !q || f.nameEn.toLowerCase().includes(q)||f.nameVn.toLowerCase().includes(q);
    const mC = dictFilter==='all'||f.category===dictFilter;
    return mQ && mC;
  });

  if (!entries.length) {
    grid.innerHTML=`<div style="grid-column:span 2;text-align:center;padding:40px;color:var(--grey)">
      <div style="font-size:48px">🔍</div><p>Không tìm thấy</p></div>`;
    return;
  }

  grid.innerHTML='';
  entries.forEach(([id,raw])=>{
    const f = enhanceObject(id, raw);
    const cat=CATEGORY_LABEL[f.category]||CATEGORY_LABEL.object;
    const card=document.createElement('div');
    card.className='dict-card';
    card.innerHTML=`
      <div class="dict-card-inner">
        <div class="dict-card-front">
          <div class="dict-card-circle" style="background:${f.color}18">${visualHtml(id, f)}</div>
          <div class="dict-card-en" style="color:${f.color}">${f.nameEn}</div>
          <div class="dict-card-vn">${f.nameVn}</div>
          <div class="cat-badge" style="background:${cat.color}15;color:${cat.color};margin-top:6px">${cat.label}</div>
          <div class="flip-hint">Bấm để lật 👆</div>
        </div>
        <div class="dict-card-back" style="background:${f.color}08">
          <div style="font-size:36px;margin-bottom:8px">${f.emoji}</div>
          <div style="font-size:20px;font-weight:900;color:${f.color}">${f.nameEn}</div>
          <div style="font-size:13px;color:#999;margin:4px 0 10px">${f.phonetic||''}</div>
          <div style="font-size:14px;color:#555;line-height:1.5">${f.funFact||''}</div>
          <button class="btn-speak-card" onclick="event.stopPropagation();speak('${f.nameEn.replace(/'/g,"\\'")}')">🔊</button>
        </div>
      </div>`;
    card.querySelector('.dict-card-inner').addEventListener('click', e=>{
      if(!e.target.closest('.btn-speak-card')) card.classList.toggle('flipped');
    });
    card.addEventListener('dblclick',()=>openDetailModal(id));
    grid.appendChild(card);
  });
  hydrateVisuals(grid);
}

// ── DETAIL MODAL ──────────────────────────────────────────────────────────────
function openDetailModal(id) {
  const f=getObj(id); if(!f) return;
  currentDetailId=id;
  const cat=CATEGORY_LABEL[f.category]||CATEGORY_LABEL.object;

  setObjectVisual($('detail-emoji'), id, f);
  $('detail-name-en').textContent=f.nameEn; $('detail-name-en').style.color=f.color;
  $('detail-name-vn').textContent=f.nameVn;
  $('detail-phonetic').textContent=f.phonetic;
  $('detail-phonetic').style.cssText=`background:${f.color}18;color:${f.color}`;
  ensureCatBadge('detail-cat', $('detail-phonetic'), 'afterend', cat, 'margin:0 auto 16px');
  $('detail-taste').textContent=f.taste||f.category||''; $('detail-taste').style.color=f.color;
  $('detail-nutrition').textContent=f.nutrition||''; $('detail-nutrition').style.color='#4CAF82';
  $('detail-funfact').textContent=f.funFact||'';
  $('detail-listen-btn').onclick=()=>speak(f.nameEn);
  $('detail-listen-btn').style.cssText=`border-color:${f.color};color:${f.color}`;
  $('detail-modal').classList.remove('hidden');
}

function closeDetail(e) {
  if (!e||e.target===$('detail-modal')||e.target.closest('.modal-close'))
    $('detail-modal').classList.add('hidden');
}

function goToPronunciation() {
  $('detail-modal').classList.add('hidden');
  pron.index=Math.max(0, pron.keys.indexOf(currentDetailId));
  showScreen('pronunciation');
}

// ── PRONUNCIATION ─────────────────────────────────────────────────────────────
function initPron() {
  pron.keys=Object.keys(ALL_OBJECTS);
  if(pron.index<0||pron.index>=pron.keys.length) pron.index=0;
  renderPron();
}

function renderPron() {
  const id=pron.keys[pron.index]; const f=getObj(id);
  const cat=CATEGORY_LABEL[f?.category]||CATEGORY_LABEL.object;

  // Dots (10 max)
  $('pron-dots').innerHTML=pron.keys.slice(0,10).map((_,i)=>
    `<div class="dot${i===pron.index%10?' active':''}"
          style="width:${i===pron.index%10?'28px':'8px'}"></div>`
  ).join('');

  $('pron-circle').style.background=(f?.color||'#ccc')+'18';
  setObjectVisual($('pron-emoji'), id, f);
  $('pron-name-en').textContent=f?.nameEn||'';
  $('pron-name-en').style.color=f?.color||'var(--pink)';
  $('pron-phonetic').textContent=f?.phonetic||'';
  $('pron-name-vn').textContent =f?.nameVn||'';
  ensureCatBadge('pron-cat',$('pron-name-vn'),'afterend',cat,'margin-bottom:16px;display:inline-block');

  $('btn-mic').classList.remove('listening');
  $('mic-label').textContent='Bấm để nói';
  $('spoken-bubble').classList.add('hidden');
  $('pron-stars').classList.add('hidden');
  $('btn-pron-next').classList.add('hidden');
  pron.listening=false;
}

function pronounciationSpeak() { speak(getObj(pron.keys[pron.index])?.nameEn); }
function toggleListening()     { pron.listening ? stopListening() : startListening(); }

function startListening() {
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if (!SR) { alert('Dùng Chrome để sử dụng tính năng microphone!'); return; }
  pron.recognition=new SR();
  pron.recognition.lang='en-US'; pron.recognition.interimResults=false;
  pron.recognition.onresult=e=>{
    const spoken=e.results[0][0].transcript;
    $('spoken-bubble').textContent=`"${spoken}"`;
    $('spoken-bubble').classList.remove('hidden');
    evaluatePron(spoken);
  };
  pron.recognition.onerror=pron.recognition.onend=()=>{
    $('btn-mic').classList.remove('listening');
    $('mic-label').textContent='Bấm để nói';
    pron.listening=false;
  };
  pron.recognition.start();
  pron.listening=true;
  $('btn-mic').classList.add('listening');
  $('mic-label').textContent='Đang nghe... (bấm để dừng)';
}

function stopListening() {
  pron.recognition?.stop();
  pron.listening=false;
  $('btn-mic').classList.remove('listening');
  $('mic-label').textContent='Bấm để nói';
}

function evaluatePron(spoken) {
  const expected=(getObj(pron.keys[pron.index])?.nameEn||'').toLowerCase();
  const s=spoken.toLowerCase().trim();
  let score=s===expected?1.0:(s.includes(expected)||expected.includes(s))?0.75
    :[...new Set(s)].filter(c=>expected.includes(c)).length/(new Set(expected).size||1);

  const stars=score>=.85?3:score>=.55?2:score>=.25?1:0;
  const msgs=['Thử lại nhé! 🔄','Cố thêm nhé! 💪','Rất tốt! 👍','Hoàn hảo! 🎉'];

  // Animate stars one by one
  $('star-row').textContent='';
  $('pron-stars').classList.remove('hidden');
  for(let i=0;i<3;i++){
    setTimeout(()=>{
      $('star-row').textContent+= i<stars ? '⭐' : '☆';
      if(i<stars) playSound('star');
    }, i*300);
  }
  setTimeout(()=>{
    $('pron-feedback').textContent=msgs[stars];
    $('pron-feedback').style.color=stars>=2?'var(--green)':'var(--primary)';
    if(stars===3) launchConfetti();
  }, 1000);

  $('btn-pron-next').textContent=pron.index<pron.keys.length-1?'Từ tiếp theo →':'Bắt đầu lại 🔄';
  $('btn-pron-next').classList.remove('hidden');
}

function nextPronunciation() { pron.index=(pron.index+1)%pron.keys.length; renderPron(); }

// ── TTS ───────────────────────────────────────────────────────────────────────
function speak(text) {
  if(!text) return;
  window.speechSynthesis.cancel();
  const u=new SpeechSynthesisUtterance(text);
  u.lang='en-US'; u.rate=0.8; u.pitch=1.1;
  window.speechSynthesis.speak(u);
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function $(id){ return document.getElementById(id); }
function shuffle(a){ return [...a].sort(()=>Math.random()-.5); }

function ensureCatBadge(id, anchor, position, cat, extraStyle='') {
  let el=document.getElementById(id);
  if (!el) {
    el=document.createElement('div');
    el.id=id; el.className='cat-badge';
    anchor.insertAdjacentElement(position, el);
  }
  el.textContent=cat.label;
  el.style.cssText=`background:${cat.color}18;color:${cat.color};${extraStyle}`;
}
