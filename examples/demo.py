"""
Example usage scenarios and demo script for the AI User Learning System
"""

import sys
import time
import asyncio
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from database import db_manager, UserRepository, InteractionRepository, LearnedFactRepository
from ai.learning_engine import LearningEngine
from models import InteractionType

class AILearningDemo:
    """Demo class showing various usage scenarios"""
    
    def __init__(self):
        self.learning_engine = LearningEngine()
        self.demo_user_id = None
    
    def create_demo_user(self):
        """Create a demo user for the scenarios"""
        print("🚀 Creating demo user...")
        
        with db_manager.get_session() as session:
            user_repo = UserRepository(session)
            
            # Create demo user
            demo_user = user_repo.create_user(
                username="demo_alice",
                email="alice@example.com",
                data_sharing_consent=True,
                learning_enabled=True
            )
            
            # Update profile with some initial info
            profile = demo_user.profile
            profile.preferred_language = "en"
            profile.communication_style = "friendly"
            profile.technical_level = "intermediate"
            profile.interests = ["technology", "learning", "productivity"]
            
            self.demo_user_id = demo_user.id
            print(f"✅ Created demo user: {demo_user.username} (ID: {demo_user.id})")
            return demo_user.id
    
    def scenario_1_learning_preferences(self):
        """Scenario 1: Learning user preferences through conversation"""
        print("\n📚 Scenario 1: Learning User Preferences")
        print("=" * 50)
        
        interactions = [
            "I really love learning about artificial intelligence and machine learning",
            "I prefer detailed explanations when someone is teaching me something new",
            "I'm not a big fan of short, superficial answers",
            "I enjoy working on coding projects in Python and JavaScript",
            "I like to understand the theory behind concepts before jumping into practice"
        ]
        
        print("Simulating user interactions about preferences...")
        self._process_interactions(interactions, InteractionType.PREFERENCE.value)
        
        # Show learned facts
        self._display_learned_facts("preferences")
    
    def scenario_2_communication_style(self):
        """Scenario 2: Learning communication style"""
        print("\n💬 Scenario 2: Learning Communication Style")
        print("=" * 50)
        
        interactions = [
            "Hey there! How's it going?",
            "Thanks so much for your help, I really appreciate it!",
            "Could you please explain that concept in more detail?",
            "That's awesome! I love how you explained that.",
            "I'm super excited to learn more about this topic!",
            "You're amazing at teaching, thank you!"
        ]
        
        print("Simulating casual, friendly communication...")
        self._process_interactions(interactions, InteractionType.MESSAGE.value)
        
        self._display_learned_facts("communication")
    
    def scenario_3_behavioral_patterns(self):
        """Scenario 3: Learning behavioral patterns"""
        print("\n🎯 Scenario 3: Learning Behavioral Patterns")
        print("=" * 50)
        
        # Simulate interactions at different times to show time patterns
        morning_interactions = [
            "Good morning! Ready to start learning today.",
            "I'm most productive in the morning hours.",
            "Let's tackle some challenging problems while I'm fresh."
        ]
        
        evening_interactions = [
            "I prefer lighter content in the evening.",
            "Can we review what we learned today?",
            "I like to reflect on new concepts before bed."
        ]
        
        print("Simulating time-based behavioral patterns...")
        self._process_interactions(morning_interactions, InteractionType.BEHAVIOR.value)
        time.sleep(1)  # Simulate time gap
        self._process_interactions(evening_interactions, InteractionType.BEHAVIOR.value)
        
        self._display_learned_facts("behavior")
    
    def scenario_4_feedback_learning(self):
        """Scenario 4: Learning from user feedback"""
        print("\n📝 Scenario 4: Learning from User Feedback")
        print("=" * 50)
        
        feedback_interactions = [
            "That explanation was perfect - just the right level of detail!",
            "I found that too technical, could you simplify it next time?",
            "I love when you include practical examples",
            "The step-by-step approach really works for me",
            "Visual diagrams would help me understand better"
        ]
        
        print("Processing user feedback to improve responses...")
        self._process_interactions(feedback_interactions, InteractionType.FEEDBACK.value)
        
        self._display_learned_facts("learning")
    
    def scenario_5_adaptive_responses(self):
        """Scenario 5: Demonstrating adaptive responses based on learned information"""
        print("\n🤖 Scenario 5: Adaptive AI Responses")
        print("=" * 50)
        
        print("Based on learned information, here's how the AI might adapt:")
        
        # Get learned facts to demonstrate adaptation
        with db_manager.get_session() as session:
            fact_repo = LearnedFactRepository(session)
            facts = fact_repo.get_user_facts(self.demo_user_id)
            
            print("\n🧠 Learned Facts Summary:")
            for fact in facts[:10]:  # Show top 10 facts
                print(f"  • {fact.category}: {fact.fact_value} (Confidence: {fact.confidence_level})")
            
            print("\n🎯 Adaptive Response Examples:")
            print("  • Response Length: Detailed (learned from preferences)")
            print("  • Tone: Friendly and encouraging (learned from communication style)")
            print("  • Content: Include practical examples (learned from feedback)")
            print("  • Timing: More complex topics in morning (learned from behavior)")
            print("  • Topics: Focus on AI/ML and programming (learned from interests)")
    
    def scenario_6_privacy_compliance(self):
        """Scenario 6: Demonstrating privacy and compliance features"""
        print("\n🔒 Scenario 6: Privacy and Compliance")
        print("=" * 50)
        
        from security import privacy_manager
        
        print("Demonstrating privacy features:")
        
        # Show data encryption
        sensitive_data = {"email": "alice@example.com", "personal_note": "I live in San Francisco"}
        encrypted = privacy_manager.encrypt_sensitive_data(sensitive_data, ["email", "personal_note"])
        print(f"  • Data Encryption: {list(encrypted.keys())} fields encrypted")
        
        # Show data anonymization
        user_data = {
            "user_id": self.demo_user_id,
            "age": 28,
            "location": "San Francisco, CA, USA",
            "email": "alice@example.com"
        }
        anonymized = privacy_manager.anonymizer.anonymize_user_data(user_data)
        print(f"  • Data Anonymization: {list(anonymized.keys())} (identifiers removed)")
        
        # Show content pseudonymization
        content = "My email is alice@example.com and my phone is 555-123-4567"
        pseudonymized = privacy_manager.anonymizer.pseudonymize_content(content)
        print(f"  • Content Pseudonymization: '{pseudonymized}'")
        
        print("  • Audit Logging: All data access events are logged")
        print("  • Consent Management: User consent tracked and enforced")
        print("  • Data Subject Rights: Export, deletion, and rectification supported")
    
    def _process_interactions(self, interactions, interaction_type):
        """Helper method to process a list of interactions"""
        with db_manager.get_session() as session:
            interaction_repo = InteractionRepository(session)
            fact_repo = LearnedFactRepository(session)
            
            processed_interactions = []
            
            for content in interactions:
                # Create interaction
                interaction = interaction_repo.create_interaction(
                    user_id=self.demo_user_id,
                    interaction_type=interaction_type,
                    content=content,
                    source="demo"
                )
                processed_interactions.append(interaction)
                print(f"  📝 {content}")
            
            # Process with learning engine
            print("  🧠 Processing with AI learning engine...")
            result = self.learning_engine.process_user_interactions(
                self.demo_user_id, 
                processed_interactions
            )
            
            # Store learned facts
            for fact_data in result.new_facts:
                fact_repo.create_or_update_fact(**fact_data)
            
            # Mark interactions as processed
            for interaction in processed_interactions:
                interaction_repo.mark_interaction_processed(interaction.id)
            
            print(f"  ✅ Learned {len(result.new_facts)} new facts, generated {len(result.insights)} insights")
            
            time.sleep(0.5)  # Small delay for demo effect
    
    def _display_learned_facts(self, category_filter=None):
        """Display learned facts for a category"""
        with db_manager.get_session() as session:
            fact_repo = LearnedFactRepository(session)
            facts = fact_repo.get_user_facts(self.demo_user_id, category_filter)
            
            if facts:
                print(f"\n🧠 Learned Facts ({category_filter or 'all'}):")
                for fact in facts:
                    print(f"  • {fact.fact_key}: {fact.fact_value}")
                    print(f"    Confidence: {fact.confidence_level} | Evidence: {fact.evidence_count}")
            else:
                print(f"\n💭 No facts learned yet for category: {category_filter or 'all'}")
    
    def run_all_scenarios(self):
        """Run all demo scenarios"""
        print("🎭 AI User Learning System - Demo Scenarios")
        print("=" * 60)
        print("This demo shows how AI can learn about users through interactions")
        print()
        
        # Create demo user
        if not self.demo_user_id:
            self.create_demo_user()
        
        # Run scenarios
        self.scenario_1_learning_preferences()
        self.scenario_2_communication_style()
        self.scenario_3_behavioral_patterns()
        self.scenario_4_feedback_learning()
        self.scenario_5_adaptive_responses()
        self.scenario_6_privacy_compliance()
        
        print("\n🎉 Demo Complete!")
        print("=" * 60)
        print("The AI has successfully learned about the user through various interactions.")
        print("In a real application, this learning would enable:")
        print("  • Personalized responses and recommendations")
        print("  • Adaptive user interfaces")
        print("  • Improved user experience over time")
        print("  • Intelligent content curation")
        print("  • Proactive assistance and suggestions")


