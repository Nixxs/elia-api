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

## **Next Steps**
- Set up the FastAPI back-end to handle Gemini and ArcGIS REST API integrations.
- Build a React front-end with Google Maps integration.
- Develop function-calling workflows to query and interpret ArcGIS Server data.
- Enable users to upload or provide live URLs for geospatial analysis.

---

## **License**
This project is licensed under the MIT License. See `LICENSE` for more details.

