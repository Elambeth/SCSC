from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db.init_app(app)

#=========================================================
# Models
#=========================================================

# Move People into models.py
class People(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)

# Move this into views.py
@app.route('/')
def index():
    new_person = People(first_name='Steve', last_name='Stevenson', email='jhdfgw4e5sdfgadsfasdfasdf6@example.com')
    db.session.add(new_person)
    db.session.commit()
    students = People.query.all()
    return render_template('index.html', students=students)

if __name__ == "__main__":
    with app.app_context():
        db.create_all() # This creates the instance directory if does not exist
    app.run(debug=True)