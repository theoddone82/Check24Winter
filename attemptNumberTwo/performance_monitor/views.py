import psutil
from django.http import JsonResponse
import subprocess

def get_metrics(request):
    metrics = {
        'cpu': psutil.cpu_percent(interval=1),
        'memory': psutil.virtual_memory()._asdict(),
        'disk': psutil.disk_usage('/')._asdict(),
    }
    return JsonResponse(metrics)

def get_htop_screenshot(request):
    # Save the htop screenshot to a temporary file
    output_file = "/tmp/htop_screenshot.png"
    subprocess.run(['htop', '-C', '--no-color', '-d', '1'], stdout=open(output_file, 'wb'))
    return JsonResponse({'image_path': output_file})
