import os
import time
import json
from flask_cors import CORS
import firebase_admin
from flask import Flask, request, jsonify, redirect, session, render_template
from firebase_admin import credentials, firestore, initialize_app
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from time import sleep
from datetime import date, datetime, timedelta
import datetime
# Initialize Flask app
app = Flask(__name__)
CORS(app)

from_number = '+15739733743' # put your twilio number here'
to_number = '+16467326671' # put your own phone number here

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']

api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']


app.secret_key = api_secret
client = Client(account_sid, auth_token)

# Initialize Firestore DB
if not firebase_admin._apps:
    cred = credentials.Certificate('google-credentials.json')
    default_app = initialize_app(cred)
db = firestore.client()
user_ref = db.collection('users')

# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to our Remintodo !!</h1>"

#Adding user phone number to Twilio Verified Users
def verifyTwilioPhoneNum(username, phoneNum):
    if '+1' not in phoneNum:
        phoneNum = '+1' + phoneNum
    validation_request = client.validation_requests.create(
        friendly_name=username,
        phone_number=phoneNum)
    return validation_request.validation_code
                          
@app.route('/add-user', methods=['POST'])
def add_user():
    document_id = request.json['number']
    username = request.json['name']

    try:
        user_ref.document(document_id).set(request.json)
        user = user_ref.document(document_id).get()
        validationCode = verifyTwilioPhoneNum(username, document_id)
        user = user.to_dict()
        user['validationCode'] = validationCode
        return jsonify(user), 200
    except Exception as e:
        return f"An Error Occured: {e}"
    
@app.route('/user', methods=['GET'])
def fetch_user():
    try:
        # Check if ID was passed to URL query
        user_id = request.args.get('number')
        user = user_ref.document(user_id).get()
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return f"An Error Occured: {e}"

 
@app.route('/users', methods=['GET'])
def fetch_all_user():
    try:
        # Check if ID was passed to URL query
        all_users = [doc.to_dict() for doc in user_ref.stream()]
        return jsonify(all_users), 200
    except Exception as e:
        return f"An Error Occured: {e}"
    
@app.route('/update-user',  methods=['POST', 'PUT'])
def update_user():
    pass
    
@app.route('/<number>/add', methods=['POST'])
def create(number):
    """
        create() : Add document to Firestore collection with request body.
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json={'id': '1', 'title': 'Write a blog post'}
    """
    try:
        id = request.json['id']
        todo_ref = user_ref.document(number).collection("todos")
        todo_ref.document(id).set(request.json)
        all_todos = [doc.to_dict() for doc in todo_ref.stream()]
        return jsonify(all_todos), 200
    except Exception as e:
        return f"An Error Occured: {e}"

@app.route('/<number>/list', methods=['GET'])
def read(number):
    """
        read() : Fetches documents from Firestore collection as JSON.
        todo : Return document that matches query ID.
        all_todos : Return all documents.
    """
    try:
        # Check if ID was passed to URL query
        todo_id = request.args.get('id')
        if todo_id:
            todo_ref = user_ref.document(number).collection("todos")
            todo = todo_ref.document(todo_id).get()
            return jsonify(todo.to_dict()), 200
        else:
            todo_ref = user_ref.document(number).collection("todos")
            all_todos = [doc.to_dict() for doc in todo_ref.stream()]
            return jsonify(all_todos), 200
    except Exception as e:
        return f"An Error Occured: {e}"

@app.route('/<number>/update', methods=['POST', 'PUT'])
def update(number):
    """
        update() : Update document in Firestore collection with request body.
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json={'id': '1', 'title': 'Write a blog post today'}
    """
    try:
        todo_ref = user_ref.document(number).collection("todos")
        id = request.json['id']
        todo_ref.document(id).update(request.json)
        all_todos = [doc.to_dict() for doc in todo_ref.stream()]
        return jsonify(all_todos), 200
    except Exception as e:
        return f"An Error Occured: {e}"

