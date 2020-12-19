mkdir -p ~/.streamlit/
echo "[general]
email = \"iveferreirach@unal.edu.co\"
" > ~/.streamlit/credentials.toml
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml