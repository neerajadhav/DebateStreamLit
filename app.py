import streamlit as st
import google.generativeai as genai
from datetime import datetime
import json
import time

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
                del st.session_state[key]
            st.rerun()
    
    # Main application
    if not st.session_state.debate_started:
        setup_debate()
    else:
        run_debate()

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
                
                # Option to export debate
                st.subheader("📄 Export Debate")
                debate_export = {
                    'topic': st.session_state.debate_topic,
                    'participants': [st.session_state.party1_name, st.session_state.party2_name],
                    'rounds': len(st.session_state.debate_history),
                    'history': st.session_state.debate_history,
                    'final_verdict': final_verdict,
                    'timestamp': datetime.now().isoformat()
                }
                
                st.download_button(
                    label="💾 Download Debate Summary",
                    data=json.dumps(debate_export, indent=2),
                    file_name=f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

if __name__ == "__main__":
    main()
