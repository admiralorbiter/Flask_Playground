from app import db

class Student(db.Model):
    student_id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String)
    projects=db.relationship("Project", backref="student")

class Project(db.Model):
    project_id=db.Column(db.Integer, primary_key=True)
    student_id=db.Column(db.Integer, db.ForeignKey("student.student_id"))
    name=db.Column(db.String)
    description=db.Column(db.String)
    grade=db.Column(db.Integer)