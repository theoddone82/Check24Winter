# Streaming Table App

This project is a Django-based application designed to provide users with tailored streaming options for football games based on their selected clubs and leagues. It dynamically fetches and displays available streaming packages, annotates prices, calculates costs, and determines optimal package combinations for users.

## Features
- **Dynamic Querying**: Retrieve relevant games, tournaments, and streaming offers based on user selections.
- **Cost Analysis**: Compute costs for streaming packages, including support for annual-only subscriptions.
- **Caching**: Enhance performance by caching results using Django's caching framework.
- **Intelligent Selection**: Determine the best combination of streaming packages based on coverage-to-cost ratios.
- **Responsive Templates**: User-friendly HTML templates render the data for seamless user experience.

---

## How Django Works
Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design. Here's how Django operates in this project:
1. **Models**: Represent data structures such as `game`, `clubs`, `lieges`, `streaming_package`, and `streaming_offer` in the database.
2. **Views**: Handle the business logic for fetching, processing, and passing data to templates. Key views in this project include:
   - `homepage`: Renders the home page for initial user interaction.
   - `display_table`: Processes user selections, retrieves relevant data, computes costs, and renders results.
   - `streaming_table`: Displays a detailed table of streaming options.
3. **Templates**: Use the Django template language to render dynamic HTML pages.
4. **Caching**: Improve efficiency by storing query results and computation outputs to minimize redundant operations.

---

## Project Workflow

1. **User Interaction**: Users select their favorite clubs and leagues on the homepage.
2. **Data Processing**: The `display_table` view processes the selections:
   - Fetches games and streaming offers based on user criteria.
   - Computes cost-effective streaming options.
   - Annotates packages with price details.
   - Builds availability and coverage data for user-selected tournaments.
3. **Results Display**: The `result-v3.html` template dynamically renders the final results, showing available streaming packages, their costs, and coverage information.

---

## Deployment

The application is deployed using **Gunicorn** as the WSGI server and **NGINX** as the reverse proxy. Here's a step-by-step guide for deployment:

### Prerequisites
- Install **Python 3.x**, **Django**, **Gunicorn**, and **NGINX** on your server.
- Ensure you have PostgreSQL or your database of choice set up.

### Deployment Steps

#### 1. Collect Static Files
Run the following command to gather static assets:
```bash
python manage.py collectstatic
```

#### 2. Configure Gunicorn
Run Gunicorn to serve your Django app:
```bash
gunicorn project_name.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

#### 3. Configure NGINX
Create an NGINX server block for your app:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /path/to/your/static/files;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```
Reload NGINX to apply changes:
```bash
sudo systemctl reload nginx
```

#### 4. Run Gunicorn as a Service
Create a systemd service for Gunicorn:
```bash
sudo nano /etc/systemd/system/gunicorn.service
```
Add the following configuration:
```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=youruser
Group=yourgroup
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/your/venv/bin/gunicorn --workers 3 --bind unix:/path/to/your/project/gunicorn.sock project_name.wsgi:application

[Install]
WantedBy=multi-user.target
```
Start and enable the service:
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

---

## About This Project

This application is part of **GENDEV**, a project for **Check24** that focuses on dynamic streaming data aggregation and optimization. It integrates data from various sources to provide users with actionable insights into streaming packages and options.

Key Objectives:
- Optimize user experience by presenting cost-efficient streaming options.
- Implement advanced caching mechanisms for high performance.
- Leverage Django's robust features to handle complex data querying and processing.