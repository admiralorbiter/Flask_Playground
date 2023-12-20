from app import db, app
from app.models import User, Role

def assign_admin(username):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        admin_role = Role.query.filter_by(name='admin').first()

        if user and admin_role:
            user.role_id = admin_role.id
            db.session.commit()
            print(f"Admin role assigned to {username}.")
        else:
            if not user:
                print(f"User '{username}' not found.")
            if not admin_role:
                print("Admin role not found. Please ensure the 'admin' role exists.")

if __name__ == '__main__':
    username = 'jon'  # Replace with your username
    assign_admin(username)