from app import app, db
from flask import render_template, request, jsonify
from app.models import Student, Project

@app.route("/", methods=["GET"])
def home():
  projects = db.session.query(Project, Student).filter(Project.student_id == Student.student_id).all()
  return render_template("index.html", projects=projects)

@app.route("/submit", methods=["POST"])
def submit():
  
  global_project_object = Project()
  name = request.form["title"]
  student_name = request.form["lead"]
  student_exists = db.session.query(Student).filter(Student.name == student_name).first()
  print(student_exists)
  # check if student already exists in db
  if student_exists:
    student_id = student_exists.student_id
    project = Project(student_id=student_id, name=name)
    db.session.add(project)
    db.session.commit()
    global_project_object = project
  else:
    student = Student(name=student_name)
    db.session.add(student)
    db.session.commit()

    project = Project(student_id=student.student_id, name=name)
    db.session.add(project)
    db.session.commit()
    global_project_object = project


  response = f"""
  <tr>
      <td>{name}</td>
      <td>{student_name}</td>
      <td>
          <button class="btn btn-primary"
              hx-get="/get-edit-form/{global_project_object.project_id}">
              Edit Title
          </button>
      </td>
      <td>
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
  student = Student.query.get(project.student_id)
  response = f"""
    <tr hx-trigger='cancel' class='editing' hx-get="/get-book-row/{id}">
    <td><input name="title" value="{project.title}"/></td>
    <td>{student.name}</td>
    <td>
    <button class="btn btn-primary" hx-get="/get-book-row/{id}">
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