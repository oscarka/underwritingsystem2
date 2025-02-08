from flask import Blueprint, render_template

rules = Blueprint('rules', __name__)

@rules.route('/')
def index():
    return render_template('rules/index.html')

@rules.route('/ai-parameters')
def ai_parameters():
    return render_template('rules/ai_parameters.html') 