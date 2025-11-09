import streamlit as st
import pandas as pd
import os
from pathlib import Path
import time
from agents import CoordinatorAgent
from PIL import Image
import glob

# Page configuration
st.set_page_config(
    page_title="Business Analytics AI Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #1f77b4;
        color: white;
    }
    .stButton>button:hover {
        background-color: #145a8a;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 5px solid #1f77b4;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 5px solid #4caf50;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'coordinator' not in st.session_state:
    st.session_state.coordinator = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'temp_file_path' not in st.session_state:
    st.session_state.temp_file_path = None
if 'data_summary' not in st.session_state:
    st.session_state.data_summary = None

# Create outputs directory
OUTPUT_DIR = "outputs"
TEMP_DIR = "temp_uploads"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)


def initialize_coordinator(file_path: str):
    """Initialize the coordinator agent with uploaded file and load data."""
    try:
        coordinator = CoordinatorAgent(data_path=file_path)
        result = coordinator.process({"user_input": "load data"})

        # Ensure we always have a dict
        if not isinstance(result, dict):
            result = {
                "success": False,
                "error": f"Coordinator returned non-dict result: {result}"
            }

        # If it failed but didn't provide an error, synthesize one
        if not result.get("success") and "error" not in result:
            result["error"] = (
                "Coordinator reported failure without error details. "
                f"Raw result: {result}"
            )

        return coordinator, result

    except Exception as e:
        # Surface the full error back to Streamlit
        return None, {
            "success": False,
            "error": f"initialize_coordinator crashed: {e}"
        }


