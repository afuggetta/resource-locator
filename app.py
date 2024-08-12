from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    resources = db.relationship('Resource', backref='project', lazy=True)

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    percentage = db.Column(db.Integer, default=100, nullable=False)

@app.route('/')
def index():
    projects = Project.query.all()
    return render_template('index.html', projects=projects)

@app.route('/add_project', methods=['POST'])
def add_project():
    project_name = request.form.get('name')
    if project_name:
        new_project = Project(name=project_name)
        db.session.add(new_project)
        db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/add_resource', methods=['POST'])
def add_resource():
    resource_name = request.form.get('name')
    project_id = request.form.get('project_id')
    percentage = request.form.get('percentage', 100)
    if resource_name:
        new_resource = Resource(name=resource_name, project_id=project_id, percentage=percentage)
        db.session.add(new_resource)
        db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/move_resource', methods=['POST'])
def move_resource():
    resource_id = request.form.get('resource_id')
    project_id = request.form.get('project_id')
    resource = Resource.query.get(resource_id)
    if resource:
        resource.project_id = project_id
        db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/get_assignments')
def get_assignments():
    projects = Project.query.all()
    return jsonify([
        {
            'project': project.name,
            'resources': [resource.name for resource in project.resources]
        } for project in projects
    ])

@app.route('/manage')
def manage():
    projects = Project.query.all()
    return render_template('manage.html', projects=projects)

@app.route('/remove_resource', methods=['POST'])
def remove_resource():
    resource_id = request.form.get('resource_id')
    resource = Resource.query.get(resource_id)
    if resource:
        db.session.delete(resource)
        db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/update_percentage', methods=['POST'])
def update_percentage():
    resource_id = request.form.get('resource_id')
    percentage = request.form.get('percentage')
    resource = Resource.query.get(resource_id)
    if resource and percentage.isdigit():
        resource.percentage = int(percentage)
        db.session.commit()
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
