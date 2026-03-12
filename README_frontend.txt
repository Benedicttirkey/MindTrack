MindTrack frontend package

Included
- templates/base.html
- templates/home.html
- templates/daily_record.html
- templates/data_visualizations.html
- templates/profile.html
- refreshed templates/login.html
- refreshed templates/register.html
- static/css/style.css
- static/js/main.js
- static/js/daily-record.js
- static/js/dashboard.js
- small URL/view additions in account/views.py and account/urls.py
- static files setting added to IT_Project/settings.py

Pages created
- /home/
- /daily-record/
- /data-visualizations/
- /profile/

Notes
- The charts use Chart.js from CDN.
- The visualization page currently uses demo sample data in JavaScript.
  Replace those arrays with backend values or pass JSON from Django context.
- The daily record form is frontend-ready, but save logic still needs to be connected to your POST handling.
- Django was not installed in this container, so I could not run `manage.py` locally for a full verification.

venv

Database settings
- Default database is now SQLite (works out-of-the-box).
- To use MySQL, set:
  - `USE_MYSQL=True`
  - `MYSQL_DB`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_PORT`

Email settings
- Default email backend is console (verification codes print in terminal).
- To send real emails, set:
  - `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
  - `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`
