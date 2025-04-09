import streamlit as st
from pymongo import MongoClient
from streamlit_option_menu import option_menu
from datetime import datetime

# MongoDB setup
# ConnectionString = "mongodb+srv://freego:freego%2322Monkey@freego-c0.y47x2e3.mongodb.net/user_recommendation?retryWrites=true&w=majority&serverSelectionTimeoutMS=30000&tls=true&tlsAllowInvalidCertificates=true"
# client = MongoClient(ConnectionString)
# # Define database and collection
client = MongoClient("mongodb://localhost:27017/")
db = client["bubble_db"]
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
    selected = option_menu(menu_title=None,options=["My Profile", "Create Post", "My Posts","Notifications"], 
    icons=["People-Circle","hash","chat-square-quote-fill","bell-fill"], 
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
        country = address.get('country', 'N/A')

        st.write("*Address:*")
        st.markdown(
            f"""
            <div style="margin-left: 20px;">
                <p><b>Street:</b> {street}</p>
                <p><b>City:</b> {city}</p>
                <p><b>ZIP:</b> {zip_code}</p>
                <p><b>Country:</b> {country}</p>
            </div>
             """,
             unsafe_allow_html=True
    )

    # Occupation Details
        st.write(f"*Occupation:* {user.get('occupation', 'N/A')}")
        st.write(f"*Job Specialization:* {user.get('job_specialization', 'N/A')}")
        st.write(f"*Domain:* {user.get('domain', 'N/A')}")
        st.write(f"*Company:* {user.get('company', 'N/A')}")
        st.write(f"*Years of Experience:* {user.get('years_of_experience', 'N/A')}")

    # Skills
        skills = user.get('skills', {})
        technical_skills = skills.get('technical_skills', {})
        soft_skills = skills.get('soft_skills', {})
        certifications = skills.get('certifications_and_training', {}).get('certifications', [])

        st.write("*Skills:*")
        st.markdown(
            f"""
            <div style="margin-left: 20px;">
                <p><b>Technical Skills:</b> {', '.join(technical_skills.get('project_management_tools', []))}</p>
                <p><b>Methodologies:</b> {', '.join(technical_skills.get('methodologies', []))}</p>
                <p><b>Soft Skills:</b> Leadership: {soft_skills.get('leadership', 'N/A')}, Communication: {soft_skills.get('communication', 'N/A')}</p>
                <p><b>Certifications:</b> {', '.join(certifications)}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Education
        education = user.get('education', {})
        st.write("*Education:*")
        st.markdown(
            f"""
            <div style="margin-left: 20px;">
                <p><b>Degree:</b> {education.get('degree', 'N/A')}</p>
                <p><b>Institution:</b> {education.get('institution', 'N/A')}</p>
                <p><b>Field of Study:</b> {education.get('field_of_study', 'N/A')}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Interests and Hobbies
        st.write("*Interests:*")
        interests = user.get('interests', {})
        st.markdown(
            f"""
            <div style="margin-left: 20px;">
                <p><b>Professional:</b> {', '.join(interests.get('professional', []))}</p>
                <p><b>Personal:</b> {', '.join(interests.get('personal', []))}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("*Hobbies:*")
        st.write(", ".join(user.get('hobbies', [])))

        # Profile Bio
        st.write("*Profile Bio:*")
        st.write(user.get('profile_bio', 'N/A'))

        # Language Proficiency
        language_proficiency = user.get('language_proficiency', {})
        st.write("*Language Proficiency:*")
        st.markdown(
            f"""
            <div style="margin-left: 20px;">
                <p><b>Spoken:</b> {', '.join(language_proficiency.get('spoken', []))}</p>
                <p><b>Read:</b> {', '.join(language_proficiency.get('read', []))}</p>
                <p><b>Understood:</b> {', '.join(language_proficiency.get('understood', []))}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Extended Details
        extended_details = user.get('extended_details', {})
        st.write("*Extended Details:*")
        st.markdown(
            f"""
            <div style="margin-left: 20px;">
                <p><b>Availability for Opportunities:</b> {extended_details.get('availability_for_opportunities', 'N/A')}</p>
                <p><b>Professional Goals:</b> {extended_details.get('professional_goals', 'N/A')}</p>
                <p><b>Groups/Communities:</b> {', '.join(extended_details.get('groups_communities', []))}</p>
                <p><b>Events Attended:</b> {', '.join(extended_details.get('events_attended', []))}</p>
                <p><b>Events Interested In:</b> {', '.join(extended_details.get('events_interested_in', []))}</p>
                <p><b>Volunteer Interests:</b> {extended_details.get('volunteer_interests', 'N/A')}</p>
                <p><b>Social Causes:</b> {', '.join(extended_details.get('social_causes', []))}</p>
                <p><b>Preferred Content Types:</b> {', '.join(extended_details.get('preferred_content_types', []))}</p>
                <p><b>Topics of Interest:</b> {', '.join(extended_details.get('topics_of_interest', []))}</p>
                <p><b>Skills to Learn:</b> {', '.join(extended_details.get('skills_to_learn', []))}</p>
                <p><b>Courses/Training:</b> {', '.join(extended_details.get('courses_training', []))}</p>
                <p><b>Cultural Background:</b> {extended_details.get('cultural_background', 'N/A')}</p>
                <p><b>Bucket List Items:</b> {', '.join(extended_details.get('bucket_list_items', []))}</p>
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
        post_content = st.text_area("Enter your post")
        
        if st.button("Submit"):
            if len(post_content) < 25:
                st.error("Post must be at least 25 characters long.")
            else:
                # Get the count of documents in the collection
                post_count = posts_collection.count_documents({}) + 1
                post_data = {
                    "post_number": post_count,
                    "user_id": user.get("_id"),
                    "name": user.get("name"),
                    "content": post_content,
                    "created_at": datetime.now(),
                    "process flag": False,  # Initial flag for processed_text
                    "embedded flag": False  # Initial flag for embedded_text
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
                # Setting font color to orange and italic style
                    st.markdown(
                        f"<div style='color: orange; font-style: italic;'>Post ID: {post.get('_id')}</div>",
                        unsafe_allow_html=True
                    )
                with col2:
                    # Setting font color to orange, italic style, and aligning text to the right
                    st.markdown(
                        f"<div style='color: orange; text-align: right; font-style: italic;'>Posted On: {post.get('created_at').strftime('%d-%m-%Y %H:%M:%S')}</div>",
                        unsafe_allow_html=True
                    )
                st.write(f"\n{post.get('content')}")
                st.markdown("---")


    elif selected == "Notifications":
        # Notifications Tab
        st.subheader("Notifications Section")
        st.write("Here you can see your notifications.")