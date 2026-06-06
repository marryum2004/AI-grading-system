import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        self.output_dir = "outputs"
        os.makedirs(f"{self.output_dir}", exist_ok=True)
    
    def generate_excel_report(self, results, course_name):
        """Generate Excel report with multiple sheets"""
        df = pd.DataFrame(results)
        
        # Clean filename
        clean_name = "".join(c for c in course_name if c.isalnum() or c in (' ', '_')).rstrip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"{self.output_dir}/{clean_name}_{timestamp}.xlsx"
        
        # Create Excel writer
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Sheet 1: All Results
            df.to_excel(writer, sheet_name='All Grades', index=False)
            
            # Sheet 2: Student Summary
            student_summary = df.groupby(['student_name', 'student_email']).agg({
                'score': 'sum',
                'max_score': 'sum',
                'assignment': 'count'
            }).reset_index()
            student_summary['average'] = (student_summary['score'] / student_summary['max_score']) * 100
            student_summary = student_summary.rename(columns={'assignment': 'assignments_count'})
            student_summary.to_excel(writer, sheet_name='Student Summary', index=False)
            
            # Sheet 3: Assignment Summary
            assignment_summary = df.groupby('assignment').agg({
                'score': ['mean', 'max', 'min', 'count'],
                'student_name': 'count'
            }).reset_index()
            assignment_summary.columns = ['assignment', 'avg_score', 'max_score', 'min_score', 'total_score', 'students_count']
            assignment_summary['avg_percentage'] = (assignment_summary['avg_score'] / df['max_score'].mean()) * 100
            assignment_summary.to_excel(writer, sheet_name='Assignment Summary', index=False)
        
        return filename
    
    def generate_performance_charts(self, results, course_name):
        """Generate multiple performance charts including pie chart"""
        if not results:
            return None, None
        
        df = pd.DataFrame(results)
        df['percentage'] = (df['score'] / df['max_score']) * 100
        
        # 1. PIE CHART - Performance Distribution
        # Create grade categories
        bins = [0, 50, 60, 70, 80, 90, 100]
        labels = ['F (<50%)', 'D (50-60%)', 'C (60-70%)', 'B (70-80%)', 'A (80-90%)', 'A+ (90-100%)']
        
        df['grade_category'] = pd.cut(df['percentage'], bins=bins, labels=labels, right=False)
        grade_counts = df['grade_category'].value_counts().reindex(labels, fill_value=0)
        
        # Create pie chart
        pie_colors = ['#FF6B6B', '#FFD166', '#06D6A0', '#118AB2', '#073B4C', '#EF476F']
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=grade_counts.index,
            values=grade_counts.values,
            hole=0.3,
            marker_colors=pie_colors,
            textinfo='label+percent',
            hoverinfo='label+value+percent'
        )])
        
        fig_pie.update_layout(
            title=f'Grade Distribution - {course_name}',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            height=400
        )
        
        # 2. HISTOGRAM - Score Distribution
        fig_hist = go.Figure(data=[go.Histogram(
            x=df['percentage'],
            nbinsx=20,
            marker_color='#118AB2',
            opacity=0.7
        )])
        
        fig_hist.update_layout(
            title=f'Score Distribution - {course_name}',
            xaxis_title='Percentage Score (%)',
            yaxis_title='Number of Students',
            height=400
        )
        
        return fig_pie, fig_hist
    
    def generate_student_analytics(self, results, course_name):
        """Generate student-specific analytics"""
        if not results:
            return None
        
        df = pd.DataFrame(results)
        
        # Top 10 performing students
        student_avg = df.groupby('student_name').agg({
            'score': 'mean',
            'max_score': 'mean',
            'assignment': 'count'
        }).reset_index()
        student_avg['percentage'] = (student_avg['score'] / student_avg['max_score']) * 100
        student_avg = student_avg.sort_values('percentage', ascending=False).head(10)
        
        fig_bar = go.Figure(data=[go.Bar(
            x=student_avg['student_name'],
            y=student_avg['percentage'],
            marker_color='#06D6A0',
            text=student_avg['percentage'].round(1),
            textposition='auto'
        )])
        
        fig_bar.update_layout(
            title=f'Top 10 Students - {course_name}',
            xaxis_title='Student',
            yaxis_title='Average Percentage (%)',
            height=400
        )
        
        return fig_bar
    
    def generate_assignment_analytics(self, results, course_name):
        """Generate assignment-specific analytics"""
        if not results:
            return None
        
        df = pd.DataFrame(results)
        
        # Average score by assignment
        assignment_avg = df.groupby('assignment').agg({
            'score': 'mean',
            'max_score': 'mean',
            'student_name': 'count'
        }).reset_index()
        assignment_avg['percentage'] = (assignment_avg['score'] / assignment_avg['max_score']) * 100
        
        fig_bar = go.Figure(data=[go.Bar(
            x=assignment_avg['assignment'],
            y=assignment_avg['percentage'],
            marker_color='#FFD166',
            text=assignment_avg['percentage'].round(1),
            textposition='auto'
        )])
        
        fig_bar.update_layout(
            title=f'Assignment Performance - {course_name}',
            xaxis_title='Assignment',
            yaxis_title='Average Percentage (%)',
            height=400
        )
        
        return fig_bar
    
    def generate_class_comparison(self, all_results):
        """Generate comparison charts for multiple classes"""
        if not all_results:
            return None, None
        
        df = pd.DataFrame(all_results)
        df['percentage'] = (df['score'] / df['max_score']) * 100
        
        # 1. Bar chart - Average by class
        avg_by_course = df.groupby('course_name')['percentage'].mean().reset_index()
        
        fig_bar = go.Figure(data=[go.Bar(
            x=avg_by_course['course_name'],
            y=avg_by_course['percentage'],
            marker_color='#118AB2',
            text=avg_by_course['percentage'].round(1),
            textposition='auto'
        )])
        
        fig_bar.update_layout(
            title='Class Performance Comparison',
            xaxis_title='Class',
            yaxis_title='Average Percentage (%)',
            height=400
        )
        
        # 2. Box plot - Distribution comparison
        fig_box = go.Figure()
        
        for course in df['course_name'].unique():
            course_data = df[df['course_name'] == course]['percentage']
            fig_box.add_trace(go.Box(
                y=course_data,
                name=course,
                boxmean=True
            ))
        
        fig_box.update_layout(
            title='Score Distribution by Class',
            yaxis_title='Percentage (%)',
            height=400
        )
        
        return fig_bar, fig_box