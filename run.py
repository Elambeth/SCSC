
from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
import csv


db = SQLAlchemy()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db.init_app(app)

#=========================================================
# Models
class People(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)

class Sports(db.Model):
    __tablename__ = 'sports'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

class Students(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    year_level = db.Column(db.String, nullable=False)
    health_info = db.Column(db.String)
    payment_method = db.Column(db.String)

class StaffType(db.Model):
    __tablename__ = 'staff_type'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False, unique=True)

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    staff_type_id = db.Column(db.Integer, db.ForeignKey('staff_type.id'), nullable=False)

class Other(db.Model):
    __tablename__ = 'other'
    id = db.Column(db.Integer, primary_key=True)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    name = db.Column(db.String)

class Teams(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    sport_id = db.Column(db.Integer, db.ForeignKey('sports.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    division = db.Column(db.String, nullable=False)

class StudentTeam(db.Model):
    __tablename__ = 'student_team'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
#=========================================================






'''
def unique_sports(csv_data):
    sports = set()
    for row in csv_data:
        sports.add(row[6])
    return list(sports)

'''
def cleaning(form_list):
        # Pop the headings to a list
    headings = []
    if len(form_list) > 0:
        headings.append(form_list.pop(0))
    #remove the uneeded parts from the csv, this could be done by the user...
    for i in form_list:
        if len(i) > 9:
            del i[9]
        if len(i) > 8:
            del i[8]
        if len(i) > 7:
            del i[7]
        if len(i) > 0:
            del i[0]

    return headings, form_list


'''
with open("form.csv", 'r') as f:
    reader = csv.reader(f)
    csv_data = list(reader)
headings, data = cleaning(csv_data)
'''

@app.route('/csv')
def csv_view():
    with open("form.csv", 'r') as f:
        reader = csv.reader(f)
        csv_data = list(reader)
    headings, data = cleaning(csv_data)
    return render_template('csvdata.html', headings=headings, data=data[:5])  # Pass first 5 rows of data


@app.route('/')
def home():
    return render_template('home.html')

'''
# Move this into views.py
@app.route('/')
def index():
    new_person = People(first_name='Steve', last_name='Stevenson', email='jhdfgw4e5sdfgsdfajojs76@example.com')
    db.session.add(new_person)
    db.session.commit()
    students = People.query.all()
    return render_template('index.html', students=students)
'''

if __name__ == "__main__":
    with app.app_context():
        db.create_all() # This creates the instance directory if does not exist
    app.run(debug=True)