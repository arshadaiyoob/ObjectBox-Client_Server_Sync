from flask import Flask, request, jsonify
from objectbox import *

app = Flask(__name__)

# Define the Person entity
@Entity()
class Person:
    id = Id
    name = String
    age = Int32

# Initialize ObjectBox
store = Store(directory="objectbox-server-data")


# Create a Box for the Person entity
person_box = store.box(Person)

# Endpoint to create or update a person
@app.route('/persons', methods=['POST'])
def add_or_update_person():
    data = request.json
    person_id = data.get('id')
    if person_id:
        person = person_box.get(person_id)
        if person:
            person.name = data['name']
            person.age = data['age']
            person_box.put(person)
        else:
            person = Person(id=person_id, name=data['name'], age=data['age'])
            person_box.put(person)
    else:
        person = Person(name=data['name'], age=data['age'])
        person_box.put(person)
    return jsonify(person_box.get(person.id).__dict__), 200

# Endpoint to get all persons
@app.route('/persons', methods=['GET'])
def get_all_persons():
    persons = person_box.get_all()
    return jsonify([person.__dict__ for person in persons]), 200

# Endpoint to get a specific person by ID
@app.route('/persons/<int:person_id>', methods=['GET'])
def get_person(person_id):
    person = person_box.get(person_id)
    if person:
        return jsonify(person.__dict__), 200
    return jsonify({"error": "Person not found"}), 404

# Endpoint to delete a person by ID
@app.route('/persons/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    if person_box.get(person_id):
        person_box.remove(person_id)
        return jsonify({"message": "Person deleted"}), 200
    return jsonify({"error": "Person not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
