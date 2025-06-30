import streamlit as st
from aux import open_info, save_info

saved_info_file = "saved_info.txt"
target_audience_file = "target_audience.txt"

def main():    
    st.title("🛠️ Informações que você quer salvar")
    st.subheader("Compartilhe informações relevantes e preferencias para ter as melhores respostas.")

    # Saved Info Section
    txt = st.text_area(
        "Informações salvas",
        open_info(saved_info_file),
    )

    if st.button("Salvar", key="saved_info"):
        save_info(saved_info_file, txt)
        st.success("Informações salvas com sucesso")

    # Target Audience Section  
    target_audience = st.text_area(
        "Audience alvo",
        open_info(target_audience_file),
    )

    if st.button("Salvar", key="target_audience"):
        save_info(target_audience_file, target_audience)
        st.success("Informações salvas com sucesso!")

if __name__ == "__main__":
    main()