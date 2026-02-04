let bowlWeight = 0;
let dailyChart = null;
let periodChart = null;
let entryToDelete = null;
let entryToEdit = null;

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

  // Edit modal elements
  ui.editModal = document.getElementById('editModal');
  ui.editForm = document.getElementById('editForm');
  ui.editEntryId = document.getElementById('editEntryId');
  ui.editDate = document.getElementById('editDate');
  ui.editTime = document.getElementById('editTime');
  ui.editTotal = document.getElementById('editTotal');
  ui.editDrink = document.getElementById('editDrink');
  ui.editRefill = document.getElementById('editRefill');
  ui.editNotes = document.getElementById('editNotes');
  ui.editWaterHint = document.getElementById('editWaterHint');

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
  setupEditFormHandlers();
});

function escapeHtml(text) {
  if (text === null || text === undefined) {
    return '';
  }
  return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
}

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

function setupEditFormHandlers() {
  ui.editForm.addEventListener('submit', handleEditFormSubmit);
  ui.editTotal.addEventListener('input', handleEditTotalWeightInput);
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

function handleEditTotalWeightInput(e) {
  const total = parseInt(e.target.value);
  if (total) {
    const water = total - bowlWeight;
    ui.editWaterHint.textContent = `= ${water}g water`;
  } else {
    ui.editWaterHint.textContent = '';
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
          <span class="entry-date">${escapeHtml(e.date)} ${escapeHtml(e.time)}</span>
          ${e.refill_to ? `<span class="entry-refill">Refilled</span>` : ''}
          <div class="entry-details">
            Water: ${e.water_weight}g
            ${e.notes ? ` · ${escapeHtml(e.notes)}` : ''}
          </div>
        </div>
        <span class="entry-drink">${e.drink || 0}g</span>
        <div class="entry-actions">
          <button class="btn btn-icon btn-edit" onclick="editEntry(${e.id})" title="Edit">
            ${iconHtml('edit')}
          </button>
          <button class="btn btn-icon btn-delete" onclick="deleteEntry(${e.id})" title="Delete">
            ${iconHtml('trash')}
          </button>
        </div>
      </div>
    `).join('');

  } catch (err) {
    console.error('Failed to load entries:', err);
  }
}

async function editEntry(id) {
  try {
    const res = await fetch(`/api/entries/${id}`);
    const data = await res.json();
    if (!data.success) {
      showToast('Failed to load entry', 'error');
      return;
    }

    const entry = data.entry;
    entryToEdit = id;

    ui.editEntryId.value = entry.id;
    ui.editDate.value = entry.date;
    ui.editTime.value = entry.time;
    ui.editTotal.value = entry.total_weight;
    ui.editDrink.value = entry.drink || 0;
    ui.editRefill.value = entry.refill_to || '';
    ui.editNotes.value = entry.notes || '';

    const water = entry.total_weight - bowlWeight;
    ui.editWaterHint.textContent = `= ${water}g water`;
    ui.editModal.classList.add('active');
  } catch (err) {
    showToast('Failed to load entry', 'error');
  }
}

async function handleEditFormSubmit(e) {
  e.preventDefault();

  const entryId = ui.editEntryId.value;
  const updateData = {
    date: ui.editDate.value,
    time: ui.editTime.value,
    total_weight: parseInt(ui.editTotal.value),
    drink: parseInt(ui.editDrink.value) || 0,
    refill_to: ui.editRefill.value ? parseInt(ui.editRefill.value) : null,
    notes: ui.editNotes.value || ""
  };

  try {
    const res = await fetch(`/api/entries/${entryId}`, {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(updateData)
    });
    const data = await res.json();

    if (data.success) {
      showToast('Entry updated!', 'success');
      closeEditModal();
      loadStats();
      loadEntries();
    } else {
      showToast('Error: ' + data.error, 'error');
    }
  } catch (err) {
    showToast('Failed to update entry', 'error');
  }
}

function closeEditModal() {
  ui.editModal.classList.remove('active');
  entryToEdit = null;
  ui.editForm.reset();
  ui.editWaterHint.textContent = '';
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
