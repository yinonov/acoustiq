"""
AI Agent for Acoustic Analysis
Handles intelligent pattern recognition and natural language queries about audio data.
"""

import os
from typing import List, Dict, Any, Optional
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from openai import AsyncOpenAI


class AcousticAgent:
    """AI Agent specialized for acoustic measurement analysis."""
    
    def __init__(self, github_token: Optional[str] = None):
        """Initialize the acoustic analysis agent.
        
        Args:
            github_token: GitHub Personal Access Token for model access
        """
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            raise ValueError("GitHub token required. Set GITHUB_TOKEN environment variable.")
        
        self.client = None
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the AI agent with acoustic analysis capabilities."""
        openai_client = AsyncOpenAI(
            base_url="https://models.github.ai/inference",
            api_key=self.github_token,
        )
        
        chat_client = OpenAIChatClient(
            async_client=openai_client,
            model_id="microsoft/phi-4-mini-instruct"  # Efficient model for analysis
        )
        
        # Define tools for acoustic analysis
        tools = [
            self._analyze_frequency_spectrum,
            self._detect_anomalies,
            self._find_patterns,
            self._generate_summary
        ]
        
        self.agent = ChatAgent(
            chat_client=chat_client,
            name="AcousticAnalysisAgent",
            instructions="""You are an expert acoustic measurement engineer assistant.
            You help analyze audio data, identify patterns, detect anomalies, and provide insights.
            
            Your capabilities include:
            - Analyzing frequency spectra and spectrograms
            - Detecting acoustic anomalies and irregularities
            - Finding specific patterns in audio signals
            - Generating detailed analysis summaries
            - Answering technical questions about acoustic measurements
            
            Always provide clear, technical explanations suitable for engineers.
            When suggesting actions, focus on practical measurement and analysis steps.""",
            tools=tools
        )
    
    def _analyze_frequency_spectrum(self, audio_features: Dict[str, Any]) -> str:
        """Analyze frequency spectrum characteristics."""
        # This would integrate with speckit for actual analysis
        return f"Analyzed frequency spectrum: {audio_features.get('frequency_range', 'unknown')} Hz"
    
    def _detect_anomalies(self, audio_features: Dict[str, Any]) -> str:
        """Detect anomalies in audio signal."""
        # This would use speckit + ML for anomaly detection
        return f"Anomaly detection completed. Found {audio_features.get('anomaly_count', 0)} potential issues."
    
    def _find_patterns(self, pattern_query: str, audio_features: Dict[str, Any]) -> str:
        """Find specific patterns in audio data."""
        # This would search for specific acoustic patterns
        return f"Pattern search for '{pattern_query}' completed."
    
    def _generate_summary(self, analysis_results: Dict[str, Any]) -> str:
        """Generate analysis summary report."""
        # This would create comprehensive reports
        return f"Generated analysis summary with {len(analysis_results)} key findings."
    
    async def analyze_audio_features(self, features: Dict[str, Any]) -> str:
        """Analyze extracted audio features and provide insights.
        
        Args:
            features: Dictionary containing extracted audio features
            
        Returns:
            Analysis results and insights
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized")
        
        thread = self.agent.get_new_thread()
        
        query = f"""
        Please analyze these audio features and provide insights:
        
        Features: {features}
        
        Focus on:
        1. Frequency characteristics
        2. Any anomalies or irregularities
        3. Acoustic measurement implications
        4. Recommendations for further analysis
        """
        
        result = await self.agent.run(query, thread=thread)
        return result.text
    
    async def answer_question(self, question: str, context: Dict[str, Any] = None) -> str:
        """Answer questions about audio analysis.
        
        Args:
            question: Natural language question about the audio
            context: Optional context from previous analysis
            
        Returns:
            Answer to the question
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized")
        
        thread = self.agent.get_new_thread()
        
        if context:
            query = f"""
            Context from previous analysis: {context}
            
            Question: {question}
            
            Please provide a detailed technical answer based on the acoustic analysis context.
            """
        else:
            query = f"""
            Question about acoustic analysis: {question}
            
            Please provide a detailed technical answer suitable for acoustic measurement engineers.
            """
        
        result = await self.agent.run(query, thread=thread)
        return result.text
    
    async def suggest_analysis_approach(self, audio_info: Dict[str, Any]) -> str:
        """Suggest analysis approach for given audio characteristics.
        
        Args:
            audio_info: Information about the audio file
            
        Returns:
            Suggested analysis approach
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized")
        
        thread = self.agent.get_new_thread()
        
        query = f"""
        Audio file information: {audio_info}
        
        As an acoustic measurement expert, suggest the best analysis approach including:
        1. Which measurements to prioritize
        2. Potential challenges or considerations
        3. Expected outcomes and insights
        4. Tools or methods to use
        """
        
        result = await self.agent.run(query, thread=thread)
        return result.text