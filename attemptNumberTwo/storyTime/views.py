from django.shortcuts import render
import os
from django.conf import settings
def story(request):
    images_path = os.path.join(settings.BASE_DIR, 'static/images')
    
    # Get a list of all files in the folder
    image_files = [
        f"images/{filename}" for filename in os.listdir(images_path)
        if filename.endswith(('jpg', 'jpeg', 'png', 'gif'))
    ]    
    return render(request,'story.html', {'images': image_files})

def shooting_stars(request):
    images_path = os.path.join(settings.BASE_DIR, 'static/images')
    
    # Get a list of all files in the folder
    image_files = [
        f"images/{filename}" for filename in os.listdir(images_path)
        if filename.endswith(('jpg', 'jpeg', 'png', 'gif'))
    ]    
    return render(request,'shooting_stars.html',{'images': image_files})

def timeline(request):
    return render(request,'timeline.html')

def story22(request):
    images_path = os.path.join(settings.BASE_DIR, 'static/images/2022')
    
    # Get a list of all files in the folder
    image_files = [
        f"images/2022/{filename}" for filename in os.listdir(images_path)
        if filename.endswith(('jpg', 'jpeg', 'png', 'gif'))
    ]    
    return render(request,'shooting_stars_story.html', {'images': image_files, 'year': 2023, 'last_digit': 2})

def story23(request):
    images_path = os.path.join(settings.BASE_DIR, 'static/images/2023')
    
    # Get a list of all files in the folder
    image_files = [
        f"images/2023/{filename}" for filename in os.listdir(images_path)
        if filename.endswith(('jpg', 'jpeg', 'png', 'gif'))
    ]    
    return render(request,'shooting_stars_story.html', {'images': image_files, 'year': 2024, 'last_digit': 3})

def story24(request):
    images_path = os.path.join(settings.BASE_DIR, 'static/images/2024' )
    
    # Get a list of all files in the folder
    image_files = [
        f"images/2024/{filename}" for filename in os.listdir(images_path)
        if filename.endswith(('jpg', 'jpeg', 'png', 'gif'))
    ]    
    return render(request,'shooting_stars_story.html', {'images': image_files, 'year': 2024, 'last_digit': 4})