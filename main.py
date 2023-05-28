import sqlite3
import csv
from art import text2art
from tabulate import tabulate as tab


connect = sqlite3.connect('TeamBuilder.db')
c = connect.cursor()

# - 1st
def people_table():
    c.execute("DROP TABLE IF EXISTS People;")
    c.execute("""
        CREATE TABLE People(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Firstname TEXT NOT NULL,
            LastName TEXT NOT NULL,
            Email TEXT NOT NULL UNIQUE
    );
    """)    
# - 2nd
def student_table():
    c.execute("DROP TABLE IF EXISTS Students;")
    c.execute("""
        CREATE TABLE Students(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            PeopleID INTEGER NOT NULL,
            YearLevel INTEGER NOT NULL,
            FOREIGN KEY(PeopleID) REFERENCES People(ID)
        );
    """)
# - 3rd
def coach_table():
    c.execute("DROP TABLE IF EXISTS Coaches;")
    c.execute("""
    CREATE TABLE Coaches(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        PeopleID INTEGER NOT NULL,
        FOREIGN KEY(PeopleID) REFERENCES People(ID)
    );
    """)
# - 4th
def staff_table():
    c.execute("DROP TABLE IF EXISTS Staff;")
    c.execute("""
    CREATE TABLE Staff(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        PeopleID INTEGER NOT NULL,
        FOREIGN KEY(PeopleID) REFERENCES People(ID)
    );
    """)
# - 5th
def sport_table():
    c.execute("DROP TABLE IF EXISTS Sports;")
    c.execute("""
    CREATE TABLE Sports(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL
    );
    """)
# - 6th
def team_table():
    c.execute("DROP TABLE IF EXISTS Teams;")
    c.execute("""
    CREATE TABLE Teams(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        StaffID INTEGER NOT NULL,
        CoachID INTEGER NOT NULL,
        SportID INTEGER NOT NULL,
        Name TEXT NOT NULL,
        Division TEXT NOT NULL,
        FOREIGN KEY(SportID) REFERENCES Sports(ID),
        FOREIGN KEY(StaffID) REFERENCES Staff(ID),
        FOREIGN KEY(CoachID) REFERENCES Coaches(ID)
    );
    """)
# - 7th
def student_team_join():
    c.execute("DROP TABLE IF EXISTS StudentTeam;")
    c.execute("""
    CREATE TABLE StudentTeam(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        TeamID INTEGER NOT NULL,
        StudentID INTEGER NOT NULL,
        FOREIGN KEY(TeamID) REFERENCES Teams(ID),
        FOREIGN KEY(StudentID) REFERENCES Students(ID)
    );
    """)
# - 8th
def student_sport_join():
    c.execute("DROP TABLE IF EXISTS StudentSport;")
    c.execute("""
    CREATE TABLE StudentSport(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        SportID INTEGER NOT NULL,
        StudentID INTEGER NOT NULL,
        FOREIGN KEY(SportID) REFERENCES Sports(ID),
        FOREIGN KEY(StudentID) REFERENCES Students(ID)
    );
    """)

def tables():
    people_table()
    student_table()
    coach_table()
    staff_table()
    sport_table()
    team_table()
    student_team_join()
    student_sport_join()

def unique_sports(csv_data):
    sports = set()
    for row in csv_data:
        sports.add(row[6])
    return list(sports)

def cleaning(form_list):
    # Removing timestamps
    for i in form_list:
        del i[0]
    # Pop the headings to a list
    headings = []
    headings.append(form_list.pop(0))
    return headings, form_list

def readcsv(name):
    with open((name + ".csv"), 'r') as f:
        reader = csv.reader(f)
        csv_data = list(reader)

    headings, data = cleaning(csv_data)

    for r in data:
        c.execute("INSERT INTO People(Firstname, LastName, Email) VALUES (?,?,?);", (r[2], r[3], r[1]))

        # Check if the YearLevel value is not empty
        if r[4]:
            c.execute("INSERT INTO Students(PeopleID, YearLevel) VALUES (?,?);", (c.lastrowid, r[4]))

        # Check if the Sport value is not empty
        if r[5]:
            c.execute("INSERT INTO Sports(Name) VALUES (?);", (r[5],))
            sport_id = c.lastrowid
        else:
            sport_id = None

        # Check if the Health Info value is not empty
        if r[6]:
            c.execute("INSERT INTO StudentSport(SportID, StudentID) VALUES (?,?);", (sport_id, c.lastrowid))

        # Check if the Payment method value is not empty
        if r[7]:
            c.execute("INSERT INTO Staff(PeopleID) VALUES (?);", (c.lastrowid,))

    connect.commit()

