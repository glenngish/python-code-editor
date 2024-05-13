from flask import Flask, render_template_string, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from pytz import timezone
import pytz
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///signin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = 'outlook.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'bfurn1589@outlook.com'
app.config['MAIL_PASSWORD'] = 'Test123!!!!'
mail = Mail(app)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

PASSWORD = "Testing1234"

store_email_map = {
    "Dania": "testing@example.com",
    "Winter Garden": "wg.manager@example.com",
    "Casselberry": "casselberry.manager@example.com",
    "Port Charlotte": "portcharlotte.manager@example.com",
    "Melbourne": "melbourne.manager@example.com",
    "Jacksonville": "jacksonville.manager@example.com",
    "North Palm Beach": "npb.manager@example.com",
    "Naples": "naples.manager@example.com",
    "Stuart": "stuart.manager@example.com",
    "Boca": "boca.manager@example.com",
    "Fort Myers": "fortmyers.manager@example.com",
    "Sarasota": "sarasota.manager@example.com",
    "West Palm Beach": "wpb.manager@example.com",
    "Pembroke Pines": "pembrokepines.manager@example.com",
    "Pinecrest": "pinecrest.manager@example.com",
    "Fort Lauderdale": "ftlauderdale.manager@example.com"
}

class Representative(db.Model):
    __tablename__ = 'representative'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    department = db.Column(db.String(255))
    store = db.Column(db.String(255))
    vendor = db.Column(db.String(255))
    visit_summary = db.Column(db.String(255))
    time = db.Column(db.DateTime)
    confirmed = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Representative {self.name}, {self.department}, {self.store}>'

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    home_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Store Rep Sign-in</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #e0f7fa;
                text-align: center;
                padding: 20px;
            }
            .menu a {
                color: #00695c;
                font-size: 20px;
                text-decoration: none;
                padding: 10px;
                border: 1px solid #00695c;
                border-radius: 5px;
                background-color: #b2dfdb;
                display: inline-block;
                
                margin: 10px;
            }
            .menu a:hover {
                background-color: #00695c;
                color: white;
            }
        </style>
    </head>
    <body>
        <h1>Welcome to the Store Representative Sign-in Page</h1>
        <div class="menu">
            <a href="/signin/furniture">Furniture Rep Sign-in</a>
            <a href="/signin/Design or Flooring">Design or Flooring Rep Sign-in</a>
            <a href="/check">Reps Sign-in History</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(home_html)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/signin/<department>', methods=['GET', 'POST'])
