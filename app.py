import streamlit as st
from supabase import create_client, Client
from datetime import date

# --- Database Connection ---
# In production, these URLs and Keys are stored in Streamlit's secure "Secrets" manager
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- App Configuration & Styling ---
st.set_page_config(page_title="Daily Admission Data Entry", layout="centered")
st.title("🏛️ Daily College Admission Portal")
st.markdown("Submit daily admission figures for Aided and Self-Financing courses.")

# --- Data Entry Form ---
with st.form("admission_form", clear_on_submit=True):
    
    st.subheader("Institution Details")
    col1, col2 = st.columns(2)
    with col1:
        entry_date = st.date_input("Date of Entry", date.today())
        rjd_region = st.selectbox("RJD Region", ["Chennai", "Coimbatore", "Madurai", "Trichy", "Tirunelveli"]) # Add all regions
    with col2:
        tndce_college_id = st.text_input("TNDCE College ID")
        college_name = st.text_input("Full Name of the College")

    st.subheader("Course Details")
    scheme_type = st.radio("Scheme Type", ["Aided", "Self-Financing"], horizontal=True)
    course_name = st.text_input("Course Name (e.g., B.Sc. Mathematics)")
    
    col3, col4 = st.columns(2)
    with col3:
        sanctioned_seats = st.number_input("Sanctioned Seats", min_value=0, step=1)
    with col4:
        admitted_students = st.number_input("Admitted Students", min_value=0, step=1)

    # Submit button
    submitted = st.form_submit_button("Submit Daily Record")

    if submitted:
        # 1. Automated Validations & Calculations
        if admitted_students > sanctioned_seats:
            st.error("Error: Admitted students cannot exceed Sanctioned seats.")
        elif not tndce_college_id or not course_name:
            st.warning("Please fill in the College ID and Course Name.")
        else:
            vacant_seats = sanctioned_seats - admitted_students
            admission_percentage = round((admitted_students / sanctioned_seats) * 100, 2) if sanctioned_seats > 0 else 0.0

            # 2. Package the data for the SQL Database
            data_payload = {
                "entry_date": str(entry_date),
                "tndce_college_id": tndce_college_id,
                "rjd_region": rjd_region,
                "college_name": college_name,
                "scheme_type": scheme_type,
                "course_name": course_name,
                "sanctioned_seats": sanctioned_seats,
                "admitted_students": admitted_students,
                "vacant_seats": vacant_seats,
                "admission_percentage": admission_percentage
            }

            # 3. Write to Supabase
            try:
                data, count = supabase.table("daily_admissions").insert(data_payload).execute()
                st.success(f"✅ Successfully submitted {course_name} for {college_name}!")
                st.info(f"Calculated Vacancy: {vacant_seats} | Fill Rate: {admission_percentage}%")
            except Exception as e:
                st.error(f"Database Error: {e}")