import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import db, User, Character, Planet, Favorite

class FavoriteModelView(ModelView):
    column_list = ('id', 'user', 'character', 'planet')
    form_columns = ('user', 'character', 'planet')

    # Optional: add validation to enforce at least one favorite type selected
    def on_model_change(self, form, model, is_created):
        if not model.character and not model.planet:
            raise ValueError("Select at least a favorite character or a favorite planet.")

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Character, db.session))
    admin.add_view(ModelView(Planet, db.session))
    admin.add_view(FavoriteModelView(Favorite, db.session))
