import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import httpx
from dotenv import load_dotenv
import uvicorn
from pydantic import BaseModel
import google.generativeai as genai
import PyPDF2
import io


# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="GrowEasy: AI-Powered Business Ally")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize local storage
STORAGE_DIR = "local_storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

# Google Gemini API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Custom classes for storage
class ChatHistory(BaseModel):
    id: str
    messages: List[Dict[str, str]]
    created_at: str

class FinancialReport(BaseModel):
    id: str
    filename: str
    content: str
    summary: Optional[str] = None
    advice: Optional[str] = None
    created_at: str

class BudgetPlan(BaseModel):
    id: str
    financial_data: Dict
    goals: List[str]
    plan: Optional[Dict] = None
    created_at: str

class RiskAssessment(BaseModel):
    id: str
    decision: str
    context: str
    assessment: Optional[Dict] = None
    created_at: str

# Local storage functions
def save_data(data_type, data):
    filepath = os.path.join(STORAGE_DIR, f"{data_type}.json")
    
    # Load existing data
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []
    
    # Add new data
    existing_data.append(data)
    
    # Save updated data
    with open(filepath, "w") as f:
        json.dump(existing_data, f, indent=2)
    
    return data

def load_data(data_type):
    filepath = os.path.join(STORAGE_DIR, f"{data_type}.json")
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# Google Gemini API functions
def init_gemini_model():
    """Initialize the Google Gemini model"""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not set")
        
    # Configure the API
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Set up model configurations
    generation_config = {
        "temperature": 0.4,
        "top_p": 1,
        "top_k": 32,
        "max_output_tokens": 4096,
    }
    
    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        }
    ]
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
        safety_settings=safety_settings
    )
    
    return model

# Global model instance
gemini_model = None

# Function to get or initialize model
def get_gemini_model():
    global gemini_model
    if gemini_model is None:
        try:
            gemini_model = init_gemini_model()
        except Exception as e:
            print(f"Error initializing Gemini model: {str(e)}")
            raise
    return gemini_model

async def query_gemini_model(prompt, max_tokens=4096):
    """Query Google Gemini model with a prompt"""
    try:
        model = get_gemini_model()
        
        # Print debug information
        print(f"Sending prompt to Google Gemini model. Length: {len(prompt)}")
        
        # Generate response
        response = model.generate_content(prompt)
        
        # Print debug information
        print(f"Received response from Google Gemini model")
        
        # Return generated text
        return response.text
    except Exception as e:
        print(f"Error querying Google Gemini model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error querying Gemini model: {str(e)}")

# Routes

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# Business Queries Chatbot
@app.get("/chatbot", response_class=HTMLResponse)
async def chatbot_page(request: Request):
    chat_history = load_data("chat_history")
    return templates.TemplateResponse("chatbot.html", {"request": request, "chat_history": chat_history})

@app.post("/chatbot")
async def process_chatbot_query(question: str = Form(...)):
    try:
        # Print for debugging
        print(f"Received question: {question}")
        
        # Create system prompt for business advisor context
        system_prompt = """You are GrowEasy, an AI-powered business advisor specializing in helping small and medium enterprises (SMEs).
        You provide expert advice on business strategy, operations, marketing, finance, and legal matters.
        Your responses should be professional, practical, and actionable.
        Format your answers in a structured way with clear sections and bullet points where appropriate."""
        
        # Create the full prompt
        full_prompt = f"{system_prompt}\n\nQuestion: {question}\n\nAnswer:"
        
        # Check if API key is available
        if not GEMINI_API_KEY:
            print("Gemini API key not found")
            return {"answer": "Sorry, I'm having trouble connecting to my knowledge base. Please try again later."}
        
        # Query the Google Gemini model
        try:
            response = await query_gemini_model(full_prompt, max_tokens=4096)
            print(f"Received response from Gemini API: {response[:100]}...")  # Print first 100 chars for debugging
        except Exception as e:
            print(f"Error querying Gemini model: {str(e)}")
            return {"answer": "I encountered an issue processing your question. Please try again later."}
        
        # Save chat history
        chat_data = {
            "id": str(uuid.uuid4()),
            "messages": [
                {"role": "user", "content": question},
                {"role": "assistant", "content": response}
            ],
            "created_at": datetime.now().isoformat()
        }
        save_data("chat_history", chat_data)
        
        return {"answer": response}
    except Exception as e:
        print(f"Unexpected error in process_chatbot_query: {str(e)}")
        return {"answer": "An unexpected error occurred. Please try again later."}

