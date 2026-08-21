import json
import os
from llama_cpp import Llama

# --- 1. Define Tools (Agentic Actions) ---
def get_temperature():
    """Tool: Get the current temperature."""
    # In reality, this would read from a GPIO pin on the Uno Q
    return {"temperature": 24.5, "unit": "Celsius"}

def activate_facial_recognition():
    """Tool: Activate the facial recognition system."""
    # In reality, this would trigger the facial_recognition_system.py script
    return {"status": "Facial recognition system activated successfully"}

# Map of available tools
TOOLS = {
    "get_temperature": get_temperature,
    "activate_facial_recognition": activate_facial_recognition
}

# --- 2. Load the Edge LLM ---
def load_model():
    print("[INFO] Loading LLM into RAM... (This may take a few seconds)")
    # n_ctx is the context window. Keeping it small (2048) ensures it fits in 2GB RAM.
    llm = Llama(
        model_path="qwen2.5-1.5b-instruct-q4_k_m.gguf",
        n_ctx=2048,
        n_threads=4, # Optimize for 4-core ARM CPU (Arduino Uno Q)
        verbose=False # Set to True to see memory usage logs
    )
    return llm

# --- 3. The Agent Loop ---
def run_agent(llm, user_prompt):
    # System prompt forces the model to choose between natural language or a JSON tool call
    system_prompt = """You are a highly capable AI agent running on an Arduino Uno Q. You have access to the following tools:
1. get_temperature(): Returns the current room temperature.
2. activate_facial_recognition(): Turns on the facial recognition camera.

To use a tool, output exactly this JSON format and nothing else:
{"tool": "tool_name"}

If you do not need to use a tool, just respond naturally."""

    # Format prompt for Qwen 2.5
    prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n"
    
    print(f"\n[User]: {user_prompt}")
    print("[Agent Thinking...]")
    
    response = llm(
        prompt,
        max_tokens=256,
        stop=["<|im_end|>"],
        temperature=0.1 # Low temperature for more deterministic reasoning
    )
    
    output = response["choices"][0]["text"].strip()
    
    # --- 4. Parse output for Tool Calls ---
    try:
        if output.startswith("{") and "tool" in output:
            tool_call = json.loads(output)
            tool_name = tool_call.get("tool")
            
            if tool_name in TOOLS:
                print(f"[Agent Action]: Calling tool -> {tool_name}()")
                tool_result = TOOLS[tool_name]()
                print(f"[Tool Result]: {tool_result}")
                
                # Feed the tool result back to the model so it can answer the user
                follow_up_prompt = prompt + output + f"<|im_end|>\n<|im_start|>user\nTool result: {json.dumps(tool_result)}<|im_end|>\n<|im_start|>assistant\n"
                
                print("[Agent Thinking...]")
                final_response = llm(
                    follow_up_prompt,
                    max_tokens=256,
                    stop=["<|im_end|>"],
                    temperature=0.1
                )
                print(f"[Agent]: {final_response['choices'][0]['text'].strip()}")
            else:
                print(f"[Agent Error]: Attempted to call unknown tool '{tool_name}'")
        else:
            # Natural language response
            print(f"[Agent]: {output}")
    except json.JSONDecodeError:
        print(f"[Agent]: {output}")

if __name__ == "__main__":
    if not os.path.exists("qwen2.5-1.5b-instruct-q4_k_m.gguf"):
        print("[ERROR] Model file not found. Please run download_model.py first.")
        exit(1)
        
    llm = load_model()
    
    print("\n" + "="*50)
    print("Edge Agent Initialized. Ready for testing.")
    print("="*50)
    
    # Test 1: Simple Knowledge (No tool needed)
    run_agent(llm, "Hello, what kind of hardware are you running on?")
    
    # Test 2: Sensor Tool Call
    run_agent(llm, "It feels hot in here. What is the temperature right now?")
    
    # Test 3: Camera Tool Call
    run_agent(llm, "Someone is at the door, can you check who it is?")
