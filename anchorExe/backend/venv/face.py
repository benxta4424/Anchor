from typing import Dict, Any, List, Optional
import logging
import json

logger = logging.getLogger(__name__)


def process_face_api_result(face_detection_data: Dict[str, Any]) -> Dict[str, Any]:
    logger.info('Start processing Face API result')
    """
    Process raw Face-API.js detection result
    
    Input format (from frontend Face-API.js):
    {
        "expressions": {
            "neutral": 0.95,
            "happy": 0.02,
            "sad": 0.01,
            "angry": 0.01,
            "fearful": 0.005,
            "disgusted": 0.002,
            "surprised": 0.001
        },
        "detection": {
            "score": 0.95,  // confidence
            "box": { "x": 100, "y": 50, "width": 200, "height": 250 }
        },
        "landmarks": { /* 68 face landmarks */ }
    }
    
    Args:
        face_detection_data: Raw Face-API.js detection result
    
    Returns:
        Processed analysis with emotion scores and depression indicators
    """
    
    try:
        expressions = face_detection_data.get('expressions', {})
        detection = face_detection_data.get('detection', {})
        
        # Extract emotion scores (0-1 scale)
        sad_score = float(expressions.get('sad', 0))
        angry_score = float(expressions.get('angry', 0))
        fearful_score = float(expressions.get('fearful', 0))
        neutral_score = float(expressions.get('neutral', 0))
        happy_score = float(expressions.get('happy', 0))
        disgusted_score = float(expressions.get('disgusted', 0))
        surprised_score = float(expressions.get('surprised', 0))
        
        # Confidence of face detection
        confidence = float(detection.get('score', 0))
        
        # Determine dominant emotion with bias/refinement to better detect irritability/anger
        emotions_dict = {
            'sad': sad_score,
            'angry': angry_score,
            'fearful': fearful_score,
            'neutral': neutral_score,
            'happy': happy_score,
            'disgusted': disgusted_score,
            'surprised': surprised_score,
        }
        
        # Raw dominant emotion
        dominant_emotion = max(emotions_dict, key=emotions_dict.get)
        
        # Refinement to avoid misclassifying irritability (angry) as sadness or neutral.
        # Face-API often underestimates anger (frowning can be read as neutral or sad).
        # We lower the active threshold to 1% (> 0.01) for both anger and disgust,
        # aggressively promoting even minor signals that coexist with sadness or flat faces.
        if (angry_score > 0.01 or disgusted_score > 0.01) and (angry_score * 3.5 > sad_score or disgusted_score * 3.0 > sad_score or (angry_score + disgusted_score) * 1.5 > neutral_score):
            dominant_emotion = 'angry'
        
        return {
            "status": "success",
            "confidence": confidence,
            "dominant_emotion": dominant_emotion,
            "emotions": {
                "sad": sad_score,
                "angry": angry_score,
                "fearful": fearful_score,
                "neutral": neutral_score,
                "happy": happy_score,
                "disgusted": disgusted_score,
                "surprised": surprised_score,
            },
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "confidence": 0,
            "dominant_emotion": "unknown",
            "emotions": {},
        }


