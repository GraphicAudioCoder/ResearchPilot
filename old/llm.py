def split_request_in_steps(request):
	# Suddivisione semplice in step per data cleaning, analisi e plotting
	steps = []
	if "pulizia" in request or "pulire" in request or "rimuovere" in request:
		steps.append("Scrivi uno script Python che legge il dataset CSV 'dataset.csv' e rimuove le righe duplicate e corregge eventuali errori di formattazione. Rispondi solo con il codice.")
	if "media" in request or "calcola" in request or "analisi" in request:
		steps.append("Scrivi uno script Python che calcola il salario medio per ogni professione dal dataset 'dataset.csv'. Rispondi solo con il codice.")
	if "grafico" in request or "plot" in request or "visualizza" in request:
		steps.append("Scrivi uno script Python che visualizza i risultati in un grafico a barre usando matplotlib, partendo dal dataset 'dataset.csv'. Rispondi solo con il codice.")
	if not steps:
		steps.append(request)
	return steps
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


def generate_llm(prompt):
	model_name = "microsoft/phi-3-mini-4k-instruct"
	tokenizer = AutoTokenizer.from_pretrained(model_name)
	# Scegli device: MPS (Apple Silicon), CUDA (NVIDIA), o CPU
	if torch.backends.mps.is_available():
		device = torch.device("mps")
		print("Usando GPU Apple Silicon (MPS)")
	elif torch.cuda.is_available():
		device = torch.device("cuda")
		print("Usando GPU NVIDIA (CUDA)")
	else:
		device = torch.device("cpu")
		print("Usando CPU")
	model = AutoModelForCausalLM.from_pretrained(model_name, dtype=torch.float16).to(device)
	inputs = tokenizer(prompt, return_tensors="pt").to(device)
	with torch.no_grad():
		outputs = model.generate(**inputs, max_new_tokens=256)
	return tokenizer.decode(outputs[0], skip_special_tokens=True)

if __name__ == "__main__":
	# Leggi il contenuto del file CSV
	csv_path = os.path.join(os.path.dirname(__file__), "dataset.csv")
	with open(csv_path, "r", encoding="utf-8") as f:
		csv_data = f.read()

	# Prompt precedente commentato
	# prompt1 = f"Scrivi uno script Python che legge il seguente dataset CSV, rimuove le righe duplicate, corregge eventuali errori di formattazione e calcola il salario medio per ogni professione. Il file si chiama 'dataset.csv'. Rispondi solo con il codice.\n\n{csv_data}"
	# print("Script Python generato dall'LLM e salvato su 'script_output.py':")
	# script_code = generate_llm(prompt1)
	# import re
	# match = re.search(r"```python(.*?)```", script_code, re.DOTALL)
	# if match:
	#     clean_code = match.group(1).strip()
	# else:
	#     lines = script_code.splitlines()
	#     code_lines = [line for line in lines if line.strip().startswith("import ") or line.strip().startswith("#") or line.strip().startswith("df ") or line.strip().startswith("df.")]
	#     clean_code = "\n".join(code_lines)
	# print(clean_code)
	# with open("script_output.py", "w", encoding="utf-8") as script_file:
	#     script_file.write(clean_code)

	# Richiesta utente generica
	user_request = "Pulire il dataset, calcolare il salario medio per professione e visualizzare il risultato in un grafico."
	steps = split_request_in_steps(user_request)
	final_code = ""
	for step in steps:
		prompt = f"{step}\n\n{csv_data}"
		print(f"Prompt step: {step}")
		script_code = generate_llm(prompt)
		import re
		match = re.search(r"```python(.*?)```", script_code, re.DOTALL)
		if match:
			clean_code = match.group(1).strip()
		else:
			lines = script_code.splitlines()
			code_lines = [line for line in lines if line.strip().startswith("import ") or line.strip().startswith("#") or line.strip().startswith("df ") or line.strip().startswith("df.") or line.strip().startswith("plt.")]
			clean_code = "\n".join(code_lines)
		print(clean_code)
		final_code += clean_code + "\n\n"
	with open("script_output.py", "w", encoding="utf-8") as script_file:
		script_file.write(final_code)
