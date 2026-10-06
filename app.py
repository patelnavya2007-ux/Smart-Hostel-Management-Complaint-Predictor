import streamlit as st
from database import SessionLocal, Student, Complaint, Room
import joblib
import pandas as pd


# =========================
# AI MODEL
# =========================

model = joblib.load("complaint_model.pkl")


# =========================
# PAGE SETTINGS
# =========================

st.set_page_config(
    page_title="Smart Hostel Management",
    page_icon="🏠",
    layout="wide"
)


# =========================
# SESSION STATE
# =========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "page" not in st.session_state:
    st.session_state.page = "Login"

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False


# =========================
# STUDENT LOGIN
# =========================

def login_page():

    st.title("🏠 Smart Hostel Management")
    st.subheader("🔐 Student Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        db = SessionLocal()

        student = db.query(Student).filter(
            Student.username == username,
            Student.password == password
        ).first()

        db.close()

        if student:

            st.session_state.logged_in = True
            st.session_state.username = student.username
            st.session_state.page = "Dashboard"

            st.rerun()

        else:

            st.error("Invalid username or password")

    st.divider()

    if st.button("New Student? Register Here"):

        st.session_state.page = "Register"
        st.rerun()

    if st.button("🔑 Admin Login"):

        st.session_state.page = "Admin Login"
        st.rerun()


# =========================
# REGISTRATION
# =========================

def registration_page():

    st.title("📝 Student Registration")

    name = st.text_input("Full Name")
    username = st.text_input("Create Username")
    password = st.text_input("Create Password", type="password")
    room_number = st.text_input("Room Number")

    if st.button("Register"):

        if not name or not username or not password or not room_number:

            st.warning("Please fill all the fields.")

        else:

            db = SessionLocal()

            existing = db.query(Student).filter(
                Student.username == username
            ).first()

            if existing:

                st.error("Username already exists.")
                db.close()

            else:

                room = db.query(Room).filter(
                    Room.room_number == room_number
                ).first()

                if not room:

                    st.error("Room number does not exist.")

                else:

                    room_taken = db.query(Student).filter(
                        Student.room_number == room_number
                    ).first()

                    if room_taken:

                        st.error("This room is already occupied.")

                    else:

                        student = Student(
                            name=name,
                            username=username,
                            password=password,
                            room_number=room_number
                        )

                        db.add(student)
                        db.commit()
                        db.close()

                        st.success(
                            "Registration successful! 🎉"
                        )

                        st.info(
                            "Go back to Login and login."
                        )

    if st.button("← Back to Login"):

        st.session_state.page = "Login"
        st.rerun()


# =========================
# STUDENT DASHBOARD
# =========================

def dashboard():

    st.title(
        "🏠 Smart Hostel Management & Complaint Predictor"
    )

    st.success(
        f"Welcome, {st.session_state.username}! 👋"
    )

    if st.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.page = "Login"

        st.rerun()

    st.divider()

    # =========================
    # ACTUAL DATABASE COUNTS
    # =========================

    db = SessionLocal()

    total_students = db.query(Student).count()

    total_rooms = db.query(Room).count()

    occupied_rooms = db.query(Student.room_number).filter(
        Student.room_number.isnot(None),
        Student.room_number != ""
    ).distinct().count()

    available_rooms = total_rooms - occupied_rooms

    pending_complaints = db.query(Complaint).filter(
        Complaint.status == "Pending"
    ).count()

    db.close()

    st.subheader("📊 Hostel Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Students",
            total_students
        )

    with col2:
        st.metric(
            "Total Rooms",
            total_rooms
        )

    with col3:
        st.metric(
            "Occupied Rooms",
            occupied_rooms
        )

    with col4:
        st.metric(
            "Available Rooms",
            available_rooms
        )

    st.metric(
        "Pending Complaints",
        pending_complaints
    )

    st.divider()

    # =========================
    # COMPLAINT
    # =========================

    st.subheader("📝 Register a Complaint")

    complaint_text = st.text_area(
        "Enter your hostel complaint",
        placeholder="Example: Water is not available in bathroom..."
    )

    if st.button("Submit Complaint"):

        if complaint_text.strip():

            predicted_category = model.predict(
                [complaint_text]
            )[0]

            db = SessionLocal()

            complaint = Complaint(
                username=st.session_state.username,
                complaint=complaint_text,
                category=predicted_category,
                priority="Medium",
                status="Pending"
            )

            db.add(complaint)
            db.commit()
            db.close()

            st.success(
                "Complaint submitted successfully! 🎉"
            )

            st.info(
                f"🤖 AI Predicted Category: {predicted_category}"
            )

        else:

            st.warning(
                "Please enter a complaint."
            )

    st.divider()

    # =========================
    # COMPLAINT HISTORY
    # =========================

    st.subheader("📋 My Complaint History")

    db = SessionLocal()

    complaints = db.query(Complaint).filter(
        Complaint.username == st.session_state.username
    ).all()

    db.close()

    for complaint in complaints:

        st.write(
            f"📝 **Complaint:** {complaint.complaint}"
        )

        st.write(
            f"🤖 **AI Category:** {complaint.category}"
        )

        st.write(
            f"⚡ **Priority:** {complaint.priority}"
        )

        st.write(
            f"📌 **Status:** {complaint.status}"
        )

        st.divider()


# =========================
# ADMIN LOGIN
# =========================

def admin_login():

    st.title("🔑 Admin Login")

    username = st.text_input("Admin Username")
    password = st.text_input(
        "Admin Password",
        type="password"
    )

    if st.button("Admin Login"):

        if username == "admin" and password == "admin123":

            st.session_state.admin_logged_in = True
            st.session_state.page = "Admin Dashboard"

            st.rerun()

        else:

            st.error(
                "Invalid admin username or password"
            )

    if st.button("← Back"):

        st.session_state.page = "Login"
        st.rerun()


# =========================
# ADMIN DASHBOARD
# =========================

def admin_dashboard():

    st.title("👨‍💼 Admin Dashboard")

    st.success("Welcome, Admin! 👋")

    if st.button("Admin Logout"):

        st.session_state.admin_logged_in = False
        st.session_state.page = "Login"

        st.rerun()

    db = SessionLocal()

    students = db.query(Student).all()
    complaints = db.query(Complaint).all()

    total_rooms = db.query(Room).count()

    occupied_rooms = db.query(Student.room_number).filter(
        Student.room_number.isnot(None),
        Student.room_number != ""
    ).distinct().count()

    available_rooms = total_rooms - occupied_rooms

    st.divider()

    # =========================
    # ROOM INFORMATION
    # =========================

    st.subheader("🏠 Room Management")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Rooms",
            total_rooms
        )

    with col2:
        st.metric(
            "Occupied Rooms",
            occupied_rooms
        )

    with col3:
        st.metric(
            "Available Rooms",
            available_rooms
        )

    st.divider()

    # =========================
    # STUDENTS
    # =========================

    st.subheader("👨‍🎓 Registered Students")

    st.write(
        f"Total Students: **{len(students)}**"
    )

    for student in students:

        st.write(
            f"👤 **{student.name}** | "
            f"Username: {student.username} | "
            f"Room: {student.room_number}"
        )

    st.divider()

    # =========================
    # COMPLAINTS
    # =========================

    st.subheader("📝 All Student Complaints")

    st.write(
        f"Total Complaints: **{len(complaints)}**"
    )

    for complaint in complaints:

        st.markdown("---")

        st.write(
            f"🆔 **Complaint ID:** {complaint.id}"
        )

        st.write(
            f"👤 **Student:** {complaint.username}"
        )

        st.write(
            f"📝 **Complaint:** {complaint.complaint}"
        )

        st.write(
            f"🤖 **AI Category:** {complaint.category}"
        )

        st.write(
            f"⚡ **Priority:** {complaint.priority}"
        )

        st.write(
            f"📌 **Current Status:** {complaint.status}"
        )

        new_status = st.selectbox(
            "Update Status",
            ["Pending", "Resolved"],
            index=(
                0 if complaint.status == "Pending"
                else 1
            ),
            key=f"status_{complaint.id}"
        )

        if st.button(
            "Update Status",
            key=f"update_{complaint.id}"
        ):

            complaint.status = new_status

            db.commit()

            st.success(
                "Status updated successfully! ✅"
            )

            st.rerun()

    st.divider()

    # =========================
    # REPORTS
    # =========================

    st.subheader("📊 Reports & Analytics")

    if complaints:

        data = []

        for complaint in complaints:

            data.append({
                "Category": complaint.category,
                "Priority": complaint.priority,
                "Status": complaint.status
            })

        df = pd.DataFrame(data)

        st.write("### 🤖 Complaints by Category")

        st.bar_chart(
            df["Category"].value_counts()
        )

        st.write("### 📌 Complaint Status")

        st.bar_chart(
            df["Status"].value_counts()
        )

        st.write("### ⚡ Complaint Priority")

        st.bar_chart(
            df["Priority"].value_counts()
        )

        st.write("### 📋 Report Summary")

        st.dataframe(
            df,
            use_container_width=True
        )

    else:

        st.info(
            "No complaints available for reports."
        )

    db.close()


# =========================
# MAIN PROGRAM
# =========================

if st.session_state.admin_logged_in:

    admin_dashboard()

elif st.session_state.logged_in:

    dashboard()

else:

    if st.session_state.page == "Login":

        login_page()

    elif st.session_state.page == "Register":

        registration_page()

    elif st.session_state.page == "Admin Login":

        admin_login()