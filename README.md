
# GrowEasy: AI-Powered Business Ally

GrowEasy is an intelligent web application designed to assist Small and Medium Enterprises (SMEs) with various business challenges. Leveraging the power of Google's Gemini Pro API and built with FastAPI, GrowEasy offers a suite of tools including a business queries chatbot, financial report analysis, budget optimization, and risk-aware decision guidance.

## Features

1.  **Business Queries Chatbot (`/chatbot`)**:
    *   Ask business-related questions (strategy, operations, marketing, finance, legal).
    *   Receives professional, practical, and actionable advice.
    *   Chat history is saved locally.

2.  **Financial Report Summarizer and Advisor (`/financial-summarizer`)**:
    *   Upload financial reports (supports `.txt`, `.csv`, `.xlsx`, `.xls`, `.pdf`).
    *   Get AI-generated summaries highlighting key metrics, trends, and concerns.
    *   Receive actionable advice for improving financial performance.
    *   Reports and analyses are saved locally.

3.  **Budget Optimization Planner (`/budget-planner`)**:
    *   Input current financial data (revenue, expenses, growth targets, industry, company size) and business goals.
    *   Receive a comprehensive budget optimization plan including expense allocation, cost-cutting, investment priorities, and revenue strategies.
    *   Plans are saved locally.

4.  **Risk-Aware Financial Decision Guide (`/risk-analyzer`)**:
    *   Describe a financial decision, its context, industry, and investment amount.
    *   Get a structured risk assessment including overall risk rating, specific risks, probability/impact, mitigation strategies, and alternative approaches.
    *   Assessments are saved locally.

## Technology Stack

*   **Backend:** Python, FastAPI
*   **AI Model:** Google Gemini API (via `google-generativeai` SDK)
*   **Frontend:** HTML, CSS, JavaScript (served via Jinja2Templates)
*   **Data Storage:** Local JSON files (in `local_storage/` directory)
*   **File Handling:** PyPDF2 (for PDFs), Pandas (for Excel files)
*   **Environment Management:** `python-dotenv`
*   **ASGI Server:** Uvicorn

## Prerequisites

*   Python 3.8+
*   pip (Python package installer)
*   A Google Gemini API Key. You can obtain one from [Google AI Studio](https://aistudio.google.com/app/apikey).

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd groweasy-ai-ally # Or your project directory name
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    Create a `requirements.txt` file with the following content:
    ```txt
    fastapi
    uvicorn[standard]
    python-dotenv
    google-generativeai
    pydantic
    Jinja2
    PyPDF2
    pandas
    # httpx might be needed if you extend API calls or for FastAPI's TestClient
    ```
    Then run:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  Create a `.env` file in the root directory of the project.
2.  Add your Google Gemini API Key to the `.env` file:
    ```env
    GEMINI_API_KEY=YOUR_GOOGLE_GEMINI_API_KEY_HERE
    ```
    Replace `YOUR_GOOGLE_GEMINI_API_KEY_HERE` with your actual API key.

## Running the Application

Once the setup and configuration are complete, run the FastAPI application using Uvicorn:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## Usage

Run the FastAPI app with the following command:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

* `app:app`: Refers to the app instance of FastAPI in the `app.py` file.
* `--host 0.0.0.0`: Makes the server accessible on your network.
* `--port 8000`: Specifies the port number.
* `--reload`: Enables auto-reloading when code changes (useful for development).

Open your web browser and navigate to:

* Homepage: [http://localhost:8000/](http://localhost:8000/)
* Chatbot: [http://localhost:8000/chatbot](http://localhost:8000/chatbot)
* Financial Summarizer: [http://localhost:8000/financial-summarizer](http://localhost:8000/financial-summarizer)
* Budget Planner: [http://localhost:8000/budget-planner](http://localhost:8000/budget-planner)
* Risk Analyzer: [http://localhost:8000/risk-analyzer](http://localhost:8000/risk-analyzer)

Follow the on-screen instructions to interact with each tool.

## File Storage

All generated data, including chat history, financial report analyses, budget plans, and risk assessments, are stored locally in JSON files within the `local_storage/` directory. This directory will be created automatically if it doesn't exist.

## Project Structure

```
groweasy-ai-ally/
├── app.py                 # Main FastAPI application logic
├── local_storage/         # Directory for storing JSON data files (auto-created)
│   ├── chat_history.json
│   ├── financial_reports.json
│   ├── budget_plans.json
│   └── risk_assessments.json
├── static/                # Static files (CSS, JS, images)
│   └── css/
│       └── style.css      # Example CSS
├── templates/             # HTML templates for Jinja2
│   ├── home.html
│   ├── chatbot.html
│   ├── financial_summarizer.html
│   ├── budget_planner.html
│   └── risk_analyzer.html
├── .env                   # Environment variables (API keys) - YOU CREATE THIS
├── requirements.txt       # Python dependencies - YOU CREATE THIS
└── README.md              # This file
```

## Future Enhancements

* User authentication and accounts to store data per user.
* Integration with a proper database (e.g., PostgreSQL, MongoDB) instead of local JSON files.
* More sophisticated AI models or fine-tuning for specific business domains.
* Advanced data visualization for financial reports and budget plans.
* Deployment to a cloud platform (e.g., AWS, Google Cloud, Azure).
* Real-time collaboration features.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue for bugs, feature requests, or improvements.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See LICENSE file for more information.
