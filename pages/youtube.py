import streamlit as st
from aux import open_info, ai_text_generate, ai_text_stream_generate, image_generate
import json
import pyperclip


def generate_thumbnail_prompts(title, script):
    """
    Gera uma miniatura para o vídeo com base no prompt fornecido.
    """

    response_json_str = ai_text_generate(
        system="Você é um especialista em design de miniaturas para YouTube. Sua tarefa é criar uma descrição de miniatura atraente e otimizada.",
        prompt=f"""Crie uma descrição de miniatura para o vídeo com o título '{title}' e a ideia principal '{script}'. A miniatura deve ser visualmente impactante, incluir texto curto e chamativo, e refletir o conteúdo do vídeo. Gere três variações de miniatura, cada uma com um estilo diferente (por exemplo, minimalista, colorido, com texto grande).
        
         Sua resposta deve ser um objeto JSON com a seguintes chave:
        "prompt": [lista de strings com as 3 opções de prompts de miniatura],
        """,
    )
  
    try:
        image_prompt_data = json.loads(response_json_str)
    except json.JSONDecodeError:
        start_idx = response_json_str.find('{')
        end_idx = response_json_str.rfind('}')
        if start_idx != -1 and end_idx != -1:
            clean_json_str = response_json_str[start_idx : end_idx + 1]
            image_prompt_data = json.loads(clean_json_str)
        else:
            st.error("Erro: A resposta da IA para os títulos não é um JSON válido e não pôde ser corrigida. Tentando extrair o título como texto simples.")
            return response_json_str.split('\n')[0].strip() if response_json_str else "Título padrão", "Justificativa padrão"
    
    prompts = image_prompt_data.get("prompt", "")
    return prompts

def revisor(script, prompt_idea, context):
    """
    Função para revisar o roteiro com instruções mais detalhadas.
    """
    system_instruction = f"""Você é um revisor de roteiros de vídeo para YouTube. Sua tarefa é aprimorar a clareza, engajamento, fluxo, tom, ortografia e otimização para fala do roteiro, evitando repetições."""
    content_prompt = f"""Revise o seguinte roteiro de vídeo para YouTube, sempre considerando que o criador tem o seguinte perfil e áreas de interesse: '{context}',
    e o vídeo é sobre: '{prompt_idea}'.

    Retorne apenas o roteiro revisado, sem explicações sobre as alterações.
    Roteiro original para revisão:
    {script}
    """
    with st.spinner("Revisando o roteiro..."):
        script_placeholder = st.empty()
        revised_script = ""
        for chunk in ai_text_stream_generate(system=system_instruction, prompt=content_prompt):
            revised_script += chunk
            script_placeholder.markdown(revised_script)


    return revised_script


def generate_seo_titles(prompt, context):
    """
    Gera múltiplas opções de títulos otimizados para SEO e seleciona o melhor.
    A função espera um JSON como resposta do modelo.
    """
    system_instruction = "Você é um especialista em SEO e criador de títulos de vídeos para YouTube."
    content_prompt = f"""Dada a seguinte ideia de vídeo: '{prompt}', e o contexto do criador: '{context}',
    gere 5 opções de títulos altamente otimizados para SEO. Inclua palavras-chave relevantes,
    crie um senso de curiosidade e urgência, e pense em como o algoritmo do YouTube e o público vão reagir.
    Em seguida, analise essas 5 opções e escolha a *melhor* delas, justificando brevemente sua escolha.

    Sua resposta deve ser um objeto JSON com as seguintes chaves:
    "titles": [lista de strings com as 5 opções de títulos],
    "best_title": "o título escolhido",
    "justification": "justificativa para a escolha"
    """
    try:
        response_json_str = ai_text_generate(system=system_instruction, prompt=content_prompt)
        try:
            titles_data = json.loads(response_json_str)
        except json.JSONDecodeError:
            start_idx = response_json_str.find('{')
            end_idx = response_json_str.rfind('}')
            if start_idx != -1 and end_idx != -1:
                clean_json_str = response_json_str[start_idx : end_idx + 1]
                titles_data = json.loads(clean_json_str)
            else:
                st.error("Erro: A resposta da IA para os títulos não é um JSON válido e não pôde ser corrigida. Tentando extrair o título como texto simples.")
                return response_json_str.split('\n')[0].strip() if response_json_str else "Título padrão", "Justificativa padrão"
        
        best_title = titles_data.get("best_title", "Título Padrão (falha ao gerar)")
        justification = titles_data.get("justification", "Justificativa não fornecida.")
        return best_title, justification
    except Exception as e:
        st.error(f"Erro ao gerar títulos SEO: {e}")
        return "Título de Vídeo", "Justificativa Padrão"


