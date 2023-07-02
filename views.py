from flask import Blueprint, render_template
from .models import People  # Import your models
from . import db  # Import the db instance

auth = Blueprint('auth', __name__)


@auth.route('home')
def homePage():
    # Fetch data from db table

    # Mock data
    students = [
        {
            "firstName": "Ethan",
            "lastName": "Lambeth"
        }, 
        {
            "firstName": "Oscar",
            "lastName": "Lambeth"
        }
    ]
    return render_template('home.html', students=students)
