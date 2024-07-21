import os
import streamlit

if __name__ == "__main__":
    
    streamlit.set_page_config(page_title="Home Page", layout="wide")

    # Print the homepage content
    with open(os.path.join(os.getcwd(), "htmls", "index.html"), "r") as f:
        homepage_content = f.read()  
    
    streamlit.markdown(homepage_content, unsafe_allow_html=True)

