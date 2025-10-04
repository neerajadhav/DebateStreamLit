import streamlit as st
import google.generativeai as genai
from datetime import datetime
import json
import time
import os
import glob
import re
import pandas as pd

# Configure Gemini API
def configure_gemini():
    api_key = st.sidebar.text_input("Enter your Gemini API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

class DebateHost:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        
    def generate_opening_statement(self, topic):
        prompt = f"""
        You are an AI debate host. Generate a professional opening statement for a debate on the topic: "{topic}"
        
        Your opening should:
        1. Welcome participants
        2. Clearly state the debate topic
        3. Explain the format (alternating arguments, AI analysis after each round)
        4. Set ground rules for respectful discourse
        5. Encourage both parties to present their strongest arguments
        
        Keep it concise but authoritative.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating opening statement: {str(e)}"
    
    def analyze_arguments(self, party1_name, party1_argument, party2_name, party2_argument, round_number, topic):
        prompt = f"""
        You are an impartial AI debate analyst. Analyze the following debate round objectively:

        Topic: {topic}
        Round: {round_number}
        
        {party1_name}'s Argument:
        {party1_argument}
        
        {party2_name}'s Argument:
        {party2_argument}
        
        Provide an unbiased analysis covering:
        
        1. SCORING (Rate each party on these criteria from 0-10):
           - Argument Strength: Logic, reasoning, and validity of claims
           - Evidence Quality: Use of facts, data, examples, and sources
           - Rebuttal Effectiveness: Addressing opponent's points
           - Clarity & Delivery: Communication quality and structure
           
           Format your scores EXACTLY like this at the START of your response:
           SCORES:
           {party1_name}: Argument=X, Evidence=X, Rebuttal=X, Clarity=X
           {party2_name}: Argument=X, Evidence=X, Rebuttal=X, Clarity=X
           
        2. DETAILED ANALYSIS (for each party):
           - Strengths in this round
           - Weaknesses or areas to improve
           - Key points made
           
        3. ROUND ASSESSMENT:
           - Which argument was stronger this round and why
           - Critical moments or turning points
           - Impact on overall debate trajectory
        
        Be fair, constructive, and specific in your feedback.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error analyzing arguments: {str(e)}"
    
    def generate_final_verdict(self, debate_history, topic, party1_total_score, party2_total_score):
        prompt = f"""
        You are an impartial AI judge concluding a debate on: "{topic}"
        
        Here is the complete debate history:
        {json.dumps(debate_history, indent=2)}
        
        FINAL SCORES:
        Party 1 Total: {party1_total_score} points
        Party 2 Total: {party2_total_score} points
        
        Provide a comprehensive final verdict that includes:
        
        1. OVERALL PERFORMANCE SUMMARY:
           - Strengths and weaknesses of each debater
           - Quality of arguments throughout the debate
           - Score breakdown analysis
           
        2. KEY MOMENTS:
           - Most compelling arguments from each side
           - Critical turning points in the debate
           - Best rounds for each debater
           
        3. FINAL JUDGMENT:
           - Which side presented the stronger overall case
           - Reasoning for your decision based on scores and performance
           - Margin of victory assessment
           
        4. CONSTRUCTIVE FEEDBACK:
           - Areas for improvement for both parties
           - Positive highlights from the debate
           - Lessons learned
        
        Be thorough, fair, and provide educational value in your analysis.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating final verdict: {str(e)}"

def initialize_session_state():
    if 'debate_started' not in st.session_state:
        st.session_state.debate_started = False
    if 'current_round' not in st.session_state:
        st.session_state.current_round = 1
    if 'debate_history' not in st.session_state:
        st.session_state.debate_history = []
    if 'opening_statement' not in st.session_state:
        st.session_state.opening_statement = ""
    if 'debate_topic' not in st.session_state:
        st.session_state.debate_topic = ""
    if 'party1_name' not in st.session_state:
        st.session_state.party1_name = ""
    if 'party2_name' not in st.session_state:
        st.session_state.party2_name = ""
    if 'max_rounds' not in st.session_state:
        st.session_state.max_rounds = 3
    if 'debate_finished' not in st.session_state:
        st.session_state.debate_finished = False
    # Scoring system
    if 'party1_total_score' not in st.session_state:
        st.session_state.party1_total_score = 0
    if 'party2_total_score' not in st.session_state:
        st.session_state.party2_total_score = 0
    if 'party1_round_scores' not in st.session_state:
        st.session_state.party1_round_scores = []
    if 'party2_round_scores' not in st.session_state:
        st.session_state.party2_round_scores = []

def parse_scores_from_analysis(analysis_text, party1_name, party2_name):
    """Extract scores from AI analysis text"""
    
    scores = {
        'party1': {'argument': 0, 'evidence': 0, 'rebuttal': 0, 'clarity': 0, 'total': 0},
        'party2': {'argument': 0, 'evidence': 0, 'rebuttal': 0, 'clarity': 0, 'total': 0}
    }
    
    try:
        # Look for SCORES: section
        if "SCORES:" in analysis_text:
            scores_section = analysis_text.split("SCORES:")[1].split("\n\n")[0]
            
            # Parse party1 scores
            party1_pattern = rf"{re.escape(party1_name)}[:\s]+Argument[=\s]+(\d+).*?Evidence[=\s]+(\d+).*?Rebuttal[=\s]+(\d+).*?Clarity[=\s]+(\d+)"
            party1_match = re.search(party1_pattern, scores_section, re.IGNORECASE | re.DOTALL)
            
            if party1_match:
                scores['party1']['argument'] = int(party1_match.group(1))
                scores['party1']['evidence'] = int(party1_match.group(2))
                scores['party1']['rebuttal'] = int(party1_match.group(3))
                scores['party1']['clarity'] = int(party1_match.group(4))
                scores['party1']['total'] = sum([
                    scores['party1']['argument'],
                    scores['party1']['evidence'],
                    scores['party1']['rebuttal'],
                    scores['party1']['clarity']
                ])
            
            # Parse party2 scores
            party2_pattern = rf"{re.escape(party2_name)}[:\s]+Argument[=\s]+(\d+).*?Evidence[=\s]+(\d+).*?Rebuttal[=\s]+(\d+).*?Clarity[=\s]+(\d+)"
            party2_match = re.search(party2_pattern, scores_section, re.IGNORECASE | re.DOTALL)
            
            if party2_match:
                scores['party2']['argument'] = int(party2_match.group(1))
                scores['party2']['evidence'] = int(party2_match.group(2))
                scores['party2']['rebuttal'] = int(party2_match.group(3))
                scores['party2']['clarity'] = int(party2_match.group(4))
                scores['party2']['total'] = sum([
                    scores['party2']['argument'],
                    scores['party2']['evidence'],
                    scores['party2']['rebuttal'],
                    scores['party2']['clarity']
                ])
    except Exception as e:
        st.warning(f"Could not parse scores automatically. Using default values. Error: {str(e)}")
    
    return scores

def main():
    st.set_page_config(
        page_title="AI Debate Platform",
        page_icon="🎭",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎭 AI-Powered Debate Platform")
    st.markdown("*Where ideas clash and wisdom emerges*")
    
    initialize_session_state()
    
    # Create navigation tabs
    tab1, tab2 = st.tabs(["🎯 Current Debate", "📚 Records"])
    
    with tab1:
        run_debate_tab()
    
    with tab2:
        run_records_tab()

def run_debate_tab():
    # Sidebar for API configuration and controls
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_configured = configure_gemini()
        
        if not api_configured:
            st.warning("Please enter your Gemini API key to proceed")
            st.info("Get your API key from: https://makersuite.google.com/app/apikey")
            return
        
        st.success("✅ Gemini API configured")
        
        st.header("🎮 Debate Controls")
        if st.button("🔄 Reset Debate"):
            for key in list(st.session_state.keys()):
                if key.startswith('debate') or key in ['current_round', 'max_rounds', 'opening_statement', 'party1_name', 'party2_name']:
                    del st.session_state[key]
            st.rerun()
    
    # Main application
    if not st.session_state.debate_started:
        setup_debate()
    else:
        run_debate()

def run_records_tab():
    st.header("📚 Debate Records")
    
    # Ensure records directory exists
    records_dir = "records"
    if not os.path.exists(records_dir):
        os.makedirs(records_dir)
    
    # Get all JSON files in records directory
    json_files = glob.glob(os.path.join(records_dir, "*.json"))
    json_files.sort(reverse=True)  # Most recent first
    
    if not json_files:
        st.info("No debate records found. Complete a debate to see records here!")
        return
    
    st.subheader(f"Found {len(json_files)} debate record(s)")
    
    # Display records
    for file_path in json_files:
        try:
            with open(file_path, 'r') as f:
                debate_data = json.load(f)
            
            filename = os.path.basename(file_path)
            
            with st.expander(f"📋 {debate_data.get('topic', 'Unknown Topic')} - {filename}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Topic:** {debate_data.get('topic', 'N/A')}")
                    st.write(f"**Participants:** {', '.join(debate_data.get('participants', []))}")
                    st.write(f"**Rounds:** {debate_data.get('rounds', 'N/A')}")
                    
                    # Display final scores if available
                    if 'final_scores' in debate_data:
                        st.write("**Final Scores:**")
                        for participant, score in debate_data['final_scores'].items():
                            st.write(f"  • {participant}: {score} points")
                    
                    # Format timestamp if available
                    if 'timestamp' in debate_data:
                        try:
                            dt = datetime.fromisoformat(debate_data['timestamp'])
                            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                            st.write(f"**Date:** {formatted_time}")
                        except:
                            st.write(f"**Date:** {debate_data['timestamp']}")
                
                with col2:
                    # Download button for individual record
                    st.download_button(
                        label="💾 Download JSON",
                        data=json.dumps(debate_data, indent=2),
                        file_name=filename,
                        mime="application/json",
                        key=f"download_{filename}"
                    )
                
                # Show debate history
                if 'history' in debate_data and debate_data['history']:
                    st.subheader("🗣️ Debate Rounds")
                    for round_data in debate_data['history']:
                        round_num = round_data.get('round', 'Unknown')
                        with st.expander(f"Round {round_num}", expanded=False):
                            # Display scores if available
                            if 'scores' in round_data:
                                score_col1, score_col2 = st.columns(2)
                                with score_col1:
                                    party1_scores = round_data['scores']['party1']
                                    st.markdown(f"**{round_data.get('party1_name', 'Party 1')} - Score: {party1_scores['total']}/40**")
                                    st.caption(f"Arg: {party1_scores['argument']} | Ev: {party1_scores['evidence']} | Reb: {party1_scores['rebuttal']} | Cl: {party1_scores['clarity']}")
                                
                                with score_col2:
                                    party2_scores = round_data['scores']['party2']
                                    st.markdown(f"**{round_data.get('party2_name', 'Party 2')} - Score: {party2_scores['total']}/40**")
                                    st.caption(f"Arg: {party2_scores['argument']} | Ev: {party2_scores['evidence']} | Reb: {party2_scores['rebuttal']} | Cl: {party2_scores['clarity']}")
                                
                                st.divider()
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**{round_data.get('party1_name', 'Party 1')}:**")
                                st.write(round_data.get('party1_argument', 'No argument recorded'))
                            with col2:
                                st.markdown(f"**{round_data.get('party2_name', 'Party 2')}:**")
                                st.write(round_data.get('party2_argument', 'No argument recorded'))
                            
                            if 'analysis' in round_data:
                                st.markdown("**🤖 AI Analysis:**")
                                st.write(round_data['analysis'])
                
                # Show final verdict
                if 'final_verdict' in debate_data:
                    with st.expander("🏆 Final Verdict", expanded=False):
                        st.write(debate_data['final_verdict'])
                
                st.divider()
        
        except Exception as e:
            st.error(f"Error loading {filename}: {str(e)}")

def save_debate_to_records(debate_data):
    """Save debate data to records directory as JSON file"""
    try:
        # Ensure records directory exists
        records_dir = "records"
        if not os.path.exists(records_dir):
            os.makedirs(records_dir)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"debate_{timestamp}.json"
        filepath = os.path.join(records_dir, filename)
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(debate_data, f, indent=2)
        
        return filepath
    except Exception as e:
        st.error(f"Error saving debate record: {str(e)}")
        return None

def setup_debate():
    st.header("🚀 Setup New Debate")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Participants")
        party1_name = st.text_input("Party 1 Name", placeholder="e.g., Team Alpha")
        party2_name = st.text_input("Party 2 Name", placeholder="e.g., Team Beta")
    
    with col2:
        st.subheader("📋 Debate Settings")
        debate_topic = st.text_input("Debate Topic", placeholder="e.g., Should AI replace human teachers?")
        max_rounds = st.selectbox("Number of Rounds", [3, 5, 7], index=0)
    
    st.subheader("📝 Instructions")
    st.info("""
    **How it works:**
    1. Enter participant names and debate topic
    2. AI host will provide opening statement
    3. Parties alternate presenting arguments
    4. AI analyzes each round objectively
    5. Final verdict after all rounds complete
    """)
    
    if st.button("🎯 Start Debate", type="primary"):
        if party1_name and party2_name and debate_topic:
            st.session_state.party1_name = party1_name
            st.session_state.party2_name = party2_name
            st.session_state.debate_topic = debate_topic
            st.session_state.max_rounds = max_rounds
            st.session_state.debate_started = True
            
            # Generate opening statement
            host = DebateHost()
            with st.spinner("AI Host preparing opening statement..."):
                opening = host.generate_opening_statement(debate_topic)
                st.session_state.opening_statement = opening
            
            st.rerun()
        else:
            st.error("Please fill in all fields before starting the debate!")

def run_debate():
    host = DebateHost()
    
    # Display opening statement
    if st.session_state.opening_statement:
        st.header("🎤 AI Host Opening Statement")
        st.info(st.session_state.opening_statement)
        st.divider()
    
    # Display current debate info and scores
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Topic", st.session_state.debate_topic)
    with col2:
        st.metric("Current Round", f"{st.session_state.current_round}/{st.session_state.max_rounds}")
    with col3:
        progress = st.session_state.current_round / st.session_state.max_rounds
        st.metric("Progress", f"{progress:.0%}")
    
    # Display live scoreboard
    st.header("📊 Live Scoreboard")
    score_col1, score_col2, score_col3 = st.columns([2, 2, 1])
    
    with score_col1:
        st.subheader(f"🔵 {st.session_state.party1_name}")
        st.metric("Total Score", f"{st.session_state.party1_total_score} pts", 
                  delta=st.session_state.party1_round_scores[-1]['total'] if st.session_state.party1_round_scores else None)
        
        if st.session_state.party1_round_scores:
            latest = st.session_state.party1_round_scores[-1]
            cols = st.columns(4)
            cols[0].metric("Argument", latest['argument'], delta_color="off")
            cols[1].metric("Evidence", latest['evidence'], delta_color="off")
            cols[2].metric("Rebuttal", latest['rebuttal'], delta_color="off")
            cols[3].metric("Clarity", latest['clarity'], delta_color="off")
    
    with score_col2:
        st.subheader(f"🔴 {st.session_state.party2_name}")
        st.metric("Total Score", f"{st.session_state.party2_total_score} pts",
                  delta=st.session_state.party2_round_scores[-1]['total'] if st.session_state.party2_round_scores else None)
        
        if st.session_state.party2_round_scores:
            latest = st.session_state.party2_round_scores[-1]
            cols = st.columns(4)
            cols[0].metric("Argument", latest['argument'], delta_color="off")
            cols[1].metric("Evidence", latest['evidence'], delta_color="off")
            cols[2].metric("Rebuttal", latest['rebuttal'], delta_color="off")
            cols[3].metric("Clarity", latest['clarity'], delta_color="off")
    
    with score_col3:
        st.subheader("Lead")
        score_diff = st.session_state.party1_total_score - st.session_state.party2_total_score
        if score_diff > 0:
            st.success(f"🔵 +{score_diff}")
        elif score_diff < 0:
            st.error(f"🔴 +{abs(score_diff)}")
        else:
            st.info("Tied")
    
    # Score progression chart
    if len(st.session_state.party1_round_scores) > 0:
        st.subheader("📈 Score Progression")
        
        rounds = list(range(1, len(st.session_state.party1_round_scores) + 1))
        party1_cumulative = []
        party2_cumulative = []
        
        cumulative1 = 0
        cumulative2 = 0
        for i in range(len(st.session_state.party1_round_scores)):
            cumulative1 += st.session_state.party1_round_scores[i]['total']
            cumulative2 += st.session_state.party2_round_scores[i]['total']
            party1_cumulative.append(cumulative1)
            party2_cumulative.append(cumulative2)
        
        chart_data = pd.DataFrame({
            'Round': rounds,
            st.session_state.party1_name: party1_cumulative,
            st.session_state.party2_name: party2_cumulative
        })
        
        st.line_chart(chart_data.set_index('Round'))
    
    st.divider()
    
    # Show debate history
    if st.session_state.debate_history:
        st.header("📚 Debate History")
        for i, round_data in enumerate(st.session_state.debate_history, 1):
            with st.expander(f"Round {i} - Analysis & Scores", expanded=(i == len(st.session_state.debate_history))):
                # Show scores for this round
                if 'scores' in round_data:
                    score_col1, score_col2 = st.columns(2)
                    with score_col1:
                        st.markdown(f"**🔵 {round_data['party1_name']} - Round Score: {round_data['scores']['party1']['total']}/40**")
                        score_details = f"Argument: {round_data['scores']['party1']['argument']}/10 | "
                        score_details += f"Evidence: {round_data['scores']['party1']['evidence']}/10 | "
                        score_details += f"Rebuttal: {round_data['scores']['party1']['rebuttal']}/10 | "
                        score_details += f"Clarity: {round_data['scores']['party1']['clarity']}/10"
                        st.caption(score_details)
                    
                    with score_col2:
                        st.markdown(f"**🔴 {round_data['party2_name']} - Round Score: {round_data['scores']['party2']['total']}/40**")
                        score_details = f"Argument: {round_data['scores']['party2']['argument']}/10 | "
                        score_details += f"Evidence: {round_data['scores']['party2']['evidence']}/10 | "
                        score_details += f"Rebuttal: {round_data['scores']['party2']['rebuttal']}/10 | "
                        score_details += f"Clarity: {round_data['scores']['party2']['clarity']}/10"
                        st.caption(score_details)
                    
                    st.divider()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**{round_data['party1_name']}:**")
                    st.write(round_data['party1_argument'])
                with col2:
                    st.markdown(f"**{round_data['party2_name']}:**")
                    st.write(round_data['party2_argument'])
                
                st.markdown("**🤖 AI Analysis:**")
                st.write(round_data['analysis'])
        st.divider()
    
    # Current round input (if debate not finished)
    if not st.session_state.debate_finished:
        st.header(f"⚔️ Round {st.session_state.current_round}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"🗣️ {st.session_state.party1_name}")
            party1_argument = st.text_area(
                f"{st.session_state.party1_name}'s Argument",
                height=150,
                placeholder="Present your argument here..."
            )
        
        with col2:
            st.subheader(f"🗣️ {st.session_state.party2_name}")
            party2_argument = st.text_area(
                f"{st.session_state.party2_name}'s Argument",
                height=150,
                placeholder="Present your argument here..."
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Analyze This Round", type="primary"):
                if party1_argument.strip() and party2_argument.strip():
                    with st.spinner("AI analyzing arguments..."):
                        analysis = host.analyze_arguments(
                            st.session_state.party1_name,
                            party1_argument,
                            st.session_state.party2_name,
                            party2_argument,
                            st.session_state.current_round,
                            st.session_state.debate_topic
                        )
                        
                        # Parse scores from analysis
                        scores = parse_scores_from_analysis(
                            analysis,
                            st.session_state.party1_name,
                            st.session_state.party2_name
                        )
                        
                        # Update scores
                        st.session_state.party1_round_scores.append(scores['party1'])
                        st.session_state.party2_round_scores.append(scores['party2'])
                        st.session_state.party1_total_score += scores['party1']['total']
                        st.session_state.party2_total_score += scores['party2']['total']
                        
                        # Store round data
                        round_data = {
                            'round': st.session_state.current_round,
                            'party1_name': st.session_state.party1_name,
                            'party1_argument': party1_argument,
                            'party2_name': st.session_state.party2_name,
                            'party2_argument': party2_argument,
                            'analysis': analysis,
                            'scores': scores,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        st.session_state.debate_history.append(round_data)
                        
                        # Check if this was the last round
                        if st.session_state.current_round >= st.session_state.max_rounds:
                            st.session_state.debate_finished = True
                        else:
                            st.session_state.current_round += 1
                        
                        st.rerun()
                else:
                    st.error("Both parties must provide arguments before analysis!")
        
        with col2:
            if st.session_state.current_round > 1:
                if st.button("🏁 End Debate Early"):
                    st.session_state.debate_finished = True
                    st.rerun()
    
    # Final verdict (if debate finished)
    if st.session_state.debate_finished:
        st.header("🏆 Final Verdict")
        
        # Display final scores prominently
        st.subheader("🎯 Final Scores")
        final_col1, final_col2, final_col3 = st.columns([2, 2, 1])
        
        with final_col1:
            st.metric(f"🔵 {st.session_state.party1_name}", 
                     f"{st.session_state.party1_total_score} points",
                     delta=None)
        
        with final_col2:
            st.metric(f"� {st.session_state.party2_name}", 
                     f"{st.session_state.party2_total_score} points",
                     delta=None)
        
        with final_col3:
            score_diff = abs(st.session_state.party1_total_score - st.session_state.party2_total_score)
            if st.session_state.party1_total_score > st.session_state.party2_total_score:
                st.success(f"🔵 Wins\nby {score_diff}")
            elif st.session_state.party2_total_score > st.session_state.party1_total_score:
                st.error(f"🔴 Wins\nby {score_diff}")
            else:
                st.info("Tie!")
        
        st.divider()
        
        if st.button("�📋 Generate Final Analysis", type="primary"):
            with st.spinner("AI Judge preparing final verdict..."):
                final_verdict = host.generate_final_verdict(
                    st.session_state.debate_history,
                    st.session_state.debate_topic,
                    st.session_state.party1_total_score,
                    st.session_state.party2_total_score
                )
                
                st.success("**🎯 Final Analysis Complete!**")
                st.write(final_verdict)
                
                # Prepare debate export data
                debate_export = {
                    'topic': st.session_state.debate_topic,
                    'participants': [st.session_state.party1_name, st.session_state.party2_name],
                    'rounds': len(st.session_state.debate_history),
                    'final_scores': {
                        st.session_state.party1_name: st.session_state.party1_total_score,
                        st.session_state.party2_name: st.session_state.party2_total_score
                    },
                    'round_scores': {
                        st.session_state.party1_name: st.session_state.party1_round_scores,
                        st.session_state.party2_name: st.session_state.party2_round_scores
                    },
                    'history': st.session_state.debate_history,
                    'final_verdict': final_verdict,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Automatically save to records directory
                saved_path = save_debate_to_records(debate_export)
                if saved_path:
                    st.success(f"✅ Debate automatically saved to: `{saved_path}`")
                    st.info("💡 You can view this and other saved debates in the **Records** tab!")
                
                # Option to download debate
                st.subheader("📄 Export Options")
                st.download_button(
                    label="💾 Download Debate Summary",
                    data=json.dumps(debate_export, indent=2),
                    file_name=f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

if __name__ == "__main__":
    main()
