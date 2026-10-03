import os
import sys
import json
import sqlite3

sys.path.append(os.path.join(os.path.dirname(__file__), 'UNO'))
from assistant import init_llm, generate_response
from database import get_inventory, get_patient_by_name

def test_model():
    print("Loading Qwen model... (This might take a moment)")
    llm = init_llm()
    current_patient = "Unknown" 
    
    print("\n==============================================")
    print("BlisterBot Interactive Tester")
    print("Type your queries to test the model's output.")
    print("Type 'quit' or 'exit' to stop.")
    print("==============================================\n")

    while True:
        try:
            cmd_text = input("You: ")
        except (KeyboardInterrupt, EOFError):
            break
            
        if cmd_text.lower() in ['quit', 'exit']:
            break
            
        intent_prompt = f"""Classify the user's command into one of these exact categories:
1. ADD_PATIENT
2. DRILL_MEDICINE
3. PATIENT_DETAILS
4. UPDATE_PATIENT
5. DOSAGE_QUERY (e.g. "dose for panadol")
6. SCHEDULE_QUERY (e.g. "when should I take")
7. MEDICINE_QUERY (e.g. "what is ibuprofen for")
8. PAIN_REPORT (e.g. "I have a headache", "I feel sick")
9. CONVERSATION (e.g. "hello", "how are you")
10. Q_AND_A (fallback)

Command: '{cmd_text}'
Output ONLY the category name."""
        
        intent = generate_response(llm, intent_prompt).strip().upper()
        print(f"\n[System Detected Intent]: {intent}")
        
        if any(q in intent for q in ["DOSAGE", "SCHEDULE", "MEDICINE_QUERY"]):
            patient_info = get_patient_by_name(current_patient)
            inv = get_inventory()
            prompt = f"Answer this concisely. Question: '{cmd_text}'. Context: Current patient info: {patient_info}. Inventory/Dosages: {inv}"
            answer = generate_response(llm, prompt)
            print(f"[Bot Response]: {answer}\n")
            
        elif "PAIN_REPORT" in intent:
            prompt = f"The user is reporting pain or discomfort: '{cmd_text}'. As a medical assistant, give a short, friendly, and encouraging response."
            answer = generate_response(llm, prompt)
            print(f"[Bot Response]: {answer}")
            print(f"*(System silently logs this report to painrec/{current_patient}.md)*\n")
            
        elif "CONVERSATION" in intent:
            prompt = f"Answer this conversational input in a friendly and encouraging way: '{cmd_text}'."
            answer = generate_response(llm, prompt)
            print(f"[Bot Response]: {answer}\n")
            
        else:
            inv = get_inventory()
            prompt = f"Answer this question concisely as a medical assistant. Question: '{cmd_text}'. Context: We have these medicines in inventory: {inv}"
            answer = generate_response(llm, prompt)
            print(f"[Bot Response]: {answer}\n")

if __name__ == "__main__":
    test_model()
