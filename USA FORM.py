import streamlit as st
import pandas as pd
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK with your credentials
cred = credentials.Certificate("path_to_your_firebase_credential.json")  # Path to your Firebase Admin SDK JSON file
firebase_admin.initialize_app(cred)

# Firestore Database instance
db = firestore.client()

# Reference to the Firestore collection where data will be stored
collection_ref = db.collection("collab_form_data")

# Function to fetch data from Firestore
def fetch_data_from_firestore():
    docs = collection_ref.stream()
    data = []
    for doc in docs:
        data.append(doc.to_dict())
    return pd.DataFrame(data)

# Function to submit data to Firestore
def submit_data_to_firestore(agent_name, type_, id_, comment):
    new_data = {
        "Agent Name": agent_name,
        "TYPE": type_,
        "ID": id_,
        "COMMENT": comment,
        "Timestamp": datetime.now().strftime("%H:%M:%S")  # Only time (hour:minute:second)
    }
    collection_ref.add(new_data)

# Streamlit UI
st.title("USA Collab Form")

# Tabs
tab = st.sidebar.radio("Select Tab", ["Request", "HOLD"])

if tab == "Request":
    st.header("Request Section")

    # Input fields for Agent Name, Type, ID, Comment
    agent_name_input = st.text_input("Agent Name", placeholder="Enter Agent Name")
    type_input = st.selectbox("Type", ["Email", "Phone Number", "Ticket ID"])
    id_input = st.text_input("ID", placeholder="Enter ID")
    comment_input = st.text_area("Comment", placeholder="Enter Comment")

    # Buttons
    submit_button = st.button("Submit Data")
    refresh_button = st.button("Refresh Data")

    # Submit data to Firestore
    if submit_button:
        submit_data_to_firestore(agent_name_input, type_input, id_input, comment_input)
        st.success("Data submitted successfully!")

    # Refresh and fetch the latest data from Firestore
    if refresh_button:
        data = fetch_data_from_firestore()
        st.dataframe(data)

elif tab == "HOLD":
    st.header("HOLD Section")

    # Image upload
    image_input = st.file_uploader("Upload Image (HOLD Section)", type=["png", "jpg", "jpeg"])

    if image_input:
        st.image(image_input, caption="Uploaded Image")

    # Check hold button
    if st.button("Check Latest Image"):
        st.write("No image uploaded yet.")
