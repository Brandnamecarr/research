import argparse
from transformers import AutoModelForCasualLM, AutoTokenizer, pipeline

def generate_text(prompt, model_name="TheBlone/Mistral-7B-Instruct-v0.1-GGUF", max_tokens=200):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
    result = pipe(prompt, max_new_tokens=max_tokens)[0]['generated_text']
    return result

def main():
    parser = argparse.ArgumentParser(description="Local Generative AI CLI")
    parser.add_argument("prompt", type=str, help="Prompt for the local model")
    parser.add_argument("--tokens", type=int, default=200, help="Max tokens to generate")
    args = parser.parse_args()

    print("\nGenerating...\n")
    output = generate_text(args.prompt, max_tokens=args.tokens)
    print(f"\n📝 Output:\n{output}")

if __name__ == "__main__":
    main()