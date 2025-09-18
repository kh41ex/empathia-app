# triggers.py - SUPER-ENHANCED TRIGGER SYSTEM
import re
from typing import Tuple
import numpy as np

def calculate_advice_priority(user_input: str, peer_response: str) -> float:
    """
    Calculate a priority score (0-1) for expert advice.
    Higher score = more urgent need for expert guidance.
    """
    user_input_lower = user_input.lower()
    peer_response_lower = peer_response.lower()
    
    # 🔥 CRISIS INDICATORS (IMMEDIATE EXPERT HELP)
    crisis_keywords = [
        r'\b(suicide|self harm|end it all|can\'t go on|want to die|not want to live)\b',
        r'\b(panic attack|anxiety attack|can\'t breathe|hyperventilat|chest pain)\b',
        r'\b(emergency|crisis|help me|desperate|hopeless|overwhelmed)\b',
        r'\b(can\'t function|can\'t get out of bed|can\'t stop crying)\b'
    ]
    
    # 🔥 HIGH PRIORITY: Explicit requests & deep emotional needs
    high_need_triggers = [
        # Explicit help-seeking
        r'\b(how to|what should|what can|how do I|how did you)\b',
        r'\b(need advice|want advice|looking for advice|seek guidance)\b',
        r'\b(professional help|therapist|counselor|psychologist|expert)\b',
        
        # Emotional struggles
        r'\b(guilt|regret|blame|should have|could have|why did I)\b',
        r'\b( depression|depressed|hopeless|despair|numb|empty)\b',
        r'\b(anxiety|anxious|worry|worried|overwhelmed|panic)\b',
        r'\b(anger|rage|furious|resentment|bitter|frustrat)\b',
        
        # Functional impairment
        r'\b(can\'t sleep|insomnia|sleep problems|nightmares)\b',
        r'\b(can\'t eat|appetite|weight loss|weight gain)\b',
        r'\b(can\'t work|can\'t focus|concentration|memory)\b',
        r'\b(daily routine|function|get through day|basic tasks)\b',
        
        # Question patterns
        r'\?\s*$',  # Ends with question mark
        r'\b(is this normal|am I normal|is it normal)\b',
        r'\b(why do I|why am I|what does it mean)\b'
    ]
    
    # 🔥 MEDIUM PRIORITY: Relationship & social contexts
    medium_need_triggers = [
        # Social relationships
        r'\b(children|kids|family|partner|spouse|husband|wife)\b',
        r'\b(friends| coworkers|colleagues|people don\'t understand)\b',
        r'\b(social|isolated|lonely|alone|no one gets it)\b',
        
        # Decision struggles
        r'\b(decision|decide|choice|what to do|whether to)\b',
        r'\b(euthanasia|put down|put to sleep|when to)\b',
        r'\b(adopt|new pet|another pet|when to get)\b',
        
        # Time-based concerns
        r'\b(months later|years later|still grieving|long time)\b',
        r'\b(anniversary|birthday|holiday|special date)\b',
        
        # Physical & behavioral
        r'\b(dreams|visit|sign|message from|felt presence)\b',
        r'\b(avoiding|avoid|can\'t go|can\'t visit|can\'t look)\b'
    ]
    
    # 🔥 LOW PRIORITY: General grief expressions
    low_need_triggers = [
        r'\b(sad|heartbroken|hurt|pain|miss|missing)\b',
        r'\b(memories|remember|thinking about|reminisc)\b',
        r'\b(cry|crying|tears|emotional|feelings)\b',
        r'\b(thank you|appreciate|grateful|kind|support)\b'
    ]
    
    # 🚨 CHECK FOR CRISIS FIRST (IMMEDIATE RESPONSE)
    for pattern in crisis_keywords:
        if re.search(pattern, user_input_lower):
            return 0.95  # Highest priority - near certain
    
    # 📊 CALCULATE SCORE BASED ON MULTIPLE FACTORS
    score = 0.0
    
    # 1. User input content scoring
    for pattern in high_need_triggers:
        if re.search(pattern, user_input_lower):
            score += 0.25
            break  # Only count once per category
    
    for pattern in medium_need_triggers:
        if re.search(pattern, user_input_lower):
            score += 0.15
            break
    
    for pattern in low_need_triggers:
        if re.search(pattern, user_input_lower):
            score += 0.08
            break
    
    # 2. Peer response quality indicators
    if len(peer_response.split()) < 20:  # Very short response
        score += 0.20
    
    if any(phrase in peer_response_lower for phrase in [
        "i don't know", "i'm not sure", "not sure", 
        "can't imagine", "hard to say", "difficult question"
    ]):
        score += 0.25
    
    if "i'm not a professional" in peer_response_lower or "i'm not an expert" in peer_response_lower:
        score += 0.30
    
    # 3. Conversation context boosts
    # If user has asked multiple questions recently
    if '?' in user_input and score > 0.3:
        score += 0.15
    
    # If peer response is purely emotional without practical support
    emotional_words = ['sorry', 'heart', 'pain', 'sad', 'hard', 'difficult']
    practical_words = ['try', 'suggest', 'recommend', 'maybe', 'could', 'consider']
    
    emotional_count = sum(1 for word in emotional_words if word in peer_response_lower)
    practical_count = sum(1 for word in practical_words if word in peer_response_lower)
    
    if emotional_count > 2 and practical_count == 0:
        score += 0.18
    
    # 4. Specific phrase boosts
    boost_phrases = {
        'professional advice': 0.35,
        'expert opinion': 0.30,
        'psychological': 0.28,
        'research': 0.25,
        'science': 0.25,
        'evidence': 0.25,
        'what would a therapist': 0.40
    }
    
    for phrase, boost in boost_phrases.items():
        if phrase in user_input_lower:
            score += boost
            break
    
    # 🎯 FINAL SCORE ADJUSTMENT
    # Ensure minimum score for any grief-related input
    if any(word in user_input_lower for word in ['pet', 'loss', 'grief', 'mourn', 'died', 'pass']):
        score = max(score, 0.15)  # At least some priority for grief topics
    
    # Cap at 0.9 for non-crisis (leave room for crisis responses)
    return min(score, 0.9)

# Keep the legacy function for compatibility
def check_if_needs_expert_advice(user_input: str, peer_response: str) -> bool:
    """Legacy function for compatibility"""
    return calculate_advice_priority(user_input, peer_response) > 0.3