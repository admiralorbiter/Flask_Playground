from app import app, db
from flask import render_template, request, jsonify, redirect, url_for, flash
from app.models import Student, Project, Task
from datetime import datetime


@app.route("/", methods=["GET"])
def home():
  projects = Project.query.all()
  return render_template("index.html", projects=projects)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["title"]
    lead_name = request.form["lead"]
    team_names = request.form["team"].split(',')

    # Function to add a student to the project
    def add_student(name):
        student = Student.query.filter_by(name=name.strip()).first()
        if not student:
            student = Student(name=name.strip())
            db.session.add(student)
            db.session.flush()  # Ensure the student gets an ID if it's a new entry
        return student

    # Create a new project
    project = Project(name=name)

    # Set the lead student
    lead_student = add_student(lead_name)
    project.project_lead = lead_student  # Use the backref from the Student model

    # Default Values
    project.progress = 0

    # Add other team members
    for member_name in team_names:
        if member_name.strip() and member_name.strip() != lead_name:
            project.team_members.append(add_student(member_name))

    db.session.add(project)
    db.session.commit()

    # Prepare team member names for the response
    team_member_names = ', '.join([student.name for student in project.team_members])

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
        <td>{project.project_lead.name if project.project_lead else 'No lead'}</td>
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
    <td>{project.project_lead.name if project.project_lead else 'No lead'}</td>
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

@app.route("/project/<int:id>", methods=["GET"])
def project_detail(id):
    project = Project.query.get_or_404(id)
    tasks = Task.query.filter_by(project_id=id).all()  # Fetch tasks for this project
    return render_template("project_details.html", project=project, tasks=tasks)


@app.route("/project/update/<int:id>", methods=["POST"])
def update_project(id):
    project = Project.query.get_or_404(id)

    try:
        # Update project's attributes based on form data
        project.name = request.form.get('name')
        project.overview = request.form.get('overview')
        project.links = request.form.get('links')
        project.comments = request.form.get('comments')
        project.feedback = request.form.get('feedback')
        project.due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d') if request.form.get('due_date') else None
        project.priority = request.form.get('priority')
        progress = request.form.get('progress', type=int)
        if progress is not None:
            project.progress = progress
        else:
            flash('Progress must be an integer between 0 and 100', 'error')
            return redirect(url_for('project_detail', id=id))

        project.short_description = request.form.get('short_description')

        # Save changes to the database
        db.session.commit()

        flash('Project updated successfully!', 'success')
    except Exception as e:
        # Handle errors and roll back any changes
        db.session.rollback()
        flash(f'An error occurred: {e}', 'danger')

    # Redirect to a page (e.g., project detail page) or return a response
    return redirect(url_for('project_detail', id=id))

@app.route("/project/<int:project_id>/add_task", methods=["POST"])
def add_task(project_id):
    project = Project.query.get_or_404(project_id)
    try:
        new_task = Task(
            name=request.form.get("task_name"),
            description=request.form.get("task_description"),
            # Add other fields as necessary, e.g., due_date, priority
            progress = 0,
            project_id=project.project_id
        )

        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while adding the task: {e}', 'danger')

    return redirect(url_for('project_detail', id=project_id))

@app.route("/task/update/<int:task_id>", methods=["POST"])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)

    try:
        task.name = request.form.get("task_name")
        task.description = request.form.get("task_description")
        # Update other fields as necessary, e.g., due_date, priority
        # You might also need to handle changes in assigned students

        db.session.commit()
        flash('Task updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while updating the task: {e}', 'danger')

    return redirect(url_for('project_detail', id=task.project_id))