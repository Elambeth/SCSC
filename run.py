
from flask import Flask,render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
import csv
from csv import field_size_limit



db = SQLAlchemy()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db.init_app(app)

#=========================================================
# Models
#=========================================================
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
    person = db.relationship('People', backref='students')
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
    
    # Add a unique constraint for student_id and team_id
    __table_args__ = (db.UniqueConstraint('student_id', 'team_id', name='_student_team_uc'),)


class StudentSport(db.Model):
    __tablename__ = 'student_sport'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    sport_id = db.Column(db.Integer, db.ForeignKey('standard_sports.id'), nullable=False)
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
    "Other",
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
        field_size_limit(int(1e6))
        with open("form.csv", 'r') as f:
            reader = csv.reader(f)
            csv_data = list(reader)
        headings, form_list = cleaning(csv_data)
        for row in form_list:
            row_sports = row[5].split(',')
            row_sports = [sport.strip() for sport in row_sports if sport.strip() not in sports_to_delete]
            row[5] = ','.join(row_sports)
        with open("form.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headings)
            writer.writerows(form_list)
        return redirect(url_for('map_sports'))# Redirecting to map_sports route
    field_size_limit(int(1e6))
    with open("form.csv", 'r') as f:
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
        return redirect(url_for('other_map'))
    field_size_limit(int(1e6))
    with open("form.csv", 'r') as f:
        reader = csv.reader(f)
        csv_data = list(reader)
    headings, form_list = cleaning(csv_data)
    sports = unique_sports(form_list)
    return render_template('map_sports.html', sports=sports, standard_sports=sports_list)


@app.route('/other_map', methods=['GET', 'POST'])
def other_map():
    if request.method == 'POST':
        mappings = dict(request.form)
        for csv_sport, standard_sport in mappings.items():
            # Check if the new sport already exists
            standard_sport_obj = Sports.query.filter_by(name=standard_sport).first()
            if not standard_sport_obj:
                # Create a new sport entry
                standard_sport_obj = Sports(name=standard_sport)
                db.session.add(standard_sport_obj)
                db.session.commit()
            
            # Update the existing mapping
            existing_mapping = SportMapping.query.filter_by(csv_sport=csv_sport).first()
            if existing_mapping:
                existing_mapping.standard_sport_id = standard_sport_obj.id
                
        db.session.commit()
        return redirect(url_for('display_mapping'))

    # Fetch all sports previously mapped as "Other"
    other_sports = SportMapping.query.join(
        Sports, SportMapping.standard_sport_id == Sports.id
    ).filter(Sports.name == 'Other').all()

    return render_template('other_map.html', other_sports=other_sports)


@app.route('/display_mapping')
def display_mapping():
    mappings = db.session.query(SportMapping).join(Sports, SportMapping.standard_sport_id == Sports.id).all()
    return render_template('display_mapping.html', mappings=mappings)


@app.route('/sports')
def display_sports():
    sports_data = db.session.query(SportMapping.id, Sports.name).join(Sports, Sports.id == SportMapping.standard_sport_id).all()
    return render_template('sports.html', sports_data=sports_data)

@app.route('/dashboard')
def dashboard():
    # Querying Sports which are mapped in SportMapping table
    sports = db.session.query(Sports).join(
        SportMapping, Sports.id == SportMapping.standard_sport_id
    ).distinct().all()
    return render_template('dashboard.html', sports=sports)


@app.route('/adding_people')
def adding_people():
    field_size_limit(int(1e6))
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
    return redirect(url_for('populating_students'))


@app.route('/populating_students')
def populating_students():
    #where email is in form.csv 
    field_size_limit(int(1e6))
    with open("form.csv", 'r') as f:
            reader = csv.reader(f)
            csv_data = list(reader)
            headings, listy = cleaning(csv_data)
    # Extract the relevant information from each row
    for row in listy:
        email = row[2].replace(" ","").lower()
        print(email)
        year_level = row[4]
        health_info = row[6]
        payment_method = row[9]
 # Query the People table to get the ID of the person with this email
        person = People.query.filter_by(email=email).first()
        if person:
            # Create a new Student record for this person
            new_student = Students(
                people_id=person.id,
                year_level=year_level,
                health_info=health_info,
                payment_method=payment_method
            )
            
            # Add to the session
            db.session.add(new_student)
                
            # Commit the session to insert all new Students
    db.session.commit()
    return redirect(url_for('link_students_sports'))


@app.route('/link_students_sports')
def link_students_sports():
    # Open the CSV
    field_size_limit(int(1e6))
    with open("form.csv", 'r') as f:
        reader = csv.reader(f)
        csv_data = list(reader)
        headings, bulk = cleaning(csv_data)
    
    # Iterate over each row to get student details
    for row in bulk:
        email = row[2].replace(" ","").lower()
        
        # Get people_id using the email
        person = People.query.filter_by(email=email).first()
        if not person:
            # Skip to the next row if the person with this email is not found
            continue
        
        # Get student_id using the people_id
        student = Students.query.filter_by(people_id=person.id).first()
        if not student:
            # Skip to the next row if the student with this people_id is not found
            continue
        
        # Get the sports the student plays
        student_sports = row[5].split(',')
        
        # For each sport, get the sport_id and add an entry in the StudentSport table
        for sport_name in student_sports:
            sport_name = sport_name.strip()  # Remove any leading or trailing whitespaces
            sport = SportMapping.query.filter_by(csv_sport=sport_name).first()
            if sport:
                # Check if this mapping already exists
                existing_entry = StudentSport.query.filter_by(student_id=student.id, sport_id=sport.standard_sport_id).first()
                if not existing_entry:
                    new_student_sport = StudentSport(student_id=student.id, sport_id=sport.standard_sport_id)
                    db.session.add(new_student_sport)
    
    # Commit the changes to the database
    db.session.commit()

    return redirect(url_for('dashboard'))


@app.route('/student_list')
def student_list():
    students = Students.query.all()
    return render_template('student_list.html', students=students)


@app.route('/people_list')
def people_list():
    all_people = People.query.all()  # Querying all rows from the People table
    return render_template('people_list.html', all_people=all_people)


@app.route('/display_student_sports')
def display_student_sports():
    # Fetching all entries from StudentSport and joining with Students and Sports to fetch related data
    student_sports = db.session.query(
        StudentSport, Students, People, Sports
    ).join(
        Students, StudentSport.student_id == Students.id
    ).join(
        People, Students.people_id == People.id
    ).join(
        Sports, StudentSport.sport_id == Sports.id
    ).all()

    # Preparing data for display
    display_data = [
        {
            "student_name": f"{entry.People.first_name} {entry.People.last_name}",
            "sport_name": entry.Sports.name
        }
        for entry in student_sports
    ]

    return render_template('student_sport_list.html', display_data=display_data)


@app.route('/sport/<int:sport_id>')
def sport_detail(sport_id):
    sport = Sports.query.get_or_404(sport_id)
    teams = Teams.query.filter_by(sport_id=sport_id).all()

    # Fetch all students who play the sport
    students_for_sport = db.session.query(Students).join(
        StudentSport, Students.id == StudentSport.student_id
    ).filter(StudentSport.sport_id == sport_id).all()

    # Fetch student-team pairs for the sport
    students_with_teams = db.session.query(Students, Teams).join(
        StudentTeam, Students.id == StudentTeam.student_id
    ).join(
        Teams, Teams.id == StudentTeam.team_id
    ).filter(Teams.sport_id == sport_id).all()

    # Create a dictionary to map student IDs to their teams
    student_team_map = {}
    for student, team in students_with_teams:
        student_team_map[student.id] = team

    return render_template('sport_detail.html', sport=sport, teams=teams, students=students_for_sport, student_team_map=student_team_map)


@app.route('/team/<int:team_id>')
def team_details(team_id):
    team = Teams.query.get_or_404(team_id)
    
    # Fetch the students associated with this team
    students_in_team = db.session.query(Students).join(
        StudentTeam, Students.id == StudentTeam.student_id
    ).filter(StudentTeam.team_id == team_id).all()

    return render_template('team_detail.html', team=team, students=students_in_team)


@app.route('/student_profile/<int:student_id>')
def student_profile(student_id):
    student = Students.query.get_or_404(student_id)
        
    # Fetch the sports and possible teams for the student
    student_sports_teams = db.session.query(
        Sports.id, Sports.name, Teams.id, Teams.name
    ).join(
        StudentSport, Sports.id == StudentSport.sport_id
    ).outerjoin(
        StudentTeam, StudentSport.student_id == StudentTeam.student_id
    ).outerjoin(
        Teams, and_(StudentTeam.team_id == Teams.id, StudentSport.sport_id == Teams.sport_id)
    ).filter(
        StudentSport.student_id == student_id
    ).all()

    sports_teams = [
        {
            "sport_id": sport_team[0],
            "sport_name": sport_team[1],
            "team_id": sport_team[2],
            "team_name": sport_team[3] or "NOT ASSIGNED"
        }
        for sport_team in student_sports_teams
    ]



    return render_template('student_profile.html', student=student, sports_teams=sports_teams)




@app.route('/sports_grid')
def sports_grid():
    sports = db.session.query(Sports).join(
        SportMapping, Sports.id == SportMapping.standard_sport_id
    ).distinct().all()

    sports_data = []
    for sport in sports:
        # Count the number of students playing this sport
        num_students = StudentSport.query.filter_by(sport_id=sport.id).count()
        
        # Count the number of teams for this sport
        num_teams = Teams.query.filter_by(sport_id=sport.id).count()

        sports_data.append({
            "sport": sport,
            "num_students": num_students,
            "num_teams": num_teams
        })

    return render_template('sports_grid.html', sports_data=sports_data)


#*---------------------------------------------------------------
#* These are the functional functions (User Actions)
#*---------------------------------------------------------------


@app.route('/create_team/<int:sport_id>', methods=['GET', 'POST'])
def create_team(sport_id):
    sport = Sports.query.get_or_404(sport_id)
    
    if request.method == 'POST':
        team_name = request.form.get('team_name')
        division = request.form.get('division')
        # For now, we'll set a placeholder for staff_id and coach_id. You can later update this logic to select staff and coach from your database.
        staff_id = 1
        coach_id = 1
        
        new_team = Teams(name=team_name, division=division, sport_id=sport_id, staff_id=staff_id, coach_id=coach_id)
        db.session.add(new_team)
        db.session.commit()
        
        return redirect(url_for('sport_detail', sport_id=sport_id))
    
    return render_template('create_team.html', sport=sport)


@app.route('/add_student_to_team/<int:student_id>', methods=['GET', 'POST'])
def add_student_to_team(student_id):
    student = Students.query.get_or_404(student_id)
    
    # Fetch all sports associated with the student
    student_sports_ids = [mapping.sport_id for mapping in StudentSport.query.filter_by(student_id=student_id).all()]

    # Fetch teams only associated with the sports that the student plays
    teams = Teams.query.filter(Teams.sport_id.in_(student_sports_ids)).all()

    if request.method == 'POST':
        team_id = request.form.get('team')
        if team_id:
            # Check if the student is already associated with the selected team
            existing_association = StudentTeam.query.filter_by(student_id=student_id, team_id=team_id).first()
            if not existing_association:
                # Add student to the selected team
                new_student_team = StudentTeam(student_id=student_id, team_id=team_id)
                db.session.add(new_student_team)
                db.session.commit()

            # Redirect to the sport details of the team's sport
            team = Teams.query.get(team_id)
            return redirect(url_for('sport_detail', sport_id=team.sport_id))
    
    return render_template('add_student_to_team.html', student=student, teams=teams)





if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        for sport in sports_list:
            if not Sports.query.filter_by(name=sport).first():
                new_sport = Sports(name=sport)
                db.session.add(new_sport)
        db.session.commit()
    app.run(debug=True)