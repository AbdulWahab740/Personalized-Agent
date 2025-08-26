# Personalized Automation Agent

A Personalized AI Automation Agent that helps automate tasks across LinkedIn and Gmail with a single user input.
It uses LangChain, LangGraph, FastAPI, and Streamlit to provide an interactive and extensible workflow.

# 🚀 Features

🔹 **1. LinkedIn Post Creation & Publishing**

- Generates professional LinkedIn posts based on my given **Personal Data**

- Ask me to review/change

- Upload and publish the post automatically.

🔹 **2. LinkedIn Profile Analytics**

- Upload your LinkedIn Analytics Excel/CSV file.

- Agent analyzes your profile performance.

- Ask for top posts, demographics, general overview, 

= Suggests improvements for engagement and reach.

🔹 **3. LinkedIn Post Analytics**

- Provide a LinkedIn post URL.

- Agent analyzes content
  
= Suggests changes for better content performance.

🔹 **4. Email Agent (Gmail Automation)**

- Generate professional emails with AI.

- Review/edit drafts before sending.

= Send emails using Gmail API with one click.

- Human-in-the-loop flow with LangGraph to ensure approval before sending.

🔹 **5. Event Agent (Calender Events Automation)**

- Generate the details for the event

- Review/edit the event details before sending ( Human in the loop )

= After the approval, it creates Calender events

  
# ⚙️ Tech Stack
```
Python
LangChain → for LLM-driven tools & agents
LangGraph → for stateful workflows & human-in-the-loop approvals
FastAPI → backend API for agent orchestration
Streamlit → frontend for user interaction
Google Gmail API → send emails directly via Gmail
Qdrant → memory/personalized info preservation
```

# 🏗️ Architecture
```
User Input → FastAPI → Main Agent → Tools
                                ↳ LinkedIn Post Agent
                                ↳ Profile Analytics Agent
                                ↳ Post Analytics Agent
                                ↳ Email Agent (draft + send)
```

▶️ Run Locally 
  
1️⃣ Clone the repository  
```
git clone https://github.com/AbdulWahab740/personal-agent.git
cd personal-agent
```  
2️⃣ Install dependencies  
```pip install -r requirements.txt```

3️⃣ Setup Gmail and Calender API and GROQ API

Create credentials on Google Cloud Console
.

Download credentials.json and place it in the root folder.

On first run, you’ll authenticate and generate gmailtoken.json.

Visit Grok website for the api!

4️⃣ Run FastAPI backend
```uvicorn app:app --reload ```

5️⃣ Run Streamlit frontend
```streamlit run frontend.py```

# 💡 Usage

Open the Streamlit app.

Enter your request in plain English, e.g.:

- "Write a LinkedIn post about AI trends in 2025"

- "Analyze this LinkedIn post: <url>"

- "Can you write an email to example@gmail.com for an invitation to our event on 5 September 2025?"

Upload LinkedIn analytics Excel if needed.

Review outputs.

Approve & send emails directly from the UI.

✅ Example Flow (Email Agent)

Input:

Can you write an email to abdulwahab272006@gmail.com to invite him to our product launch at Serena, Sept 5, 2025.


Agent Generates Draft:

To: abdulwahab272006@gmail.com
Subject: Product Launch Invitation
Body: Dear Abdulwahab, we are pleased to invite you to our product launch on September 5, 2025, at Serena. We look forward to your presence.

User reviews & edits.

Click "Send Email" → Sent via Gmail API.

# 🔮 Future Improvements

🔹 Automate LinkedIn scheduling.

🔹 Extend analytics to other social media platforms.

🔹 Multi-agent memory with Qdrant for personalization.

# 🧑‍💻 Author

Abdul Wahab
AI & Data Science Enthusiast
LinkedIn: [abwahab07](www.linkedin.com/in/abwahab07)