def generate_youtube_script(prompt):
    """Function to generate a YouTube script based on the provided prompt."""
    saved_info = open_info("saved_info.txt") or ""
    target_audience = open_info("target_audience.txt") or ""
    context = saved_info + "\n" + target_audience

    # 1. Generate SEO Titles and choose the best
    chosen_title, title_justification = generate_seo_titles(prompt, context)
    st.markdown(f"**Título Escolhido:** `{chosen_title}`")
    st.info(f"**Justificativa do Título:** {title_justification}")

    # 2. Generate script for the choosen title
    system_instruction = f"""Você é um roteirista profissional de vídeos para YouTube.
    Seu objetivo é criar um roteiro detalhado e envolvente."""
    content_prompt = f"""O vídeo tem o título '{chosen_title}'. Será baseado na ideia principal: '{prompt}'.
    O criador do vídeo tem o seguinte perfil e áreas de interesse: '{saved_info}'.

    O roteiro deve seguir a seguinte estrutura:
    1.  **Gancho Inicial (Hook):** Algo que prenda a atenção nos primeiros 15 segundos.
    2.  **Introdução:** Apresentar o tema e o que o espectador aprenderá.
    3.  **Desenvolvimento (Corpo do Vídeo):** Dividir o conteúdo em seções lógicas, com transições suaves.
        Use exemplos práticos, analogias e dados, se aplicável, alinhando com os interesses do criador.
    4.  **Conclusão:** Resumir os pontos chave e reforçar a mensagem principal.
    5.  **Chamada para Ação (Call to Action - CTA):** Incentivar o espectador a curtir, comentar, se inscrever ou visitar algum link.

    Considere o seguinte ao escrever:
    * **Público-alvo:** {target_audience}.
    * **Linguagem:** Clara, concisa e envolvente. Evite jargões desnecessários ou explique-os.
    * **Formato:** Markdown, com cabeçalhos para cada seção e marcadores para os pontos.

    Gere o roteiro completo.
    """
    with st.spinner("Gerando o roteiro do vídeo..."):
        script_content = ai_text_generate(system=system_instruction, prompt=content_prompt)

    st.subheader("Roteiro Gerado")

    # 3. Revisar o roteiro
    st.subheader("Roteiro Revisado:")
    revised_script = revisor(script_content, prompt, context)
    # st.markdown(revised_script)

    return revised_script, chosen_title, title_justification # Retorna também o título para uso posterior

