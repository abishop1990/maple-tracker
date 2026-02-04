let bowlWeight = 0;
let dailyChart = null;
let periodChart = null;
let entryToDelete = null;

const ui = {};

function cacheElements() {
  // Form elements
  ui.logForm = document.getElementById('logForm');
  ui.logDate = document.getElementById('logDate');
  ui.logTime = document.getElementById('logTime');
  ui.logTotal = document.getElementById('logTotal');
  ui.logRefill = document.getElementById('logRefill');
  ui.logNotes = document.getElementById('logNotes');
  ui.waterHint = document.getElementById('waterHint');
  ui.manualDrink = document.getElementById('manualDrink');
  ui.logDrinkManual = document.getElementById('logDrinkManual');

  // Stats elements
  ui.statAvg = document.getElementById('statAvg');
  ui.statDays = document.getElementById('statDays');
  ui.statTotal = document.getElementById('statTotal');
  ui.statBowl = document.getElementById('statBowl');

  // Lists and containers
  ui.entriesList = document.getElementById('entriesList');
  ui.importModal = document.getElementById('importModal');
  ui.importText = document.getElementById('importText');
  ui.settingsBowl = document.getElementById('settingsBowl');
  ui.deleteModal = document.getElementById('deleteModal');
  ui.confirmDeleteBtn = document.getElementById('confirmDeleteBtn');

  // Toast
  ui.toast = document.getElementById('toast');
}

document.addEventListener('DOMContentLoaded', () => {
  cacheElements();

  initBowlWeight();
  setDefaultDateTime();
  loadStats();
  loadEntries();
  setupTabs();
  setupFormHandlers();
});


function iconHtml(name, className = '') {
  const classAttr = className ? ` class="${className}"` : '';
  return `<svg${classAttr}><use href="${window.ICONS_PATH}#${name}"></use></svg>`;
}

function initBowlWeight() {
  if (ui.statBowl) {
    bowlWeight = parseInt(ui.statBowl.textContent) || 0;
  }
}

function setDefaultDateTime() {
  const now = new Date();
  ui.logDate.value = now.toISOString().split('T')[0];
  ui.logTime.value = now.toTimeString().slice(0, 5);
}

function setupFormHandlers() {
  ui.logForm.addEventListener('submit', handleFormSubmit);
  ui.logTotal.addEventListener('input', handleTotalWeightInput);
  ui.manualDrink.addEventListener('change', handleManualDrinkToggle);
}

async function handleFormSubmit(e) {
  e.preventDefault();

  const entry = {
    date: ui.logDate.value,
    time: ui.logTime.value,
    total_weight: parseInt(ui.logTotal.value),
    refill_to: ui.logRefill.value ? parseInt(ui.logRefill.value) : null,
    notes: ui.logNotes.value || "",
    drink_manual: ui.manualDrink.checked ? parseInt(ui.logDrinkManual.value) : null
  };

  try {
    const res = await fetch('/api/entries', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(entry)
    });
    const data = await res.json();

    if (data.success) {
      showToast('Entry logged!', 'success');
      ui.logForm.reset();
      setDefaultDateTime();
      loadStats();
      loadEntries();
    } else {
      showToast('Error: ' + data.error, 'error');
    }
  } catch (err) {
    showToast('Failed to save entry', 'error');
  }
}

function handleTotalWeightInput(e) {
  const total = parseInt(e.target.value);
  if (total) {
    const water = total - bowlWeight;
    ui.waterHint.textContent = `= ${water}g water`;
  } else {
    ui.waterHint.textContent = '';
  }
}

function handleManualDrinkToggle(e) {
  ui.logDrinkManual.disabled = !e.target.checked;
}

async function loadStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();

    const stats = data.summary || data;

    if (stats) {
      ui.statAvg.textContent = stats.average || '--';
      ui.statDays.textContent = stats.total_days || '--';
      ui.statTotal.textContent = stats.total_intake || '--';
    }

    updateDailyChart(data.daily || []);
    updatePeriodChart(data.periods || {});
  } catch (err) {
    console.error('Failed to load stats:', err);
  }
}

function updateDailyChart(dailyData) {
  const ctx = document.getElementById('dailyChart').getContext('2d');
  if (dailyChart) {
    dailyChart.destroy();
  }

  const labels = dailyData.map(d => {
    [year, month, day] = d.date.split('-');
    return `${day}-${month}`;
  });
  const values = dailyData.map(d => d.total);

  dailyChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Daily Intake (g)',
        data: values,
        backgroundColor: '#E07B39',
        borderColor: '#2D2A26',
        borderWidth: 1,
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {display: false}
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {color: 'rgba(45, 42, 38, 0.06)'},
          ticks: {color: '#6B665E', font: {weight: 600}}
        },
        x: {
          grid: {display: false},
          ticks: {color: '#6B665E', font: {weight: 600}}
        }
      }
    }
  });
}

