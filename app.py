import streamlit as st
import google.generativeai as genai
from datetime import datetime
import json
import time
import os
import glob

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
        
        1. ARGUMENT STRENGTH (for each party):
           - Logic and reasoning quality
           - Evidence and support provided
           - Clarity of communication
           
        2. DEBATE TECHNIQUE (for each party):
           - Addressing opponent's points
           - Use of persuasive elements
           - Structure and flow
           
        3. ROUND ASSESSMENT:
           - Which argument was stronger this round and why
           - Key points that stood out
           - Areas for improvement for each party
           
        4. CURRENT STANDING:
           - Brief assessment of overall debate progress
           - No final winner declaration (debate continues)
        
        Be fair, constructive, and specific in your feedback.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error analyzing arguments: {str(e)}"
    
    def generate_final_verdict(self, debate_history, topic):
        prompt = f"""
        You are an impartial AI judge concluding a debate on: "{topic}"
        
        Here is the complete debate history:
        {json.dumps(debate_history, indent=2)}
        
        Provide a comprehensive final verdict that includes:
        
        1. OVERALL PERFORMANCE SUMMARY:
           - Strengths and weaknesses of each debater
           - Quality of arguments throughout the debate
           
        2. KEY MOMENTS:
           - Most compelling arguments from each side
           - Critical turning points in the debate
           
        3. FINAL JUDGMENT:
           - Which side presented the stronger overall case
           - Reasoning for your decision
           - Final score or assessment
           
        4. CONSTRUCTIVE FEEDBACK:
           - Areas for improvement for both parties
           - Positive highlights from the debate
        
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
    
    # Display current debate info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Topic", st.session_state.debate_topic)
    with col2:
        st.metric("Current Round", f"{st.session_state.current_round}/{st.session_state.max_rounds}")
    with col3:
        progress = st.session_state.current_round / st.session_state.max_rounds
        st.metric("Progress", f"{progress:.0%}")
    
    # Show debate history
    if st.session_state.debate_history:
        st.header("📚 Debate History")
        for i, round_data in enumerate(st.session_state.debate_history, 1):
            with st.expander(f"Round {i} - Analysis", expanded=(i == len(st.session_state.debate_history))):
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
                        
                        # Store round data
                        round_data = {
                            'round': st.session_state.current_round,
                            'party1_name': st.session_state.party1_name,
                            'party1_argument': party1_argument,
                            'party2_name': st.session_state.party2_name,
                            'party2_argument': party2_argument,
                            'analysis': analysis,
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
        
        if st.button("📋 Generate Final Analysis", type="primary"):
            with st.spinner("AI Judge preparing final verdict..."):
                final_verdict = host.generate_final_verdict(
                    st.session_state.debate_history,
                    st.session_state.debate_topic
                )
                
                st.success("**🎯 Final Analysis Complete!**")
                st.write(final_verdict)
                
                # Prepare debate export data
                debate_export = {
                    'topic': st.session_state.debate_topic,
                    'participants': [st.session_state.party1_name, st.session_state.party2_name],
                    'rounds': len(st.session_state.debate_history),
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
