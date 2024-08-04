import streamlit as st
import requests as r
import json

# Function to validate token
def validate_token(TOK):
    head = {
        "Authorization": f"Bearer {TOK}",
        "Referer": "https://tesseractonline.com/"
    }
    response = r.get(url="https://api.tesseractonline.com/studentmaster/subjects/4/6", headers=head)
    if response.status_code == 200:
        l = json.loads(response.text)
        if not l['Error']:
            return True, head
    return False, None

# Function to get quiz
def get_quiz(i, head):
    url = f"https://api.tesseractonline.com/quizattempts/create-quiz/{i}"
    res = r.get(url=url, headers=head).text
    return json.loads(res)

# Function to save quiz answer
def save_quiz(Zid, Qid, Opt, head):
    url = "https://api.tesseractonline.com/quizquestionattempts/save-user-quiz-answer"
    payload = {
        "quizId": f'{Zid}',
        "questionId": f'{Qid}',
        "userAnswer": f'{Opt}'
    }
    save = r.post(url=url, json=payload, headers=head).text
    return save

# Function to submit quiz
def submit_quiz(a, head):
    url = "https://api.tesseractonline.com/quizattempts/submit-quiz"
    payload = {
        "branchCode": "CSM",
        "sectionName": "CSM-PS1",
        "quizId": f'{a}'
    }
    submit = r.post(url=url, json=payload, headers=head).text
    submit = json.loads(submit)
    return submit

# Function to complete a quiz
def write_quiz(i, head):
    try:
        rc = get_quiz(i, head)
        quizId = rc["payload"]['quizId']
        questions = rc["payload"]["questions"]
        opt = ['a', 'b', 'c', 'd']
        prev = submit_quiz(quizId, head)["payload"]["score"]
        st.write("Work in progress. Please wait...")
        for i in range(5):
            for j in opt:
                save_quiz(quizId, rc["payload"]["questions"][i]['questionId'], j, head)
                scr = submit_quiz(quizId, head)["payload"]["score"]
                if scr == 5:
                    st.write('Test completed. Refresh the page.')
                    return
                if scr > prev:
                    prev = scr
                    break
    except KeyError:
        st.write('This subject or topic is inactive')

# Function to fetch dashboard data
def fetch_dashboard(head):
    url = "https://api.tesseractonline.com/studentmaster/subjects/4/6"
    response = r.get(url=url, headers=head).text
    l = json.loads(response)
    return {i['subject_id']: i['subject_name'] for i in l['payload']}

# Function to fetch units
def fetch_units(subject_id, head):
    url = f"https://api.tesseractonline.com/studentmaster/get-subject-units/{subject_id}"
    response = r.get(url=url, headers=head).text
    l = json.loads(response)
    return {i['unitId']: i['unitName'] for i in l['payload']}

# Function to fetch topics
def fetch_topics(unit_id, head):
    url = f"https://api.tesseractonline.com/studentmaster/get-topics-unit/{unit_id}"
    response = r.get(url=url, headers=head).text
    l = json.loads(response)
    topics = l['payload']['topics']
    return {f"{i['id']}. {i['name']}  {i['learningFlag']}": {'pdf': f"https://api.tesseractonline.com{i['pdf']}", 'video': i['videourl']} for i in topics}

# Streamlit app
st.title("Quiz Automation App")

# Token input
TOK = st.text_input("Enter token:", type="password")
if TOK:
    valid, head = validate_token(TOK)
    if valid:
        st.success("Token validated successfully.")
        # Fetch and display subjects
        subjects = fetch_dashboard(head)
        selected_subject = st.selectbox("Select a subject:", options=list(subjects.keys()), format_func=lambda x: subjects[x])

        # Fetch and display units
        if selected_subject:
            units = fetch_units(selected_subject, head)
            selected_unit = st.selectbox("Select a unit:", options=list(units.keys()), format_func=lambda x: units[x])

            # Fetch and display topics
            if selected_unit:
                topics = fetch_topics(selected_unit, head)
                selected_topic = st.multiselect("Select topics:", options=list(topics.keys()))

                # Write quiz for selected topics
                if st.button("Start Quiz"):
                    for topic_key in selected_topic:
                        topic_id = topic_key.split('.')[0]
                        write_quiz(topic_id, head)
    else:
        st.error("The given token is expired or may be incorrect.")
