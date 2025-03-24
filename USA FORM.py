import streamlit as st
import pandas as pd
from datetime import datetime

# Initialize an empty DataFrame to store the data (for the session)
columns = ["Agent Name", "TYPE", "ID", "COMMENT", "Timestamp"]
data = pd.DataFrame(columns=columns)

# Function to submit data
def submit_data(agent_name, type_, id_, comment):
    global data
    
    # Add the new data with timestamp
    new_data = {
        "Agent Name": agent_name,
        "TYPE": type_,
        "ID": id_,
        "COMMENT": comment,
        "Timestamp": datetime.now().strftime("%H:%M:%S")  # Only time (hour:minute:second)
    }

    # Add to local DataFrame for display
    new_row = pd.DataFrame([new_data])
    data = pd.concat([data, new_row], ignore_index=True)

    return data

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

    # Output Dataframe
    if submit_button:
        data = submit_data(agent_name_input, type_input, id_input, comment_input)
        st.dataframe(data)

    if refresh_button:
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
