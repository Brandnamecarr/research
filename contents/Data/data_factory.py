'''
    Generates data for use in algorithms
'''

import csv
import random

# Lists of sample first and last names
first_names = [
    "Liam", "Noah", "Ethan", "Aiden", "James", "Mohamed", "José", "Amir", "Jackson", "David",
    "Carlos", "Mateo", "Juan", "Elijah", "Carter", "William", "Darius", "Micah", "Daniel", "Aditya",
    "Sebastian", "Isaac", "Leonardo", "Arjun", "Xavier", "Ibrahim", "Julian", "Caleb", "Oscar", "Andre",
    "Nathan", "Kevin", "Elias", "Hamza", "Ezra", "Gabriel", "Rajesh", "Lucas", "Isaiah", "Joshua",
    "Anthony", "Diego", "Alejandro", "Dominic", "Ravi", "Benjamin", "Samuel", "Theodore", "Ryan", "Dylan",
    "Olivia", "Emma", "Ava", "Sophia", "Isabella", "Mia", "Fatima", "Layla", "Chloe", "Harper",
    "Charlotte", "Amara", "Aisha", "Emily", "Scarlett", "Maya", "Madison", "Zoe", "Sofia", "Lila",
    "Gabriella", "Eliana", "Hannah", "Lily", "Amelia", "Nora", "Abigail", "Aria", "Radhika", "Aurora",
    "Evelyn", "Valeria", "Maria", "Sienna", "Anaya", "Jasmine", "Vanessa", "Hailey", "Priya", "Bianca",
    "Ellie", "Naomi", "Kayla", "Fiona", "Ruby", "Grace", "Juliana", "Natalia", "Leah", "Victoria"
]

last_names = [
   
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Patel", "Chen", "Nguyen", "Kim", "Kumar", "Sharma", "Ali", "Hassan", "Ahmed", "Singh",
    "Yamamoto", "Kawasaki", "Ibrahim", "Chowdhury", "Torres", "Castillo", "Silva", "Fernandez", "Rivera", "Morales",
    "Diaz", "Castro", "Gomez", "Vargas", "Santos", "Reyes", "Gupta", "Banerjee", "Omar", "Rahman",
    "Schmidt", "Kovacs", "Ivanov", "Petrov", "Novak", "Horvath", "Toth", "Popescu", "Rossi", "Ferrari",
    "Weber", "Fischer", "Müller", "Lombardi", "Giordano", "Ricci", "Bianchi", "Moretti", "Krause", "Hansen",
    "Okafor", "Abebe", "Mensah", "Nkrumah", "Achebe", "Tshabalala", "Mwangi", "Adebayo", "Chike", "Zulu",
    "Al-Farsi", "Haddad", "Zayed", "Jaber", "Nasr", "Saleh", "Khalil", "Fahmy", "Barakat", "El-Sayed",
    "Murphy", "O'Connor", "Mendoza", "Serrano", "Palacios", "Bautista", "Montoya", "Esposito", "Ramos", "Delgado"
]

email_domains = [
    "gmail.com", "yahoo.com", "outlook.com", "example.com", "aol.com"
]


# Function to generate a random email
def generate_email(first_name, last_name):
    return f"{first_name.lower()}.{last_name.lower()}@{random.choice(email_domains)}"

# create person and return
def create_person():
    first = random.choice(first_names)
    last = random.choice(last_names)
    email = generate_email(first, last)
    return first, last, email

# generate mass amounts of people
def create_people(quantity, write_to_file=False):
    people = []
    for _ in range(quantity):
        people.append(create_person())
    

    if write_to_file:
        write_to_csv(people, ['First', 'Last', 'Email'], './data/people.csv')
    else:
        print('not writing to csv')

def write_to_csv(data, labels, filepath):
    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(labels)
        writer.writerows(data)
