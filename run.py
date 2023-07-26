
from flask import Flask,render_template, request, redirect, url_for
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
    csv_sport = db.Column(db.String, nullable=False, unique=True)
    standard_sport = db.Column(db.String, nullable=False)

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



sports_list = [
    "Adventure Racing",
    "Aerobics",
    "AFL",
    "Archery",
    "Athletics",
    "Badminton",
    "Baseball",
    "Basketball",
    "Basketball - 3 X 3",
    "Beach Volleyball",
    "Bocce",
    "Boccia (AWD)",
    "Bowls - Indoor",
    "Bowls - Lawn",
    "Canoe Polo",
    "Cheerleading",
    "Clay Target",
    "Cricket (Outdoor)",
    "Croquet",
    "Cross Country",
    "Curling",
    "Cycling - Cyclocross",
    "Cycling - Mountain biking",
    "Cycling - Road",
    "Cycling - Track",
    "Disability Sports",
    "Diving",
    "Dragon Boats",
    "Equestrian",
    "Fencing",
    "Floorball",
    "Football (Outdoor)",
    "Futsal",
    "Golf",
    "Gymsports",
    "Handball",
    "Hockey (Outdoor)",
    "Ice Hockey",
    "Inline Hockey",
    "Judo",
    "Karate",
    "Kart Sport",
    "Kayaking - Sprint",
    "Kayaking - White Water",
    "Kilikiti",
    "Ki O Rahi",
    "Korfball",
    "Lacrosse",
    "Life saving - Surf",
    "Marching",
    "Moto-Cross",
    "Multi Sports",
    "Netball (Outdoor)",
    "Orienteering",
    "Petanque",
    "Road Racing",
    "Rowing",
    "Rugby League",
    "Rugby Sevens",
    "Rugby Union",
    "Shooting (Target)",
    "Skiing",
    "8 Ball",
    "Snowboarding",
    "Softball",
    "Sport Climbing",
    "Squash",
    "Surfing",
    "Swimming",
    "Synchronised Swimming",
    "Table tennis",
    "Tennis",
    "TenPin Bowling",
    "Touch",
    "Triathlon/Duathlon",
    "Ultimate frisbee",
    "Underwater Hockey",
    "Volleyball",
    "Waka Ama",
    "Water Polo",
    "Weightlifting",
    "Windsurfing",
    "Wrestling",
    "X Country Skiing",
    "Yachting",
]


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


def unique_sports(data):
    sports = set()
    for row in data:
        row_sports = row[4].split(',')
        for sport in row_sports:
            sports.add(sport.strip())
    return list(sports)

@app.route('/csv')
def csv_view():
    with open("form.csv", 'r') as f:
        reader = csv.reader(f)
        csv_data = list(reader)
    headings, data = cleaning(csv_data)
    return render_template('csvdata.html', headings=headings, data=data[:5])

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/assign_sports', methods=['GET', 'POST'])
def assign_sports():
    if request.method == 'POST':
        mappings = request.form.to_dict()
        for csv_sport, standard_sport in mappings.items():
            mapping = Sports.query.filter_by(csv_sport=csv_sport).first()
            if mapping:
                mapping.standard_sport = standard_sport
            else:
                mapping = Sports(csv_sport=csv_sport, standard_sport=standard_sport)
                db.session.add(mapping)
        db.session.commit()
        return redirect(url_for('results'))

    with open("form.csv", 'r') as f:
        reader = csv.reader(f)
        csv_data = list(reader)
    headings, data = cleaning(csv_data)
    unique_sports_list = unique_sports(data)

    return render_template('assign_sports.html', unique_sports=unique_sports_list, sports_list=sports_list)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Creates the instance directory if it does not exist
    app.run(debug=True)