from flask import Flask, request, render_template, redirect, url_for, jsonify
from database import db, Login, Health
import os
import subprocess
from datetime import datetime
import re
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:thachiyath10@localhost/nutridiet'

# Initialize the database
db.init_app(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/nurse')
def nurse():
    return render_template('nurse.html')


@app.route('/question')
def question():
    return render_template('question.html')


@app.route('/why')
def why():
    return render_template('why.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/tryAI')
def tryAI():
    user_id = request.args.get('user_id')
    return render_template('tryAI.html', user_id=user_id)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/trainer')
def trainer():
    return render_template('trainer.html')


@app.route('/welcome')
def welcome():
    return render_template('welcome.html')


from flask import render_template
from database import NutrientsIntake


@app.route('/dashboard')
def dashboard():
    # Get the user_id from the query parameters
    user_id = request.args.get('user_id')

    if user_id:
        # Query the nutrients intake data for the user's health_data_id
        nutrients_data = NutrientsIntake.query.filter_by(health_data_id=user_id).all()

        return render_template('dashboard.html', nutrients_data=nutrients_data, user_id=user_id)
    else:
        # Redirect to login if user_id is not provided
        return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Create a new login object
        new_login = Login(username=username, email=email, password=password)

        # Add the new login to the database session
        db.session.add(new_login)

        # Commit the session to save the changes to the database
        db.session.commit()

        # Redirect the user to the question route after signing up
        return redirect(url_for('question'))
    return render_template('signup.html')


@app.route('/authenticate', methods=['POST'])
def authenticate():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Query the database for the user with the given username and password
        user = Login.query.filter_by(username=username, password=password).first()

        if user:
            # If user exists, redirect to dashboard with user_id as a query parameter
            return redirect(url_for('dashboard', user_id=user.user_id))
        else:
            # If user doesn't exist or password is incorrect, redirect to login page
            return redirect(url_for('login'))


@app.route('/submit_questionnaire', methods=['POST'])
def submit_questionnaire():
    if request.method == 'POST':
        # Retrieve form data
        gender = request.form.get('gender')
        height = request.form.get('height')
        weight = request.form.get('weight')
        condition1 = request.form.getlist('condition1')
        condition2 = request.form.getlist('condition2')
        condition3 = request.form.getlist('condition3')
        condition4 = request.form.getlist('condition4')
        condition5 = request.form.getlist('condition5')
        condition6 = request.form.getlist('condition6')
        condition7 = request.form.getlist('condition7')
        condition8 = request.form.getlist('condition8')
        condition9 = request.form.getlist('condition9')
        condition10 = request.form.getlist('condition10')# Change to 'condition' to match HTML

        # Create a new Health object
        new_health_record = Health(
            user_id=1,  # Replace with actual user ID
            high_cholesterol='Yes' if 'High Cholesterol (Hyperlipidemia)' in condition1 else 'No',
            diabetes_1='Yes' if 'Diabetes Mellitus Type 1' in condition2 else 'No',
            diabetes_2='Yes' if 'Diabetes Mellitus Type 2' in condition3 else 'No',
            cardiovascular_disease='Yes' if 'Cardiovascular Disease' in condition4 else 'No',
            kidney_disease='Yes' if 'Kidney Disease' in condition5 else 'No',
            hypertension='Yes' if 'Hypertension' in condition6 else 'No',
            obesity='Yes' if 'Obesity' in condition7 else 'No',
            pcos='Yes' if 'Polycystic Ovary Syndrome (PCOS)' in condition8 else 'No',
            gerd='Yes' if 'Gastroesophageal Reflux Disease (GERD)' in condition9 else 'No',
            gout='Yes' if 'Gout' in condition10 else 'No',
            weight=float(weight) if weight else None,
            height=float(height) if height else None
        )

        # Add the new Health record to the database session
        db.session.add(new_health_record)

        # Commit the session to save the changes to the database
        db.session.commit()

        # Redirect the user to the dashboard
        return redirect(url_for('login'))

    # Handle GET requests or other cases where the method is not POST
    return redirect(url_for('question'))


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        image = request.files['image']
        image_path = os.path.join('assets/Unknown', image.filename)
        image.save(image_path)

        # Execute imageClassifierTest.py and capture its output
        output = subprocess.check_output(['python', 'imageClassifierTest.py'])
        output_str = output.decode('utf-8').strip()  # Convert bytes to string


        # Determine the predicted class from the output
        predicted_class = None
        if "Predicted Class:" in output_str:
            predicted_class_match = re.search(r'Predicted Class:\s*([^,]+)', output_str)
            predicted_class = predicted_class_match.group(1).strip()
        # Based on the predicted class, construct data for NutrientsIntake table
        nutrients_data = {}
        if predicted_class == "Pav-Bhaji":
            # Define data for Class1
            nutrients_data = {
                'carbohydrates': 40,
                'added_sugars': 5,
                'saturated_fats': 15,
                'trans_fats': 0,
                'dietary_cholesterol': 20,
                'high_cholesterol_foods': 5,
                'unsaturated_fats': 10,
                'whole_grains': 5,
                'lean_proteins': 10,
                'fiber': 8,
                'sodium': 800,
                'phosphorus': 15,
                'potassium': 400,
                'protein': 8,
                'alcohol': 0,
                'fructose': 3
            }

        elif predicted_class == "Biryani":
            # Define data for Class2
            nutrients_data = {
                'carbohydrates': 60,
                'added_sugars': 3,
                'saturated_fats': 20,
                'trans_fats': 0,
                'dietary_cholesterol': 30,
                'high_cholesterol_foods': 10,
                'unsaturated_fats': 15,
                'whole_grains': 10,
                'lean_proteins': 20,
                'fiber': 5,
                'sodium': 900,
                'phosphorus': 25,
                'potassium': 500,
                'protein': 15,
                'alcohol': 0,
                'fructose': 2
            }

        elif predicted_class == "Chole-Bhature":
            # Define data for Chole Bhature
            nutrients_data = {
                'carbohydrates': 70,
                'added_sugars': 5,
                'saturated_fats': 25,
                'trans_fats': 0,
                'dietary_cholesterol': 35,
                'high_cholesterol_foods': 15,
                'unsaturated_fats': 20,
                'whole_grains': 5,
                'lean_proteins': 15,
                'fiber': 7,
                'sodium': 1000,
                'phosphorus': 30,
                'potassium': 550,
                'protein': 10,
                'alcohol': 0,
                'fructose': 3
            }

        elif predicted_class == "Dabeli":
            # Define data for Dabeli
            nutrients_data = {
                'carbohydrates': 50,
                'added_sugars': 8,
                'saturated_fats': 15,
                'trans_fats': 0,
                'dietary_cholesterol': 25,
                'high_cholesterol_foods': 5,
                'unsaturated_fats': 10,
                'whole_grains': 5,
                'lean_proteins': 10,
                'fiber': 6,
                'sodium': 700,
                'phosphorus': 20,
                'potassium': 450,
                'protein': 8,
                'alcohol': 0,
                'fructose': 4
            }

        elif predicted_class == "Dal":
            # Define data for Dal
            nutrients_data = {
                'carbohydrates': 30,
                'added_sugars': 2,
                'saturated_fats': 5,
                'trans_fats': 0,
                'dietary_cholesterol': 0,
                'high_cholesterol_foods': 0,
                'unsaturated_fats': 5,
                'whole_grains': 10,
                'lean_proteins': 25,
                'fiber': 8,
                'sodium': 500,
                'phosphorus': 40,
                'potassium': 600,
                'protein': 15,
                'alcohol': 0,
                'fructose': 1
            }

        elif predicted_class == "Dhokla":
            # Define data for Dhokla
            nutrients_data = {
                'carbohydrates': 35,
                'added_sugars': 5,
                'saturated_fats': 2,
                'trans_fats': 0,
                'dietary_cholesterol': 0,
                'high_cholesterol_foods': 0,
                'unsaturated_fats': 3,
                'whole_grains': 15,
                'lean_proteins': 5,
                'fiber': 4,
                'sodium': 600,
                'phosphorus': 20,
                'potassium': 300,
                'protein': 6,
                'alcohol': 0,
                'fructose': 2
            }

        elif predicted_class == "Masala-Dosa":
            # Define data for Masala Dosa
            nutrients_data = {
                'carbohydrates': 40,
                'added_sugars': 2,
                'saturated_fats': 3,
                'trans_fats': 0,
                'dietary_cholesterol': 0,
                'high_cholesterol_foods': 0,
                'unsaturated_fats': 4,
                'whole_grains': 20,
                'lean_proteins': 5,
                'fiber': 6,
                'sodium': 700,
                'phosphorus': 25,
                'potassium': 350,
                'protein': 8,
                'alcohol': 0,
                'fructose': 1
            }

        elif predicted_class == "Jalebi":
            # Define data for Jalebi
            nutrients_data = {
                'carbohydrates': 50,
                'added_sugars': 30,
                'saturated_fats': 10,
                'trans_fats': 0,
                'dietary_cholesterol': 0,
                'high_cholesterol_foods': 0,
                'unsaturated_fats': 5,
                'whole_grains': 0,
                'lean_proteins': 2,
                'fiber': 1,
                'sodium': 50,
                'phosphorus': 10,
                'potassium': 100,
                'protein': 2,
                'alcohol': 0,
                'fructose': 20
            }

        elif predicted_class == "Kathi-Roll":
            # Define data for Kathi Roll
            nutrients_data = {
                'carbohydrates': 35,
                'added_sugars': 2,
                'saturated_fats': 8,
                'trans_fats': 0,
                'dietary_cholesterol': 20,
                'high_cholesterol_foods': 5,
                'unsaturated_fats': 10,
                'whole_grains': 10,
                'lean_proteins': 15,
                'fiber': 4,
                'sodium': 600,
                'phosphorus': 20,
                'potassium': 250,
                'protein': 12,
                'alcohol': 0,
                'fructose': 1
            }

        elif predicted_class == "Kofta":
            # Define data for Kofta
            nutrients_data = {
                'carbohydrates': 15,
                'added_sugars': 2,
                'saturated_fats': 10,
                'trans_fats': 0,
                'dietary_cholesterol': 30,
                'high_cholesterol_foods': 10,
                'unsaturated_fats': 5,
                'whole_grains': 5,
                'lean_proteins': 25,
                'fiber': 3,
                'sodium': 600,
                'phosphorus': 20,
                'potassium': 300,
                'protein': 20,
                'alcohol': 0,
                'fructose': 1
            }

        elif predicted_class == "Naan":
            # Define data for Naan
            nutrients_data = {
                'carbohydrates': 30,
                'added_sugars': 2,
                'saturated_fats': 5,
                'trans_fats': 0,
                'dietary_cholesterol': 0,
                'high_cholesterol_foods': 0,
                'unsaturated_fats': 3,
                'whole_grains': 5,
                'lean_proteins': 5,
                'fiber': 2,
                'sodium': 400,
                'phosphorus': 15,
                'potassium': 100,
                'protein': 5,
                'alcohol': 0,
                'fructose': 1
            }

        elif predicted_class == "Pakora":
            # Define data for Pakora
            nutrients_data = {
                'carbohydrates': 25,
                'added_sugars': 2,
                'saturated_fats': 5,
                'trans_fats': 0,
                'dietary_cholesterol': 10,
                'high_cholesterol_foods': 5,
                'unsaturated_fats': 5,
                'whole_grains': 5,
                'lean_proteins': 10,
                'fiber': 3,
                'sodium': 500,
                'phosphorus': 15,
                'potassium': 200,
                'protein': 8,
                'alcohol': 0,
                'fructose': 1
            }

        elif predicted_class == "Paneer-Tikka":
            # Define data for Paneer Tikka
            nutrients_data = {
                'carbohydrates': 10,
                'added_sugars': 2,
                'saturated_fats': 5,
                'trans_fats': 0,
                'dietary_cholesterol': 15,
                'high_cholesterol_foods': 5,
                'unsaturated_fats': 3,
                'whole_grains': 0,
                'lean_proteins': 20,
                'fiber': 1,
                'sodium': 400,
                'phosphorus': 20,
                'potassium': 150,
                'protein': 15,
                'alcohol': 0,
                'fructose': 1
            }

        elif predicted_class == "Pizza":
            # Define data for Pizza
            nutrients_data = {
                'carbohydrates': 40,
                'added_sugars': 5,
                'saturated_fats': 15,
                'trans_fats': 0,
                'dietary_cholesterol': 20,
                'high_cholesterol_foods': 10,
                'unsaturated_fats': 10,
                'whole_grains': 5,
                'lean_proteins': 10,
                'fiber': 4,
                'sodium': 800,
                'phosphorus': 30,
                'potassium': 300,
                'protein': 12,
                'alcohol': 0,
                'fructose': 2
            }

        elif predicted_class == "Samosa":
            # Define data for Samosa
            nutrients_data = {
                'carbohydrates': 30,
                'added_sugars': 2,
                'saturated_fats': 8,
                'trans_fats': 0,
                'dietary_cholesterol': 0,
                'high_cholesterol_foods': 0,
                'unsaturated_fats': 5,
                'whole_grains': 5,
                'lean_proteins': 5,
                'fiber': 3,
                'sodium': 400,
                'phosphorus': 20,
                'potassium': 200,
                'protein': 5,
                'alcohol': 0,
                'fructose': 1
            }

        elif predicted_class == "Momos":
            # Define data for Momos
            nutrients_data = {
                'carbohydrates': 25,
                'added_sugars': 2,
                'saturated_fats': 5,
                'trans_fats': 0,
                'dietary_cholesterol': 10,
                'high_cholesterol_foods': 5,
                'unsaturated_fats': 5,
                'whole_grains': 5,
                'lean_proteins': 10,
                'fiber': 3,
                'sodium': 500,
                'phosphorus': 15,
                'potassium': 200,
                'protein': 8,
                'alcohol': 0,
                'fructose': 1
            }

        elif predicted_class == "Kulfi":
            # Define data for Kulfi
            nutrients_data = {
                'carbohydrates': 30,
                'added_sugars': 15,
                'saturated_fats': 10,
                'trans_fats': 0,
                'dietary_cholesterol': 30,
                'high_cholesterol_foods': 10,
                'unsaturated_fats': 5,
                'whole_grains': 0,
                'lean_proteins': 5,
                'fiber': 1,
                'sodium': 100,
                'phosphorus': 10,
                'potassium': 150,
                'protein': 5,
                'alcohol': 0,
                'fructose': 10
            }

        elif predicted_class == "Idli":
            # Define data for Idli
            nutrients_data = {
                'carbohydrates': 25,
                'added_sugars': 1,
                'saturated_fats': 1,
                'trans_fats': 0,
                'dietary_cholesterol': 0,
                'high_cholesterol_foods': 0,
                'unsaturated_fats': 1,
                'whole_grains': 20,
                'lean_proteins': 5,
                'fiber': 3,
                'sodium': 200,
                'phosphorus': 15,
                'potassium': 100,
                'protein': 3,
                'alcohol': 0,
                'fructose': 1
            }

        elif predicted_class == "Chai":
            # Define data for Chai
            nutrients_data = {
                'carbohydrates': 5,
                'added_sugars': 3,
                'saturated_fats': 1,
                'trans_fats': 0,
                'dietary_cholesterol': 0,
                'high_cholesterol_foods': 0,
                'unsaturated_fats': 1,
                'whole_grains': 0,
                'lean_proteins': 1,
                'fiber': 0,
                'sodium': 50,
                'phosphorus': 5,
                'potassium': 50,
                'protein': 1,
                'alcohol': 0,
                'fructose': 1
            }

        elif predicted_class == "Burger":
            # Define data for Burger
            nutrients_data = {
                'carbohydrates': 30,
                'added_sugars': 5,
                'saturated_fats': 10,
                'trans_fats': 1,
                'dietary_cholesterol': 30,
                'high_cholesterol_foods': 20,
                'unsaturated_fats': 10,
                'whole_grains': 5,
                'lean_proteins': 15,
                'fiber': 3,
                'sodium': 800,
                'phosphorus': 20,
                'potassium': 300,
                'protein': 15,
                'alcohol': 0,
                'fructose': 2
            }
        # Add more elif blocks for other classes as needed

        # Insert data into NutrientsIntake table
        if nutrients_data:
            # Get the user_id from the query parameters or session
            user_id = request.args.get('user_id')  # Assuming user_id is passed in the request parameters
            # Construct NutrientsIntake object
            new_nutrients_intake = NutrientsIntake(
                health_data_id=user_id,
                requirement_id=None,
                intake_date=datetime.now().date(),
                **nutrients_data
            )

            # Add the new NutrientsIntake record to the database session
            db.session.add(new_nutrients_intake)

            # Commit the session to save the changes to the database
            db.session.commit()

        response_data = {'output': output_str}
        return jsonify(response_data)  # Return success response


if __name__ == '__main__':
    app.run(debug=True)