def interactive_demo():
    """Interactive demo where user can try the system"""
    print("\n🎮 Interactive Demo Mode")
    print("=" * 40)
    print("Try interacting with the AI learning system!")
    print("Type 'exit' to quit, 'facts' to see learned facts")
    print()
    
    demo = AILearningDemo()
    user_id = demo.create_demo_user()
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'exit':
            break
        elif user_input.lower() == 'facts':
            demo._display_learned_facts()
            continue
        elif not user_input:
            continue
        
        # Process the interaction
        with db_manager.get_session() as session:
            interaction_repo = InteractionRepository(session)
            fact_repo = LearnedFactRepository(session)
            
            # Create interaction
            interaction = interaction_repo.create_interaction(
                user_id=user_id,
                interaction_type=InteractionType.MESSAGE.value,
                content=user_input,
                source="interactive_demo"
            )
            
            # Process with learning engine
            result = demo.learning_engine.process_user_interactions(user_id, [interaction])
            
            # Store learned facts
            for fact_data in result.new_facts:
                fact_repo.create_or_update_fact(**fact_data)
            
            interaction_repo.mark_interaction_processed(interaction.id)
            
            # Generate a simple response
            response = generate_demo_response(user_input, result)
            print(f"AI: {response}")
            
            if result.new_facts:
                print(f"🧠 (Learned {len(result.new_facts)} new things about you)")
            print()


