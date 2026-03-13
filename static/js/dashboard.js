document.addEventListener('DOMContentLoaded', () => {
  // alert("new dashboard.js loaded");

  const readJSON = (id, fallback = []) => {
    const el = document.getElementById(id);
    if (!el || !el.textContent.trim()) return fallback;
    try {
      return JSON.parse(el.textContent);
    } catch (error) {
      console.error(`Failed to parse JSON from #${id}:`, error);
      return fallback;
    }
  };

  const labels = readJSON('week-labels', ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']);
  const moodData = readJSON('mood-data', []);
  const stressData = readJSON('stress-data', []);
  const anxietyData = readJSON('anxiety-data', []);
  const sleepData = readJSON('sleep-data', []);
  const exerciseData = readJSON('exercise-data', []);
  const studyData = readJSON('study-data', []);

  const createChart = (canvasId, config) => {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    new Chart(canvas, config);
  };

  createChart('moodChart', {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'Mood', data: moodData, tension: 0.35, spanGaps: true },
        { label: 'Stress', data: stressData, tension: 0.35, spanGaps: true },
        { label: 'Anxiety', data: anxietyData, tension: 0.35, spanGaps: true }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { min: 0, max: 5, ticks: { stepSize: 1 } }
      }
    }
  });

  createChart('sleepChart', {
    type: 'bar',
    data: {
      labels,
      datasets: [{ label: 'Hours slept', data: sleepData }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true, suggestedMax: 10 }
      }
    }
  });

  createChart('exerciseChart', {
    type: 'bar',
    data: {
      labels,
      datasets: [{ label: 'Exercise mins', data: exerciseData }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true }
      }
    }
  });

  createChart('studyChart', {
    type: 'line',
    data: {
      labels,
      datasets: [{ label: 'Study hours', data: studyData, tension: 0.35, spanGaps: true }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
});










