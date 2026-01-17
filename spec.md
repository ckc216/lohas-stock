# Project Refactoring Functional Specification

## 1. System Architecture (Refactor Path)
- `YFinanceService`: Responsible for the Yahoo Finance API, fetches stock prices from yfinance.
- `LohasService`: Calculates the 5-lines and channel logic.
- `AppView`: Responsible for Streamlit UI rendering, tab switching, and interaction.

## 2. Technical Constraints
- Maintain the classic Apple white style.
- Data calculation and UI logic must be decoupled.