import os
import time
import json
from flask_cors import CORS
import firebase_admin
from flask import Flask, request, jsonify, redirect, session, render_template
from firebase_admin import credentials, firestore, initialize_app
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

# Initialize Flask app
app = Flask(__name__)
CORS(app)



api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
app.secret_key = api_secret
client = Client(account_sid, auth_token)

# Initialize Firestore DB
if not firebase_admin._apps:
    cred = credentials.Certificate('google-credentials.json')
    default_app = initialize_app(cred)
db = firestore.client()
todo_ref = db.collection('todos')
motivator_ref = db.collection('motivators')

# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to our Remintodo !!</h1>"


@app.route('/add', methods=['POST'])
def create():
    """
        create() : Add document to Firestore collection with request body.
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json={'id': '1', 'title': 'Write a blog post'}
    """
    try:
        id = request.json['id']
        todo_ref.document(id).set(request.json)
        all_todos = [doc.to_dict() for doc in todo_ref.stream()]
        return jsonify(all_todos), 200
    except Exception as e:
        return f"An Error Occured: {e}"

@app.route('/list', methods=['GET'])
def read():
    """
        read() : Fetches documents from Firestore collection as JSON.
        todo : Return document that matches query ID.
        all_todos : Return all documents.
    """
    try:
        # Check if ID was passed to URL query
        todo_id = request.args.get('id')
        if todo_id:
            todo = todo_ref.document(todo_id).get()
            return jsonify(todo.to_dict()), 200
        else:
            all_todos = [doc.to_dict() for doc in todo_ref.stream()]
            return jsonify(all_todos), 200
    except Exception as e:
        return f"An Error Occured: {e}"

@app.route('/update', methods=['POST', 'PUT'])
def update():
    """
        update() : Update document in Firestore collection with request body.
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json={'id': '1', 'title': 'Write a blog post today'}
    """
    try:
        id = request.json['id']
        todo_ref.document(id).update(request.json)
        all_todos = [doc.to_dict() for doc in todo_ref.stream()]
        return jsonify(all_todos), 200
    except Exception as e:
        return f"An Error Occured: {e}"

@app.route('/delete', methods=['GET', 'DELETE'])
def delete():
    """
        delete() : Delete a document from Firestore collection.
    """
    try:
        # Check for ID in URL query
        todo_id = request.args.get('id')
        todo_ref.document(todo_id).delete()
        all_todos = [doc.to_dict() for doc in todo_ref.stream()]
        return jsonify(all_todos), 200
    except Exception as e:
        return f"An Error Occured: {e}"
    
@app.route('/add-motivator', methods=['POST'])
def create_motivator():
    """
        create() : Add document to Firestore collection with request body.
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json={'id': '1', 'title': 'Write a blog post'}
    """
    try:
        id = request.json['id']
        motivator_ref.document(id).set(request.json)
        all_motivators = [doc.to_dict() for doc in motivator_ref.stream()]
        return jsonify(all_motivators), 200
    except Exception as e:
        return f"An Error Occured: {e}"
    
@app.route('/list-motivator', methods=['GET'])
def read_motivator():
    """
        read() : Fetches documents from Firestore collection as JSON.
        todo : Return document that matches query ID.
        all_todos : Return all documents.
    """
    try:
        # Check if ID was passed to URL query
        motivator_id = request.args.get('id')
        if motivator_id:
            motivator = motivator_ref.document(motivator_id).get()
            return jsonify(motivator.to_dict()), 200
        else:
            all_motivators = [doc.to_dict() for doc in motivator_ref.stream()]
            return jsonify(all_motivators), 200
    except Exception as e:
        return f"An Error Occured: {e}"
    
@app.route('/delete-motivator', methods=['GET', 'DELETE'])
def delete_motivator():
    """
        delete() : Delete a document from Firestore collection.
    """
    try:
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
                                to='+16467326671',
                                from_='+15739733743'
                            )
        
        return jsonify({'sid' : call.sid}), 200
    except Exception as e:
        return f"An Error Occured: {e}"

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Start our TwiML response
    resp = MessagingResponse()

    # Add a message
    resp.message("The Robots are coming! Head for the hills!")

    return str(resp)

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run()