# Financial Report Summarizer and Advisor
@app.get("/financial-summarizer", response_class=HTMLResponse)
async def financial_summarizer_page(request: Request):
    reports = load_data("financial_reports")
    return templates.TemplateResponse("financial_summarizer.html", {"request": request, "reports": reports})

@app.post("/financial-summarizer")
async def process_financial_report(file: UploadFile = File(...)):
    try:
        content = await file.read()
        
        # Get file extension to determine file type
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        # Extract text content based on file type
        try:
            if file_extension in ['txt', 'csv']:
                # For text files, try UTF-8 decoding first
                try:
                    content_str = content.decode('utf-8')
                except UnicodeDecodeError:
                    # If UTF-8 fails, try other common encodings
                    content_str = content.decode('latin-1')  # Latin-1 can decode any byte values
            elif file_extension in ['xlsx', 'xls']:
                # For Excel files, you'll need pandas or a similar library
                try:
                    import pandas as pd
                    df = pd.read_excel(io.BytesIO(content))
                    content_str = df.to_string()
                except ImportError:
                    content_str = "Excel file detected. Required libraries not available for processing."
            elif file_extension == 'pdf':
                # For PDF files using PyPDF2
                try:
                    # Create a PDF reader object
                    pdf_file = io.BytesIO(content)
                    reader = PyPDF2.PdfReader(pdf_file)
                    
                    # Extract text from all pages
                    content_str = ""
                    for page_num in range(len(reader.pages)):
                        page = reader.pages[page_num]
                        content_str += page.extract_text() + "\n\n"
                    
                    if not content_str.strip():
                        content_str = "PDF document appears to be empty or contains non-extractable text."
                except Exception as pdf_error:
                    print(f"PDF processing error: {str(pdf_error)}")
                    content_str = "Error processing PDF file. The file may be corrupted or password-protected."
            else:
                # For unsupported file types
                content_str = f"Unsupported file format: {file_extension}. Please upload CSV, TXT, Excel, or PDF files."
        except Exception as extract_error:
            print(f"Error extracting content: {str(extract_error)}")
            raise HTTPException(status_code=400, detail=f"Error processing file content: {str(extract_error)}")
        
        # Limit the content size for API processing
        limited_content = content_str[:3000]  # Limit to 3000 characters
        
        # Create prompts for summarization and advice
        summary_prompt = f"""Analyze and summarize the following financial report for a small business:
        
        {limited_content}
        
        Provide a concise summary of the financial status, highlighting key metrics, trends, and concerns."""
        
        advice_prompt = f"""Based on the following financial report for a small business:
        
        {limited_content}
        
        Provide specific, actionable advice for improving financial performance, addressing any issues identified,
        and optimizing resource allocation. Include 3-5 priority recommendations."""
        
        # Query the Google Gemini model for summary and advice
        try:
            summary = await query_gemini_model(summary_prompt, max_tokens=4096)
            advice = await query_gemini_model(advice_prompt, max_tokens=4096)
        except Exception as e:
            print(f"Error querying model: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating analysis: {str(e)}")
        
        # Save report data
        report_data = {
            "id": str(uuid.uuid4()),
            "filename": file.filename,
            "content": content_str[:5000],  # Store truncated content
            "summary": summary,
            "advice": advice,
            "created_at": datetime.now().isoformat()
        }
        save_data("financial_reports", report_data)
        
        return {"summary": summary, "advice": advice, "id": report_data["id"]}
    except Exception as e:
        print(f"Unexpected error in process_financial_report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing report: {str(e)}")

