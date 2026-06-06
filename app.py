import streamlit as st
import pandas as pd
import time
import os
from gcr_agent import GCRAgent
from report_generator import ReportGenerator

# Disable unnecessary features for speed
st.set_option('client.showErrorDetails', False)
st.set_option('client.toolbarMode', 'minimal')

# Professional page config
st.set_page_config(
    page_title="Autonomous GCR Grading Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal CSS for speed
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #A23B72;
        margin: 0.5rem 0;
        font-weight: 600;
    }
    .connection-status {
        padding: 6px 12px;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.8rem;
        display: inline-block;
    }
    .connected {
        background-color: #D4EDDA;
        color: #155724;
        border: 1px solid #C3E6CB;
    }
    .disconnected {
        background-color: #F8D7DA;
        color: #721C24;
        border: 1px solid #F5C6CB;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<div class="main-header">Autonomous Google Classroom Grading Agent</div>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'grading_complete' not in st.session_state:
        st.session_state.grading_complete = False
    if 'results' not in st.session_state:
        st.session_state.results = []
    
    # Sidebar for navigation
    st.sidebar.title(" Navigation")
    page = st.sidebar.radio("Go to", [" Dashboard", " Grading Agent", " Reports & Analytics"])
    
    # Display connection status in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader(" Connection Status")
    
    is_connected = (
        st.session_state.agent is not None and 
        hasattr(st.session_state.agent, 'is_connected') and 
        st.session_state.agent.is_connected()
    )
    
    if is_connected:
        st.sidebar.markdown('<div class="connection-status connected"> Connected to GCR</div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<div class="connection-status disconnected"> Not Connected</div>', unsafe_allow_html=True)
    
    # Remove page icons for routing
    if "Dashboard" in page:
        show_dashboard()
    elif "Grading Agent" in page:
        show_grading_agent()
    elif "Reports & Analytics" in page:
        show_reports_analytics()

def show_dashboard():
    st.markdown('<div class="sub-header">Dashboard Overview</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**Autonomous**\n\nAgent automatically finds and grades all ungraded submissions")
    
    with col2:
        st.info("**Analytics**\n\nGenerates performance charts and Excel reports automatically")
    
    with col3:
        st.info("**GCR Integrated**\n\nDirect integration with Google Classroom API")
    
    st.markdown("---")
    st.markdown("""
    ### How it works:
    1. **Connect** with Google Classroom
    2. **Select** classes to grade
    3. **AI Agent** grades submissions automatically
    4. **View** results and analytics
    5. **Download** reports
    """)

def show_grading_agent():
    st.markdown('<div class="sub-header"> Autonomous Grading Agent</div>', unsafe_allow_html=True)
    
    # Check credentials file
    CREDENTIALS_PATH = "credentials/credentials.json"
    if not os.path.exists(CREDENTIALS_PATH):
        st.error(f" Credentials file not found at: {CREDENTIALS_PATH}")
        st.info("Please place your Google Classroom `credentials.json` file in the `credentials/` folder")
        return
    
    # SIMPLE CONNECTION FLOW
    if st.session_state.agent is None or not st.session_state.agent.is_connected():
        # Show connect button
        connect_btn = st.button(" Connect to Google Classroom", type="primary", use_container_width=True)
        
        if connect_btn:
            with st.spinner(" Connecting to Google Classroom..."):
                try:
                    # Clear any old agent
                    st.session_state.agent = None
                    st.session_state.grading_complete = False
                    st.session_state.results = []
                    
                    # Create and connect new agent
                    agent = GCRAgent()
                    if agent.connect():
                        st.session_state.agent = agent
                        st.success(" Successfully connected!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(" Failed to connect")
                except Exception as e:
                    st.error(f"Connection error: {str(e)[:100]}")
        
        # Show help if not connected
        st.info("Click 'Connect to Google Classroom' to get started")
        
        with st.expander("Need help with Google credentials?"):
            st.markdown("""
            ### Quick setup:
            1. Go to [Google Cloud Console](https://console.cloud.google.com)
            2. Create new project
            3. Enable "Google Classroom API"
            4. Create OAuth 2.0 Desktop credentials
            5. Download `credentials.json`
            6. Place in `credentials/` folder
            """)
        
        # STOP HERE if not connected
        return
    
    # --- ONLY REACH THIS POINT IF CONNECTED ---
    
    # Simple management buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button(" Switch Account", use_container_width=True):
            if st.session_state.agent.gcr_client.switch_account():
                st.session_state.agent = None
                st.rerun()
    with col2:
        if st.button(" Logout", use_container_width=True):
            if st.session_state.agent.gcr_client.logout():
                st.session_state.agent = None
                st.success("Logged out!")
                st.rerun()
    
    st.markdown("---")
    
    # Get available courses
    with st.spinner(" Loading courses..."):
        courses = st.session_state.agent.gcr_client.get_courses()
    
    if not courses:
        st.warning("No active courses found in your Google Classroom account.")
        return
    
    st.markdown("### Select Classes to Grade")
    
    course_options = {f"{course['name']}": course['id'] for course in courses}
    selected_courses = st.multiselect(
        "Choose classes:",
        options=list(course_options.keys()),
        placeholder="Select classes..."
    )
    
    if selected_courses:
        selected_course_ids = [course_options[course] for course in selected_courses]
        
        st.info(f"Selected {len(selected_courses)} class(es)")
        
        if st.button(" Start Autonomous Grading", type="primary", use_container_width=True):
            with st.spinner("AI Agent is working..."):
                try:
                    results = st.session_state.agent.run_autonomous_grading(selected_course_ids)
                    st.session_state.results = results
                    st.session_state.grading_complete = True
                    
                    st.success(" Grading completed!")
                    
                    # Show quick summary
                    if results:
                        df = pd.DataFrame(results)
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total", len(results))
                        with col2:
                            avg = df['score'].mean()
                            st.metric("Avg Score", f"{avg:.1f}")
                        with col3:
                            st.metric("Status", "Complete")
                except Exception as e:
                    st.error(f"Error: {str(e)[:100]}")

def show_reports_analytics():
    st.markdown('<div class="sub-header"> Reports & Analytics</div>', unsafe_allow_html=True)
    
    if not st.session_state.grading_complete:
        st.info("Please run the grading agent first to generate reports.")
        
        if st.button(" Load Sample Data for Demo"):
            sample_results = [
                {'course_name': 'Mathematics 101', 'student_name': 'John Doe', 'student_email': 'john@example.com', 
                 'assignment': 'Algebra Quiz 1', 'score': 8.5, 'max_score': 10, 'feedback': 'Excellent work!'},
                {'course_name': 'Mathematics 101', 'student_name': 'Jane Smith', 'student_email': 'jane@example.com', 
                 'assignment': 'Algebra Quiz 1', 'score': 7.0, 'max_score': 10, 'feedback': 'Good effort'},
                {'course_name': 'Mathematics 101', 'student_name': 'Alex Johnson', 'student_email': 'alex@example.com', 
                 'assignment': 'Algebra Quiz 1', 'score': 9.5, 'max_score': 10, 'feedback': 'Outstanding!'},
                {'course_name': 'Mathematics 101', 'student_name': 'Mike Brown', 'student_email': 'mike@example.com', 
                 'assignment': 'Algebra Quiz 1', 'score': 6.5, 'max_score': 10, 'feedback': 'Needs improvement'},
                {'course_name': 'Science 202', 'student_name': 'Sarah Williams', 'student_email': 'sarah@example.com', 
                 'assignment': 'Physics Lab Report', 'score': 9.0, 'max_score': 10, 'feedback': 'Excellent analysis'},
                {'course_name': 'Science 202', 'student_name': 'Tom Davis', 'student_email': 'tom@example.com', 
                 'assignment': 'Physics Lab Report', 'score': 8.0, 'max_score': 10, 'feedback': 'Well done'},
                {'course_name': 'Science 202', 'student_name': 'Lisa Miller', 'student_email': 'lisa@example.com', 
                 'assignment': 'Physics Lab Report', 'score': 7.5, 'max_score': 10, 'feedback': 'Good work'},
                {'course_name': 'English 301', 'student_name': 'Robert Wilson', 'student_email': 'robert@example.com', 
                 'assignment': 'Essay Writing', 'score': 9.0, 'max_score': 10, 'feedback': 'Excellent writing'},
                {'course_name': 'English 301', 'student_name': 'Emily Clark', 'student_email': 'emily@example.com', 
                 'assignment': 'Essay Writing', 'score': 8.5, 'max_score': 10, 'feedback': 'Very good'},
                {'course_name': 'English 301', 'student_name': 'David Lee', 'student_email': 'david@example.com', 
                 'assignment': 'Essay Writing', 'score': 7.0, 'max_score': 10, 'feedback': 'Satisfactory'},
            ]
            st.session_state.results = sample_results
            st.session_state.grading_complete = True
            st.rerun()
        return
    
    if st.session_state.results:
        # Create reporter
        reporter = ReportGenerator()
        results = st.session_state.results
        
        # Overall statistics
        st.markdown("###  Overall Statistics")
        
        df = pd.DataFrame(results)
        total_students = df['student_name'].nunique()
        total_courses = df['course_name'].nunique()
        total_assignments = df['assignment'].nunique()
        avg_score = df['score'].mean()
        avg_max = df['max_score'].mean()
        avg_percentage = (avg_score / avg_max * 100) if avg_max > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Courses", total_courses)
        with col2:
            st.metric("Total Students", total_students)
        with col3:
            st.metric("Total Assignments", total_assignments)
        with col4:
            st.metric("Overall Average", f"{avg_percentage:.1f}%")
        
        st.markdown("---")
        
        # Generate reports for each course
        courses_data = {}
        for result in results:
            course_name = result['course_name']
            if course_name not in courses_data:
                courses_data[course_name] = []
            courses_data[course_name].append(result)
        
        for course_name, course_results in courses_data.items():
            st.markdown(f"###  {course_name}")
            
            # Generate charts
            fig_pie, fig_hist = reporter.generate_performance_charts(course_results, course_name)
            fig_students = reporter.generate_student_analytics(course_results, course_name)
            fig_assignments = reporter.generate_assignment_analytics(course_results, course_name)
            
            # Display charts in columns
            col1, col2 = st.columns(2)
            with col1:
                if fig_pie:
                    st.plotly_chart(fig_pie, use_container_width=True)
            with col2:
                if fig_hist:
                    st.plotly_chart(fig_hist, use_container_width=True)
            
            col3, col4 = st.columns(2)
            with col3:
                if fig_students:
                    st.plotly_chart(fig_students, use_container_width=True)
            with col4:
                if fig_assignments:
                    st.plotly_chart(fig_assignments, use_container_width=True)
            
            # Display results table
            st.markdown("####  Detailed Results")
            df_display = pd.DataFrame(course_results)[['student_name', 'assignment', 'score', 'max_score', 'feedback']]
            st.dataframe(df_display, use_container_width=True)
            
            # Generate and download Excel report
            excel_file = reporter.generate_excel_report(course_results, course_name)
            with open(excel_file, "rb") as f:
                excel_data = f.read()
            
            st.download_button(
                label=f" Download Excel Report for {course_name}",
                data=excel_data,
                file_name=os.path.basename(excel_file),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"excel_{course_name}"
            )
            
            st.markdown("---")
        
        # Class comparison (if multiple courses)
        if len(courses_data) > 1:
            st.markdown("###  Class Comparison")
            fig_comparison, fig_box = reporter.generate_class_comparison(results)
            
            if fig_comparison:
                st.plotly_chart(fig_comparison, use_container_width=True)
            if fig_box:
                st.plotly_chart(fig_box, use_container_width=True)
        
        # Export options
        st.markdown("---")
        st.markdown("###  Export Data")
        
        col1, col2 = st.columns(2)
        with col1:
            # Export all data as CSV
            all_df = pd.DataFrame(results)
            csv = all_df.to_csv(index=False)
            st.download_button(
                label=" Download All Data (CSV)",
                data=csv,
                file_name="all_grading_results.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Clear results button
            if st.button(" Clear All Results", use_container_width=True):
                st.session_state.grading_complete = False
                st.session_state.results = []
                st.success("All results cleared!")
                st.rerun()
    else:
        st.warning("No results available. Please run grading first.")

if __name__ == "__main__":
    main()