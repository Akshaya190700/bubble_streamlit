import streamlit as st
from pymongo import MongoClient

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client['user_db']
users_collection = db['users']
posts_collection = db['posts']

# Function to verify credentials
def login_user(username, password):
    user = users_collection.find_one({"email": username})
    if user and user['password'] == password:  # Plain text password check (replace with hashing in production)
        return user
    return None

# Main Login Page
if "user" not in st.session_state:
    # Display the login form
    st.title("Login Page")
    username = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login_user(username, password)
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
    selected_tab = st.radio(
        "Navigation",
        options=["Profile", "Create Post", "My Post"],
        horizontal=True
    )

    # Define behavior for each tab
    if selected_tab == "Profile":
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
    elif selected_tab == "Create Post":
        # Create Post Tab
        st.subheader("Create Post")
        
        # Post creation form
        post_content = st.text_area("Enter your post (25-500 characters)", max_chars=500)
        
        if st.button("Submit"):
            if len(post_content) < 25:
                st.error("Post must be at least 25 characters long.")
            else:
                post_data = {
                    "user_id": user.get("_id"),
                    "name": user.get("name", "Anonymous"),
                    "content": post_content
                }
                posts_collection.insert_one(post_data)
                st.success("Post submitted successfully!")

    elif selected_tab == "My Post":
        # My Post Tab
        st.subheader("My Post")
        
        # Fetch and display posts by the user
        user_posts = list(posts_collection.find({"user_id": user.get("_id")}))
        
        if not user_posts:
            st.info("You have not created any posts yet.")
        else:
            for post in user_posts:
                st.write(f"*Post ID:* {post.get('_id')}")
                st.write(f"*Content:* {post.get('content')}")
                st.markdown("---")
