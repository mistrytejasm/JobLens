# JobLens 🔍

JobLens is a specialized job insights tool built with **Streamlit** and **Playwright**. It allows you to scrape and analyze job postings from a single URL, providing a clean, distraction-free view of the position details.

## Setup

1. **Install Python 3.8+**
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

## Running the App

```bash
streamlit run app.py
```

## Features
- **One-Click Analysis**: Paste any job URL.
- **Clean UI**: formatted markdown description, key metrics (applicants, company).
- **Extensible**: Built on Pydantic models for easy API integration.
