document.addEventListener('DOMContentLoaded', () => {
  const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  new Chart(document.getElementById('moodChart'), {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'Mood', data: [3, 4, 4, 5, 4, 3, 5], tension: 0.35 },
        { label: 'Stress', data: [2, 3, 3, 4, 4, 3, 4], tension: 0.35 },
        { label: 'Anxiety', data: [2, 2, 3, 3, 4, 3, 4], tension: 0.35 }
      ]
    },
    options: { responsive: true, maintainAspectRatio: false, scales: { y: { min: 0, max: 5, ticks: { stepSize: 1 }}}}
  });

  new Chart(document.getElementById('sleepChart'), {
    type: 'bar',
    data: { labels, datasets: [{ label: 'Hours slept', data: [7.2, 7.5, 6.8, 8.1, 7.4, 7.0, 7.6] }] },
    options: { responsive: true, maintainAspectRatio: false }
  });

  new Chart(document.getElementById('exerciseChart'), {
    type: 'bar',
    data: { labels, datasets: [{ label: 'Exercise mins', data: [20, 45, 0, 30, 60, 0, 35] }] },
    options: { responsive: true, maintainAspectRatio: false }
  });

  new Chart(document.getElementById('studyChart'), {
    type: 'line',
    data: { labels, datasets: [{ label: 'Study hours', data: [4, 5, 6.5, 5.5, 4.5, 3, 5] , tension: 0.35}] },
    options: { responsive: true, maintainAspectRatio: false }
  });
});
