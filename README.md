# Elia: AI-Powered GIS Assistant

**Elia** stands for **Enhanced Location Intelligence Assistant**. It is a demonstration project designed to showcase how artificial intelligence, specifically **Google's Gemini LLM**, can be integrated with geospatial technologies like **ArcGIS Server** and **Google Maps** to enhance geospatial workflows.

Elia is more than just a tool—it's an assistant that simplifies complex geospatial data by combining the power of modern AI with intuitive user interaction.

---

## **What is Elia?**

Elia is an application that bridges the gap between GIS (Geographic Information Systems) and AI. It aims to:
- Explore how **Google's Gemini LLM** can function as a geospatial assistant.
- Integrate **ArcGIS Server** to analyze and describe geospatial data layers.
- Provide users with a dynamic interface that visualizes geospatial data on **Google Maps**.

---

## **Key Features**
1. **Gemini LLM Integration**:
   - Leverage Google's cutting-edge large language model for natural language interaction.
   - Utilize function calling to process geospatial queries dynamically.

2. **ArcGIS Server Support**:
   - Allow users to input an ArcGIS Server URL.
   - Query the server to list and describe available layers.

3. **Google Maps Integration**:
   - Embed Google Maps for geospatial visualization.
   - Display ArcGIS Server data layers interactively.

4. **Modern Architecture**:
   - Front-End: React for a dynamic user interface.
   - Back-End: FastAPI for a lightweight and efficient Python server.

---

## **Planned Architecture**

### Monorepo Structure
/elia /client # React front-end /server # FastAPI back-end

### Back-End (FastAPI)
- Handles communication with:
  - **Google's Gemini API** for AI functionality.
  - **ArcGIS REST API** for querying geospatial data.
- Processes user inputs (e.g., ArcGIS Server URLs) and provides layer descriptions.

### Front-End (React)
- Provides an intuitive chat-based interface for interacting with Elia.
- Integrates Google Maps for data visualization.

---

## **How Elia Works**
1. **Input**: Users provide an ArcGIS Server URL.
2. **Processing**:
   - Back-end queries the ArcGIS Server for layer information.
   - Gemini LLM interprets and describes the layers in user-friendly language.
3. **Output**:
   - The front-end displays layer descriptions.
   - Visualize layers on Google Maps (if available).

---

## **Why Elia?**

Elia demonstrates how AI and GIS can work together to:
- Simplify the interpretation of complex geospatial datasets.
- Provide actionable insights through conversational AI.
- Bridge traditional GIS workflows with cutting-edge AI technology.

This project is a stepping stone toward smarter geospatial tools, showcasing the potential for enhanced decision-making powered by AI.

---

## **Setting up your dev environment**
- Clone the repo down locally
- setup your .env:
    ```
    ENV_STATE=global
    DB_NAME=elia-api-db
    DB_HOST=localhost
    DB_PORT=5432 
    DB_SSL=prefer 
    DB_USER=postgres
    DB_PASSWORD=pa55word

    FRONTEND_URL=http://127.0.0.1:8080
    JWT_SECRET=somekindofsupersecretsecret
    GOOGLE_API_KEY=thisisobiouslyyourownapikeymakesureitsgotgeminiapi
    BIGQUERY_JSON_KEY_B64=base64 encoded string of the google service account .json
    GOOGLE_LLM_MODEL=gemini-1.5-pro-001
    CHAT_HISTORY_LIMIT=100
    ```
- setup python virtual environment
    - `python -m venv .venv`
- install dependancies with
    - `python -m pip install -r requirements.txt`
- start the database via docker using the docker-compose
    - `docker-compose up -d`
- start the local dev environment with (note that the port is 8001 because docker will run on 8000)
    - `uvicorn elia_api.main:app --reload --port 8001`

---

## **License**
This project is licensed under the MIT License. See `LICENSE` for more details.

