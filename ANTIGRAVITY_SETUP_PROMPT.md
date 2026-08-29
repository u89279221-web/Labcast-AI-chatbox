# 🤖 Antigravity AI Automated Setup Prompt

**Instructions for the Teammate:**
Copy the text below the line and paste it directly into your Antigravity AI chat. It contains all the exact instructions Antigravity needs to automatically install dependencies, set up environment variables (like API keys), download the embedding models, and start the servers for you!

---

**Copy and paste everything below this line to Antigravity AI:**

<USER_REQUEST>
Hello Antigravity! I need you to automatically set up the local environment for the **LabCast-AI** project in this workspace. Please execute the following setup steps automatically using your tools:

### 1. Backend Setup (`labcast-ai-backend/`)
- Navigate to the `labcast-ai-backend` directory.
- Create a Python virtual environment (`python -m venv venv`).
- Activate the virtual environment and install the dependencies from `requirements.txt`.
- After dependencies are installed, run a quick python script to force-download the embedding model so it's cached locally:
  `python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"`
- Check if a `.env` file exists in `labcast-ai-backend`. If it does not exist, create it with the following template:
  ```env
  DATABASE_URL="sqlite:///./labcast.db"
  GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
  MQTT_BROKER_HOST="127.0.0.1"
  SECRET_KEY="supersecretkey_change_me_in_production"
  ```
- **IMPORTANT**: If you had to create the `.env` file or if the `GEMINI_API_KEY` is still a placeholder, STOP and explicitly ask me (the user) to provide my Gemini API key before proceeding to run the servers.

### 2. Frontend Setup (`frontend/`)
- Navigate to the `frontend` directory.
- Run `npm install` to install all React/Vite dependencies.

### 3. Run the Servers
- Once the API key is verified and dependencies are installed, please run the backend server in the background:
  `uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload`
- Then run the frontend server in the background:
  `npm run dev -- --host`
- Finally, verify the servers are running and let me know the URLs to access the web portal and backend API!
</USER_REQUEST>