def analyze_face_depression_indicators(face_data: Dict[str, Any]) -> Dict[str, Any]:
    logger.info('Start analyzing face depression indicators')
    """
    Extract depression indicators from face analysis, focusing on the 5 clinical dimensions (DSM-5):
    - Tristețe (sadness)
    - Anxietate (anxiety/fear)
    - Iritabilitate (irritability/anger/disgust)
    - Anhedonie (anhedonia/lack of pleasure)
    - Indiferență (indifference/flat affect)
    
    Args:
        face_data: Processed face analysis from process_face_api_result()
    
    Returns:
        Dictionary with depression scores (0-100) and descriptions
    """
    
    emotions = face_data.get('emotions', {})
    confidence = face_data.get('confidence', 0)
    dominant_emotion = face_data.get('dominant_emotion', 'unknown')
    
    depression_indicators = {
        "sadness_indicator": 0,       # 0-100
        "anxiety_indicator": 0,       # 0-100
        "irritability_indicator": 0,    # 0-100
        "anhedonia_indicator": 0,      # 0-100
        "indifference_indicator": 0,    # 0-100
        "overall_face_depression_score": 0,  # 0-100
        "descriptions": [],
    }
    
    sad_score = emotions.get('sad', 0) * 100
    angry_score = emotions.get('angry', 0) * 100
    fearful_score = emotions.get('fearful', 0) * 100
    neutral_score = emotions.get('neutral', 0) * 100
    happy_score = emotions.get('happy', 0) * 100
    disgusted_score = emotions.get('disgusted', 0) * 100
    surprised_score = emotions.get('surprised', 0) * 100
    
    # 1. TRISTEȚE (Sadness): Core clinical marker of depressive mood
    sadness_val = sad_score
    if dominant_emotion == 'sad':
        sadness_val = max(sadness_val, 30) + (100 - max(sadness_val, 30)) * 0.25
    depression_indicators["sadness_indicator"] = int(min(100, sadness_val))
    
    # 2. ANXIETATE (Anxiety/Fear): Indicates anxious distress
    anxiety_val = fearful_score * 1.1 + surprised_score * 0.3
    if dominant_emotion == 'fearful':
        anxiety_val = max(anxiety_val, 35) + (100 - max(anxiety_val, 35)) * 0.25
    depression_indicators["anxiety_indicator"] = int(min(100, anxiety_val))
    
    # 3. IRITABILITATE (Irritability): Irritable mood, typical in agitated depression
    # Fuses angry and disgusted expressions
    # Multiply disgusted_score by 3.0 and angry_score by 2.0 to aggressively capture micro-expressions
    irritability_val = angry_score * 2.0 + disgusted_score * 3.0
    if dominant_emotion == 'angry' or dominant_emotion == 'disgusted' or (angry_score > 1.5 and angry_score * 1.2 > sad_score) or (disgusted_score > 1.5):
        base_irritability = max(angry_score, disgusted_score, sad_score)
        if dominant_emotion == 'angry' or dominant_emotion == 'disgusted':
            # Boost angry/disgusted dominant faces by 40% and add baseline 25 points
            irritability_val = max(base_irritability * 1.40, irritability_val + 25)
        else:
            irritability_val = max(base_irritability, irritability_val)
    else:
        if angry_score >= sad_score:
            irritability_val = angry_score * 1.5
        elif angry_score > 1.5:
            anger_ratio = angry_score / max(angry_score + sad_score, 1)
            irritability_val = angry_score * (1.0 + anger_ratio * 0.5)
        else:
            irritability_val = angry_score * 1.0
    depression_indicators["irritability_indicator"] = int(min(100, irritability_val))
    
    # 4. ANHEDONIE (Anhedonia): Inability to feel pleasure
    if happy_score > 35:
        anhedonia_val = max(0, (35 - happy_score) * 2.8)
    else:
        anhedonia_val = 100 - happy_score * 2.0
    depression_indicators["anhedonia_indicator"] = int(max(0, min(100, anhedonia_val)))
    
    # 5. INDIFERENȚĂ (Indifference/Flat Affect): Emotional flattening derived from neutral
    if neutral_score > 85 and max(sad_score, angry_score, fearful_score) < 10:
        indifference_val = neutral_score * 0.25 # suppressed normal resting face
    else:
        indifference_val = neutral_score
    depression_indicators["indifference_indicator"] = int(min(100, indifference_val))
    
    # --- Overall face depression score ---
    # Scientific weighted aggregation of the clinical dimensions, mitigated by happiness
    if dominant_emotion == 'happy' or happy_score >= 35:
        overall_score = 0
    else:
        # Base clinical risk score
        base_risk = (
            sadness_val * 0.35 +
            irritability_val * 0.20 +
            anxiety_val * 0.15 +
            indifference_val * 0.15 +
            anhedonia_val * 0.15
        )
        
        # Apply dominant emotion scaling to emphasize active conditions
        if dominant_emotion == 'sad':
            overall_score = base_risk * 1.25
        elif dominant_emotion == 'angry':
            overall_score = base_risk * 1.15
        elif dominant_emotion == 'fearful':
            overall_score = base_risk * 1.15
        else:
            overall_score = base_risk
            
        overall_score = int(overall_score)
    
    depression_indicators["overall_face_depression_score"] = max(0, min(100, overall_score))
    
    # Generate descriptions based on what's actually dominant and active
    if dominant_emotion == 'angry' or depression_indicators["irritability_indicator"] > 25:
        depression_indicators["descriptions"].append(f"Semne de iritabilitate/nervozitate ({depression_indicators['irritability_indicator']:.0f}%)")
    if dominant_emotion == 'sad' or depression_indicators["sadness_indicator"] > 25:
        depression_indicators["descriptions"].append(f"Expresie de tristețe detectată ({depression_indicators['sadness_indicator']:.0f}%)")
    if dominant_emotion == 'fearful' or depression_indicators["anxiety_indicator"] > 25:
        depression_indicators["descriptions"].append(f"Expresie de teamă/anxietate ({depression_indicators['anxiety_indicator']:.0f}%)")
    if depression_indicators["anhedonia_indicator"] > 60:
        depression_indicators["descriptions"].append(f"Semne de anhedonie / aplatizare afectivă pozitivă ({depression_indicators['anhedonia_indicator']:.0f}%)")
    if neutral_score > 70:
        depression_indicators["descriptions"].append(f"Mimică indiferentă/plată ({neutral_score:.0f}%)")
    if happy_score > 40:
        depression_indicators["descriptions"].append(f"Afect pozitiv / zâmbet ({happy_score:.0f}%)")
        
    if confidence < 0.5:
        depression_indicators["descriptions"].append("⚠️ Încredere scăzută în detecția feței")
        
    return depression_indicators


