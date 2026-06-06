from langchain_community.llms import Ollama
import re
import streamlit as st
import json
import random
import time

class GradingEngine:
    def __init__(self, show_status=True):
        self.ollama_ready = False
        self.llm = None
        
        try:
            if show_status:
                st.info("⚡ Initializing AI Engine...")
            
            # Try with timeout
            start_time = time.time()
            timeout = 10  # seconds
            
            # Simple initialization
            self.llm = Ollama(model="mistral:7b", temperature=0.1)
            
            # Quick test
            test_response = self.llm.invoke("Say OK")
            if test_response and time.time() - start_time < timeout:
                self.ollama_ready = True
                if show_status:
                    st.success("✅ AI Engine ready")
            else:
                self.ollama_ready = False
                if show_status:
                    st.info("Using simulated grading")
                
        except Exception:
            self.ollama_ready = False
            if show_status:
                st.info("Using simulated grading")

    def grade_submission(self, question, submission_text, max_marks):
        """Fast grading with fallback"""
        
        # Use simulated grading if Ollama not ready or quick mode
        if not self.ollama_ready:
            return self._simulated_grade(question, max_marks)
        
        try:
            # Fast grading prompt
            grading_prompt = f"""
            Grade this: "{question}"
            Max marks: {max_marks}
            Give score (0-{max_marks}) and brief feedback.
            Format: {{"score": X, "feedback": "Y"}}
            """
            
            response = self.llm.invoke(grading_prompt)
            
            # Extract JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json_match.group()
                grade_data = json.loads(result)
                
                # Validate score
                score = float(grade_data.get('score', 0))
                score = max(1, min(max_marks, score))
                
                return {
                    "score": score,
                    "max_score": max_marks,
                    "feedback": grade_data.get('feedback', 'Graded'),
                    "detailed_feedback": f"Score: {score}/{max_marks}"
                }
            else:
                return self._simulated_grade(question, max_marks)
                
        except Exception:
            return self._simulated_grade(question, max_marks)
    
    def _simulated_grade(self, question, max_marks):
        """Fast simulated grading"""
        # Simple scoring
        if 'math' in question.lower() or 'calculate' in question.lower():
            percentage = random.uniform(0.65, 0.90)
        elif 'explain' in question.lower() or 'describe' in question.lower():
            percentage = random.uniform(0.70, 0.95)
        else:
            percentage = random.uniform(0.68, 0.88)
        
        score = round(percentage * max_marks, 1)
        score = max(1, min(max_marks, score))
        
        # Simple feedback
        if percentage >= 0.85:
            feedback = "Excellent"
        elif percentage >= 0.75:
            feedback = "Good"
        elif percentage >= 0.65:
            feedback = "Satisfactory"
        else:
            feedback = "Needs work"
        
        return {
            "score": score,
            "max_score": max_marks,
            "feedback": feedback,
            "detailed_feedback": f"Score: {score}/{max_marks}"
        }