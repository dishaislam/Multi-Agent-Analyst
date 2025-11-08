# 🤖 Multi-Agent Business Analytics System

A sophisticated AI-powered business analytics platform that uses multi-agent architecture to coordinate data processing, analysis, and conversational insights. Built with Python, integrating advanced analytics with natural language interaction powered by Mistral AI.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Agent Documentation](#-agent-documentation)
- [Examples](#-examples)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🎯 Core Capabilities

- **Multi-Agent Architecture**: Coordinated system with specialized agents for different tasks
- **Natural Language Interface**: Chat with your data using conversational AI
- **Advanced Analytics**: Comprehensive business intelligence and KPI tracking
- **Automated Insights**: AI-generated recommendations and trend analysis
- **Interactive Visualizations**: Automated chart generation for key metrics
- **Real-time Data Processing**: Efficient ETL pipeline with feature engineering

### 🤖 Intelligent Agents

1. **Data Agent** - Data loading, cleaning, and feature engineering
2. **Analytics Agent** - Statistical analysis and visualization generation
3. **Conversational Agent** - Natural language understanding and response generation
4. **Coordinator Agent** - Orchestrates workflow between all agents

### 📊 Analytics Features

- ✅ Yearly KPI summaries
- ✅ Profit margin analysis
- ✅ Revenue trend tracking
- ✅ Top product performance analysis
- ✅ Customer segmentation and RFM analysis
- ✅ Correlation analysis
- ✅ Time-series forecasting support
- ✅ Geographic performance analysis

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│                  (Chat / CLI / API)                      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Coordinator Agent                           │
│         (Orchestration & Routing Logic)                  │
└──────┬───────────────┬──────────────────┬───────────────┘
       │               │                  │
       ▼               ▼                  ▼
┌─────────────┐ ┌─────────────┐  ┌──────────────────┐
│ Data Agent  │ │  Analytics  │  │  Conversational  │
│             │ │    Agent    │  │      Agent       │
│ • Loading   │ │             │  │                  │
│ • Cleaning  │ │ • Analysis  │  │ • NLP            │
│ • Features  │ │ • Viz       │  │ • Mistral AI     │
│ • Queries   │ │ • Reports   │  │ • Insights       │
└─────────────┘ └─────────────┘  └──────────────────┘
       │               │                  │
       └───────────────┴──────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   Data Storage  │
              │   CSV / Parquet │
              └─────────────────┘
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (optional)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/multi-agent-analytics.git
cd multi-agent-analytics
```

### Step 2: Create Virtual Environment

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
python test_api.py
```

## ⚙️ Configuration

### 1. API Key Setup

Create a `.env` file in the project root:

```bash
MISTRAL_API_KEY=your_mistral_api_key_here
```

**Get Your Mistral API Key:**
1. Visit https://console.mistral.ai/
2. Sign up or log in
3. Navigate to "API Keys"
4. Create a new key
5. Copy and paste into `.env` file

### 2. Data Configuration

Place your CSV file in the project directory or specify the path when running the application.

**Required CSV Columns:**
- `Date` - Transaction date (format: DD/MM/YYYY)
- `Revenue` - Sales revenue
- `Profit` - Profit amount
- `Cost` - Cost amount
- `Order_Quantity` - Number of items ordered
- `Product` - Product name
- `Product_Category` - Product category
- `Customer_Age` - Customer age
- `Customer_Gender` - Customer gender
- `Country` - Country
- `State` - State/Province

## 📖 Usage

### Basic Usage

```bash
python main.py
```

### Interactive Session

```
============================================================
🤖 MULTI-AGENT BUSINESS ANALYTICS SYSTEM
============================================================

📁 Enter path to your CSV file: data/sales_data.csv

✅ Data loaded successfully!
📊 112,036 records from 2011-01-01 to 2016-07-31

============================================================
💬 CHAT INTERFACE
============================================================

You: What was the profit margin in 2015?

🤖 Assistant: In 2015, your business achieved a profit margin of 
42.5%. This represents strong profitability with total revenue of 
$1.2M and profit of $510K...

   📈 Detailed Metrics:
      Revenue: $1,200,000.00
      Profit: $510,000.00
      Profit Margin: 42.5%
```

### Common Queries

```
# Financial Analysis
"What was the profit margin in 2015?"
"Show me revenue trends from 2013 to 2016"
"Compare profit margins across all years"

# Product Analysis
"What are the top 5 products by revenue?"
"Analyze top products for 2016"
"Which product categories perform best?"

# Customer Insights
"How many unique customers do we have?"
"Show customer segmentation analysis"
"What's the average order value?"

# Comprehensive Analysis
"Create a full analysis report"
"Analyze sales performance"
"Generate business insights"
```

## 📁 Project Structure

```
multi-agent-analytics/
│
├── agents/                          # Agent modules
│   ├── __init__.py
│   ├── agent_base.py               # Base agent class
│   ├── data_agent.py               # Data processing agent
│   ├── analytics_agent.py          # Analytics & visualization agent
│   ├── conversational_agent.py     # NLP & chat agent
│   └── coordinator.py              # Orchestration agent
│
├── data/                           # Data directory
│   └── sales_data.csv             # Sample dataset
│
├── outputs/                        # Generated outputs
│   ├── yearly_kpi_summary.csv
│   ├── revenue_by_year.png
│   ├── profit_margin_by_year.png
│   └── ...                        # Additional reports
│
├── utils/                          # Utility functions
│   ├── __init__.py
│   └── helpers.py
│
├── main.py                         # Main application
├── test_api.py                     # API testing script
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (not tracked)
├── .env.example                   # Example environment file
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 🤖 Agent Documentation

### Data Agent

**Responsibilities:**
- Load and validate CSV data
- Clean and preprocess data
- Engineer features (RFM, temporal, financial metrics)
- Execute data queries
- Create specialized datasets

**Capabilities:**
```python
capabilities = [
    "load_data",
    "clean_data",
    "engineer_features",
    "create_specialized_datasets",
    "query_data"
]
```

**Key Methods:**
- `load_and_prepare_data(file_path)` - Complete data pipeline
- `query_data(params)` - Execute specific queries
- `get_data_summary()` - Overall data statistics

### Analytics Agent

**Responsibilities:**
- Generate KPI summaries
- Create visualizations
- Perform correlation analysis
- Track trends and patterns

**Capabilities:**
```python
capabilities = [
    "yearly_kpi_summary",
    "top_performers",
    "correlation_analysis",
    "trend_analysis",
    "create_visualizations"
]
```

**Key Methods:**
- `yearly_kpi_summary(df)` - Annual performance metrics
- `top_performers(df, year)` - Best products/categories
- `correlation_analysis(df)` - Feature correlations
- `trend_analysis(df)` - Time-series patterns

### Conversational Agent

**Responsibilities:**
- Natural language understanding
- Generate human-readable insights
- Explain analytical results
- Maintain conversation context

**Capabilities:**
```python
capabilities = [
    "chat",
    "explain_results",
    "answer_questions",
    "provide_recommendations"
]
```

**Key Methods:**
- `chat(message, context)` - Process user messages
- `explain_results(results)` - Convert data to insights
- `generate_insights(data)` - Create recommendations

### Coordinator Agent

**Responsibilities:**
- Parse user intent
- Route requests to appropriate agents
- Coordinate multi-agent workflows
- Aggregate and format responses

**Key Methods:**
- `process(task)` - Main request handler
- `_parse_intent(input)` - Extract user intent
- `_handle_data_query()` - Route data queries
- `_handle_analytics_request()` - Route analysis tasks

## 💡 Examples

### Example 1: Profit Margin Analysis

```python
# User query
"What was the profit margin in 2015?"

# System workflow
1. Coordinator parses intent → "profit_margin_query"
2. Data Agent queries 2015 financial data
3. Conversational Agent explains results

# Output
📊 Results for 2015:
   💰 Revenue: $1,245,678.00
   💵 Profit: $529,434.50
   💸 Cost: $716,243.50
   📈 Profit Margin: 42.51%
   📦 Total Orders: 15,234
   👥 Unique Customers: 8,456
```

### Example 2: Revenue Trends

```python
# User query
"Show me revenue trends from 2013 to 2016"

# Output
📈 Revenue Trends:

Year 2013:
   Revenue: $1,125,340.00
   Profit Margin: 40.23%
   Growth: --

Year 2014:
   Revenue: $1,187,920.00
   Profit Margin: 41.15%
   Growth: 5.56%

Year 2015:
   Revenue: $1,245,678.00
   Profit Margin: 42.51%
   Growth: 4.86%

Year 2016:
   Revenue: $1,098,450.00
   Profit Margin: 39.87%
   Growth: -11.82%
```

### Example 3: Top Products Analysis

```python
# User query
"Analyze top products for 2016"

# Output
🏆 Top Products (2016):

1. Mountain-200 Black, 38
   Revenue: $45,678.00
   Profit: $18,234.50

2. Road-150 Red, 62
   Revenue: $42,345.00
   Profit: $16,890.00

3. Mountain-100 Silver, 44
   Revenue: $38,920.00
   Profit: $15,234.00
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. API Key Error (401 Unauthorized)

**Problem:** `API error occurred: Status 401 Unauthorized`

**Solutions:**
- Verify API key is correct in `.env` file
- Regenerate API key at https://console.mistral.ai/
- Check for extra spaces in `.env` file
- Restart application after updating `.env`

```bash
# Test API connection
python test_api.py
```

#### 2. Module Not Found Error

**Problem:** `ModuleNotFoundError: No module named 'agents'`

**Solutions:**
- Ensure you're in the project root directory
- Verify all `__init__.py` files exist in agent folders
- Check Python path: `echo $PYTHONPATH`

```bash
# Create missing __init__.py
touch agents/__init__.py
```

#### 3. Pandas FutureWarning

**Problem:** `FutureWarning: The default of observed=False is deprecated`

**Solution:** Already fixed in code with `observed=True` parameter in groupby operations.

#### 4. Data Loading Errors

**Problem:** `FileNotFoundError` or CSV parsing errors

**Solutions:**
- Verify CSV file path is correct
- Check CSV format matches expected columns
- Ensure date format is DD/MM/YYYY
- Try absolute path instead of relative path

```python
# Use absolute path
data_path = "D:/Akij AI Project/Customer_Segmentation_py.csv"
```

#### 5. Rate Limit (429 Error)

**Problem:** `Status 429: Service tier capacity exceeded`

**Solutions:**
- Wait a few minutes and retry
- System will automatically try different models
- Consider upgrading Mistral API tier
- Use offline mode (see below)

### Debug Mode

Enable verbose logging:

```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Offline Mode (Without API)

If Mistral API is unavailable, the system automatically provides formatted data responses without AI insights.

To force offline mode:
```python
# In .env
MISTRAL_API_KEY=
```

## 🔒 Security Best Practices

1. **Never commit `.env` file** to version control
2. **Regenerate API keys** if accidentally exposed
3. **Use environment variables** for sensitive data
4. **Restrict API key permissions** to minimum required
5. **Regularly rotate API keys**

## 🚀 Advanced Usage

### Programmatic API

```python
from agents.coordinator import CoordinatorAgent

# Initialize
coordinator = CoordinatorAgent(data_path="data/sales.csv")

# Load data
result = coordinator.process({"user_input": "load data"})

# Query
result = coordinator.process({
    "user_input": "What was the profit margin in 2015?"
})

print(result['response'])
```

### Custom Queries

```python
from agents.data_agent import DataAgent

# Direct data access
data_agent = DataAgent("data/sales.csv")
data_agent.load_and_prepare_data("data/sales.csv")

# Custom query
result = data_agent.query_data({
    "query_type": "profit_margin_by_year",
    "year": 2015
})
```

### Batch Processing

```python
queries = [
    "What was the profit margin in 2015?",
    "Show revenue trends",
    "Analyze top products"
]

for query in queries:
    result = coordinator.process({"user_input": query})
    print(f"Q: {query}")
    print(f"A: {result['response']}\n")
```

## 📊 Performance Optimization

### For Large Datasets (>1M rows)

```python
# Use chunking for data loading
df = pd.read_csv('large_file.csv', chunksize=100000)

# Optimize dtypes
df = df.astype({
    'Year': 'int16',
    'Customer_Age': 'int8',
    'Order_Quantity': 'int16'
})

# Use categorical for text columns
df['Product_Category'] = df['Product_Category'].astype('category')
```

### Memory Management

```python
# Clear cache periodically
coordinator.data_agent.df = None
coordinator.conversational_agent.clear_history()

# Use generators for large operations
def process_in_batches(data, batch_size=1000):
    for i in range(0, len(data), batch_size):
        yield data[i:i+batch_size]
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Development Setup

```bash
# Fork and clone
git clone https://github.com/dishaislam/Multi-Agent-Analyst.git
cd Multi-Agent-Analyst

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
python -m pytest tests/

# Commit and push
git commit -m "Add your feature"
git push origin feature/your-feature-name
```

### Contribution Guidelines

1. **Code Style**: Follow PEP 8
2. **Documentation**: Update README for new features
3. **Testing**: Add tests for new functionality
4. **Commits**: Use clear, descriptive commit messages
5. **Pull Requests**: Provide detailed description of changes

### Areas for Contribution

- 🌐 Web dashboard interface
- 📧 Email report generation
- 🗄️ Database connectivity (PostgreSQL, MySQL)
- 📱 Mobile app integration
- 🔮 Advanced ML predictions
- 🌍 Multi-language support
- 📊 Additional visualization types

## 🧪 Testing

Run tests:

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_data_agent.py

# With coverage
python -m pytest --cov=agents tests/
```

## 📈 Roadmap

### Version 2.0 (Planned)

- [ ] Web-based dashboard with Streamlit/Dash
- [ ] Real-time data streaming support
- [ ] Advanced ML models for forecasting
- [ ] Multi-user support with authentication
- [ ] API endpoints (REST/GraphQL)
- [ ] Database backend integration
- [ ] Docker containerization
- [ ] Kubernetes deployment configs

### Version 2.1 (Future)

- [ ] Voice interface integration
- [ ] Mobile apps (iOS/Android)
- [ ] Advanced NLP with custom models
- [ ] Automated report scheduling
- [ ] Integration with BI tools (Tableau, Power BI)


## 👥 Authors & Acknowledgments

**Lead Developer:** Sharmin Islam Disha
- 🎓 Bachelor in Computer Science and Engineering
- 💼 AI Engineer
- 🗺️ RAG Specialist

**Technologies Used:**
- Python 3.8+
- Pandas & NumPy for data processing
- Matplotlib & Seaborn for visualization
- Mistral AI for conversational intelligence
- Multi-agent architecture design patterns

**Special Thanks:**
- Anthropic's Claude for development assistance
- Mistral AI for providing the LLM API
- Open-source community for libraries and tools

## 📞 Support & Contact

- **Issues:** [GitHub Issues](https://github.com/dishaislam/Multi-Agent-Analyst.git/issues)
- **Discussions:** [GitHub Discussions](https://github.com/dishaislam/Multi-Agent-Analyst.git/discussions)
- **Email:** your.email@example.com
- **LinkedIn:** [Your Profile](https://linkedin.com/in/sharmin-islam-disha/)

## 🌟 Star History

If you find this project useful, please consider giving it a star ⭐ on GitHub!

[![Star History Chart](https://api.star-history.com/svg?repos=dishaislam/Multi-Agent-Analyst&type=Date)](https://star-history.com/#dishaislam/Multi-Agent-Analyst&Date)

## 📚 Additional Resources

- [Mistral AI Documentation](https://docs.mistral.ai/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Business Intelligence Best Practices](https://www.tableau.com/learn/articles/business-intelligence)

---

*Last Updated: November 2024*