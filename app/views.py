from app import app, db
from flask import render_template, request, jsonify, redirect, url_for, flash
from app.models import Student, Project, Task, Link, project_students, Comment
from datetime import datetime

from sqlalchemy import select, delete

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
    project_detail_url = url_for('project_detail', id=project.project_id)
    
    response = f"""
    <tr>
       <td><a href="{project_detail_url}">{project.name}</a></td>
        <td>{lead_student.name}</td>
        <td>{team_member_names}</td>
        <td>
            <button hx-delete="/delete/{project.project_id}"
                class="btn btn-danger">
                Delete
            </button>
        </td>
    </tr>
    """
    return response

@app.route("/delete/<int:id>", methods=["DELETE"])
def delete_project(id):
    project = Project.query.get_or_404(id)

    try:
        # Manually delete related rows in project_students
        db.session.execute(delete(project_students).where(project_students.c.project_id == id))
        
        db.session.delete(project)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting the project: {e}', 'danger')

    return ""

# @app.route("/get-project-row/<int:id>", methods=["GET"])
# def get_project_row(id):
#     project = Project.query.get(id)
#     team_member_names = ', '.join([student.name for student in project.students])
#     response = f"""
#     <tr>
#         <td>{project.name}</td>
#         <td>{project.project_lead.name if project.project_lead else 'No lead'}</td>
#         <td>{team_member_names}</td>
#         <td>
#             <button class="btn btn-primary" hx-get="/get-edit-form/{id}">
#                 Edit Title
#             </button>
#              <button hx-delete="/delete/{project.project_id}"
#                 class="btn btn-primary">
#                 Delete
#             </button>
#         </td>
#     </tr>
#     """
#     return response

# @app.route("/update/<int:id>", methods=["PUT"])
# def update(id):
#   project = Project.query.get(id)
#   project.name = request.form["title"]
#   team_member_names = ', '.join([student.name for student in project.students])
#   db.session.commit()
#   response = f"""
#     <tr>
#     <td><a href="{{ url_for('project_detail', id={project.project_id}) }}">{{ project.name }}</a></td>
#     <td>{project.project_lead.name if project.project_lead else 'No lead'}</td>
#     <td>{team_member_names}</td>
#     <td>
#     <button class="btn btn-primary" hx-get="/get-edit-form/{id}">
#         Edit Title
#     </button>
#     <button hx-delete="/delete/{id}"
#         class="btn btn-primary">
#         Delete
#     </button>
#     </td>
#     </tr>
#     """
#   return response

@app.route("/task/update/<int:task_id>", methods=["GET", "POST"])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == "GET":
        # Generate HTML for the edit form
        edit_form_html = f"""
            <!-- Create your edit form here -->
            <form action="{url_for('update_task', task_id=task.task_id)}" method="post">
                <!-- Add form fields for editing the task -->
                <input type="text" name="task_name" value="{task.name}">
                <textarea name="task_description">{task.description}</textarea>
                <!-- Add other form fields as necessary -->
                <button type="submit" class="btn btn-primary">Update Task</button>
            </form>
        """
        return edit_form_html

    elif request.method == "POST":
        try:
            task.name = request.form.get("task_name")
            task.description = request.form.get("task_description")
            # Update other fields as necessary
            db.session.commit()
            flash('Task updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while updating the task: {e}', 'danger')

        # After updating the task, you can return a response, such as a redirect
        return redirect(url_for('project_detail', id=task.project_id))

