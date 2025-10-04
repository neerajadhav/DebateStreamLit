# 🎭 AI-Powered Debate Platform

A sophisticated Streamlit application that facilitates structured debates between two parties with an AI host managing the flow and providing unbiased analysis.

## Features

- **AI Host**: Gemini-powered AI that manages debate flow and provides opening statements
- **Two-Party System**: Support for two debating parties with customizable names
- **Round-by-Round Analysis**: AI analyzes each round objectively, providing feedback on argument strength and technique
- **Final Verdict**: Comprehensive analysis and judgment after all rounds complete
- **Export Functionality**: Download complete debate transcripts and analysis
- **User-Friendly Interface**: Clean, intuitive Streamlit interface

## Setup Instructions

### 1. Prerequisites
- Python 3.8 or higher
- Google Gemini API key (get from [Google AI Studio](https://makersuite.google.com/app/apikey))

### 2. Installation

```bash
# Clone or download the project
cd DebateStreamLit

# Install dependencies
pip install -r requirements.txt
```

### 3. Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### 4. Usage

1. **API Configuration**: Enter your Gemini API key in the sidebar
2. **Setup Debate**: 
   - Enter names for both parties
   - Specify the debate topic
   - Choose number of rounds (3, 5, or 7)
3. **Start Debating**:
   - AI host provides opening statement
   - Parties take turns presenting arguments
   - AI analyzes each round objectively
4. **Final Analysis**: Get comprehensive verdict and export results

## Application Structure

```
DebateStreamLit/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Key Components

### DebateHost Class
- `generate_opening_statement()`: Creates professional debate opening
- `analyze_arguments()`: Provides unbiased round-by-round analysis
- `generate_final_verdict()`: Delivers comprehensive final judgment

### Main Features
- **Session Management**: Tracks debate state across interactions
- **Real-time Analysis**: Immediate feedback after each round
- **Export Capability**: JSON export of complete debate history
- **Responsive Design**: Works on desktop and mobile devices

## API Usage

The application uses Google's Gemini Pro model for:
- Generating opening statements
- Analyzing debate rounds
- Providing final verdicts

All AI interactions are designed to be:
- **Unbiased**: Fair analysis of both sides
- **Constructive**: Educational feedback for improvement
- **Comprehensive**: Detailed reasoning for all judgments

## Customization Options

- **Round Numbers**: Choose between 3, 5, or 7 rounds
- **Participant Names**: Customize party names
- **Topic Flexibility**: Any debate topic supported
- **Early Termination**: Option to end debate before all rounds

## Security Notes

- API keys are entered securely (password field)
- No sensitive data is stored permanently
- All processing happens in real-time

## Troubleshooting

### Common Issues:
1. **API Key Issues**: Ensure valid Gemini API key is entered
2. **Loading Problems**: Check internet connection for API calls
3. **Performance**: Large debates may take longer to analyze

### Getting Help:
- Check API key validity at Google AI Studio
- Ensure all dependencies are installed correctly
- Restart the application if session state becomes corrupted

## Future Enhancements

Potential improvements could include:
- Multiple AI judge options
- Scoring systems
- Debate templates
- User authentication
- Historical debate tracking
- Team debate support

---

**Built with Streamlit and Google Gemini AI** 🚀
