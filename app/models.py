
from app import db
from sqlalchemy.orm import backref
from werkzeug.security import generate_password_hash, check_password_hash

project_students = db.Table('project_students',
    db.Column('project_id', db.Integer, db.ForeignKey('project.project_id', ondelete="CASCADE")),
    db.Column('student_id', db.Integer, db.ForeignKey('student.student_id', ondelete="CASCADE"))
)

task_students = db.Table('task_students',
    db.Column('task_id', db.Integer, db.ForeignKey('task.task_id')),
    db.Column('student_id', db.Integer, db.ForeignKey('student.student_id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', backref='users')

    linked_students = db.relationship('Student', backref='linked_by', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        # If you have a field to activate/deactivate users, use it here
        # Otherwise, just return True
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        # Assuming your user model has an 'id' field
        return str(self.id)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)

    # ForeignKey references
    project_id = db.Column(db.Integer, db.ForeignKey('project.project_id'), nullable=True)

    # Relationships
    project = db.relationship('Project', backref='comments')

class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='student_links')

    # Relationship where student is a team member
    projects = db.relationship('Project', secondary=project_students, 
                               backref=backref('team_members', lazy='dynamic', overlaps="participating_projects"))

    # Relationship for projects where student is participating (possibly in a different role)
    participating_projects = db.relationship('Project', secondary=project_students, 
                                             backref=backref('participating_students', lazy='dynamic', overlaps="projects,team_members"))

    # Relationship for projects where student is the lead
    lead_for_projects = db.relationship('Project', backref=backref('project_lead', lazy=True, uselist=False, overlaps="team_members,participating_students"))

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)

    # ForeignKey references
    project_id = db.Column(db.Integer, db.ForeignKey('project.project_id'), nullable=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.task_id'), nullable=True)

    # Relationships
    project = db.relationship('Project', back_populates='links')
    task = db.relationship('Task', back_populates='links')

class Project(db.Model):
    project_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    overview = db.Column(db.Text)
    feedback = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    priority = db.Column(db.Integer)
    progress = db.Column(db.Integer)
    short_description = db.Column(db.String)

    # Foreign key for the lead student
    lead_student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'))

    # Relationship with students
    students = db.relationship('Student', secondary=project_students, 
                           backref=backref('member_of_projects', lazy='dynamic', overlaps="team_members,participating_students"))

    
    # Relationship with tasks
    tasks = db.relationship('Task', backref='project', lazy=True)

    # Relationship with links
    links = db.relationship('Link', back_populates='project', cascade="all, delete-orphan")

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    progress = db.Column(db.Integer)
    priority = db.Column(db.String)
    due_date = db.Column(db.DateTime)
    feedback = db.Column(db.Text)
    comments = db.Column(db.Text)

    # Foreign key to reference the project
    project_id = db.Column(db.Integer, db.ForeignKey('project.project_id'))

    # Relationship with students
    assigned_students = db.relationship('Student', secondary=task_students, 
                                        backref=backref('assigned_tasks', lazy='dynamic'))

    # Relationship with links
    links = db.relationship('Link', back_populates='task', cascade="all, delete-orphan")