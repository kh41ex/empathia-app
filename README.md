# EMPATHIA - Pet Loss Support Companion

A compassionate AI companion that provides evidence-based psychological support and empathetic peer-like responses for those grieving the loss of a pet.

## Project Structure
empathia-project/
├── data/ # Data storage (raw, processed, outputs)
├── notebooks/ # Jupyter notebooks for exploration
├── src/ # Source code package
│ ├── core/ # Main application components
│ ├── data_processing/ # Data preparation scripts
│ └── training/ # Model training scripts
├── app.py # Main Streamlit application
└── requirements.txt # Project dependencies


## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Add your API keys to `.env` file:
OPENAI_API_KEY=your_key_here
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
4. Add psychology PDFs to `data/raw/psychology_books/`

## Usage

1. Build knowledge base: `python src/data_processing/build_knowledge_base.py`
2. Run the app: `streamlit run app.py`