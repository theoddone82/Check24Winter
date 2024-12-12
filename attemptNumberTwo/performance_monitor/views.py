from django.shortcuts import render
import psutil
import subprocess
import os

def performance_dashboard(request):
    # Generate the current system metrics
    metrics = {
        'cpu': psutil.cpu_percent(interval=1),
        'memory': psutil.virtual_memory()._asdict(),
        'disk': psutil.disk_usage('/')._asdict(),
    }

    # Generate the htop screenshot
    output_file = "/tmp/htop_screenshot.png"
    subprocess.run(['htop', '-C', '--no-color', '-d', '1'], stdout=open(output_file, 'wb'))

    return render(request, 'performance_monitor/dashboard.html', {
        'metrics': metrics,
        'htop_image': '/performance/static/htop_screenshot.png'  # Static path for the image
    })
