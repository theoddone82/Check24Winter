from django.shortcuts import render
from models import game, streaming_package, streaming_offer
import csv

# Create your views here.

def setUpDb():
    with open('your_file.csv', mode='r', newline='') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            print(row)
