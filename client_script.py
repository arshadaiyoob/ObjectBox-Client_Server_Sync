import requests
import time
from threading import Thread
from objectbox import *

from objectbox.model import PropertyType
from objectbox.query import OBX_query_builder

# Store.remove_db_files("objectbox-data")

# Define the Person entity
@Entity()
class Person:
    id = Id()
    name = String()
    age = Int32()
    is_synced = String()  # To track if the record is synced with the server

# Initialize ObjectBox
store = Store(directory="objectbox-data")

# Get a box for the "Person" entity; a Box is the main interaction point with objects and the database.
person_box = store.box(Person)

# CRUD operations
def add_person(name, age):
    person = Person(name=name, age=age, is_synced='False')
    person_box.put(person)
    return person

def get_all_persons():
    return person_box.get_all()

def update_person(person_id, name=None, age=None):
    person = person_box.get(person_id)
    if person:
        if name:
            person.name = name
        if age:
            person.age = age
        person.is_synced = 'False'
        person_box.put(person)

def delete_person(person_id):
    person_box.remove(person_id)

# Online synchronization
API_URL = "http://127.0.0.1:5000/persons"  # Server endpoint

def sync_with_server():
    # Correct way to query for unsynced persons
    # Create a query builder
    query_builder = person_box.query()

    # Build the query condition explicitly
    query_builder.equals_string(Person.is_synced, 'False')

    # Execute the query and retrieve unsynced persons
    unsynced_persons = query_builder.build().find()
    for person in unsynced_persons:
        try:
            response = requests.post(API_URL, json={"id": person.id, "name": person.name, "age": person.age})
            if response.status_code == 200:
                person.is_synced = 'True'
                person_box.put(person)
        except requests.RequestException as e:
            print(f"Failed to sync person {person.id}: {e}")

def fetch_from_server():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            persons = response.json()
            for person_data in persons:
                person = Person(id=person_data["id"], name=person_data["name"], age=person_data["age"], is_synced='True')
                person_box.put(person)
    except requests.RequestException as e:
        print(f"Failed to fetch persons from server: {e}")

def periodic_sync(interval=60):
    while True:
        sync_with_server()
        fetch_from_server()
        time.sleep(interval)

# Start background sync
sync_thread = Thread(target=periodic_sync, args=(60,))
sync_thread.daemon = True
sync_thread.start()

# Example usage
if __name__ == "__main__":
    # Add a new person
    new_person = add_person("John Doe", 30)

    # Print all persons
    persons = get_all_persons()
    for person in persons:
        print(person.id, person.name, person.age, person.is_synced)

    # Keep the script running to allow background sync
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
