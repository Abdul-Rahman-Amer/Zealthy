from flask import Flask, request, jsonify
import mysql.connector

from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def create_tickets_table():
    connection = mysql.connector.connect(
        host='zealthy.ckjcs4air21b.us-east-1.rds.amazonaws.com',
        database='zealthy',
        user='admin',
        password='123456789'
    )
    cursor = connection.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS tickets (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        email VARCHAR(255),
        priority VARCHAR(50),
        description TEXT,
        attachment BLOB,  # Updated to store image as BLOB
        submission_date DATETIME
    );
    """
    cursor.execute(create_table_query)
    connection.commit()
    cursor.close()
    connection.close()


@app.route('/submit_ticket', methods=['POST'])
def submit_ticket():
    data = request.form  # Use .form to get form data

    # Use .get() with default values for potentially missing fields
    name = data.get('name', None)
    email = data.get('email', None)
    priority = data.get('priority', None)
    description = data.get('description', None)
    submission_date = datetime.now()

    # Connect to the database
    connection = mysql.connector.connect(host='zealthy.ckjcs4air21b.us-east-1.rds.amazonaws.com',
                                         database='zealthy',
                                         user='admin',
                                         password='123456789')
    cursor = connection.cursor()

    # Check if attachment is provided
    image = request.files.get('attachment')
    image_binary = image.read() if image else None

    # Insert query
    insert_query = """
    INSERT INTO tickets (name, email, priority, description, attachment, submission_date)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    ticket_data = (name, email, priority, description, image_binary, submission_date)

    cursor.execute(insert_query, ticket_data)
    connection.commit()
    cursor.close()
    connection.close()

    return "Ticket submitted successfully"

@app.route('/tickets', methods=['GET'])
def get_tickets():
    # Database connection
    connection = mysql.connector.connect(
        host='zealthy.ckjcs4air21b.us-east-1.rds.amazonaws.com',
        database='zealthy',
        user='admin',
        password='123456789'
    )
    cursor = connection.cursor(dictionary=True)

    # Fetching all tickets
    cursor.execute("SELECT * FROM tickets")
    tickets = cursor.fetchall()

    cursor.close()
    connection.close()

    # Return the fetched tickets as JSON
    return jsonify(tickets)

@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.json
    ticket_id = data.get('ticketId')
    new_status = data.get('status')

    print(ticket_id)

    # Check if the ticket_id and new_status are valid
    if not ticket_id or not new_status:
        return jsonify({'message': 'Invalid data'}), 400

    # Check if the new_status is valid (e.g., 'new', 'in progress', 'resolved')
    if new_status not in ('new', 'in progress', 'resolved'):
        return jsonify({'message': 'Invalid status'}), 400

    # Update the status of the ticket with the given ID
    connection = mysql.connector.connect(
        host='zealthy.ckjcs4air21b.us-east-1.rds.amazonaws.com',
        database='zealthy',
        user='admin',
        password='123456789'
    )
    cursor = connection.cursor()

    update_query = """
    UPDATE tickets
    SET status = %s
    WHERE id = %s
    """
    update_data = (new_status, ticket_id)

    cursor.execute(update_query, update_data)
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Status updated successfully'})


if __name__ == '__main__':
    create_tickets_table()  # Ensure the table exists
    app.run(debug=True)
