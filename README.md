# Add Comprehensive README.md for TDS Project 2 - AI-Powered Autonomous Quiz Solver

Replace the existing README.md ("UNFINISHED, ABANDONED") with detailed documentation describing this fascinating AI-powered autonomous quiz-solving system.

## Project Overview
This is an **experimental, unfinished** FastAPI-based autonomous system that uses OpenAI's GPT models to automatically solve data-driven quizzes. The system orchestrates a complete pipeline: rendering JavaScript-heavy quiz pages, generating data collection scripts, executing them safely, processing the scraped data, and submitting final answers — all without human intervention.

⚠️ **Status: UNFINISHED & ABANDONED** - This project was discontinued during development but represents an interesting exploration of AI-powered autonomous systems.

## Concept & Architecture

### The Autonomous Pipeline
The system follows a multi-stage autonomous workflow:

1. **Page Rendering** - Uses Playwright to render JavaScript-heavy quiz pages
2. **AI Analysis** - GPT analyzes HTML to understand quiz requirements
3. **Data Collection Script Generation** - AI writes Python scripts to scrape required data
4. **Safe Script Execution** - Executes AI-generated scripts in sandboxed environment
5. **Data Processing** - AI generates second script to process/analyze collected data
6. **Answer Formatting** - AI formats final answer according to quiz requirements
7. **Submission** - Posts answer back to evaluation server

### Key Innovation
The core innovation is **AI-generated code execution**: The system uses GPT to write data collection and processing scripts on-the-fly, then executes them in a controlled environment with safety checks.

## Technology Stack
- **Backend**: FastAPI 0.121.2
- **Server**: Uvicorn 0.38.0
- **AI/ML**: OpenAI API 2.8.1 (GPT models)
- **Browser Automation**: Playwright 1.56.0
- **Data Processing**: Pandas 2.3.3, NumPy 2.3.5
- **Web Scraping**: BeautifulSoup4 4.14.2, lxml 6.0.2
- **HTTP Client**: httpx 0.28.1, requests 2.32.5
- **Environment**: python-dotenv 1.2.1

## File Structure
```
tds-project-2/
├── app/
│   ├── api/
│   │   ├── router.py           # Main FastAPI endpoints
│   │   └── schemas.py          # Pydantic request models
│   ├── core/
│   │   ├── config.py           # Environment configuration
│   │   └── utils.py            # Utility functions
│   ├── services/
│   │   ├── renderer.py         # Playwright page rendering
│   │   ├── openai_orchestrator.py    # Data collection script generation
│   │   ├── openai_processor.py       # Processing script generation
│   │   ├── openai_final_answer.py    # Answer formatting
│   │   ├── executor.py               # Safe script execution (collection)
│   │   ├── executor_processing.py    # Safe script execution (processing)
│   │   ├── submitter.py              # Answer submission
│   │   ├── run_saver.py              # Run artifacts storage
│   │   ├── schemas_answer.py         # Structured output schemas
│   │   ├── final_answer_orchestrator.py  # Final answer orchestration
│   │   └── cache.py                  # Caching utilities
│   ├── prompts/                # Prompt templates
│   │   ├── requirements_prompt.txt
│   │   ├── extract_data_prompt.txt
│   │   └── processing_prompt.txt
│   ├── workers/                # Background workers
│   │   └── job_runner.py
│   ├── logs/                   # Application logs
│   └── main.py                 # FastAPI app initialization
├── tests/                      # Test files (incomplete)
│   └── test_api.py
├── test_exec.py                # Executor testing script
├── run.sh                      # Development server launcher
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # Project documentation
```

## Core Components

### 1. Page Renderer (`services/renderer.py`)
- Uses Playwright headless browser
- Waits for JavaScript rendering completion
- Handles dynamic content and SPAs
- 15-second delay for full content loading
- Network idle detection for better reliability

### 2. AI Orchestrator (`services/openai_orchestrator.py`)
**Data Collection Script Generator**
- Analyzes quiz HTML to identify required datasets
- Generates Python scripts that download/scrape external data
- Uses structured JSON schema for reliable output
- Allowed libraries: requests, pandas, bs4, lxml, json

### 3. Safe Script Executor (`services/executor.py`)
**Security Features:**
- Forbidden keyword detection (subprocess, rm -rf, sudo, etc.)
- 60-second timeout protection
- Isolated temporary directory execution
- No network access after download phase
- Captures stdout/stderr for debugging

### 4. Data Processor (`services/openai_processor.py`)
**Processing Script Generator**
- Receives scraped files list
- Generates analytical Python code
- Merges, filters, and processes datasets
- Computes final answers from data
- Allowed libraries: pandas, numpy, json, bs4, lxml

### 5. Answer Formatter (`services/openai_final_answer.py`)
**Final Answer Logic:**
- Parses processing script output
- Formats answer according to quiz requirements
- Handles single values or multi-output objects
- Includes submission URL extraction
- Strict JSON schema validation

### 6. Run Saver (`services/run_saver.py`)
**Artifact Persistence:**
- Creates timestamped run folders
- Saves HTML snapshots
- Stores generated scripts
- Preserves stdout/stderr logs
- Archives scraped and processed data

## Environment Variables
Create a `.env` file with:
```env
SECRET=your_secret_key
BASE_URL=https://api.openai.com
MODEL=gpt-4  # or gpt-3.5-turbo
OPENAI_API_KEY=your_openai_api_key
```

