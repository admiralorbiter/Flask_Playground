from app import db, app
from app.models import User, Role
from werkzeug.security import generate_password_hash

def create_roles():
    with app.app_context():
        roles = ['admin', 'user']  # Add more roles as needed
        for role_name in roles:
            if not Role.query.filter_by(name=role_name).first():
                role = Role(name=role_name)
                db.session.add(role)
        db.session.commit()

def assign_admin(username, password):
    with app.app_context():
        # Check if the user exists
        user = User.query.filter_by(username=username).first()
        
        # Check if the admin role exists, create it if not
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin')
            db.session.add(admin_role)
            db.session.commit()
            print("Admin role created.")

        # If the user exists, assign them the admin role
        if user and admin_role:
            user.role_id = admin_role.id
            db.session.commit()
            print(f"Admin role assigned to {username}.")
        else:
            # If the user doesn't exist, create them and assign the admin role
            if not user:
                print(f"User '{username}' not found. Creating new admin user.")
                hashed_password = generate_password_hash(password)
                new_user = User(username=username, password_hash=hashed_password, role_id=admin_role.id)
                new_user.linked_student = None
                db.session.add(new_user)
                db.session.commit()
                print(f"Admin user '{username}' created with the password '{password}'.")

if __name__ == '__main__':
    username = 'jon'  # Replace with your username
    password = 'nihlism'  # Replace with your desired password
    create_roles()
    assign_admin(username, password)