# Budget Optimization Planner
@app.get("/budget-planner", response_class=HTMLResponse)
async def budget_planner_page(request: Request):
    plans = load_data("budget_plans")
    return templates.TemplateResponse("budget_planner.html", {"request": request, "plans": plans})

@app.post("/budget-planner")
async def create_budget_plan(
    revenue: float = Form(...),
    expenses: float = Form(...),
    growth_target: float = Form(...),
    industry: str = Form(...),
    company_size: str = Form(...),
    goals: str = Form(...)
):
    financial_data = {
        "revenue": revenue,
        "expenses": expenses,
        "growth_target": growth_target,
        "industry": industry,
        "company_size": company_size
    }
    
    goals_list = [goal.strip() for goal in goals.split(',')]
    
    # Create prompt for budget planning
    plan_prompt = f"""As an AI financial advisor, create a detailed budget optimization plan based on the following:
    
    Financial Data:
    - Current Monthly Revenue: ${revenue}
    - Current Monthly Expenses: ${expenses}
    - Growth Target: {growth_target}%
    - Industry: {industry}
    - Company Size: {company_size}
    
    Business Goals:
    {goals}
    
    Create a comprehensive budget optimization plan that includes:
    1. Expense allocation by category (percentages)
    2. Recommended cost-cutting measures
    3. Investment priorities for growth
    4. Revenue enhancement strategies
    5. Monthly savings targets
    6. Timeline for achieving financial goals
    
    Format your response as a structured plan with clear sections and actionable recommendations."""
    
    # Query the Google Gemini model
    plan_response = await query_gemini_model(plan_prompt, max_tokens=4096)
    
    # Parse the response into a structured format
    plan = {
        "budget_allocation": plan_response,
    }
    
    # Save plan data
    plan_data = {
        "id": str(uuid.uuid4()),
        "financial_data": financial_data,
        "goals": goals_list,
        "plan": plan,
        "created_at": datetime.now().isoformat()
    }
    save_data("budget_plans", plan_data)
    
    return {"plan": plan, "id": plan_data["id"]}

# Risk-Aware Financial Decision Guide
@app.get("/risk-analyzer", response_class=HTMLResponse)
async def risk_analyzer_page(request: Request):
    assessments = load_data("risk_assessments")
    return templates.TemplateResponse("risk_analyzer.html", {"request": request, "assessments": assessments})

@app.post("/risk-analyzer")
async def analyze_financial_decision(
    decision: str = Form(...),
    context: str = Form(...),
    industry: str = Form(...),
    investment_amount: float = Form(...)
):
    # Create prompt for risk assessment
    risk_prompt = f"""As a risk analysis expert for small businesses, provide a comprehensive risk assessment for the following financial decision:
    
    Decision: {decision}
    Context: {context}
    Industry: {industry}
    Investment Amount: ${investment_amount}
    
    Please provide:
    1. An overall risk rating (Low, Medium, High, Very High)
    2. Identification of specific risks (minimum 3)
    3. Probability and impact assessment for each risk
    4. Mitigation strategies for each identified risk
    5. Alternative approaches that might reduce risk
    
    Format your response as a structured risk assessment report with clear sections."""
    
    # Query the Google Gemini model
    risk_response = await query_gemini_model(risk_prompt, max_tokens=4096)
    
    # Structure the assessment
    assessment = {
        "analysis": risk_response,
    }
    
    # Save assessment data
    assessment_data = {
        "id": str(uuid.uuid4()),
        "decision": decision,
        "context": context,
        "industry": industry,
        "investment_amount": investment_amount,
        "assessment": assessment,
        "created_at": datetime.now().isoformat()
    }
    save_data("risk_assessments", assessment_data)
    
    return {"assessment": assessment, "id": assessment_data["id"]}

# Run the app
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)