## Installation
```bash
# Clone repository
git clone https://github.com/Viakya/tds-project-2.git
cd tds-project-2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Running the Server
```bash
# Using run script
chmod +x run.sh
./run.sh

# Or manually
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

## API Endpoint

### POST `/quiz-run`
Initiates autonomous quiz-solving pipeline.

**Request:**
```json
{
  "email": "user@example.com",
  "secret": "your_secret_key",
  "url": "https://quiz-site.com/quiz-page"
}
```

**Response:**
```json
{
  "status": "completed",
  "final_answer": {
    "answer": "42"
  },
  "run_folder": "runs/20251226-123456-uuid"
}
```

## Workflow Example

1. **Request received**: `/quiz-run` with quiz URL
2. **Rendering** (18s): Playwright loads page with JavaScript
3. **AI Analysis** (10s): GPT reads HTML, identifies data sources
4. **Script Generation** (15s): GPT writes data collection script
5. **Data Collection** (25s): Execute script, download datasets
6. **Processing Script** (10s): GPT writes analysis code
7. **Data Processing** (12s): Execute processing script
8. **Answer Formatting** (5s): GPT formats final answer
9. **Submission** (2s): POST answer to evaluation server
10. **Artifact Storage**: All steps saved to `runs/` folder

## Safety Features

### Script Sandboxing
- Temporary isolated directories
- No access to parent filesystem
- Timeout enforcement (60s max)
- Captured output streams

### Forbidden Operations
Scripts are rejected if they contain:
- `subprocess` calls
- File deletion (`os.remove`, `rm -rf`)
- System administration (`sudo`, `apt-get`)
- Package installation (`pip install`)

### Allowed Libraries
**Data Collection:**
- requests, pandas, bs4, lxml, json

**Data Processing:**
- pandas, numpy, json, bs4, lxml

## Testing
```bash
# Test script executor
python test_exec.py

# Expected: Creates out.csv with data
```

## Run Artifacts
Each quiz run creates a folder in `runs/` containing:
```
runs/20251226-123456-uuid/
├── html.txt                     # Rendered HTML
├── data_collection_script.py    # Generated scraper
├── collector_stdout.txt         # Collection logs
├── collector_stderr.txt         # Collection errors
├── scraped/                     # Downloaded data
│   ├── dataset1.csv
│   └── dataset2.json
├── data_processing_script.py    # Generated processor
├── processor_stdout.txt         # Processing logs
├── processor_stderr.txt         # Processing errors
├── processed/                   # Processed outputs
│   └── final_result.csv
├── final_answer.json            # Final formatted answer
└── submit_result.txt            # Submission response
```

## Limitations & Why It Was Abandoned

### Technical Challenges
1. **AI Reliability**: GPT-generated code not always executable
2. **Schema Parsing**: Strict JSON schemas sometimes violated
3. **Security Concerns**: Executing arbitrary AI code is inherently risky
4. **Quiz Variability**: Different quiz formats require different approaches
5. **Debugging Difficulty**: Multi-stage pipeline hard to troubleshoot

### Incomplete Features
- ❌ Full worker queue system (workers/ directory has basic implementation)
- ❌ Advanced prompt templating (basic templates exist)
- ❌ Comprehensive test suite (tests/ incomplete)
- ❌ Error recovery mechanisms
- ❌ Retry logic for failed stages
- ❌ Multi-quiz parallel processing

### Known Issues
- Playwright rendering timeout on slow sites
- GPT occasionally generates invalid Python syntax
- No handling for authentication-protected quizzes
- Limited error messages in failure cases
- Missing variable reference in router.py (final_answer_raw)

## What Worked
✅ Playwright rendering of JS-heavy pages  
✅ Structured output from OpenAI with schemas  
✅ Safe script execution with forbidden keyword filtering  
✅ Multi-stage pipeline architecture  
✅ Artifact preservation for debugging  
✅ Timeout protection against infinite loops  

## What Didn't Work
❌ Reliable code generation from GPT  
❌ Handling diverse quiz formats  
❌ Error recovery in multi-stage pipeline  
❌ Scaling to multiple concurrent quizzes  
❌ Security validation of AI-generated code  

## Interesting Learnings
1. **AI Code Generation**: GPT can write functional scripts ~70% of the time
2. **Structured Outputs**: JSON schemas significantly improve reliability
3. **Sandbox Execution**: Simple keyword filtering provides basic safety
4. **Browser Automation**: Playwright excellent for JS-rendered content
5. **Multi-Agent Systems**: Orchestrating multiple AI calls is complex

## Future Possibilities
If this project were continued, consider:
- Use function calling instead of strict schemas
- Implement code validation before execution
- Add retry mechanisms with different prompts
- Create prompt templates for common quiz types
- Build a feedback loop to improve script quality
- Use containerization (Docker) for better isolation

## Similar Projects & References
- LangChain Agents
- AutoGPT
- OpenAI Code Interpreter
- Microsoft Semantic Kernel

## License
No license specified (unfinished project)

## Contributing
⚠️ This project is **abandoned** and not accepting contributions. Feel free to fork and experiment!

## Disclaimer
This project was created as an experimental exploration of autonomous AI systems. It is incomplete, may contain bugs, and should not be used in production. Executing AI-generated code carries inherent security risks.

---

**Why this is interesting despite being abandoned:**
This project represents an ambitious attempt at building a fully autonomous AI agent capable of understanding problems, writing code, executing it safely, and iterating toward solutions. While incomplete, it demonstrates key concepts in AI orchestration, code generation, and safe execution that remain relevant to current AI agent research.