function updatePeriodChart(periods) {
  const ctx = document.getElementById('periodChart').getContext('2d');
  if (periodChart) {
    periodChart.destroy();
  }

  const values = Object.values(periods);
  if (values.every(v => v === 0)) {
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    ctx.font = '600 14px Nunito';
    ctx.fillStyle = '#6B665E';
    ctx.textAlign = 'center';
    ctx.fillText('No data yet', ctx.canvas.width / 2, ctx.canvas.height / 2);
    return;
  }

  const labels = Object.keys(periods);

  periodChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: ['#FFE8D9', '#F4A574', '#E07B39', '#3D3A36'],
        borderWidth: 3,
        borderColor: '#FFFAF5'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom', labels: {boxWidth: 14, padding: 10, font: {size: 11, weight: 600}, color: '#2D2A26'}
        }
      }
    }
  });
}

async function loadEntries() {
  try {
    const res = await fetch('/api/entries');
    const data = await res.json();
    const entries = data.entries || [];


    if (entries.length === 0) {
      ui.entriesList.innerHTML = `
        <div class="empty-state">
          <div class="icon-large">${iconHtml('paw')}</div>
          <p>No entries yet. Start logging!</p>
        </div>
      `;
      return;
    }

    const reversed = [...entries].reverse().slice(0, 20);
    ui.entriesList.innerHTML = reversed.map(e => `
      <div class="entry-item">
        <div class="entry-info">
          <span class="entry-date">${e.date} ${e.time}</span>
          ${e.refill_to ? `<span class="entry-refill">Refilled</span>` : ''}
          <div class="entry-details">
            Water: ${e.water_weight}g
            ${e.notes ? ` · ${e.notes}` : ''}
          </div>
        </div>
        <span class="entry-drink">${e.drink || 0}g</span>
        <button class="btn btn-danger btn-small" onclick="deleteEntry(${e.id})" title="Delete">x</button>
      </div>
    `).join('');

  } catch (err) {
    console.error('Failed to load entries:', err);
  }
}


function deleteEntry(id) {
  entryToDelete = id;
  ui.deleteModal.classList.add('active');

  ui.confirmDeleteBtn.onclick = async () => {
    try {
      const res = await fetch(`/api/entries/${entryToDelete}`, {method: 'DELETE'});
      const data = await res.json();

      if (data.success) {
        showToast('Entry deleted', 'info');
        closeDeleteModal();
        loadStats();
        loadEntries();
      }
    } catch (err) {
      showToast('Failed to delete', 'error');
    }
  };
}

function closeDeleteModal() {
  ui.deleteModal.classList.remove('active');
  entryToDelete = null;
}


// Setup tab navigation
function setupTabs() {
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

      tab.classList.add('active');
      document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
    });
  });
}

function openImportModal() {
  document.getElementById('importModal').classList.add('active');
}

function closeImportModal() {
  document.getElementById('importModal').classList.remove('active');
}

async function importData() {
  const text = ui.importText.value;
  if (!text.trim()) {
    showToast('No data to import', 'error');
    return;
  }

  try {
    const res = await fetch('/api/import-raw', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({raw_text: text})
    });
    const data = await res.json();

    if (data.success) {
      showToast(`Imported ${data.imported} entries!`, 'success');
      closeImportModal();
      ui.importText.value = '';
      loadStats();
      loadEntries();
    } else {
      showToast('Import failed', 'error');
    }
  } catch (err) {
    showToast('Import failed', 'error');
  }
}

async function updateBowlWeight() {
  const newWeight = ui.settingsBowl.value;

  try {
    const res = await fetch('/api/bowl-weight', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({bowl_weight: newWeight})
    });
    const data = await res.json();

    if (data.success) {
      bowlWeight = parseInt(newWeight);
      ui.statBowl.textContent = bowlWeight;
      showToast('Bowl weight updated!', 'success');
    }
  } catch (err) {
    showToast('Failed to update', 'error');
  }
}

function showToast(message, type = 'info') {
  const iconEl = ui.toast.querySelector('.toast-icon');
  const messageEl = ui.toast.querySelector('.toast-message');
  ui.toast.classList.remove('toast-success', 'toast-error', 'toast-info');

  let iconName;
  switch (type) {
    case 'success':
      iconName = 'check';
      ui.toast.classList.add('toast-success');
      break;
    case 'error':
      iconName = 'x-circle';
      ui.toast.classList.add('toast-error');
      break;
    case 'info':
    default:
      iconName = 'trash';
      ui.toast.classList.add('toast-info');
      break;
  }

  iconEl.innerHTML = iconHtml(iconName);
  messageEl.textContent = message;
  ui.toast.classList.add('show');
  setTimeout(() => ui.toast.classList.remove('show'), 3000);
}
