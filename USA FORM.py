import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image

# Initialize an empty DataFrame to store the data
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

    # Create a new DataFrame for the new data
    new_row = pd.DataFrame([new_data])

    # Concatenate the new row to the existing DataFrame
    data = pd.concat([data, new_row], ignore_index=True)

    # Return the updated dataframe after submission
    return data

# Function to refresh the data (to show all submissions)
def refresh_data():
    return data

# Function to check the latest uploaded image
def check_hold():
    return image_storage["image"]

# Initialize the image storage as a dictionary
image_storage = {"image": None}

# Streamlit interface
st.title("USA Collab")

# Tabs
tab = st.radio("Choose a Section", ["Request", "HOLD"])

# Request Tab
if tab == "Request":
    st.header("Request Section")
    
    # Create input fields for Agent Name, Type, ID, Comment
    agent_name_input = st.text_input("Agent Name")
    type_input = st.selectbox("Type", ["Email", "Phone Number", "Ticket ID"])
    id_input = st.text_input("ID")
    comment_input = st.text_area("Comment")
    
    # Create buttons for submit and refresh
    if st.button("Submit Data"):
        data = submit_data(agent_name_input, type_input, id_input, comment_input)
        st.write("Data Submitted!")
    
    if st.button("Refresh Data"):
        st.write("Data Table:")
        st.write(refresh_data())

# HOLD Tab
if tab == "HOLD":
    st.header("HOLD Section")

    # Inputs for image upload
    uploaded_image = st.file_uploader("Upload Image (HOLD Section)", type=["jpg", "jpeg", "png"])

    if uploaded_image:
        image_storage["image"] = Image.open(uploaded_image)
        st.image(image_storage["image"], caption="Uploaded Image", use_column_width=True)

    if st.button("CHECK HOLD"):
        if image_storage["image"] is not None:
            st.image(image_storage["image"], caption="Latest Uploaded Image", use_column_width=True)
        else:
            st.write("No image uploaded.")
