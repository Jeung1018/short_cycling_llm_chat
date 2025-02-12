# Short Cycling LLM Chat

An interactive chat application for analyzing short cycling energy anomalies using LangChain and Streamlit.

## Project Structure

    short_cycling_llm_chat/
    ├── backend/               # LangGraph backend
    │   ├── chains/           # LangChain components
    │   ├── nodes/            # Workflow nodes
    │   ├── models/           # Data models
    │   ├── utils/            # Utility functions
    │   ├── prompts/          # LLM prompts
    │   ├── workflows/        # Main workflow
    │   ├── config.py         # Configuration
    │   └── main.py          # Backend entry point
    │
    ├── frontend/             # Streamlit frontend
    │   ├── streamlit_app.py  # Main Streamlit app
    │   └── utils/           # Frontend utilities
    │
    ├── tests/               # Test files
    │   ├── test_backend/    # Backend tests
    │   ├── test_frontend/   # Frontend tests
    │   └── README.md        # Test documentation
    │
    ├── .env                 # Environment variables
    ├── .gitignore          # Git ignore rules
    ├── requirements.txt     # Project dependencies
    └── README.md           # This file

## Setup

1. Create a virtual environment:

    # Create venv
    python -m venv venv

    # Activate venv (Linux/macOS)
    source venv/bin/activate
    
    # Activate venv (Windows)
    venv\Scripts\activate

2. Install dependencies:

    pip install -r requirements.txt

3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your API keys and configuration

## Running the Application

Start the Streamlit app:

    streamlit run frontend/streamlit_app.py

## Features

- Interactive chat interface
- Short cycling anomaly detection
- Building 530 data analysis
- October 2024 timeframe focus
- Conversation history tracking
- Clear and informative responses

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
