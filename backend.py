import requests
import os.path
import csv
from config import Config

# Import smtplib for the actual sending function
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

key = Config.KEY
token = Config.TOKEN

authentication = "key="+key+"&token="+token

# Structures
class Task:
    def __init__(self, card_id, list_id, name, desc, members, labels, list_name=None):
        self.card_id = card_id
        self.list_id = list_id

        self.name = name
        self.list_name = list_name

        self.desc = desc
        self.members = members
        self.labels = labels

# Commands
def get_board_lists(board):
    end_point = "https://api.trello.com/1/boards/" + board + "/lists?" + authentication

    r = requests.get(end_point)

    list_ids = []
    list_names = []

    for l in r.json():
        list_ids.append(l["id"])
        list_names.append(l["name"])

    return list_ids, list_names

def get_done_list(board):
    list_ids, list_names = get_board_lists(board)
    done_list_id = -1

    for i in range(len(list_names)):
        if list_names[i].lower() == "done":
            done_list_id = list_ids[i]

    return done_list_id

def get_list_cards(list):
    end_point = "https://api.trello.com/1/lists/" + list + "/cards?" + authentication

    r = requests.get(end_point)

    cards = []

    for l in r.json():
        cards.append(l["name"])

    return cards

def get_list_info(list):
    end_point = "https://api.trello.com/1/lists/"+list +"?"+ authentication

    r = requests.get(end_point)

    return r.json()

def get_label_info(label):
    end_point = "https://api.trello.com/1/labels/"+label +"?"+ authentication

    r = requests.get(end_point)

    return r.json()

def get_member_info(member):
    end_point = "https://api.trello.com/1/members/"+member +"?"+ authentication

    r = requests.get(end_point)

    return r.json()

# MOVEMENT
def archive_cards_in_list(list):
    end_point = "https://api.trello.com/1/lists/"+list+"/archiveAllCards?" + authentication

    r = requests.post(end_point)

def move_card_to_list(card_id, list_id):
    url = "https://api.trello.com/1/cards/"+ card_id + "/idList?value="+list_id+"&" + authentication

    query_string = {"id":card_id, "idList":list_id}

    response = requests.request("PUT", url, params=query_string)

# PROCESSES
def refresh_done_list(board):
    done_list_id = get_done_list(board)

    # If the list was found
    if not done_list_id == -1:
        archive_cards_in_list(done_list_id)

    else:
        return None

def save_tasks(tasks, week_no):
    filepath = "data/week"+week_no+".csv"

    first = not os.path.exists(filepath)

    with open(filepath, 'a') as record:
        for t in tasks:
            # If first time recording details for the week, write a header for info purposes
            if first:
                record.write("card_id, list_id, name, list_name, desc, members, labels\n")
                first = False

            # Join all values of the task into a csv format
            values = [t.card_id, t.list_id, t.name, t.list_name, t.desc, t.members, t.labels]
            record.write('"' + '","'.join(values) + '"')
            record.write('\n')

def move_done_cards(board, week_no):
    url = "https://api.trello.com/1/search?" + authentication

    query_string = {"query":"board:"+board+" -is:archived label:Done -list:Done"}

    response = requests.request("GET", url, params=query_string)

    tasks_completed = []
    list_map = {} # id -> name
    label_map = {} # id -> name
    member_map = {} # id -> name
    for c in response.json()["cards"]:
        task = Task(c["id"], c["idList"], c["name"], c["desc"],
                    c["idMembers"],
                    c["idLabels"])

        tasks_completed.append(task)

        # Add unique lists and labels
        list_map[task.list_id] = ""
        for l in task.labels:
            label_map[l] = ""
        for m in task.members:
            member_map[m] = ""

    # Get list names
    for list_id in list_map.keys():
        list_map[list_id] = get_list_info(list_id)["name"]

    for label_id in label_map.keys():
        label_map[label_id] = get_label_info(label_id)["name"]

    for label_id in member_map.keys():
        member_map[label_id] = get_member_info(label_id)["fullName"]

    done_list_id = get_done_list(board)
    for t in tasks_completed:
        # Update name of task list from list info map
        t.list_name = list_map[t.list_id]

        # Update name of labels from their indeces
        new_labels = []
        for i in range(len(t.labels)):
            if not label_map[t.labels[i]].lower() == "done":
                new_labels.append(label_map[t.labels[i]])
        t.labels = ','.join(new_labels)

        for i in range(len(t.members)):
            t.members[i] = member_map[t.members[i]]
        t.members = ','.join(t.members)

        print("Task " + t.name + " from " + t.list_name)

        # Move the card
        move_card_to_list(t.card_id, done_list_id)

    if len(tasks_completed) > 0:
        save_tasks(tasks_completed, week_no)

def print_list(list):
    for e in list:
        print(e)

def load_tasks_from_file(filepath):
    tasks = []
    with open(filepath, 'r') as file:
        reader = csv.reader(file)
        first = True

        for line in reader:
            if not first:
                task = Task(line[0], line[1], line[2], line[4], line[5].split(','), line[6], line[3])
                tasks.append(task)
            else:
                first = False

    return tasks

def parse_email(tasks):
    email = "<html><head></head><body>"
    email += "<h1>Weekly Review!</h1>\n"

    tasks_by_person = {}

    for t in tasks:
        for m in t.members:
            if m not in tasks_by_person.keys():
                tasks_by_person[m] = []

            tasks_by_person[m].append(t)

    for p in tasks_by_person.keys():
        if p == "":
            email += "<b>Tasks completed without anyone tagged</b><br>\n"
        else:
            email += "<b>" + p + "</b>" + "<br>\n"

        p_tasks = tasks_by_person[p]

        for t in p_tasks:
            email += t.name + " in " + t.list_name + "<br>\n"

        email += "<br>\n"

    email += "<i>With love,<br>\nCubeBot</i>"

    email += "</body></html>"
    return email

def send_email(content, week_no):
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(Config.EMAIL, Config.EMAIL_PASSWORD)

    me = Config.EMAIL
    you = Config.TARGET_EMAIL

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "CubeBot Weekly Review #" + week_no
    msg['From'] = me
    msg['To'] = you

    # Create the body of the message (a plain-text and an HTML version).
    text = "Hello World!"
    html = content

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)

    server.sendmail(me, you, msg.as_string())
    server.quit()

def review_weekly_progress(week_no):
    tasks = load_tasks_from_file("data/week"+week_no+".csv")
    parsed_review = parse_email(tasks)
    send_email(parsed_review, week_no)