def main():    
    st.title("🎥 YouTube - Gerador de roteiros")
    st.subheader("Sobre o que você quer falar hoje?")

    if 'script' not in st.session_state:
        st.session_state.script = ""
        st.session_state.chosen_title = ""
        st.session_state.title_justification = ""
        st.session_state.description = ""
        st.session_state.tags = ""
        st.session_state.thumbnail = []
        st.session_state.results_generated = False
    elif not isinstance(st.session_state.thumbnail, list):
        st.session_state.thumbnail = []

    prompt = st.text_area(
        "Insira sua ideia ou tópico principal para o vídeo:",
        st.session_state.get("prompt_input", ""),
        height=150,
        key="main_prompt_input"
    )
    st.session_state.prompt_input = prompt
  
    if st.button("Gerar Roteiro e Detalhes", key="generate_button"):
        if prompt:
            with st.spinner("Iniciando a geração do roteiro..."):
                script_gen, chosen_title_gen, title_justification_gen = generate_youtube_script(prompt)

                st.session_state.script = script_gen
                st.session_state.chosen_title = chosen_title_gen
                st.session_state.title_justification = title_justification_gen

                st.divider()

                # Generate Description
                st.subheader("Descrição do Vídeo:")
                description_system = "Você é um especialista em marketing digital e YouTube. Sua tarefa é criar uma descrição de vídeo otimizada para SEO."
                description_content = f"Gere uma descrição de vídeo para YouTube otimizada para SEO, baseada no seguinte roteiro. A descrição deve ser envolvente, incluir palavras-chave relevantes do script, e ter uma chamada para ação clara. Mantenha-a concisa, mas informativa. Retorne apenas a descrição, sem explicações ou formatação adicional. Roteiro: {script_gen}"
                with st.spinner("Gerando a descrição..."):
                    description_gen = ai_text_generate(system=description_system, prompt=description_content)
                    st.markdown(description_gen)
                    st.session_state.description = description_gen

                st.divider()

                # Generate Tags
                st.subheader("Tags do Vídeo:")
                tags_system = "Você é um especialista em SEO para YouTube. Sua tarefa é gerar as melhores tags para um vídeo."
                tags_content = f"Gere as 10-15 melhores tags para um vídeo no YouTube, baseadas no seguinte roteiro e no título '{chosen_title_gen}'. As tags devem ser relevantes, incluir variações de palavras-chave e abranger tópicos abordados no vídeo. Separe as tags por vírgulas. Retorne apenas as tags, sem explicações ou formatação adicional. Roteiro: {script_gen}"
                with st.spinner("Gerando as tags..."):
                    tags_gen = ai_text_generate(system=tags_system, prompt=tags_content)
                    st.markdown(tags_gen)
                    st.session_state.tags = tags_gen

                st.session_state.results_generated = True
                st.success("Geração concluída!")

                st.divider()

                # Generate thumbnail
                st.subheader("Miniatura do Vídeo:")
                with st.spinner("Generating your image... Please wait."):
                    prompts = generate_thumbnail_prompts(chosen_title_gen, script_gen)
                    for prompt in prompts:
                        image, _ = image_generate(prompt=prompt)   
                        if image:
                            st.image(image)
                            st.session_state.thumbnail.append(image)
                        if not image:
                            st.warning("No image was returned.")

                st.rerun() 
        else:
            st.warning("Por favor, insira um tópico para gerar o roteiro.")

    if st.session_state.results_generated:
        st.subheader("Resultados Gerados:")
        st.markdown(f"**Título Escolhido:** `{st.session_state.chosen_title}`")
        st.info(f"**Justificativa do Título:** {st.session_state.title_justification}")
        st.subheader("Roteiro Revisado:")
        st.markdown(f"{st.session_state.script}")
        st.subheader("Descrição do Vídeo:")
        st.markdown(f"{st.session_state.description}")
        st.subheader("Tags do Vídeo:")
        st.markdown(f"{st.session_state.tags}")
        
        if st.button("Copiar", key="copy_all_button"):
            full_content_to_copy = f"# Título:\n{st.session_state.chosen_title}\n\n# Justificativa:\n{st.session_state.title_justification}\n\n# Roteiro:\n{st.session_state.script}\n\n# Descrição:\n{st.session_state.description}\n\n# Tags:\n{st.session_state.tags}"
            pyperclip.copy(full_content_to_copy)
            st.success("Todo o conteúdo copiado para a área de transferência!")

        for i, thumbnail in enumerate(st.session_state.thumbnail):
            st.markdown(f"**Miniatura {i + 1}:**")
            st.image(thumbnail)

if __name__ == "__main__":
    main()