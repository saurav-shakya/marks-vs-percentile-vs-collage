import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from utils import calculate_percentile, suggest_colleges
from ai_utils import setup_gemini, get_study_suggestions, analyze_college_fit, generate_flash_cards, summarize_content, analyze_percentile # Added analyze_percentile import
from web_scraper import get_jee_resources

# Page configuration
st.set_page_config(
    page_title="JEE Main 2025 Analysis",
    page_icon="📚",
    layout="wide"
)

# Setup Gemini API
setup_gemini()

# Load custom CSS
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        jee_data = pd.read_csv('data/jee_data.csv')
        college_data = pd.read_csv('data/college_cutoffs.csv')
        return jee_data, college_data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame()

jee_data, college_data = load_data()

# Header
st.title("JEE Main 2025 Analysis")
st.markdown("### Your Gateway to Engineering Admissions")

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Score Calculator", 
    "AI Study Guide", 
    "Trends Analysis", 
    "College Finder",
    "Learning Resources"
])

with tab1:
    st.header("Score to Percentile Calculator")

    col1, col2 = st.columns(2)

    with col1:
        marks = st.number_input(
            "Enter your JEE Main marks (out of 300)", 
            min_value=0, 
            max_value=300, 
            value=150,
            help="Enter your marks from JEE Main exam (maximum 300)"
        )

        if st.button("Calculate Percentile", use_container_width=True):
            if not jee_data.empty:
                with st.spinner("Calculating percentile using AI analysis..."):
                    ai_analysis = analyze_percentile(marks, jee_data) # Call to AI analysis function
                    percentile = calculate_percentile(marks, jee_data)

                    if percentile is not None:
                        st.success(f"Your estimated percentile: {percentile:.2f}")

                        # Show detailed statistics
                        col1a, col1b = st.columns(2)
                        with col1a:
                            st.metric("Your Score", f"{marks}/300")
                        with col1b:
                            st.metric("Your Percentile", f"{percentile:.2f}")

                        # If AI analysis is available, show additional insights
                        if ai_analysis and 'analysis' in ai_analysis:
                            st.info("📊 **AI Analysis:**")
                            st.markdown(ai_analysis['analysis'])

                            if 'comparative_stats' in ai_analysis:
                                stats = ai_analysis['comparative_stats']
                                st.markdown(f"""
                                🎯 **Comparative Analysis:**
                                - Position: {stats['relative_position']}
                                - {'Above' if stats['above_average'] else 'Below'} average performance
                                """)

                        # Additional context
                        avg_marks = jee_data['marks'].mean()
                        st.info(f"""
                        **Statistics:**
                        - Your Score: {marks}/300
                        - Average Score: {avg_marks:.1f}/300
                        - Your Percentile: {percentile:.2f}
                        """)
                    else:
                        st.error("Error calculating percentile. Please try again.")
            else:
                st.error("Unable to load historical data. Please try again.")

    with col2:
        if not jee_data.empty:
            # Create percentile visualization
            fig = px.scatter(
                jee_data,
                x='marks',
                y='percentile',
                title='Marks vs Percentile Distribution',
                labels={'marks': 'Marks (out of 300)', 'percentile': 'Percentile'}
            )

            # Add your score line
            fig.add_vline(
                x=marks,
                line_dash="dash",
                line_color="red",
                annotation_text="Your Score",
                annotation_position="top"
            )

            # Customize layout
            fig.update_layout(
                title_x=0.5,
                title_y=0.95,
                showlegend=True,
                margin=dict(t=50),
                plot_bgcolor='white'
            )

            # Add grid
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

            st.plotly_chart(fig, use_container_width=True)

            # Add explanation
            st.caption("""
            This graph shows the relationship between marks and percentile based on historical data.
            The red line indicates your current score.
            """)

