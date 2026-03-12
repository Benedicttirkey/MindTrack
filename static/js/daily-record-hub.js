document.addEventListener('DOMContentLoaded', () => {
  const dateInput = document.getElementById('record_date');
  const links = document.querySelectorAll('.record-choice-card');

  if (!dateInput) {
    return;
  }

  if (!dateInput.value) {
    dateInput.value = new Date().toISOString().split('T')[0];
  }

  const syncLinks = () => {
    const recordDate = dateInput.value;
    links.forEach(link => {
      const url = new URL(link.href, window.location.origin);
      if (recordDate) {
        url.searchParams.set('record_date', recordDate);
      }
      link.href = url.pathname + url.search;
    });
  };

  dateInput.addEventListener('input', syncLinks);
  syncLinks();
});
