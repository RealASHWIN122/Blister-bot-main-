from huggingface_hub import hf_hub_download

def main():
    repo_id = "Qwen/Qwen2.5-1.5B-Instruct-GGUF"
    filename = "qwen2.5-1.5b-instruct-q4_k_m.gguf"

    print(f"Downloading {filename} from {repo_id}...")
    print("This might take a few minutes depending on your connection speed (~1.1 GB)...")
    
    model_path = hf_hub_download(repo_id=repo_id, filename=filename, local_dir=".")
    
    print(f"Model downloaded successfully to: {model_path}")

if __name__ == "__main__":
    main()
