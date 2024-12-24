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
    images_path = os.path.join(settings.BASE_DIR, 'static/images')
    
    # Get a list of all files in the folder
    image_files = [
        f"images/{filename}" for filename in os.listdir(images_path)
        if filename.endswith(('jpg', 'jpeg', 'png', 'gif'))
    ]    
    return render(request,'shooting_stars_story.html', {'images': image_files})

def story23(request):
    images_path = os.path.join(settings.BASE_DIR, 'static/images')
    
    # Get a list of all files in the folder
    image_files = [
        f"images/{filename}" for filename in os.listdir(images_path)
        if filename.endswith(('jpg', 'jpeg', 'png', 'gif'))
    ]    
    return render(request,'shooting_stars_story.html', {'images': image_files})

def story24(request):
    images_path = os.path.join(settings.BASE_DIR, 'static/images')
    
    # Get a list of all files in the folder
    image_files = [
        f"images/{filename}" for filename in os.listdir(images_path)
        if filename.endswith(('jpg', 'jpeg', 'png', 'gif'))
    ]    
    return render(request,'shooting_stars_story.html', {'images': image_files})