def display_metrics(summary):
    """Display key metrics in cards"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="📅 Total Records",
            value=f"{summary.get('total_records', 0):,}"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="💰 Total Revenue",
            value=f"${summary.get('total_revenue', 0):,.2f}"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="📈 Total Profit",
            value=f"${summary.get('total_profit', 0):,.2f}"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="👥 Unique Customers",
            value=f"{summary.get('unique_customers', 0):,}"
        )
        st.markdown('</div>', unsafe_allow_html=True)


def display_images_grid(image_paths):
    """Display images in a grid layout"""
    if not image_paths:
        st.info("No visualizations generated yet.")
        return

    # Filter existing images
    existing_images = [img for img in image_paths if os.path.exists(img)]

    if not existing_images:
        st.warning("No visualization files found.")
        return

    # Display images in 2 columns
    cols_per_row = 2
    for i in range(0, len(existing_images), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(existing_images):
                with col:
                    try:
                        img = Image.open(existing_images[idx])
                        st.image(
                            img,
                            use_container_width=True,
                            caption=Path(existing_images[idx]).stem
                        )
                    except Exception:
                        st.error(f"Error loading image: {existing_images[idx]}")


def display_chat_message(role, message):
    """Display a chat message with styling"""
    if role == "user":
        st.markdown(f"""
            <div class="chat-message user-message">
                <b>👤 You:</b><br/>
                {message}
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="chat-message assistant-message">
                <b>🤖 Assistant:</b><br/>
                {message}
            </div>
        """, unsafe_allow_html=True)


# Main App
def main():
    # Header
    st.markdown(
        '<p class="main-header">📊 Business Analytics AI Assistant</p>',
        unsafe_allow_html=True
    )

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # API Key check
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            st.error("⚠️ MISTRAL_API_KEY not found in environment variables!")
            st.info(
                "Locally: set it in a .env file.\n\n"
                "On Hugging Face: set it in Settings → Variables and secrets."
            )
        else:
            st.success("✅ API Key Configured")

        st.divider()

        # Navigation
        st.header("🧭 Navigation")
        page = st.radio(
            "Select Page:",
            ["📤 Upload & Analysis", "💬 Chat Assistant"],
            label_visibility="collapsed"
        )

        st.divider()

        # Data Status
        st.header("📊 Data Status")
        if st.session_state.data_loaded:
            st.success("✅ Data Loaded")
            if st.session_state.data_summary:
                summary = st.session_state.data_summary
                st.write(f"**Records:** {summary.get('total_records', 0):,}")
                st.write(
                    f"**Date Range:** "
                    f"{summary.get('date_range', {}).get('start', 'N/A')} "
                    f"to {summary.get('date_range', {}).get('end', 'N/A')}"
                )
                st.write(
                    f"**Products:** "
                    f"{summary.get('unique_products', 0):,}"
                )
        else:
            st.warning("⚠️ No Data Loaded")

        st.divider()

        # Clear data button
        if st.session_state.data_loaded:
            if st.button("🗑️ Clear Data & Reset"):
                st.session_state.coordinator = None
                st.session_state.chat_history = []
                st.session_state.data_loaded = False
                st.session_state.analysis_complete = False
                st.session_state.data_summary = None
                # Clear output directory
                for file in glob.glob(os.path.join(OUTPUT_DIR, "*")):
                    try:
                        os.remove(file)
                    except Exception:
                        pass
                st.rerun()

    # Page 1: Upload & Analysis
    if page == "📤 Upload & Analysis":
        st.header("📤 Upload Your Data")

        uploaded_file = st.file_uploader(
            "Upload your CSV file for analysis",
            type=['csv'],
            help="Upload a CSV file containing your business data"
        )

        if uploaded_file is not None:
            # Save uploaded file temporarily
            temp_file_path = os.path.join(TEMP_DIR, uploaded_file.name)
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.success(f"✅ File uploaded: {uploaded_file.name}")

            # Show file preview
            with st.expander("📋 Preview Data", expanded=False):
                try:
                    df_preview = pd.read_csv(temp_file_path, nrows=10)
                    st.dataframe(df_preview, use_container_width=True)
                    total_rows = len(pd.read_csv(temp_file_path))
                    st.info(
                        f"Showing first 10 rows of {total_rows:,} total records"
                    )
                except Exception as e:
                    st.error(f"Error previewing file: {str(e)}")

            col1, col2 = st.columns(2)

            # Load & Prepare Data
            with col1:
                if st.button("🚀 Load & Prepare Data", type="primary"):
                    with st.spinner("Loading and preparing data..."):
                        coordinator, result = initialize_coordinator(
                            temp_file_path
                        )

                        # DEBUG: show raw result to understand failures
                        st.write(
                            "🔎 DEBUG - result from initialize_coordinator:",
                            result
                        )

                        if result.get("success"):
                            st.session_state.coordinator = coordinator
                            st.session_state.data_loaded = True
                            st.session_state.temp_file_path = temp_file_path

                            # Get data summary
                            summary_result = (
                                coordinator.data_agent.get_data_summary({})
                            )
                            # handle potential summary errors
                            if (
                                isinstance(summary_result, dict)
                                and not summary_result.get("success", True)
                                and "error" in summary_result
                            ):
                                st.warning(
                                    "⚠️ Data summary reported an issue: "
                                    f"{summary_result['error']}"
                                )

                            st.session_state.data_summary = summary_result

                            st.success("✅ Data loaded successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            error_msg = (
                                result.get("error")
                                or result.get("message")
                                or str(result)
                                or "Unknown error"
                            )
                            st.error(
                                f"❌ Failed to load data: {error_msg}"
                            )

            # Run Full Analysis
            with col2:
                if st.session_state.data_loaded:
                    if st.button("📊 Run Full Analysis", type="primary"):
                        with st.spinner(
                            "Running comprehensive analysis... "
                            "This may take a minute."
                        ):
                            result = st.session_state.coordinator.process({
                                "user_input": "run full analysis"
                            })

                            if result.get("success"):
                                st.session_state.analysis_complete = True
                                st.success("✅ Analysis completed!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                error_msg = (
                                    result.get("error")
                                    or result.get("message")
                                    or str(result)
                                    or "Unknown error"
                                )
                                st.error(
                                    f"❌ Analysis failed: {error_msg}"
                                )

        # Display metrics and visualizations if data is loaded
        if st.session_state.data_loaded and st.session_state.data_summary:
            st.divider()
            st.header("📊 Data Overview")
            display_metrics(st.session_state.data_summary)

            # Additional summary information
            with st.expander("📈 Detailed Summary", expanded=False):
                summary = st.session_state.data_summary
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Date Information")
                    st.write(
                        f"**Start Date:** "
                        f"{summary.get('date_range', {}).get('start', 'N/A')}"
                    )
                    st.write(
                        f"**End Date:** "
                        f"{summary.get('date_range', {}).get('end', 'N/A')}"
                    )
                    st.write(
                        "**Years Available:** "
                        f"{', '.join(map(str, summary.get('years_available', [])))}"
                    )

                with col2:
                    st.subheader("Business Metrics")
                    st.write(
                        f"**Total Revenue:** "
                        f"${summary.get('total_revenue', 0):,.2f}"
                    )
                    st.write(
                        f"**Total Profit:** "
                        f"${summary.get('total_profit', 0):,.2f}"
                    )
                    revenue = summary.get('total_revenue', 0) or 1
                    profit_margin = (
                        summary.get('total_profit', 0) / revenue
                    ) * 100
                    st.write(
                        f"**Overall Profit Margin:** {profit_margin:.2f}%"
                    )

                st.subheader("Geographic Coverage")
                st.write(
                    f"**Countries:** "
                    f"{', '.join(summary.get('countries', []))}"
                )

        # Display visualizations if analysis is complete
        if st.session_state.analysis_complete:
            st.divider()
            st.header("📊 Analysis Visualizations")

            # Get all generated images
            image_files = glob.glob(os.path.join(OUTPUT_DIR, "*.png"))

            if image_files:
                # Sort for stable ordering
                image_files = sorted(image_files)

                # Organize images by type
                revenue_images = [
                    f for f in image_files if 'revenue' in f.lower()
                ]
                profit_images = [
                    f for f in image_files
                    if 'profit' in f.lower() or 'margin' in f.lower()
                ]
                top_product_images = [
                    f for f in image_files if 'top_products' in f.lower()
                ]
                correlation_images = [
                    f for f in image_files if 'correlation' in f.lower()
                ]
                trend_images = [
                    f for f in image_files if 'trend' in f.lower()
                ]
                segmentation_images = [
                    f for f in image_files
                    if 'customer_segmentation' in f.lower()
                    or 'segmentation' in f.lower()
                ]

                if revenue_images:
                    st.subheader("💰 Revenue Analysis")
                    display_images_grid(revenue_images)

                if profit_images:
                    st.subheader("📈 Profit & Margin Analysis")
                    display_images_grid(profit_images)

                if top_product_images:
                    st.subheader("🏆 Top Performing Products")
                    display_images_grid(top_product_images)

                if trend_images:
                    st.subheader("📊 Trends Analysis")
                    display_images_grid(trend_images)

                if correlation_images:
                    st.subheader("🔗 Correlation Analysis")
                    display_images_grid(correlation_images)

                if segmentation_images:
                    st.subheader("👥 Customer Segmentation")
                    display_images_grid(segmentation_images)

                # Download option
                st.divider()
                st.subheader("📥 Download Results")

                csv_files = glob.glob(os.path.join(OUTPUT_DIR, "*.csv"))
                if csv_files:
                    for csv_file in csv_files:
                        with open(csv_file, 'rb') as f:
                            st.download_button(
                                label=f"📄 Download {Path(csv_file).name}",
                                data=f,
                                file_name=Path(csv_file).name,
                                mime="text/csv"
                            )
            else:
                st.info("No visualizations found. Please run the analysis first.")

    # Page 2: Chat Assistant
    elif page == "💬 Chat Assistant":
        st.header("💬 Chat with Your Data")

        if not st.session_state.data_loaded:
            st.warning(
                "⚠️ Please upload and load data first from the 'Upload & Analysis' page."
            )
            st.info("👈 Go to the Upload & Analysis page to get started!")
        else:
            # Display data context
            with st.expander("📊 Current Data Context", expanded=False):
                if st.session_state.data_summary:
                    display_metrics(st.session_state.data_summary)

            st.divider()

            # Chat interface
            st.subheader("Ask questions about your data")

            # Display chat history
            chat_container = st.container()
            with chat_container:
                for chat in st.session_state.chat_history:
                    display_chat_message(chat["role"], chat["message"])

            # Suggested questions
            st.markdown("**💡 Suggested Questions:**")
            suggestions = [
                "What was the profit margin in 2015?",
                "Show me revenue trends over the years",
                "Which products performed best in 2016?",
                "What are the top 5 products by revenue?",
                "Analyze customer behavior patterns"
            ]

            col1, col2, col3 = st.columns(3)
            for idx, suggestion in enumerate(suggestions):
                col = [col1, col2, col3][idx % 3]
                with col:
                    if st.button(suggestion, key=f"suggestion_{idx}"):
                        st.session_state.chat_history.append({
                            "role": "user",
                            "message": suggestion
                        })

                        with st.spinner("Thinking..."):
                            result = st.session_state.coordinator.process({
                                "user_input": suggestion
                            })

                            response = result.get(
                                "response",
                                "I couldn't process that request."
                            )

                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "message": response
                            })

                        st.rerun()

            st.divider()

            # Chat input
            user_input = st.chat_input("Type your question here...")

            if user_input:
                st.session_state.chat_history.append({
                    "role": "user",
                    "message": user_input
                })

                with st.spinner("Processing your request..."):
                    result = st.session_state.coordinator.process({
                        "user_input": user_input
                    })

                    response = result.get(
                        "response",
                        "I couldn't process that request."
                    )

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "message": response
                    })

                st.rerun()

            # Clear chat button
            if st.session_state.chat_history:
                if st.button("🗑️ Clear Chat History"):
                    st.session_state.chat_history = []
                    if st.session_state.coordinator:
                        st.session_state.coordinator.conversational_agent.clear_history()
                    st.rerun()


if __name__ == "__main__":
    main()
