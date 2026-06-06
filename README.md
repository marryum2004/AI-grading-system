#  Autonomous AI Grading Agent for Google Classroom

An intelligent grading system that integrates with Google Classroom API to automatically evaluate student submissions using AI, generate comprehensive performance analytics, and export detailed reports to streamline the assessment workflow for educators.

##  Key Features

- **Google Classroom Integration** – Direct API connection with secure OAuth 2.0 authentication
- **AI-Powered Grading** – Uses Mistral 7B LLM via Ollama for intelligent, rubric-based evaluation
- **Autonomous Workflow** – Automatically discovers and grades all ungraded submissions
- **Interactive Analytics** – Visualizes student performance with pie charts, histograms, and comparative graphs
- **Comprehensive Reports** – Generates multi-sheet Excel reports with student and assignment summaries
- **Fast & Optimized** – Implements caching and lazy loading for 90% faster grading

##  Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Classroom API credentials
- Ollama (optional – system works without it, using simulated grading)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-grading-agent.git
cd ai-grading-agent

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
