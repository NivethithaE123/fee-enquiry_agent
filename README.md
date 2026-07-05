# Fee Inquiry Agent

A beautiful and modern Flask-based web application that acts as a strict **Fee Inquiry Agent**. It reads a PDF document (`fee_structure.pdf`) and answers user queries about fees strictly based on the content of that document using Google's Gemini API.

## Features

- **Strict Context Answering**: Answers queries *only* using information found in the provided PDF. If information is not present, it replies politely that it is unavailable.
- **Beautiful Glassmorphic UI**: High-fidelity dark mode user interface featuring smooth transitions, micro-animations, and dynamic status indicator badges.
- **Persistent Chat History**: Supports multi-turn conversations by maintaining dialogue history.
- **Robust Error Handling**: Gracefully handles missing PDF files, invalid API keys, and missing environment variables with user-friendly warnings and instructions.

---

## Workspace Setup (Recommended)

Since this project was generated inside a subdirectory, we recommend setting this directory as your active workspace in Antigravity.

---

## Local Setup Instructions

Follow these steps to run the application on your local machine:

### 1. Prerequisites
Ensure you have **Python 3.9+** installed on your system.

### 2. Clone or Navigate to the Project Directory
Make sure your terminal is inside the root folder of this project:
```bash
cd fee_inquiry_agent
```

### 3. Create and Activate a Virtual Environment
It is highly recommended to run this project inside a clean virtual environment:

**On Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
Install the required packages listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 5. Add Your Fee Structure Document
Place your PDF file named **`fee_structure.pdf`** directly into the project's root folder (the same directory as `app.py`).

### 6. Configure the Gemini API Key
Obtain an API key from Google AI Studio. You can configure this key in one of two ways:

#### Option A: Create a `.env` File (Recommended)
Create a file named `.env` in the project root directory and add:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

#### Option B: Set Environment Variable directly in Terminal
* **PowerShell (Windows):**
  ```powershell
  $env:GEMINI_API_KEY="your_actual_gemini_api_key_here"
  ```
* **Command Prompt (Windows):**
  ```cmd
  set GEMINI_API_KEY="your_actual_gemini_api_key_here"
  ```
* **Bash (macOS/Linux):**
  ```bash
  export GEMINI_API_KEY="your_actual_gemini_api_key_here"
  ```

### 7. Run the Flask App
Start the development server:
```bash
python app.py
```

Open your browser and navigate to:
```
https://vsb-fee-ai-363219115391.asia-southeast1.run.app
```