with tab2:
    st.header("AI-Powered Study Guide")

    if 'last_marks' not in st.session_state:
        st.session_state.last_marks = 0
        st.session_state.last_percentile = 0
        st.session_state.flash_cards = []

    col1, col2 = st.columns([2, 1])

    with col1:
        current_marks = st.number_input(
            "Enter your marks for personalized suggestions",
            min_value=0,
            max_value=300,
            value=st.session_state.last_marks
        )

        current_percentile = calculate_percentile(current_marks, jee_data)

        if st.button("Get Study Suggestions"):
            st.session_state.last_marks = current_marks
            st.session_state.last_percentile = current_percentile

            with st.spinner("Generating personalized study suggestions..."):
                suggestions = get_study_suggestions(current_marks, current_percentile)
                st.markdown(suggestions)

    with col2:
        st.subheader("Flash Cards")
        topics = ["Physics Mechanics", "Chemical Bonding", "Calculus", 
                 "Organic Chemistry", "Vectors", "Thermodynamics"]
        selected_topic = st.selectbox("Select topic for flash cards", topics)

        if st.button("Generate Flash Cards"):
            with st.spinner("Creating flash cards with Gemini 2.0..."):
                st.session_state.flash_cards = generate_flash_cards(selected_topic)

        if st.session_state.flash_cards:
            difficulties = {"basic": "🟢", "intermediate": "🟡", "advanced": "🔴"}

            for i, card in enumerate(st.session_state.flash_cards):
                difficulty_icon = difficulties.get(card.get('difficulty', 'basic').lower(), "🟢")
                with st.expander(f"Card {i+1}: {difficulty_icon} {card['front'][:50]}..."):
                    st.markdown("**Question/Concept:**")
                    st.markdown(card['front'])

                    st.markdown("**Detailed Solution:**")
                    st.markdown(card['back'])

                    st.markdown("**💡 Quick Tips:**")
                    st.markdown(card['tips'])

                    if 'related_topics' in card:
                        st.markdown("**🔗 Related Topics:**")
                        st.markdown(", ".join(card['related_topics']))

with tab3:
    st.header("Historical Trends")

    year_data = jee_data.groupby('year').agg({
        'cutoff_general': 'mean',
        'cutoff_obc': 'mean',
        'cutoff_sc': 'mean',
        'cutoff_st': 'mean'
    }).reset_index()

    fig = go.Figure()
    categories = ['General', 'OBC', 'SC', 'ST']

    for category, col in zip(categories, year_data.columns[1:]):
        fig.add_trace(go.Scatter(
            x=year_data['year'],
            y=year_data[col],
            name=category,
            mode='lines+markers'
        ))

    fig.update_layout(
        title="Category-wise Cutoff Trends",
        xaxis_title="Year",
        yaxis_title="Cutoff Percentile"
    )
    st.plotly_chart(fig)

with tab4:
    st.header("College Recommendation")

    user_percentile = st.slider("Your percentile", 0.0, 100.0, 90.0)
    category = st.selectbox("Select category", 
                          ["General", "OBC", "SC", "ST"])

    recommended_colleges = suggest_colleges(user_percentile, category, college_data)

    if not recommended_colleges.empty:
        st.write("Recommended Colleges:")
        st.dataframe(recommended_colleges)

        if st.button("Get AI Analysis"):
            with st.spinner("Analyzing college options..."):
                analysis = analyze_college_fit(user_percentile, recommended_colleges)
                st.markdown(analysis)
    else:
        st.warning("No colleges found matching your criteria")

with tab5:
    st.header("JEE Learning Resources")

    if 'resources' not in st.session_state:
        with st.spinner("Fetching latest JEE preparation resources..."):
            st.session_state.resources = get_jee_resources()

    resources = st.session_state.resources

    if not resources:
        st.error("Unable to fetch resources. Please try again later.")
    else:
        for i, resource in enumerate(resources):
            st.markdown(f"### 📚 {resource['title']}")

            if f'summary_{i}' not in st.session_state:
                with st.spinner("Generating AI summary..."):
                    summary = summarize_content(
                        resource['content'][:3000], 
                        context="JEE Main preparation material"
                    )
                    st.session_state[f'summary_{i}'] = summary

            st.markdown(st.session_state[f'summary_{i}'])

            if st.button(f"Show full content #{i}"):
                st.markdown(resource['content'])

# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>Note: This is a prediction tool based on historical data. Actual cutoffs may vary.</p>
    <p>Data last updated: 2024</p>
</div>
""", unsafe_allow_html=True)