def read_coaches_staff_csv(name):
    with open((name + ".csv"), 'r') as f:
        reader = csv.reader(f)
        csv_data = list(reader)

    headings, data = cleaning(csv_data)

    for r in data:
        # Check if the person is already in the People table
        c.execute("SELECT ID FROM People WHERE Email = ?;", (r[0],))
        person = c.fetchone()

        if person:
            person_id = person[0]
        else:
            # Insert the person into the People table
            c.execute("INSERT INTO People(Firstname, LastName, Email) VALUES (?,?,?);", (r[1], r[2], r[0]))
            person_id = c.lastrowid

        if r[2] == "Coach":
            # Insert the coach into the Coaches table
            c.execute("INSERT INTO Coaches(PeopleID) VALUES (?);", (person_id,))
        elif r[2] == "Staff":
            # Insert the staff member into the Staff table
            c.execute("INSERT INTO Staff(PeopleID) VALUES (?);", (person_id,))

    connect.commit()

def sort_players_into_teams():
    teams = []
    team_id = 1

    while True:
        print("\n1. Create a new team")
        print("2. Add a student to a new team")
        print("3. Add a student to an existing team")
        print("4. Done sorting players into teams")

        choice = input("Enter your choice: ")

        if choice == "1":
            team_name = input("Enter the name of the new team: ")
            teams.append((team_id, team_name))
            team_id += 1
            print(f"Team '{team_name}' created.")

        elif choice == "2":
            student_id = int(input("Enter the ID of the student: "))
            team_name = input("Enter the name of the new team: ")
            teams.append((team_id, team_name))
            c.execute("INSERT INTO StudentTeam(TeamID, StudentID) VALUES (?,?);", (team_id, student_id))
            team_id += 1
            print(f"Student added to the new team '{team_name}'.")

        elif choice == "3":
            student_id = int(input("Enter the ID of the student: "))
            if len(teams) > 0:
                print("Existing Teams:")
                for team in teams:
                    print(f"Team ID: {team[0]}, Team Name: {team[1]}")
                team_id = int(input("Enter the ID of the existing team: "))
                c.execute("INSERT INTO StudentTeam(TeamID, StudentID) VALUES (?,?);", (team_id, student_id))
                print(f"Student added to the existing team with ID: {team_id}.")
            else:
                print("No existing teams.")

        elif choice == "4":
            break

        else:
            print("Invalid choice. Please try again.")

    connect.commit()

    print("Players sorted into teams successfully!")

def search_database():
    while True:
        print("\nSearch Database:")
        print("1. Retrieve all students")
        print("2. Retrieve all coaches")
        print("3. Retrieve all staff members")
        print("4. Retrieve all teams")
        print("5. Retrieve all players in a specific team")
        print("6. Retrieve all sports")
        print("7. Retrieve all students participating in a specific sport")
        print("8. Retrieve the number of students in each team")
        print("9. Back to main menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            c.execute("SELECT * FROM Students")
            students = c.fetchall()
            print(tab(students, headers=[description[0] for description in c.description], tablefmt='psql'))

        elif choice == "2":
            c.execute("SELECT * FROM Coaches")
            coaches = c.fetchall()
            print(tab(coaches, headers=[description[0] for description in c.description], tablefmt='psql'))

        elif choice == "3":
            c.execute("SELECT * FROM Staff")
            staff_members = c.fetchall()
            print(tab(staff_members, headers=[description[0] for description in c.description], tablefmt='psql'))

        elif choice == "4":
            c.execute("SELECT * FROM Teams")
            teams = c.fetchall()
            print(tab(teams, headers=[description[0] for description in c.description], tablefmt='psql'))

        elif choice == "5":
            team_id = int(input("Enter the team ID: "))
            c.execute("SELECT Students.* FROM Students JOIN StudentTeam ON Students.ID = StudentTeam.StudentID WHERE StudentTeam.TeamID = ?", (team_id,))
            team_players = c.fetchall()
            print(tab(team_players, headers=[description[0] for description in c.description], tablefmt='psql'))

        elif choice == "6":
            c.execute("SELECT * FROM Sports")
            sports = c.fetchall()
            print(tab(sports, headers=[description[0] for description in c.description], tablefmt='psql'))

        elif choice == "7":
            sport_id = int(input("Enter the sport ID: "))
            c.execute("SELECT Students.* FROM Students JOIN StudentSport ON Students.ID = StudentSport.StudentID WHERE StudentSport.SportID = ?", (sport_id,))
            sport_participants = c.fetchall()
            print(tab(sport_participants, headers=[description[0] for description in c.description], tablefmt='psql'))

        elif choice == "8":
            c.execute("SELECT TeamID, COUNT(*) FROM StudentTeam GROUP BY TeamID")
            team_sizes = c.fetchall()
            print(tab(team_sizes, headers=["TeamID", "Count"], tablefmt='psql'))

        elif choice == "9":
            break

        else:
            print("Invalid choice. Please try again.")


def main():
    title = text2art("TEAMBUILDER")
    print(title)
    tables()
    readcsv("csv3")
    read_coaches_staff_csv("coaches_staff")

    while True:
        print("\nMain Menu:")
        print("1. Search Database")
        print("2. Sort players into teams")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            search_database()

        elif choice == "2":
            sort_players_into_teams()

        elif choice == "3":
            break

        else:
            print("Invalid choice. Please try again.")


main()