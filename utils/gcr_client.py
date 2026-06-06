import os
import pickle
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import time

class GCRClient:
    def __init__(self):
        self.SCOPES = [
            'https://www.googleapis.com/auth/classroom.courses.readonly',
            'https://www.googleapis.com/auth/classroom.coursework.me',
            'https://www.googleapis.com/auth/classroom.coursework.students',
            'https://www.googleapis.com/auth/classroom.student-submissions.students.readonly',
            'https://www.googleapis.com/auth/classroom.rosters.readonly'
        ]
        self.service = None
        self.credentials = None
        self.token_path = 'token.pickle'
        self.credentials_path = 'credentials/credentials.json'
        
        # Cache for performance
        self._courses_cache = None
        self._cache_time = 0
        self._cache_duration = 300  # 5 minutes

    def authenticate(self):
        """FAST authentication with Google Classroom API"""
        start = time.time()
        
        creds = None
        
        # Check if token exists
        if os.path.exists(self.token_path):
            try:
                with open(self.token_path, 'rb') as token:
                    creds = pickle.load(token)
                
                # Use valid token immediately
                if creds and creds.valid:
                    self.credentials = creds
                    self.service = build('classroom', 'v1', credentials=creds, cache_discovery=False)
                    return True
                
                # Refresh if expired
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        with open(self.token_path, 'wb') as token:
                            pickle.dump(creds, token)
                    except Exception:
                        os.remove(self.token_path)
                        creds = None
                        
            except Exception:
                if os.path.exists(self.token_path):
                    os.remove(self.token_path)
                creds = None
        
        # Fresh authentication if needed
        if not creds or not creds.valid:
            if not os.path.exists(self.credentials_path):
                return False
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, 
                    self.SCOPES,
                    redirect_uri='urn:ietf:wg:oauth:2.0:oob'
                )
                creds = flow.run_local_server(port=0, open_browser=True)
                
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)
                    
            except Exception:
                return False
        
        self.credentials = creds
        self.service = build('classroom', 'v1', credentials=creds, cache_discovery=False)
        return True
    
    def logout(self):
        """Logout from current Google account"""
        try:
            if os.path.exists(self.token_path):
                os.remove(self.token_path)
            self.service = None
            self.credentials = None
            self._courses_cache = None
            return True
        except Exception:
            return False
    
    def switch_account(self):
        """Switch to a different Google account"""
        return self.logout()

    def is_connected(self):
        """Check if currently connected"""
        return self.service is not None and self.credentials is not None

    def get_courses(self):
        """Get all courses - WITH CACHE"""
        current_time = time.time()
        
        # Return cache if valid
        if (self._courses_cache is not None and 
            (current_time - self._cache_time) < self._cache_duration):
            return self._courses_cache
            
        if not self.is_connected():
            return []
            
        try:
            courses = []
            page_token = None
            
            while True:
                response = self.service.courses().list(
                    pageToken=page_token,
                    pageSize=50
                ).execute()
                
                courses.extend(response.get('courses', []))
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
            
            # Cache active courses
            active_courses = [c for c in courses if c.get('courseState') == 'ACTIVE']
            self._courses_cache = active_courses
            self._cache_time = current_time
            
            return active_courses
        except Exception:
            return []

    def get_ungraded_submissions(self, course_id):
        """Get all ungraded submissions for a course"""
        try:
            submissions_data = []
            coursework = self.get_coursework(course_id)
            
            for work in coursework:
                if work.get('state') == 'PUBLISHED':
                    submissions = self.get_submissions(course_id, work['id'])
                    
                    for submission in submissions:
                        if submission.get('state') == 'TURNED_IN' and submission.get('assignedGrade') is None:
                            submissions_data.append({
                                'course_id': course_id,
                                'coursework_id': work['id'],
                                'submission_id': submission['id'],
                                'student_id': submission['userId'],
                                'work_title': work['title'],
                                'max_points': work.get('maxPoints', 100),
                                'submission': submission
                            })
            
            return submissions_data
        except Exception:
            return []

    def get_coursework(self, course_id):
        """Get coursework for a course"""
        try:
            coursework = []
            page_token = None
            
            while True:
                response = self.service.courses().courseWork().list(
                    courseId=course_id,
                    pageToken=page_token,
                    pageSize=30
                ).execute()
                
                coursework.extend(response.get('courseWork', []))
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
            
            return coursework
        except Exception:
            return []

    def get_submissions(self, course_id, coursework_id):
        """Get submissions for specific coursework"""
        try:
            submissions = []
            page_token = None
            
            while True:
                response = self.service.courses().courseWork().studentSubmissions().list(
                    courseId=course_id,
                    courseWorkId=coursework_id,
                    pageToken=page_token,
                    pageSize=30
                ).execute()
                
                submissions.extend(response.get('studentSubmissions', []))
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
            
            return submissions
        except Exception:
            return []

    def get_student_info(self, course_id, student_id):
        """Get student information"""
        try:
            student = self.service.courses().students().get(
                courseId=course_id,
                userId=student_id
            ).execute()
            
            profile = student.get('profile', {})
            return {
                'name': profile.get('name', {}).get('fullName', f'Student_{student_id}'),
                'email': profile.get('emailAddress', 'Unknown')
            }
        except Exception:
            return {
                'name': f'Student_{student_id}',
                'email': 'Unknown'
            }

    def post_grade(self, course_id, coursework_id, submission_id, grade, feedback):
        """Post grade and feedback to Google Classroom"""
        try:
            submission = {
                'assignedGrade': grade,
                'draftGrade': grade
            }
            
            self.service.courses().courseWork().studentSubmissions().patch(
                courseId=course_id,
                courseWorkId=coursework_id,
                id=submission_id,
                updateMask='assignedGrade,draftGrade',
                body=submission
            ).execute()
            
            return True
        except Exception:
            return False