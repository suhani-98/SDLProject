import os
import shutil
from flask import Flask, render_template, request, redirect, url_for, flash

# Initialize the Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static/uploads/')  # Static uploads folder
app.secret_key = 'supersecretkey'  # Needed for flashing messages

# Define the root directories for CW and SW
CW_ROOT = os.path.join(os.getcwd(), 'CW')  # CW directory inside app directory
SW_ROOT = os.path.join(os.getcwd(), 'SW')  # SW directory inside app directory

# Define the subfolders for each year
years = ['1st', '2nd', '3rd', '4th']

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
print(f"DEBUG: Ensured upload directory exists at {app.config['UPLOAD_FOLDER']}")

# Ensure CW and SW directories exist
for year in years:
    cw_year_dir = os.path.join(CW_ROOT, year)
    sw_year_dir = os.path.join(SW_ROOT, year)
    os.makedirs(cw_year_dir, exist_ok=True)
    os.makedirs(sw_year_dir, exist_ok=True)
    print(f"DEBUG: Ensured directories exist - CW: {cw_year_dir}, SW: {sw_year_dir}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        print("DEBUG: No file part in the request")
        return redirect(url_for('index'))

    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        print("DEBUG: No selected file")
        return redirect(url_for('index'))

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        print(f"DEBUG: Saving file temporarily at {file_path}")
        file.save(file_path)  # Save the file temporarily

        # Now process the file based on its name and move it to the right folder
        result = organize_file(file_path)
        if result:
            flash(f'File successfully moved to {result}')
            print(f"DEBUG: File successfully moved to {result}")
        else:
            flash('Invalid file name. Ensure it contains a year and CW/SW.')
            print("DEBUG: Invalid file name; file not moved.")

        return redirect(url_for('index'))

def organize_file(file_path):
    """
    Function to organize the uploaded file based on its name.
    The file will be moved to the appropriate year and category (CW/SW).
    """
    file_name = os.path.basename(file_path)
    print(f"DEBUG: Organizing file: {file_name}")

    for year in years:
        if year in file_name:
            print(f"DEBUG: Found year '{year}' in file name")
            if 'CW' in file_name:
                destination_folder = os.path.join(CW_ROOT, year)
                print(f"DEBUG: Destination folder (CW): {destination_folder}")
            elif 'SW' in file_name:
                destination_folder = os.path.join(SW_ROOT, year)
                print(f"DEBUG: Destination folder (SW): {destination_folder}")
            else:
                print("DEBUG: File name doesn't contain 'CW' or 'SW'")
                return None  # Invalid file name, doesn't contain 'CW' or 'SW'

            destination_path = os.path.join(destination_folder, file_name)
            print(f"DEBUG: Moving file from {file_path} to {destination_path}")

            # Check if the destination folder exists before moving
            if not os.path.exists(destination_folder):
                print(f"DEBUG: Destination folder does not exist: {destination_folder}")
                return None

            try:
                shutil.move(file_path, destination_path)
                print(f"DEBUG: File moved successfully to {destination_path}.")
                return destination_path  # Return where the file was moved
            except Exception as e:
                print(f"DEBUG: Error moving file: {e}")
                return None  # Handle any errors

    print("DEBUG: File name didn't match any valid year")
    return None  # File name didn't match any valid year

if __name__ == '__main__':
    try:
        print("DEBUG: Starting Flask app")
        app.run(debug=True)
    except Exception as e:
        print(f"DEBUG: Error starting Flask app: {e}")
