import os
import sys
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def generate_retention_brief(customer_id, churn_prob, uplift_score, segment, top_driver, clv):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "SYSTEM_WARN: Groq credentials unmapped. Plain text generation bypassed."
        
    client = Groq(api_key=api_key)
    
    prompt = (
        f"You are ChurnShield AI, an elite enterprise SaaS operations analyst.\n"
        f"Write a sharp, high-impact single-paragraph retention brief for Customer {customer_id}.\n\n"
        f"METRICS:\n"
        f"- 30-Day Churn Risk Probability: {churn_prob * 100:.1f}%\n"
        f"- Causal Uplift Actionability Score: {uplift_score:.4f}\n"
        f"- Causal Customer Segment Allocation: {segment}\n"
        f"- Core Negative Activity Behavioral Driver: {top_driver}\n"
        f"- Monitored Customer Lifetime Value (CLV): ${clv:,.2f}\n\n"
        f"CRITICAL COMPLIANCE RULES:\n"
        f"1. Return EXACTLY one single paragraph. No list points, no headers, no greeting, no emojis.\n"
        f"2. Explicitly interpret if the business should execute a financial intervention or hold based on their segment profile.\n"
        f"3. Be direct, authoritative, and completely humanized. Do not use generic AI buzzwords."
    )
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=150
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"SYSTEM_ERR: Failed to compile text synthesis matrix via LLM endpoint: {str(e)}"

if __name__ == "__main__":
    test_brief = generate_retention_brief(
        customer_id="CUST_99999",
        churn_prob=0.6375,
        uplift_score=0.3525,
        segment="Persuadable",
        top_driver="45% drop in weekly login velocity paired with 7 unresolved support tickets",
        clv=4500.00
    )
    print("\n--- Live Test Generation ---")
    print(test_brief)