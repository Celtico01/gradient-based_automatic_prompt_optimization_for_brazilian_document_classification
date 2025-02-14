import time
import openai
import string
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
#from llama_cpp import Llama
#from salvar_saidas_gpt import salvar_resposta
from dotenv import load_dotenv

load_dotenv()

def parse_sectioned_prompt(s):
    result = {}
    current_header = None
    
    for line in s.split('\n'):
        line = line.strip()
        if line.startswith('# '):
            current_header = line[2:].strip().lower().split()[0]
            current_header = current_header.translate(str.maketrans('', '', string.punctuation))
            result[current_header] = ''
        elif current_header is not None:
            result[current_header] += line + '\n'
    
    return result

def instructGPT_logprobs(prompt, temperature=0.5):
    try:
        client_openai = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    except:
        raise Exception('Sem chave API Openai.')
    try:
        response = client_openai.completions.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=temperature,
            max_tokens=1,
            logprobs=1,
            echo=True,
            timeout=80,
        )
        return response.choices
    except openai.APIError as e:
        print(f"Erro na API: {e}")
        return []
        
def GPT(prompt, n=1, top_p=1, stop=None, presence_penalty=0, frequency_penalty=0, logit_bias={}, timeout=80):
    messages = [{"role": "user", "content": prompt}]
    try:
        client_openai = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    except:
        raise Exception('Sem chave API Openai.')
    try:
        response = client_openai.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages,
            temperature=float(os.getenv("TEMPERATURE", 0.0)),
            n=n,
            top_p=top_p,
            stop=stop,
            max_tokens=int(os.getenv("MAX_TOKENS", 10000)),
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            logit_bias=logit_bias,
            timeout=timeout,
        )
        #for choice in response.choices:
        #    if len(choice.message.content) > 5:
        #        salvar_resposta(choice.message.content)
        
        return [choice.message.content for choice in response.choices]

    except openai.APIError as e:
        print(f"Erro na API: {e}")
        return []

#deepseek
def DEEPSEEK(prompt, n=1, top_p=1, stop=None, presence_penalty=0, frequency_penalty=0, logit_bias={}, timeout=80):
    messages = [{"role": "user", "content": prompt}]
    try:
        #client_deepseek = openai.OpenAI(api_key="<DeepSeek API Key>", base_url="https://api.deepseek.com")
        raise Exception('Não implementado')
    except:
        raise Exception('Sem chave deepseek')
    try:
        response = client_deepseek.chat.completions.create(
            #change
            model=os.getenv("MODEL"),
            messages=messages,
            temperature=float(os.getenv("TEMPERATURE", 0.0)),
            n=n,
            top_p=top_p,
            stop=stop,
            max_tokens=int(os.getenv("MAX_TOKENS", 10000)),
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            logit_bias=logit_bias,
            timeout=timeout,
        )
        #for choice in response.choices:
        #    if len(choice.message.content) > 5:
        #        salvar_resposta(choice.message.content)
        
        return [choice.message.content for choice in response.choices]

    except openai.APIError as e:
        print(f"Erro na API: {e}")
        return []

#llama
def LLAMA(prompt, top_p=1, stop=["[/INST]"], presence_penalty=0, frequency_penalty=0, logit_bias={}):
    try:
        raise Exception('Implementação em andamento.')
        # Caminho local onde o modelo foi baixado
        model_path = os.getenv('LLAMA_MODEL_PATH')
        
        # Carregar o tokenizer e o modelo
        os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

        tokenizer  = AutoTokenizer.from_pretrained("nvidia/Nemotron-Mini-4B-Instruct")
        model = AutoModelForCausalLM.from_pretrained("nvidia/Nemotron-Mini-4B-Instruct", config=model_path)
        # Verificando se há uma GPU e, se houver, movendo o modelo para a GPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)

    except Exception as e:
        raise Exception(f'Erro ao tentar iniciar modelo: {e}')
    
    try:
        # Tokenizando o prompt de entrada
        inputs = tokenizer(prompt, return_tensors="pt").to(device)

        # Gerando a resposta
        output = model.generate(
            **inputs, 
            do_sample=True,
            max_length=os.getenv('MAX_TOKENS_LLAMA'),  # Max tokens para a resposta
            top_p=top_p, 
            temperature=float(os.getenv('TEMPERATURE_LLAMA', 0.0)),
            #presence_penalty=presence_penalty,
            #requency_penalty=frequency_penalty,
            #do_sample=True,  # Ativar amostragem para diversidade de respostas
            #top_k=50,  # Top-K sampling para limitar as opções de saída
            pad_token_id=tokenizer.eos_token_id  # Certifique-se de usar o token correto para finalização
        )

        # Decodificando a resposta gerada
        response = tokenizer.decode(output, skip_special_tokens=True)

        return response

    except Exception as e:
        raise Exception(f'Erro ao gerar resposta: {e}')
'''
#def LLAMA(prompt, top_p=1, stop=["[/INST]"], presence_penalty=0, frequency_penalty=0, logit_bias={}):
#    try:
#        #print(os.getenv('LLAMA_MODEL_PATH'))
#        llama = Llama(os.getenv('LLAMA_MODEL_PATH'),
#                      #chat_format="llama-2",
#                      use_cuda=True if os.getenv('GPU_NVIDIA', 'false').lower() == 'true' else False)
#    except Exception as e:
#       raise Exception(f'Erro ao tentar iniciar modelo: {e}')#
#
#    try:
#        response = llama.create_chat_completion(
#           messages=[{"role": "user", "content": prompt}],
#            max_tokens=int(os.getenv('MAX_TOKENS_LLAMA', 10000)),
 #           temperature=float(os.getenv('TEMPERATURE_LLAMA', 0.0)),
#           top_p=top_p,
#            #stop=stop,
#            presence_penalty=presence_penalty,
#            frequency_penalty=frequency_penalty,
#            logit_bias=logit_bias
#        )
#
#        return [choice['message']['content'] for choice in response['choices']]
#    except Exception as e:
#        raise Exception(f'Erro ao gerar resposta: {e}')

'''


print(LLAMA('hi'))