import sqlite3
import random
import csv
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

def readcsv(name):
    with open((name + ".csv"), 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row
        for r in reader:
            c.execute("INSERT INTO People(Firstname, LastName, Email) VALUES (?,?,?);", (r[3], r[4], r[2]))

            # Check if the YearLevel value is not empty
            if r[5]:
                c.execute("INSERT INTO Students(PeopleID, YearLevel) VALUES (?,?);", (c.lastrowid, r[5]))

            # Check if the Sport value is not empty
            if r[6]:
                c.execute("INSERT INTO Sports(Name) VALUES (?);", (r[6],))
                sport_id = c.lastrowid
            else:
                sport_id = None

            # Check if the Health Info value is not empty
            if r[7]:
                c.execute("INSERT INTO StudentSport(SportID, StudentID) VALUES (?,?);", (sport_id, c.lastrowid))

            # Check if the Payment method value is not empty
            if r[8]:
                c.execute("INSERT INTO Staff(PeopleID) VALUES (?);", (c.lastrowid,))

    connect.commit()



def read_coaches_staff_csv(name):
    with open((name + ".csv"), 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row
        for r in reader:
            # Check if the person is already in the People table
            c.execute("SELECT ID FROM People WHERE Email = ?;", (r[0],))
            person = c.fetchone()

            if person:
                person_id = person[0]
            else:
                # Insert the person into the People table
                c.execute("INSERT INTO People(Firstname, LastName, Email) VALUES (?,?,?);", (r[1], r[2], r[0]))
                person_id = c.lastrowid

            if r[3] == "Coach":
                # Insert the coach into the Coaches table
                c.execute("INSERT INTO Coaches(PeopleID) VALUES (?);", (person_id,))
            elif r[3] == "Staff":
                # Insert the staff member into the Staff table
                c.execute("INSERT INTO Staff(PeopleID) VALUES (?);", (person_id,))

    connect.commit()

    # Fetch and display the resulting data
    c.execute("SELECT * FROM Coaches")
    coach_rows = c.fetchall()
    coach_column_names = [description[0] for description in c.description]

    c.execute("SELECT * FROM Staff")
    staff_rows = c.fetchall()
    staff_column_names = [description[0] for description in c.description]

    print("Coaches:")
    print(tab(coach_rows, headers=coach_column_names, tablefmt='psql'))
    print("\nStaff:")
    print(tab(staff_rows, headers=staff_column_names, tablefmt='psql'))



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


# ... Existing code ...

def main():
    tables()
    readcsv("csv3")
    read_coaches_staff_csv("coaches_staff")
    sort_players_into_teams()


main()
4