@app.route("/task/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    try:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting the task: {e}', 'danger')

    return ""

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
        project.project_links = request.form.get('links')
        project.comments = request.form.get('comments')
        project.feedback = request.form.get('feedback')
        project.due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d') if request.form.get('due_date') else None
        
        priority = request.form.get('priority', type=int)
        if not 1<=priority<=5:
            flash('Priority must be an integer between 1 and 5', 'error')
            return redirect(url_for('project_detail', id=id))
        else:
            project.priority = priority

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

@app.route("/add_link", methods=["POST"])
def add_link():
    try:
        new_link = Link(
            url=request.form.get("url"),
            project_id=request.form.get("project_id", type=int),
            task_id=request.form.get("task_id", type=int)
        )

        db.session.add(new_link)
        db.session.commit()
        flash('Link added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while adding the link: {e}', 'danger')

    return redirect(request.referrer or url_for('home'))

@app.route("/cancel_edit_link/<int:link_id>", methods=["GET"])
def cancel_edit_link(link_id):
    link = Link.query.get_or_404(link_id)
    return f'''
    <li hx-swap="outerHTML" id="link-{link.id}">
        <a href="{link.url}" target="_blank">{link.url}</a>
        <button hx-get="{url_for('edit_link', link_id=link.id)}" class="btn btn-sm btn-primary">Edit</button>
        <button hx-post="{url_for('delete_link', link_id=link.id)}" hx-confirm="Are you sure you want to delete this link?" hx-target="closest li" hx-swap="outerHTML" class="btn btn-sm btn-danger">Delete</button>
    </li>
    '''

@app.route("/edit_link/<int:link_id>", methods=["GET"])
def edit_link(link_id):
    link = Link.query.get_or_404(link_id)

    response = f"""
    <form hx-post="{url_for('update_link', link_id=link.id)}" hx-swap="outerHTML" id="link-{link.id}">
        <input type="hidden" name="project_id" value="{link.project_id}">
        <input type="text" name="url" value="{link.url}" placeholder="Edit URL">
        <button type="button" hx-get="{url_for('cancel_edit_link', link_id=link.id)}" hx-target="#link-{link.id}" hx-swap="outerHTML" class="btn btn-primary">Cancel</button>
        <button type="submit" class="btn btn-primary">Save</button>
    </form>
    """
    return response

@app.route("/update_link/<int:link_id>", methods=["POST"])
def update_link(link_id):
    link = Link.query.get_or_404(link_id)
    
    try:
        new_url = request.form.get("url")
        # Add form validation here if necessary

        link.url = new_url
        db.session.commit()

        # Return an HTML snippet or JSON for HTMX to update the UI
        updated_link_html = f"""
                <li id="link-{ link.id }">
            <a href="{ link.url}" target="_blank">{ link.url }</a>
            
        <!-- Edit Link Button -->
        <button hx-get="{ url_for('edit_link', link_id=link.id) }"
                hx-target="#link-{ link.id }"
                hx-swap="outerHTML"
                class="btn btn-sm btn-secondary">Edit</button>

        <!-- Delete Link Button -->
        <button hx-post="{ url_for('delete_link', link_id=link.id) }"
                hx-confirm="Are you sure you want to delete this link?"
                hx-target="closest div"
                hx-swap="outerHTML"
                class="btn btn-sm btn-danger">Delete</button>

        </li>
        """
        return updated_link_html
    except (Exception) as e:
        db.session.rollback()
        return f"<div>Error: {e}</div>", 500

@app.route("/delete_link/<int:link_id>", methods=["POST"])
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    try:
        db.session.delete(link)
        db.session.commit()
        flash('Link deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting the link: {e}', 'danger')

    return "Link deleted successfully!"  # You can return any message or empty response as needed

@app.route("/project/edit_project_overview/<int:project_id>", methods=["GET"])
def edit_project_overview(project_id):
    project = Project.query.get_or_404(project_id)

    # Generate HTML for the edit form
    edit_form_html = f"""
    <div id="overview-container">
        <form hx-post="{url_for('update_project_overview', project_id=project.project_id)}"
              hx-trigger="submit"
              hx-target="#overview-container"
              hx-swap="outerHTML">
            <label for="overview">Project Overview:</label>
            <textarea id="overview" name="overview">{project.overview}</textarea>
            <button type="submit" class="btn btn-primary">Update Overview</button>
        </form>
        <!-- You can add a cancel button or other elements if needed -->
    </div>
    """

    return edit_form_html

@app.route("/project/update_project_overview/<int:project_id>", methods=["POST"])
def update_project_overview(project_id):
    project = Project.query.get_or_404(project_id)
    try:
        project.overview = request.form.get("overview")
        db.session.commit()
        flash('Project overview updated successfully!', 'success')
        # Return the updated overview as an HTML snippet
        return f"""
        <div id="overview-container" style="position: relative; min-height: 150px;">
        <p id="project-overview">{ project.overview }</p>
        <button hx-get="{ url_for('edit_project_overview', project_id=project.project_id) }"
                hx-trigger="click"
                hx-target="#overview-container"
                hx-swap="outerHTML"
                class="edit-overview-button btn btn-primary"
                style="position: absolute; bottom: 10px; right: 10px;">
            Edit Overview
        </button>
        </div>
    """
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {e}', 'danger')
        return '', 500  # HTTP 500 for server error
    

@app.route('/add-comment/<int:project_id>', methods=['POST'])
def add_comment(project_id):
    new_comment_text = request.form.get('comment_text')
    new_comment = Comment(text=new_comment_text, project_id=project_id)
    db.session.add(new_comment)
    db.session.commit()

    # Fetch the updated list of comments
    project = Project.query.get_or_404(project_id)
    comments_html = ""
    for comment in project.comments:
        comments_html += f"""
            <div id="comment-{comment.comment_id}">
                <p>{comment.text}</p>
                <button hx-get="{ url_for('edit_comment_form', comment_id=comment.comment_id) }" hx-target="#comment-{comment.comment_id}" class="btn btn-primary">Edit</button>
                <button hx-delete="{ url_for('delete_comment', comment_id=comment.comment_id) }" hx-target="#comment-{comment.comment_id}" class="btn btn-danger">Delete</button>
            </div>
        """
    return comments_html

@app.route('/edit-comment-form/<int:comment_id>')
def edit_comment_form(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    edit_form_html = f"""
        <form method='POST' hx-post='{url_for("update_comment", comment_id=comment.comment_id)}' hx-target='#comment-{comment.comment_id}'>
            <textarea name='comment_text'>{comment.text}</textarea>
            <button type='submit' class="btn btn-primary">Update Comment</button>
        </form>
    """
    return edit_form_html

@app.route('/update-comment/<int:comment_id>', methods=['POST'])
def update_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.text = request.form.get('comment_text')
    db.session.commit()

    updated_comment_html = f"""
        <div id="comment-{comment.comment_id}">
            <p>{comment.text}</p>
            <button hx-get='{url_for('edit_comment_form', comment_id=comment.comment_id)}' hx-target="#comment-{comment.comment_id}" class="btn btn-primary">Edit</button>
            <button hx-post='{url_for('delete_comment', comment_id=comment.comment_id)}' hx-target="#comment-{comment.comment_id}" class="btn btn-danger">Delete</button>
        </div>
    """
    return updated_comment_html

@app.route('/delete-comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    project_id = comment.project_id
    db.session.delete(comment)
    db.session.commit()

    project = Project.query.get_or_404(project_id)
    comments_html = ""
    return comments_html