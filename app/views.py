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
    student_name = request.form["lead"]
    team = request.form["team"]
    print(name, student_name, team)
    team_member_list = []
    # Create a new project
    project = Project(name=name)

    def add_student_to_project(student_name):

        # Check if the student already exists in the database
        student = Student.query.filter_by(name=student_name).first()

        if not student:
            # If the student doesn't exist, create a new one
            student = Student(name=student_name)
            print(student)
            db.session.add(student)
        
        project.students.append(student)

    # Add the lead student to the project
    add_student_to_project(student_name)

    if team:
        team_member_list = [name.strip() for name in team.split(',')]
        for member_name in team_member_list:
            add_student_to_project(member_name)

    db.session.add(project)
    db.session.commit()

    # Assuming you're using global_project_object for a specific purpose
    global_project_object = project

    # Generate list of team member names for the response
    team_member_names = ', '.join([student.name for student in project.students])

    response = f"""
    <tr>
        <td>{name}</td>
        <td>{student_name}</td>
        <td>
             {team_member_names}
        </td>
        <td>
            <button class="btn btn-primary"
                hx-get="/get-edit-form/{global_project_object.project_id}">
                Edit Title
            </button>
            <button class="btn btn-secondary" hx-get="/edit-team/{{ project.id }}">
                Edit Team
            </button>
            <button hx-delete="/delete/{global_project_object.project_id}"
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
  student = Student.query.get(project.student_id)
  response = f"""
    <tr>
    <td>{project.name}</td>
    <td>{student.name}</td>
    <td>
    <button class="btn btn-primary" hx-get="/get-edit-form/{id}">
        Edit Title
    </button>
    </td>
    <td>
    <button hx-delete="/delete/{id}"
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
  student = Student.query.get(project.student_id)
  project.name = request.form["title"]
  db.session.commit()
  response = f"""
    <tr>
    <td>{project.name}</td>
    <td>{student.name}</td>
    <td>
    <button class="btn btn-primary" hx-get="/get-edit-form/{id}">
        Edit Title
    </button>
    </td>
    <td>
    <button hx-delete="/delete/{id}"
        class="btn btn-primary">
        Delete
    </button>
    </td>
    </tr>
    """
  return response