import streamlit as st
from pymongo import MongoClient
from streamlit_option_menu import option_menu
from datetime import datetime

# MongoDB setup
CONNECTION_STRING = "mongodb+srv://freego:freego%2322Monkey@freego-c0.y47x2e3.mongodb.net/user_recommendation?retryWrites=true&w=majority"
client = MongoClient(CONNECTION_STRING)
db = client['bubble_database']
users_collection = db['bubble_users']
posts_collection = db['bubble_posts']

# Function to verify credentials
def login_user(email, password):
    user = users_collection.find_one({"email": email})
    if user and user['password'] == password:  # Plain text password check
        return user
    return None

# setting page layout
st.set_page_config(
    page_title="My Streamlit App",
    page_icon="🤖"
)

# Main Login Page
if "user" not in st.session_state:
    # Display the login form
    st.title("Login Page")
    email = st.text_input("📧 Email")
    password = st.text_input("🔒 Password", type="password")

    if st.button("Login"):
        user = login_user(email, password)
        if user:
            st.session_state["user"] = user  # Store user details in session state
            st.success("Login successful!")
            st.rerun()  # Reload the page to display the dashboard
        else:
            st.error("Invalid credentials. Please try again.")
else:
    # Fetch logged-in user details
    user = st.session_state["user"]

    # Dashboard with Navigation
    st.title("Dashboard")
    selected = option_menu(menu_title=None,options=["My Profile", "Create Post", "My Posts"], 
    icons=["People-Circle","hash","chat-square-quote-fill"], 
    menu_icon=None, default_index=0, orientation="horizontal")

    # Define behavior for each tab
    if selected == "My Profile":
        # Profile Tab
        st.subheader("Profile")
        st.write(f"*Name:* {user.get('name', 'N/A')}")
        st.write(f"*Email:* {user.get('email', 'N/A')}")
        st.write(f"*Role:* {user.get('role', 'N/A')}")

        # Address (Formatted)
        address = user.get('address', {})
        street = address.get('street', 'N/A')
        city = address.get('city', 'N/A')
        zip_code = address.get('zip', 'N/A')

        st.write("*Address:*")
        st.markdown(
            f"""
            <div style="margin-left: 20px;">
                <p><b>Street:</b> {street}</p>
                <p><b>City:</b> {city}</p>
                <p><b>ZIP:</b> {zip_code}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        # Logout Button
        if st.button("Logout"):
            st.session_state.clear()  # Clear session state
            # st.success("You have been logged out. Please refresh the page.")
            st.rerun()
    elif selected == "Create Post":
        # Create Post Tab
        st.subheader("Create Post")
        
        # Post creation form
        post_content = st.text_area("Enter your post (25-400 characters)", max_chars=400)
        
        if st.button("Submit"):
            if len(post_content) < 25:
                st.error("Post must be at least 25 characters long.")
            else:
                post_data = {
                    "user_id": user.get("_id"),
                    "name": user.get("name"),
                    "content": post_content,
                    "created_at": datetime.now()
                }
                posts_collection.insert_one(post_data)
                st.success("Post submitted successfully!")

    elif selected == "My Posts":
        # My Post Tab
        st.subheader("My Posts")
        
        # Fetch and display posts by the user
        user_posts = list(posts_collection.find({"user_id": user.get("_id")}))
        user_posts.sort(key=lambda post: post.get('created_at'), reverse=True)
        
        if not user_posts:
            st.info("You have not created any posts yet.")
        else:
            for post in user_posts:
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"*Post ID:* {post.get('_id')}")
                with col2:
                    st.write(f"*Posted On:* {post.get('created_at').strftime('%d-%m-%Y %H:%M:%S')}")

                st.write(f"*Post:*  \n{post.get('content')}")
                st.markdown("---")