def extract_facial_features(face_data: Dict[str, Any], landmarks: Optional[Dict] = None) -> Dict[str, Any]:
    logger.info('Start extracting facial features')
    """
    Extract facial features from Face-API detection
    
    Features:
    - Eye contact quality: From landmark positions
    - Mouth openness: Indicates engagement/speech
    - Brow position: Indicates surprise or worry
    
    Args:
        face_data: Processed face analysis
        landmarks: Face landmarks (68 points) from Face-API
    
    Returns:
        Dictionary with facial feature descriptions
    """
    
    features = {
        "facial_expression": face_data.get('dominant_emotion', 'unknown'),
        "expression_confidence": face_data.get('confidence', 0),
        "detection_quality": "good" if face_data.get('confidence', 0) > 0.8 else "fair",
        "notes": [],
    }
    
    # If landmarks provided, analyze them
    if landmarks:
        features["landmarks_available"] = True
        features["notes"].append("Facial landmarks detected (eye contact analysis available)")
    else:
        features["landmarks_available"] = False
    
    return features


def process_face_input(face_api_data: Dict[str, Any]) -> Dict[str, Any]:
    logger.info('Start full face processing pipeline')
    """
    Complete face processing pipeline
    
    1. Process raw Face-API.js data
    2. Extract depression indicators
    3. Analyze facial features
    4. Combine results
    
    Args:
        face_api_data: Raw Face-API.js detection result from frontend
    
    Returns:
        Complete analysis with depression scores
    
    Example:
        >>> face_api_data = { /* from frontend */ }
        >>> result = process_face_input(face_api_data)
        >>> print(f"Depression score: {result['depression_indicators']['overall_face_depression_score']}")
    """
    
    try:
        # Step 1: Process Face-API data
        print("📊 Processing Face-API detection...")
        face_processed = process_face_api_result(face_api_data)
        
        if face_processed['status'] != 'success':
            return {
                "status": "error",
                "error": "Face detection failed",
                "face_processed": face_processed,
            }
        
        # Step 2: Analyze depression indicators
        print("🔍 Analyzing depression indicators...")
        depression_indicators = analyze_face_depression_indicators(face_processed)
        
        # Step 3: Extract facial features
        print("👁️ Extracting facial features...")
        facial_features = extract_facial_features(
            face_processed,
            face_api_data.get('landmarks')
        )
        
        result = {
            "status": "success",
            "face_processed": face_processed,
            "depression_indicators": depression_indicators,
            "facial_features": facial_features,
        }
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


def combine_voice_and_face_scores(voice_score: float, face_score: float, text_score: float) -> Dict[str, Any]:
    """
    Combine voice, face, and text depression scores into unified analysis
    
    Weighting:
    - Text: 50% (most reliable from LLM)
    - Voice: 25% (acoustic markers)
    - Face: 25% (visual expression)
    
    Args:
        voice_score: Voice depression indicator (0-100) from voice.py
        face_score: Face depression score (0-100) from this module
        text_score: Text depression score (0-100) from app.py analyze_text()
    
    Returns:
        Combined multimodal analysis
    """
    
    # Weighted average
    combined_score = int(
        (text_score * 0.50 +
         voice_score * 0.25 +
         face_score * 0.25)
    )
    
    # Confidence calculation
    # If all three agree, confidence is high
    agreement = 100 - abs(text_score - voice_score) - abs(text_score - face_score)
    confidence = max(0, min(100, agreement))
    
    return {
        "combined_score": combined_score,
        "confidence": confidence,
        "component_scores": {
            "text": text_score,
            "voice": voice_score,
            "face": face_score,
        },
        "component_weights": {
            "text": 0.50,
            "voice": 0.25,
            "face": 0.25,
        },
        "summary": f"Multimodal analysis shows {combined_score}% depression risk (confidence: {confidence}%)"
    }


# Test function
def test_face_module():
    """Quick test of face module"""
    print("Testing face module...")
    print("✅ Module loaded successfully")
    print("Available functions:")
    print("  - process_face_api_result(face_detection_data)")
    print("  - analyze_face_depression_indicators(face_data)")
    print("  - extract_facial_features(face_data, landmarks)")
    print("  - process_face_input(face_api_data)")
    print("  - combine_voice_and_face_scores(voice, face, text)")


if __name__ == "__main__":
    test_face_module()