@app.route('/<number>/delete', methods=['GET', 'DELETE'])
def delete(number):
    """
        delete() : Delete a document from Firestore collection.
    """
    try:
        todo_ref = user_ref.document(number).collection("todos")
        # Check for ID in URL query
        todo_id = request.args.get('id')
        todo_ref.document(todo_id).delete()
        all_todos = [doc.to_dict() for doc in todo_ref.stream()]
        return jsonify(all_todos), 200
    except Exception as e:
        return f"An Error Occured: {e}"
    
@app.route('/<number>/add-motivator', methods=['POST'])
def create_motivator(number):
    """
        create() : Add document to Firestore collection with request body.
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json={'id': '1', 'title': 'Write a blog post'}
    """
    try:
        motivator_ref = user_ref.document(number).collection("motivators")
        id = request.json['id']
        motivator_ref.document(id).set(request.json)
        all_motivators = [doc.to_dict() for doc in motivator_ref.stream()]
        return jsonify(all_motivators), 200
    except Exception as e:
        return f"An Error Occured: {e}"
    
@app.route('/<number>/list-motivator', methods=['GET'])
def read_motivator(number):
    """
        read() : Fetches documents from Firestore collection as JSON.
        todo : Return document that matches query ID.
        all_todos : Return all documents.
    """
    try:
        motivator_ref = user_ref.document(number).collection("motivators")
        # Check if ID was passed to URL query
        motivator_id = request.args.get('id')
        if motivator_id:
            motivator = motivator_ref.document(motivator_id).get()
            return jsonify(motivator.to_dict()), 200
        else:
            motivator_ref = user_ref.document(number).collection("motivators")
            all_motivators = [doc.to_dict() for doc in motivator_ref.stream()]
            return jsonify(all_motivators), 200
    except Exception as e:
        return f"An Error Occured: {e}"
    
@app.route('/<number>/delete-motivator', methods=['GET', 'DELETE'])
def delete_motivator(number):
    """
        delete() : Delete a document from Firestore collection.
    """
    try:
        motivator_ref = user_ref.document(number).collection("motivators")
        # Check for ID in URL query
        motivator_id = request.args.get('id')
        motivator_ref.document(motivator_id).delete()
        all_motivators = [doc.to_dict() for doc in motivator_ref.stream()]
        return jsonify(all_motivators), 200
    except Exception as e:
        return f"An Error Occured: {e}"

@app.route('/call-motivator', methods=['GET', 'POST'])
def call_motivator():
    try:

        client = Client(account_sid, auth_token)
        
        call = client.calls.create(
                                twiml='<Response><Say>Call Pramo to remind her of tasks!</Say></Response>',
                                to=to_number,
                                from_=from_number
                            )
        
        return jsonify({'sid' : call.sid}), 200
    except Exception as e:
        return f"An Error Occured: {e}"

def get_tasks_for_today(number):
    """
        read() : Fetches documents from Firestore collection as JSON.
        todo : Return document that matches query ID.
        all_todos : Return all documents.
    """
    our_response = "Hey!\n You NEED to complete the below tasks if you want to have a proper night's sleep. \n"
    try:
        todo_ref = user_ref.document(number).collection("todos")
        all_todos = [doc.to_dict() for doc in todo_ref.stream()]
        incomplete_task_titles = []
        for task in all_todos:
            if task['status'] != 'Completed':
                deadline_parsed = datetime.datetime.strptime(task['deadline'], "%Y-%m-%dT%H:%M:%S.%fZ")
                task_year = deadline_parsed.year
                task_month = deadline_parsed.month
                task_day = deadline_parsed.day
                now = datetime.datetime.now()
                if(task_month == now.month and task_day == now.day and task_year == now.year):
                    incomplete_task_titles.append(task['title'])
        for task_index in range(len(incomplete_task_titles)):
            our_response += str(task_index + 1) + '. ' + incomplete_task_titles[task_index] + '\n'
        return our_response
    except Exception as e:
        return f"An Error Occured: {e}"
  
@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Start our TwiML response
    users_json = {}
    users = user_ref.stream()
    for user in users:
        users_json[user.id] = user.to_dict()
        print(user.to_dict())
        tasks = get_tasks_for_today(users_json[user.id]['number'])
        print(tasks)

    resp = MessagingResponse()

    print('Tasks ', tasks)
    # Add a message
    resp.message(tasks)

    return str(resp)

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run()