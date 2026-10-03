import os
import torch
import qai_hub as hub
from transformers import AutoModelForCausalLM

def compile_qwen():
    print("Loading Qwen 0.5B model from HuggingFace...")
    # Load the base model (we use the unquantized float32 for tracing)
    model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct", torch_dtype=torch.float32)
    model.eval()

    # Create a wrapper module that only returns the logits 
    # (since standard LLM outputs are complex dictionary objects that torch.jit cannot trace)
    class TracableModel(torch.nn.Module):
        def __init__(self, model):
            super().__init__()
            self.model = model

        def forward(self, input_ids, attention_mask):
            return self.model(input_ids=input_ids, attention_mask=attention_mask).logits

    tracable_model = TracableModel(model)

    # Sequence length for the trace. We'll trace it for a fixed sequence length of 128 tokens for this edge application.
    seq_len = 128
    input_ids = torch.randint(0, 1000, (1, seq_len), dtype=torch.long)
    attention_mask = torch.ones((1, seq_len), dtype=torch.long)

    print("Tracing the PyTorch model with torch.export...")
    with torch.no_grad():
        exported_program = torch.export.export(tracable_model, (input_ids, attention_mask), strict=False)
        traced_model = exported_program

    print("Submitting compile job to Qualcomm AI Hub...")
    # Compile and optimize the model for the Qualcomm QCS6490 (Dragonwing RB3 Gen 2 Vision Kit)
    compile_job = hub.submit_compile_job(
        model=traced_model,
        device=hub.Device("Dragonwing RB3 Gen 2 Vision Kit"),
        input_specs=dict(
            input_ids=((1, seq_len), "int64"),
            attention_mask=((1, seq_len), "int64")
        ),
        options="--target_runtime tflite --truncate_64bit_io",
        name="qwen-0.5b-blisterbot"
    )

    print(f"Compilation job submitted! Job ID: {compile_job.job_id}")
    
    # Wait for the job to complete
    print("Waiting for the job to complete. This may take 5-15 minutes...")
    model_tflite = compile_job.get_target_model()
    
    # Download the optimized model
    output_path = os.path.join(os.path.dirname(__file__), "qwen_optimized.tflite")
    compile_job.download_target_model(filename=output_path)
    print(f"Success! Optimized LiteRT model saved to {output_path}")

if __name__ == "__main__":
    compile_qwen()
