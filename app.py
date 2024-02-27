from flask import Flask, render_template, request,jsonify
import base64
import csv
import os
import json
import re
import ast
from flask import redirect, url_for
app = Flask(__name__)

opens_counter = 0
open_data_dict = {}

app.static_folder = 'static'
app.static_url_path = '/static'

data_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
file_path = os.path.join(data_directory, 'opens_data.csv')

# Ensure the directory exists, create it if not
os.makedirs(data_directory, exist_ok=True)


def dashboard_csv(subject):
    print("this is sub" + subject)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'data.csv')
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        data = [row for row in reader]
        list_of_recips = []
        for index, row in enumerate(data):
            print(repr(row[0].strip()))
            print(repr(subject.strip()))
            print(subject.strip() in row[0])
            if re.match(f'^{re.escape(subject.strip().lower())}$', row[0].lower()):
                for i in range(2, len(row)):
                    print("hi" + row[0])
                    list_of_recips.append(row[i])
        return list_of_recips, row[1]

def write_user_info_to_csv(decoded_data, file_path):
    # Creating data directory if it doesn't exist
    data_directory = os.path.dirname(file_path)
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    # Extracting values from decoded_data
    data_dict = ast.literal_eval(decoded_data)
    username = data_dict.get('username', '')
    customer_id = data_dict.get('customer_id', '')

    # Customize the format of the 'Data' field as per your requirement
    user_info = f"{username},{customer_id}"

    # Writing to CSV file
    with open(file_path, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONE)
        csv_writer.writerow([username, customer_id])

    print(f"User information has been written to {file_path}")
def write_to_csv(data, file_path='your_file_path.csv'):
    with open(file_path, mode='a', newline='') as csv_file:
        fieldnames = ['User', 'Data']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        if os.stat(file_path).st_size == 0:
            writer.writeheader()

        # Extract the username and customer_id from the 'Data' field
        username, customer_id = data['Data'].get('username', ''), data['Data'].get('customer_id', '')

        # Customize the format of the 'Data' field as per your requirement
        user_info = f"{data['User']},test {customer_id} for today after successful tracking"

        writer.writerow({'User': data['User'], 'Data': user_info})


@app.route('/track/open-pixel/<encoded_data>')
def track_open_pixel(encoded_data):
    global opens_counter
    decoded_data = base64.urlsafe_b64decode(encoded_data).decode()
    print(f"Received an open with data: {decoded_data}")
    print(decoded_data)
    user_info=decoded_data
    opens_counter += 1

    # Extract and store user information
    #open_data_dict[opens_counter] = user_info
    print("this is user info")
    print()
    write_user_info_to_csv(decoded_data,file_path)
    # Write data to CSV
    #write_to_csv(user_info)

    # Return a transparent 1x1 pixel image
    pixel_content = base64.b64decode("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")
    return pixel_content, 200, {"Content-Type": "image/gif"}


@app.route('/user-info/<tracking_info>', methods=['GET'])
def user_info(tracking_info):
    users = get_users_for_tracking_info(tracking_info)
    return render_template('user_info.html', tracking_info=tracking_info, users=users)

def get_unique_tracking_info(file_path):
    try:
        with open(file_path, mode='r') as csv_file:
            reader = csv.DictReader(csv_file)
            tracking_info_list = [row['Data'].split(',')[1].strip() if ',' in row['Data'] else '' for row in reader]
            unique_tracking_info_set = set(tracking_info_list)
            sorted_unique_tracking_info = sorted(filter(None, unique_tracking_info_set))
            print(sorted_unique_tracking_info)
            return sorted_unique_tracking_info
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []
def get_users_for_tracking_info(tracking_info):
    try:
        with open(file_path, mode='r') as csv_file:
            reader = csv.DictReader(csv_file)
            users = [row['User'] for row in reader if ',' in row['Data'] and row['Data'].split(',')[1].strip() == tracking_info]
            return users
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

@app.route('/get_column_two_values', methods=['GET'])
def get_column_two_values():
    try:
        # Assuming your CSV file is in the 'data' directory and named 'opens_data.csv'
        data_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        file_path = os.path.join(data_directory, 'opens_data.csv')

        with open(file_path, 'r') as file:
            csv_reader = csv.DictReader(file)

            # Extract values from column two ("Data")
            column_two_values = sorted(set(row['Data'] for row in csv_reader))

        return render_template('index.html', column_two_values=column_two_values)

    except Exception as e:
        return jsonify({'error': str(e)})



@app.route('/display_selected_value', methods=['POST', 'GET'])
def display_selected_value():
    selected_value = request.args.get('selected_value') if request.method == 'GET' else request.form.get('selected_value')
    
    print(f"Selected Value: {selected_value}")

    if not selected_value:
        return render_template('error_page.html', error_message="Selected value not found in the request parameters")

    all_recips, number_of_recips = dashboard_csv(selected_value)

    # Assuming the CSV file has columns 'User' and 'Data'
    data_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    file_path = os.path.join(data_directory, 'opens_data.csv')

    selected_users = []

    try:
        with open(file_path, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                if row['Data'] == selected_value:
                    selected_users.append(row['User'])
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return render_template('error_page.html', error_message="Error reading CSV file")

    selected_users_num = len(selected_users)
    print(selected_users_num)

    return render_template('selected_value.html', selected_value=selected_value, selected_users=selected_users, all_recips=all_recips, selected_users_num=selected_users_num, number_of_recips=number_of_recips)


@app.route('/endpoint', methods=['POST'])
def receive_data():
    try:
        data = request.get_json()

        subject = data.get('subject', '')
        recipients = data.get('recipients', [])

        print(f"Received data - Subject: {subject}, Recipients: {recipients}")

        # Save data to CSV file
        save_to_csv(subject, recipients)

        return "Data received and saved successfully!", 200
    except Exception as e:
        return f"Error: {str(e)}", 500

def save_to_csv(subject, recipients):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'data.csv')

    try:
        with open(file_path, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            number_of_receips=str(len(recipients))

            csv_writer.writerow([subject] + [number_of_receips]+recipients)
            print(f"Data saved to CSV - Subject: {subject}, Recipients: {recipients}")
    except Exception as e:
        print(f"Error saving to CSV: {str(e)}")


if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.run(debug=True)
