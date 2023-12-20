from app import db, app
from app.models import User, Role

def create_roles():
    with app.app_context():
        roles = ['admin', 'user']  # Add more roles as needed
        for role_name in roles:
            if not Role.query.filter_by(name=role_name).first():
                role = Role(name=role_name)
                db.session.add(role)
        db.session.commit()

if __name__ == '__main__':
    create_roles()