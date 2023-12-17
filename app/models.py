from app import db
from sqlalchemy.orm import backref

project_students = db.Table('project_students',
    db.Column('project_id', db.Integer, db.ForeignKey('project.project_id')),
    db.Column('student_id', db.Integer, db.ForeignKey('student.student_id'))
)

task_students = db.Table('task_students',
    db.Column('task_id', db.Integer, db.ForeignKey('task.task_id')),
    db.Column('student_id', db.Integer, db.ForeignKey('student.student_id'))
)

class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # Relationship where student is a team member
    projects = db.relationship('Project', secondary=project_students, 
                               backref=backref('team_members', lazy='dynamic', overlaps="participating_projects"))

    # Relationship for projects where student is participating (possibly in a different role)
    participating_projects = db.relationship('Project', secondary=project_students, 
                                             backref=backref('participating_students', lazy='dynamic', overlaps="projects,team_members"))

    # Relationship for projects where student is the lead
    lead_for_projects = db.relationship('Project', backref=backref('project_lead', lazy=True, uselist=False, overlaps="team_members,participating_students"))

class Project(db.Model):
    project_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    overview = db.Column(db.Text)
    tasks = db.Column(db.Text)  # Assuming tasks are a text field; consider a relationship if more complexity is needed
    links = db.Column(db.Text)  # For storing multiple links, consider JSON encoding or a separate model
    comments = db.Column(db.Text)
    feedback = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    priority = db.Column(db.Integer)  # Could be an enum or a separate model for predefined priorities
    progress = db.Column(db.Integer)  # Progress as an integer percentage (0-100)
    short_description = db.Column(db.String)

    # Foreign key for the lead student
    lead_student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'))
    # The backref here is 'project_lead' as defined in the Student model

    # Existing relationship with students
    students = db.relationship('Student', secondary=project_students, 
                               backref=backref('member_of_projects', lazy='dynamic', overlaps="team_members,participating_students"))
    
    # One-to-many relationship: one project can have many tasks
    tasks = db.relationship('Task', backref='project', lazy=True)

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    links = db.Column(db.Text)  # Consider JSON encoding or separate model for multiple links
    progress = db.Column(db.Integer)  # Progress as an integer percentage (0-100)
    priority = db.Column(db.String)  # Could be an enum or a separate model
    due_date = db.Column(db.DateTime)
    feedback = db.Column(db.Text)
    comments = db.Column(db.Text)

    # Foreign key to reference the project
    project_id = db.Column(db.Integer, db.ForeignKey('project.project_id'))

    # Relationship with students
    assigned_students = db.relationship('Student', secondary=task_students, 
                                        backref=backref('assigned_tasks', lazy='dynamic'))