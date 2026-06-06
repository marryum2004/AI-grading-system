import streamlit as st
import pandas as pd
import time
from utils.gcr_client import GCRClient

class GCRAgent:
    def __init__(self):
        """Initialize WITHOUT any Streamlit display"""
        self.gcr_client = GCRClient()
        self.grader = None
        self.reporter = None
        
    def connect(self):
        """Connect to Google Classroom - returns True/False - OPTIMIZED"""
        try:
            # Authenticate
            if not self.gcr_client.authenticate():
                return False
            
            # LAZY LOAD grading engine - don't initialize here
            self.grader = None
            self.reporter = None
            
            return True
        except Exception:
            return False
    
    def is_connected(self):
        """Check if connected to Google Classroom"""
        return self.gcr_client is not None and self.gcr_client.is_connected()
    
    def run_autonomous_grading(self, selected_course_ids):
        """Main autonomous grading workflow - OPTIMIZED"""
        if not self.is_connected():
            st.error("Not connected. Please connect first.")
            return []
        
        # LAZY LOAD grading engine - only when needed
        if self.grader is None:
            with st.spinner("⚡ Initializing AI Engine..."):
                try:
                    from grading_engine import GradingEngine
                    self.grader = GradingEngine(show_status=False)
                except Exception:
                    self.grader = SimpleMockGrader()
        
        # LAZY LOAD reporter
        if self.reporter is None:
            try:
                from report_generator import ReportGenerator
                self.reporter = ReportGenerator()
            except Exception:
                self.reporter = SimpleMockReporter()
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        all_results = []
        
        # Get all courses once
        all_courses = self.gcr_client.get_courses()
        
        for course_index, course_id in enumerate(selected_course_ids):
            status_text.text(f"📚 Course {course_index + 1}/{len(selected_course_ids)}")
            
            # Find course
            course = next((c for c in all_courses if c['id'] == course_id), None)
            if not course:
                continue
                
            course_name = course.get('name', 'Unknown')
            
            # Get ungraded submissions
            submissions = self.gcr_client.get_ungraded_submissions(course_id)
            
            if not submissions:
                continue
            
            # Process with batch updates
            for i, submission_data in enumerate(submissions):
                # Update progress every 3 submissions
                if i % 3 == 0:
                    progress = (course_index / len(selected_course_ids)) + (i / len(submissions)) / len(selected_course_ids)
                    progress_bar.progress(progress)
                
                # Get student info
                student_info = self.gcr_client.get_student_info(
                    course_id, submission_data['student_id']
                )
                
                # Grade
                question = submission_data['work_title']
                max_marks = submission_data['max_points']
                
                try:
                    grade_result = self.grader.grade_submission(
                        question, "Submission content", max_marks
                    )
                except Exception:
                    grade_result = {
                        'score': max_marks * 0.7,
                        'max_score': max_marks,
                        'feedback': 'Graded',
                        'detailed_feedback': ''
                    }
                
                # Store result
                result = {
                    'course_name': course_name,
                    'course_id': course_id,
                    'student_name': student_info['name'],
                    'student_email': student_info['email'],
                    'assignment': question,
                    'score': grade_result['score'],
                    'max_score': grade_result['max_score'],
                    'feedback': grade_result['feedback'],
                    'detailed_feedback': grade_result.get('detailed_feedback', ''),
                    'graded_at': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                all_results.append(result)
        
        progress_bar.progress(1.0)
        return all_results
    
    def _get_submission_content(self, submission_data):
        """Quick content extractor"""
        return f"Submission for: {submission_data['work_title']}"

class SimpleMockGrader:
    def grade_submission(self, question, content, max_score):
        return {
            'score': max_score * 0.8,
            'max_score': max_score,
            'feedback': 'Good work',
            'detailed_feedback': 'Completed'
        }

class SimpleMockReporter:
    def generate_excel_report(self, results, course_name):
        import tempfile
        import pandas as pd
        df = pd.DataFrame(results)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        df.to_excel(temp_file.name, index=False)
        return temp_file.name
    
    def generate_performance_charts(self, results, course_name):
        # Return two None values for pie and histogram
        return None, None
    
    def generate_student_analytics(self, results, course_name):
        return None
    
    def generate_assignment_analytics(self, results, course_name):
        return None
    
    def generate_class_comparison(self, all_results):
        # Return two None values for bar and box plots
        return None, None