def signin(department):
    message = ""
    signin_records = []

    if request.method == 'POST':
        rep_name = request.form['name']
        selected_store = request.form['store']
        vendors = request.form.getlist('vendor')
        visit_summary = request.form['visit_summary']
        new_signin = Representative(name=rep_name, department=department, store=selected_store, vendor=', '.join(vendors), visit_summary=visit_summary, time=datetime.now())
        db.session.add(new_signin)
        db.session.commit()

        recipient_email = store_email_map.get(selected_store, 'default-email@example.com')  # Fallback email if store not found

        msg = Message('New Store Representative Sign-In',
                      sender='bfurn1589@outlook.com',
                      recipients=[recipient_email])
        msg.body = f"""
		Hello,

		This is to notify you that {rep_name} from {vendors} has signed in as a {department} Representative at the {selected_store} location.

		Summary of Visit:
		{visit_summary}

		Please confirm the visit by clicking the button below:
		<form action="{request.host_url}confirm/{new_signin.id}" method="POST">
			<input type="submit" value="Confirm Visit">
		</form>

		Regards,
		Baer's Furniture Rep Update
		"""

    def capitalize_specific_words(phrase, words_to_capitalize):
        return ' '.join(word if word.lower() not in words_to_capitalize else word.capitalize() for word in phrase.split())

    if request.method == 'POST':
        rep_name = request.form['name']
        selected_store = request.form['store']
        vendors = request.form.getlist('vendor')
        visit_summary = request.form['visit_summary']
        new_signin = Representative(name=rep_name, department=department, store=selected_store, vendor=', '.join(vendors), visit_summary=visit_summary, time=datetime.now())
        db.session.add(new_signin)
        db.session.commit()

        vendor_message = ' & '.join(vendors) if len(vendors) > 1 else vendors[0]
        words_to_capitalize = ['design', 'flooring', 'furniture']
        department_capitalized = capitalize_specific_words(department, words_to_capitalize)

        message = f"{rep_name} from {vendor_message}, you have successfully signed in as a {department_capitalized} Representative at the {selected_store} location."
        signin_records = Representative.query.filter_by(name=rep_name, department=department)\
                                             .order_by(Representative.time.desc())\
                                             .all()

    stores = [
        "Dania", "Winter Garden", "Casselberry", "Port Charlotte", "Melbourne",
        "Jacksonville", "North Palm Beach", "Naples", "Stuart", "Boca",
        "Fort Myers", "Sarasota", "West Palm Beach", "Pembroke Pines",
        "Pinecrest", "Fort Lauderdale"
    ]
    stores.sort() 
    
    signin_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sign-in</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #e0f7fa;
                padding: 20px;
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }}
            .container {{
                max-width: 600px;
                width: 100%;
                background-color: #ffffff;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            }}
            form {{
                margin-bottom: 20px;
            }}
            .form-group {{
                margin-bottom: 20px;
                position: relative;
                padding-right: 35px; /* space for plus button */
			}}
			.input-group {{
				position: relative;
				margin-bottom: 10px; /* Space between each input group */
			}}

			.vendor-input, .vendor-button {{
				height: 38px; /* Adjust the height so input and buttons are the same */
				box-sizing: border-box; /* Include padding and borders in the element's total dimensions */
			}}

			.vendor-input {{
				width: 100%;
				padding: 0 10px; /* Provide some padding inside the input */
				border: 1px solid #ced4da;
				border-radius: 5px;
				margin-bottom: 0; /* Remove any margin below the input */
			}}
			.vendor-button {{
				position: absolute;
				top: 0;
				right: -35px;
				width: 30px; /* Fixed width */
				padding: 0; /* Remove padding to fix the height */
				font-size: 16px;
				line-height: 38px; /* Center the text vertically */
				text-align: center;
				background-color: #00695c;
				color: white;
				border: none;
				border-radius: 0 5px 5px 0; /* Only round the right side to match input */
				cursor: pointer;
			}}
			.form-group input[type="file"] {{
				display: none; /* Hide the default file input */
			}}
			.custom-file-upload {{
				display: inline-block;
				padding: 10px 20px;
				background-color: #00695c;
				color: white;
				border: none;
				border-radius: 5px;
				cursor: pointer;
				text-align: center;
				font-size: 16px;
				width: 99% !important;;
			}}
			.custom-file-upload:hover {{
				background-color: #004d40;
			}}
            .form-group select {{
				width: calc(100% + 35px); /* Subtract the padding and border width */
				padding: 10px;
				border-radius: 5px;
				border: 1px solid #ced4da;
				background-color: #f8f9fa;
				
            }}	
			.form-group input[type="text"],
			.form-group textarea {{
				width: calc(100% + 35px); /* Subtract the padding and border width */
				padding: 10px;
				border-radius: 5px;
				border: 1px solid #ced4da;
				background-color: #f8f9fa;
				box-sizing: border-box;
				-moz-box-sizing: border-box;
				-webkit-box-sizing: border-box;
            }}
			.form-group input[type="text"],
			.form-group select {{
				box-sizing: border-box;
				-moz-box-sizing: border-box;
				-webkit-box-sizing: border-box;
			}}	

			.form-group select {{
				display: block;
				padding: 10px;
			}}
			.btn-primary {{
				display: block;
				padding: 10px 20px;
				background-color: #00695c;
				color: white;
				border: none;
				border-radius: 5px;
				cursor: pointer;
				text-align: center;
				margin-bottom: 10px;
				font-size: 16px;
				width: 100%;
            }}
            .btn-primary:hover {{
                background-color: #004d40;
            }}
            .back-button {{
                background-color: #00695c;
                color: white;
                text-decoration: none;
				padding: 10px 20px;
				border-radius: 5px;
				display: block; /* Change to block to center horizontally */
				margin: 20px auto 0; /* Center the button horizontally */
				width: fit-content; /* Set width to fit content */
            }}
            .back-button:hover {{
                background-color: #004d40;
            }}
            .message {{
                text-align: center;
                color: #28a745;
                margin-top: 20px;
            }}
            @media screen and (max-width: 600px) {{
                select {{
                    width: 80%;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 style="text-align: center;">{'Design or Flooring' if department.lower() == 'design or flooring' else department.capitalize()} Representative Sign-in</h1>
            <form method="POST" enctype="multipart/form-data" onsubmit="return validateFileUpload()">
                <div class="form-group">
                    <label for="name">Name:</label>
                    <input type="text" id="name" name="name" required>
                </div>
				<div class="form-group">
					<label for="vendor">Vendor:</label>
					<div class="input-group">
						<input type="text" id="vendor" name="vendor" placeholder="Enter vendor(s)" required class="vendor-input">
						<button type="button" class="vendor-button add-vendor" id="add-vendor">+</button>
					</div>
				</div>
				<div id="additional-vendors"></div>
				<div class="form-group">
                    <label for="store">Store:</label>
                    <select id="store" name="store" required>
                        <option value="" disabled selected>Select a store</option>
                        {''.join(f'<option value="{store}">{store}</option>' for store in stores)}
                    </select>
                </div>
                <div class="form-group">
                    <label for="visit_summary">Visit Summary:</label>
                    <textarea id="visit_summary" name="visit_summary" placeholder="Enter visit summary" required></textarea>
                </div>
			<button type="submit" class="btn-primary">Sign in</button>
		</form>
            <div class="message">{message}</div>
            <a href="/" class="back-button">Back to Home</a>
        </div>
        <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    const addVendorBtn = document.getElementById('add-vendor');
                    addVendorBtn.addEventListener('click', function() {{
                        const vendorList = document.getElementById('additional-vendors');
                        const newVendorGroup = document.createElement('div');
                        newVendorGroup.classList.add('form-group');

                        const newInputGroup = document.createElement('div');
                        newInputGroup.classList.add('input-group');

                        const newVendorInput = document.createElement('input');
                        newVendorInput.setAttribute('type', 'text');
                        newVendorInput.setAttribute('name', 'vendor');
                        newVendorInput.setAttribute('placeholder', 'Enter vendor(s)');
                        newVendorInput.classList.add('vendor-input');

                        const removeVendorBtn = document.createElement('button');
                        removeVendorBtn.innerText = '-';
                        removeVendorBtn.type = 'button';
                        removeVendorBtn.classList.add('vendor-button', 'remove-vendor');
                        removeVendorBtn.onclick = function() {{ newVendorGroup.remove(); }};

                        newInputGroup.appendChild(newVendorInput);
                        newInputGroup.appendChild(removeVendorBtn);

                        newVendorGroup.appendChild(newInputGroup);
                        vendorList.appendChild(newVendorGroup);
                    }});

                    document.getElementById('photo').addEventListener('change', fileSelected);
                }});

                function fileSelected() {{
                    var photoInput = document.getElementById('photo');
                    var uploadButton = document.getElementById('upload-button');
                    var photoMessage = document.getElementById('photo-message');

                    if (photoInput.files.length > 0) {{
                        uploadButton.textContent = 'File Uploaded Successfully';
                        uploadButton.style.backgroundColor = '#4CAF50';
                        fadeOutEffect(uploadButton);
                    }} else {{
						photoMessage.style.display = 'block';
						photoMessage.textContent = 'Please upload a file.'; // Custom message
						photoMessage.className = 'custom-file-upload'; // Reuse your button's style for consistency
						photoMessage.style.backgroundColor = '#FFCDD2'; // Use a light red background color for the error message
						photoMessage.style.color = '#D32F2F'; // Dark red text color for better readability
						photoMessage.style.borderColor = '#D32F2F'; // Matching border color
						photoMessage.style.display = 'inline-block'; // Override display property
						photoMessage.style.width = 'calc(100% - 20px)'; // Account for padding
						photoMessage.style.marginTop = '10px'; // Add some space between the button and the message
						photoMessage.style.textAlign = 'center'; // Center the text
					}}
                }}

                function validateFileUpload() {{
                    var photoInput = document.getElementById('photo');
                    if (photoInput.files.length === 0) {{
                        document.getElementById('photo-message').style.display = 'block';
                        return false;
                    }}
                    return true;
                }}

                function fadeOutEffect(target) {{
                    var fadeEffect = setInterval(function () {{
                        if (!target.style.opacity) {{
                            target.style.opacity = 1;
                        }}
                        if (target.style.opacity > 0) {{
                            target.style.opacity -= 0.1;
                        }} else {{
                            clearInterval(fadeEffect);
                            target.style.display = 'none';
                        }}
                    }}, 50);
                }}
            </script>
        </div>
    </body>
    </html>
    """
    return render_template_string(signin_html)

@app.route('/check', methods=['GET', 'POST'])
def check_signin():
    if request.method == 'POST':
        if 'filter' in request.form:
            return render_signin_page(request.form)
        else:
            password = request.form.get('password', '')
            if password == PASSWORD:
                return render_signin_page(request.form)
            else:
                return render_template_string("""
                <!DOCTYPE html>
                <html lang="en">
                <head>
					<meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Incorrect Password</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            background-color: #e0f7fa;
                            text-align: center;
                            padding: 20px;
                        }
                        .back-button {
                            display: inline-block;
                            padding: 10px;
                            background-color: #00695c;
                            color: white;
                            text-decoration: none;
                            border-radius: 5px;
                            margin: 10px;
                        }
                    </style>
                </head>
                <body>
                    <h1>Incorrect Password</h1>
                    <p>The password you entered is incorrect. Please try again.</p>
                    <a href="/" class="back-button">Back to Home</a>
                </body>
                </html>
                """)
    else:
        return render_template_string("""
		<!DOCTYPE html>
		<html lang="en">
		<head>
			<meta name="viewport" content="width=device-width, initial-scale=1.0">
			<title>Enter Password</title>
			<style>
				body {
					font-family: Arial, sans-serif;
					background-color: #e0f7fa;
					text-align: center;
					padding: 20px;
				}
				.password-container {
					position: relative;
					display: inline-block;
					margin: 10px;
				}

				input[type=password], input[type=text] {
					font-size: 16px;
					padding: 8px 45px 8px 8px; /* Adjust right padding to make room for the eye icon */
					border-radius: 5px;
					border: 1px solid #00695c;
					width: 220px; /* Set a fixed width to prevent size changes */
					box-sizing: border-box;
				}

				.eye-icon {
					position: absolute;
					right: -5px; /* Position the eye icon within the right padding of the input */
					top: 50%;
					transform: translateY(-50%);
					cursor: pointer;
					border: none;
					background: none;
					padding: 8px;
					color: #757575;
				}
				input[type=submit] {
					cursor: pointer;
					background-color: #00695c;
					color: white;
					border: none;
					border-radius: 5px;
					padding: 8px 20px;
				}
				input[type=submit]:hover {
					background-color: #004d40;
				}
				.back-button {
					display: inline-block;
					padding: 10px;
					background-color: #00695c;
					color: white;
					text-decoration: none;
					border-radius: 5px;
					margin: 10px;
				}
			</style>
		</head>
		<body>
			<h1>Enter Password to View Sign-in History</h1>
			<a href="/" class="back-button">Back to Home</a>
			<form method="POST">
				<div class="password-container">
					<input type="password" name="password" id="password" required>
					<span class="eye-icon" id="togglePassword">👁️</span>
				</div>
				<input type="submit" value="Submit">
			</form>
			<script>
				const togglePassword = document.getElementById('togglePassword');
				const passwordInput = document.getElementById('password');

				togglePassword.addEventListener('click', function() {
					const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
					passwordInput.setAttribute('type', type);
					this.textContent = type === 'password' ? '👁️' : '🙈';
				});
			</script>
		</body>
		</html>
        """)
def render_signin_page(form_data):
    selected_store = form_data.get('store', '')
    start_date = form_data.get('start_date', '')
    end_date = form_data.get('end_date', '')

    query = Representative.query
    if selected_store:
        query = query.filter_by(store=selected_store)
    if start_date:
        query = query.filter(Representative.time >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(Representative.time < end_datetime)

    accra_tz = pytz.timezone('Africa/Accra')

    store_signin_records = query.order_by(Representative.time.desc()).all()
    for record in store_signin_records:
        record.time = record.time.replace(tzinfo=pytz.utc).astimezone(accra_tz)

    formatted_records = [
        {
            'name': record.name,
            'date': record.time.strftime('%A, %B %d, %Y'),
            'time': record.time.strftime('%I:%M %p'),
            'department': 'Design or Flooring' if record.department.lower() == 'design or flooring' else 'Furniture',
            'store': record.store,
            'vendor': record.vendor,
            'visit_summary': record.visit_summary,
        }
        for record in store_signin_records
    ]
    stores = [
        "Dania", "Winter Garden", "Casselberry", "Port Charlotte", "Melbourne",
        "Jacksonville", "North Palm Beach", "Naples", "Stuart", "Boca",
        "Fort Myers", "Sarasota", "West Palm Beach", "Pembroke Pines",
        "Pinecrest", "Fort Lauderdale"
    ]
    stores.sort() 

    check_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reps Sign-in History</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #e0f7fa;
                padding: 20px;
                margin: 0;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            h1 {{
                color: #00695c;
                text-align: center;
            }}
            .filter-form {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .filter-form label {{
                margin-right: 10px;
            }}
            .filter-form input, .filter-form select {{
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #ced4da;
            }}
            .filter-form input[type="submit"] {{
                background-color: #00695c;
                color: white;
                border: none;
                cursor: pointer;
                transition: background-color 0.3s;
            }}
            .filter-form input[type="submit"]:hover {{
                background-color: #004d40;
            }}
            .records-table {{
                width: 100%;
                border-collapse: collapse;
            }}
            .records-table th, .records-table td {{
                padding: 15px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            .records-table th {{
                background-color: #b2dfdb;
                color: #00695c;
            }}
            .records-table tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            .records-table tr:hover {{
                background-color: #e0f2f1;
            }}
			.back-button {{
				background-color: #00695c;
				color: white;
				text-decoration: none;
				padding: 10px 20px;
				border-radius: 5px;
				display: block;
				margin: 10px auto; /* Center horizontally with margin */
				width: fit-content; /* Set width to fit content */
				margin-bottom: 20px; /* Add margin below the button */
				margin-top: 20px; /* Adjust the top margin */
			}}

			.back-button:hover {{
				background-color: #004d40;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Reps Sign-in History</h1>
            <a href="/" class="back-button">Back to Home</a>
            <form method="POST" class="filter-form" onsubmit="return validateDates()">
                        <input type="hidden" name="filter" value="1">
            <label for="store">Select Store:</label>
            <select name="store" id="store">
                <option value="">Select a store</option>
                {''.join(f'<option value="{store}" {"selected" if store == selected_store else ""}>{store}</option>' for store in stores)}
            </select>
            <label for="start_date">Start Date:</label>
            <input type="date" name="start_date" id="start_date" value="{start_date}" onchange="updateEndDateMin()">
            <label for="end_date">End Date:</label>
            <input type="date" name="end_date" id="end_date" value="{end_date}" min="{start_date}">
            <input type="submit" value="Filter Records">
        </form>
        <table class="records-table">
            <tr>
                <th>Name</th>
                <th>Vendor(s)</th>
                <th>Date</th>
                <th>Time</th>
                <th>Department</th>
                <th>Store</th>
                <th>Visit Summary</th>
            </tr>
            {''.join(f"<tr><td>{r['name']}</td><td>{r['vendor']}</td><td>{r['date']}</td><td>{r['time']}</td><td>{r['store']}</td><td>{r['department']}</td><td>{r['visit_summary']}</td></tr>" for r in formatted_records)}
        </table>
    </div>
    <script>
        function updateEndDateMin() {{
            var startDate = document.getElementById('start_date').value;
            document.getElementById('end_date').min = startDate;
        }}
        function validateDates() {{
            var startDate = document.getElementById('start_date').value;
            var endDate = document.getElementById('end_date').value;
            if (new Date(startDate) > new Date(endDate)) {{
                alert('End date cannot be earlier than start date.');
                return false;
            }}
            return true;
        }}
    </script>
	</body>
	</html>           
    """
    return render_template_string(check_html)

@app.route('/confirm/<int:signin_id>', methods=['POST'])
def confirm_visit(signin_id):
    signin = Representative.query.get_or_404(signin_id)
    signin.confirmed = True
    db.session.commit()
    
    return "Visit confirmed successfully!"

if __name__ == '__main__':
    app.run(debug=False, port=21211)
