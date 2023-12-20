from app import db, app
from app.models import User, Role

def assign_admin(username):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            user.role_id = 'admin'
            db.session.commit()
            print(f"Admin role assigned to {username}.")

if __name__ == '__main__':
    username = 'jon'  # Replace with your username
    assign_admin(username)