from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/miniProject'
db = SQLAlchemy(app)


class YourModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Add your model fields here


if __name__ == '__main__':
    app.run(debug=True)