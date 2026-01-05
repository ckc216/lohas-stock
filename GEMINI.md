# Gemini AI Context: Stock Intelligence Analyzer

## Project Overview

This is an interactive web application developed with Python and Streamlit, designed specifically for analyzing the Taiwan stock market. Its core function is to provide two technical analysis visualization tools: "Lohas 5-Lines" and "Lohas Channel". The application allows users to search by stock ticker or company name (in Chinese) and presents the analysis in interactive charts.

**Main Technology Stack:**
- **Frontend/App Framework:** Streamlit
- **Data Analysis:** Pandas, NumPy, Scikit-learn, SciPy
- **Data Visualization:** Plotly
- **Data Source:** FinMind API (for fetching Taiwan stock data)

## Project Architecture

The code structure is clear and divided into three main parts:

- `streamlit_app.py`: The main entry point of the application. It handles the UI flow, state management (using `st.cache_data`), and coordinates the `services` and `view`.
- `services.py`: Contains all the backend logic.
  - `FinMindService`: Encapsulates all calls to the FinMind API, such as fetching stock IDs and historical price data.
  - `LohasService`: Performs the core mathematical calculations, including linear regression for the "Lohas 5-Lines" and moving averages with standard deviations for the "Lohas Channel".
- `view.py`:
  - `AppView`: Responsible for rendering all UI components, including the page title, search box, metric cards, and interactive charts drawn with Plotly. It also injects custom CSS to achieve a specific visual style.

## Building and Running

To run this application locally, follow these steps:

1.  **Install Dependencies:**
    Ensure you have Python installed in your environment. Then, run the following command in the project's root directory:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Application:**
    Use the Streamlit CLI to launch the application.
    ```bash
    streamlit run streamlit_app.py
    ```
    After execution, the application will open in your default web browser.

## Development Conventions

- **Separation of Concerns (SoC):** The project effectively separates data fetching/processing (Services) from UI rendering (View), with the main application file (`streamlit_app.py`) acting as a controller.
- **Caching:** Uses Streamlit's `@st.cache_data` decorator to cache API calls and data fetching, improving performance on repeated queries and reducing the number of API requests.
- **Code Style:** The code follows PEP 8 style guidelines and includes Type Hints, which improves readability and maintainability.
- **API Key Management:** A FinMind API key is hardcoded in `streamlit_app.py`. For production environments or open-source distribution, this should be changed to use environment variables or Streamlit's Secrets Management.
- **UI Design:** `view.py` contains a significant amount of custom CSS to create a clean, modern, Apple-like user interface.