#  Autonomous AI Grading Agent for Google Classroom

An intelligent grading system that integrates with Google Classroom API to automatically evaluate student submissions using AI, generate comprehensive performance analytics, and export detailed reports to streamline the assessment workflow for educators.

##  Key Features

- **Google Classroom Integration** – Direct API connection with secure OAuth 2.0 authentication
- **AI-Powered Grading** – Uses Mistral 7B LLM via Ollama for intelligent, rubric-based evaluation
- **Autonomous Workflow** – Automatically discovers and grades all ungraded submissions
- **Interactive Analytics** – Visualizes student performance with pie charts, histograms, and comparative graphs
- **Comprehensive Reports** – Generates multi-sheet Excel reports with student and assignment summaries
- **Fast & Optimized** – Implements caching and lazy loading for 90% faster grading
  
## dashboard:
<img width="926" height="478" alt="1" src="https://github.com/user-attachments/assets/eb50d1a4-12db-4d28-b327-27fec3942197" />

## connecting with Google

<img width="923" height="477" alt="2" src="https://github.com/user-attachments/assets/703b8d2c-f746-4b0d-ae13-8d6ad756636f" />

## authentication completed
 
<img width="485" height="185" alt="3" src="https://github.com/user-attachments/assets/0e54e896-836f-451b-96ba-176885e467cd" />

## select classes to grade

<img width="820" height="421" alt="4" src="https://github.com/user-attachments/assets/78d308a0-fde3-4cb4-bcf0-85bebb9bb59d" />

## grading completed

<img width="827" height="409" alt="5" src="https://github.com/user-attachments/assets/3f8bce30-297a-4ade-9bcb-70a18149f169" />

## graphs
- 
<img width="817" height="373" alt="6" src="https://github.com/user-attachments/assets/7b832204-761c-46f5-ac6c-74e30a54a9f1" />





##  Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Classroom API credentials
- Ollama (optional – system works without it, using simulated grading)

### Installation

```bash
# Clone the repository
git clone https://github.com/marryum2004/ai-grading-agent.git
cd ai-grading-agent

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
