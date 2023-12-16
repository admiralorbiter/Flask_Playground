from app import db

project_students = db.Table('project_students',
    db.Column('project_id', db.Integer, db.ForeignKey('project.project_id')),
    db.Column('student_id', db.Integer, db.ForeignKey('student.student_id'))
)

class Student(db.Model):
    student_id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String)
    projects = db.relationship('Project', secondary=project_students, backref=db.backref('students', lazy='dynamic'))


class Project(db.Model):
    project_id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String)
    description=db.Column(db.String)
    grade=db.Column(db.Integer)