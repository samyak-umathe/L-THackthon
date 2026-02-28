import google.generativeai as genai

# Configure Gemini
genai.configure(api_key="AIzaSyDJUoETrm4Zvpk9ezvdWKparcmrbSTG2-g")
model = genai.GenerativeModel('gemini-2.5-flash')  # Free and fast

def get_feeder_recommendation(feeder_data: dict) -> str:
    prompt = f"""
    You are a senior power grid analyst for Indian electricity utilities (DISCOMs).
    
    Analyze this feeder data and provide actionable recommendations:
    
    Feeder ID: {feeder_data['feeder_id']}
    State: {feeder_data['state']}
    Current Loss %: {feeder_data['loss_percentage']}%
    Transformer Age: {feeder_data['transformer_age_years']} years
    Load Factor: {feeder_data['load_factor']}
    Temperature: {feeder_data['temperature_celsius']}°C
    Voltage Fluctuation: {feeder_data['voltage_fluctuation']}%
    Anomaly/Theft Suspected: {feeder_data['is_suspicious']}
    Asset Risk Level: {feeder_data['risk_label']}
    Smart Meter Installed: {feeder_data['smart_meter_installed']}
    Monthly Outage Hours: {feeder_data['outage_hours_monthly']}
    
    Provide your response in this exact format:
    
    **ROOT CAUSE ANALYSIS:**
    (2-3 sentences explaining why losses are high)
    
    **TOP 3 RECOMMENDATIONS:**
    1. (Action) — Estimated Cost: ₹X lakh — Expected Loss Reduction: X%
    2. (Action) — Estimated Cost: ₹X lakh — Expected Loss Reduction: X%
    3. (Action) — Estimated Cost: ₹X lakh — Expected Loss Reduction: X%
    
    **PRIORITY LEVEL:** Critical / High / Medium
    
    **ESTIMATED ANNUAL REVENUE RECOVERY:** ₹X lakh
    
    Keep recommendations practical for Indian DISCOM field conditions.
    """
    
    response = model.generate_content(prompt)
    return response.text


def get_state_strategy(state: str, avg_loss: float, 
                        suspicious_count: int, high_risk_count: int) -> str:
    prompt = f"""
    You are a power sector policy advisor for India.
    
    State: {state}
    Average T&D Loss: {avg_loss:.1f}%
    Suspicious/Theft Feeders: {suspicious_count}
    High Risk Assets: {high_risk_count}
    National Target: <2% by 2030
    
    Provide a 6-point state-level strategy to reduce losses to below 2% by 2030.
    Include policy recommendations, technology rollout plan, and estimated investment needed.
    Format as numbered points. Be specific to Indian power sector context.
    """
    
    response = model.generate_content(prompt)
    return response.text


def ask_gridsense(question: str, context_data: dict) -> str:
    prompt = f"""
    You are GridSense AI, an intelligent assistant for India's power grid loss reduction program.
    
    Current Grid Context:
    - National Average Loss: {context_data['avg_loss']:.1f}%
    - Total Suspicious Feeders: {context_data['suspicious_count']}
    - High Risk Assets: {context_data['high_risk_count']}
    - Worst Performing State: {context_data['worst_state']}
    - Best Performing State: {context_data['best_state']}
    - Estimated Annual Revenue Loss: ₹{context_data['revenue_loss']} Crore
    
    Answer this question concisely and practically:
    {question}
    """
    
    response = model.generate_content(prompt)
    return response.text