def generate_demo_response(user_input, learning_result):
    """Generate a demo response based on user input and learning"""
    input_lower = user_input.lower()
    
    responses = {
        'help': "I'd be happy to help! I'm also learning that you like to ask for assistance when needed.",
        'thank': "You're welcome! I notice you're very polite - I'm learning about your communication style.",
        'like': "That's interesting! I'm noting your preferences to better understand what you enjoy.",
        'learn': "Great attitude! I can see you're interested in learning, which helps me understand how to best assist you.",
        'default': "Thanks for sharing that! I'm continuously learning about your preferences and communication style."
    }
    
    for keyword, response in responses.items():
        if keyword in input_lower:
            return response
    
    return responses['default']


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI User Learning System Demo")
    parser.add_argument('--interactive', action='store_true', help='Run interactive demo')
    parser.add_argument('--scenario', type=int, help='Run specific scenario (1-6)')
    
    args = parser.parse_args()
    
    # Initialize database if needed
    try:
        if not db_manager.health_check():
            print("Initializing database...")
            from database import init_database
            init_database()
    except Exception as e:
        print(f"Database initialization error: {e}")
        sys.exit(1)
    
    demo = AILearningDemo()
    
    if args.interactive:
        interactive_demo()
    elif args.scenario:
        demo.create_demo_user()
        scenario_methods = {
            1: demo.scenario_1_learning_preferences,
            2: demo.scenario_2_communication_style,
            3: demo.scenario_3_behavioral_patterns,
            4: demo.scenario_4_feedback_learning,
            5: demo.scenario_5_adaptive_responses,
            6: demo.scenario_6_privacy_compliance
        }
        
        if args.scenario in scenario_methods:
            scenario_methods[args.scenario]()
        else:
            print(f"Invalid scenario number: {args.scenario}")
    else:
        demo.run_all_scenarios()