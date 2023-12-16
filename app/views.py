from app import app, db
from flask import render_template, request, jsonify
from app.models import Student, Project

@app.route("/", methods=["GET"])
def home():
  projects = Project.query.all()
  return render_template("index.html", projects=projects)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["title"]
    lead_name = request.form["lead"]
    team_names = request.form["team"].split(',')

    # Create a new project
    project = Project(name=name)

    # Function to add a student to the project
    def add_student(name):
        student = Student.query.filter_by(name=name.strip()).first()
        if not student:
            student = Student(name=name.strip())
            db.session.add(student)
        return student

    # Set the lead student
    lead_student = add_student(lead_name)
    project.lead = lead_student

    # Add other team members
    for member_name in team_names:
        if member_name.strip() and member_name.strip() != lead_name:
            project.students.append(add_student(member_name))

    db.session.add(project)
    db.session.commit()

    team_member_names = ', '.join([student.name for student in project.students])

    response = f"""
    <tr>
        <td>{project.name}</td>
        <td>{lead_student.name}</td>
        <td>{team_member_names}</td>
        <td>
            <button class="btn btn-primary"
                hx-get="/get-edit-form/{project.project_id}">
                Edit Title
            </button>
            <button hx-delete="/delete/{project.project_id}"
                class="btn btn-primary">
                Delete
            </button>
        </td>
    </tr>
    """
    return response

@app.route("/delete/<int:id>", methods=["DELETE"])
def delete_project(id):
    project = Project.query.get(id)
    db.session.delete(project)
    db.session.commit()
    return ""

@app.route("/get-edit-form/<int:id>", methods=["GET"])
def get_edit_form(id):
  project = Project.query.get(id)
  
  response = f"""
    <tr hx-trigger='cancel' class='editing' hx-get="/get-project-row/{id}">
    <td><input name="title" value="{project.name}"/></td>
    <td>
    <button class="btn btn-primary" hx-get="/get-project-row/{id}">
        Cancel
    </button>
    <button class="btn btn-primary" hx-put="/update/{id}" hx-include="closest tr">
        Save
    </button>
    </td>
    </tr>
    """
  return response

@app.route("/get-project-row/<int:id>", methods=["GET"])
def get_project_row(id):
    project = Project.query.get(id)
    team_member_names = ', '.join([student.name for student in project.students])
    response = f"""
    <tr>
        <td>{project.name}</td>
        <td>{project.lead.name if project.lead else 'No lead'}</td>
        <td>{team_member_names}</td>
        <td>
            <button class="btn btn-primary" hx-get="/get-edit-form/{id}">
                Edit Title
            </button>
             <button hx-delete="/delete/{project.project_id}"
                class="btn btn-primary">
                Delete
            </button>
        </td>
    </tr>
    """
    return response

@app.route("/update/<int:id>", methods=["PUT"])
def update(id):
  project = Project.query.get(id)
  project.name = request.form["title"]
  team_member_names = ', '.join([student.name for student in project.students])
  db.session.commit()
  response = f"""
    <tr>
    <td>{project.name}</td>
    <td>{project.lead.name if project.lead else 'No lead'}</td>
    <td>{team_member_names}</td>
    <td>
    <button class="btn btn-primary" hx-get="/get-edit-form/{id}">
        Edit Title
    </button>
    <button hx-delete="/delete/{id}"
        class="btn btn-primary">
        Delete
    </button>
    </td>
    </tr>
    """
  return response