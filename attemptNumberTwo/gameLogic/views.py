from django.shortcuts import render
from .forms import selects

# Create your views here.
def index(request):
    if request.method == "POST":
        form = selects.BookFilterForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            author = form.cleaned_data['author']
            publisher = form.cleaned_data['publisher']
            return render(request, 'index.html', {'form': form, 'category': category, 'author': author, 'publisher': publisher})
        
    else:
        form = selects.BookFilterForm()
        return render(request, 'index.html', {'form': form})
    return render(request, 'index.html')
