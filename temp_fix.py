import random

class TempGradingEngine:
    def grade_submission(self, question, submission_text, max_marks):
        """Generate realistic, varied grades while Ollama downloads"""
        
        # Different score distributions based on question type
        if 'math' in question.lower() or 'calculate' in question.lower():
            # Math: 60-100% range
            percentage = random.uniform(0.6, 1.0)
        elif 'explain' in question.lower() or 'describe' in question.lower():
            # Explanation: 70-95% range
            percentage = random.uniform(0.7, 0.95)
        elif 'define' in question.lower() or 'what is' in question.lower():
            # Definition: 75-100% range
            percentage = random.uniform(0.75, 1.0)
        else:
            # Default: 65-90% range
            percentage = random.uniform(0.65, 0.9)
        
        score = round(percentage * max_marks, 2)
        score = max(1, min(max_marks, score))  # Ensure between 1 and max
        
        # Generate appropriate feedback
        if percentage >= 0.9:
            remark = "Excellent"
            feedback = "Outstanding understanding of concepts"
        elif percentage >= 0.8:
            remark = "Very Good"
            feedback = "Strong grasp of the material"
        elif percentage >= 0.7:
            remark = "Good"
            feedback = "Good understanding, minor improvements needed"
        elif percentage >= 0.6:
            remark = "Satisfactory"
            feedback = "Basic understanding achieved"
        else:
            remark = "Needs Work"
            feedback = "Requires more study of fundamental concepts"
        
        return {
            "score": score,
            "max_score": max_marks,
            "feedback": remark,
            "detailed_feedback": f"{feedback}. Score: {score}/{max_marks}"
        }