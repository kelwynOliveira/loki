import streamlit as st



def main():

  pages = {
    "": [st.Page("pages/home.py", title="Home", icon="🏠")],
    "Social Media": [
        st.Page("pages/youtube.py", title="YouTube - Gerador de roteiros", icon="🎥"),
    ],
    "Settings": [
        st.Page("pages/saved_info.py", title="Informações salvas", icon="🛠️"),
    ],
  }
  pg = st.navigation(pages)
  pg.run()
  

if __name__ == "__main__":
    main()