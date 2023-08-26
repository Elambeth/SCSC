
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
    gender = db.Column(db.String, nullable=False)


class Sports(db.Model):
    __tablename__ = 'standard_sports'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)


class SportMapping(db.Model):
    __tablename__ = 'sport_mapping'
    id = db.Column(db.Integer, primary_key=True)
    csv_sport = db.Column(db.String, nullable=False)
    standard_sport_id = db.Column(db.Integer, db.ForeignKey('standard_sports.id'), nullable=False)
    standard_sport = db.relationship('Sports', backref='sport_mappings')


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
    sport_id = db.Column(db.Integer, db.ForeignKey('standard_sports.id'), nullable=False)
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


def cleaning(form_list):
        # Pop the headings to a list
    headings = []
    if len(form_list) > 0:
        headings.append(form_list.pop(0))
    return headings, form_list


def unique_sports(data):
    sports = set()
    for row in data:
        row_sports = row[5].split(',')
        for sport in row_sports:
            sports.add(sport.strip())
    return list(sports)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/delete_sports', methods=['GET', 'POST'])
def delete_sports():
    if request.method == 'POST':
        sports_to_delete = request.form.getlist('sports_to_delete')
        with open("snazzy.csv", 'r') as f:
            reader = csv.reader(f)
            csv_data = list(reader)
        headings, form_list = cleaning(csv_data)
        for row in form_list:
            row_sports = row[5].split(',')
            row_sports = [sport.strip() for sport in row_sports if sport.strip() not in sports_to_delete]
            row[5] = ','.join(row_sports)
        with open("snazzy.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headings)
            writer.writerows(form_list)
        return redirect(url_for('map_sports')) # Redirecting to map_sports route
    with open("snazzy.csv", 'r') as f:
        reader = csv.reader(f)
        csv_data = list(reader)
    headings, form_list = cleaning(csv_data)
    sports = unique_sports(form_list)
    return render_template('delete_sports.html', sports=sports)


@app.route('/map_sports', methods=['GET', 'POST'])
def map_sports():
    if request.method == 'POST':
        mappings = dict(request.form)
        for csv_sport, standard_sport in mappings.items():
            standard_sport_obj = Sports.query.filter_by(name=standard_sport).first()
            if standard_sport_obj:
                # Check if a mapping for this CSV sport already exists
                existing_mapping = SportMapping.query.filter_by(csv_sport=csv_sport).first()
                if existing_mapping:
                    # Update the existing mapping
                    existing_mapping.standard_sport_id = standard_sport_obj.id
                else:
                    # Create a new mapping
                    mapping = SportMapping(csv_sport=csv_sport, standard_sport_id=standard_sport_obj.id)
                    db.session.add(mapping)
        db.session.commit()
        return redirect(url_for('display_mapping'))
    with open("snazzy.csv", 'r') as f:
        reader = csv.reader(f)
        csv_data = list(reader)
    headings, form_list = cleaning(csv_data)
    sports = unique_sports(form_list)
    return render_template('map_sports.html', sports=sports, standard_sports=sports_list)


@app.route('/display_mapping')
def display_mapping():
    mappings = db.session.query(SportMapping).join(Sports, SportMapping.standard_sport_id == Sports.id).all()
    return render_template('display_mapping.html', mappings=mappings)




@app.route('/grid')
def grid_view():
    return render_template('grid.html')


@app.route('/Netball')
def netball():
    return render_template('netball.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/adding_people')
def adding_people():
    with open("student.csv", 'r') as f:
        reader = csv.reader(f)
        people_data = list(reader)
        people_headings, people_list = cleaning(people_data)
    for i in range (len(people_list)):
        if i == len(people_list) - 1:
            break
        else:
            new_person = People(
                first_name=people_list[i][1], 
                last_name=people_list[i][0], 
                email=people_list[i][3],
                gender=people_list[i][2])
            db.session.add(new_person)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/student_list')
def student_list():
    all_people = People.query.all()  # Querying all rows from the People table
    return render_template('student_list.html', all_people=all_people)




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        for sport in sports_list:
            if not Sports.query.filter_by(name=sport).first():
                new_sport = Sports(name=sport)
                db.session.add(new_sport)
        db.session.commit()
    app.run(debug=True)