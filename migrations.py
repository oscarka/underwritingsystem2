from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import all models
from app.models import *
from app.models.rules.import_record import ImportRecord
from app.models.rules.question.question import Question
from app.models.rules.disease.disease import Disease
from app.models.rules.disease.disease_category import DiseaseCategory
from app.models.rules.core.underwriting_rule import UnderwritingRule
from app.models.rules.conclusion.conclusion import Conclusion
from app.models.rules.conclusion.conclusion_type import ConclusionType

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 