# Fee Inquiry Agent

A beautiful and modern Flask-based web application that acts as a strict **Fee Inquiry Agent**. It reads a PDF document (`fee_structure.pdf`) and answers user queries about fees strictly based on the content of that document using Google's Gemini API.

## Features

- **Strict Context Answering**: Answers queries *only* using information found in the provided PDF. If information is not present, it replies politely that it is unavailable.
- **Beautiful Glassmorphic UI**: High-fidelity dark mode user interface featuring smooth transitions, micro-animations, and dynamic status indicator badges.
- **Persistent Chat History**: Supports multi-turn conversations by maintaining dialogue history.
- **Robust Error Handling**: Gracefully handles missing PDF files, invalid API keys, and missing environment variables with user-friendly warnings and instructions.

  
* **Command Prompt (Windows):**
  ```cmd
  set GEMINI_API_KEY="your_actual_gemini_api_key_here"
  ```
  export GEMINI_API_KEY="your_actual_gemini_api_key_here"
  ```

### 7. Run the REST API App
```
https://abc-fee-ai-363219115391.asia-southeast1.run.app
```
