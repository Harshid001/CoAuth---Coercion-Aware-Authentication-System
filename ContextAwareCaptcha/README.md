# Context-Aware Captcha (Coercion-Aware Authentication System)

## Overview
This project is a **Context-Aware CAPTCHA / Coercion-Aware Authentication System** designed to replace traditional static CAPTCHAs (like identifying traffic lights or reading distorted text) with dynamic, personalized challenges based on a user's recent interactions with an application.

## How it Works
1. **Behavior Tracking**: As a user navigates the site (e.g., viewing pages, clicking products), their interactions are silently tracked and logged.
2. **Risk Assessment**: When authentication or a CAPTCHA is required, these interactions are sent to an AI backend. A machine-learning model (Random Forest classifier) evaluates the behavior to determine if the user is "Low", "Medium", or "High" risk.
3. **Contextual Challenges**: 
   - **Low Risk (Human-like)**: The system asks a simple question based on recent memory, e.g., *"Which of these product IDs did you just view?"*
   - **High Risk (Bot-like)**: The system falls back to a harder, standard question, e.g., *"What is the primary color of the 'Add to Cart' button?"*

This approach provides a smoother experience for real users who naturally remember what they just did, while posing a difficult challenge for automated bots that don't retain visual or contextual memory of their actions.

## Project Structure
The project is divided into three main components:

### 1. `frontend` (Next.js)
A mock e-commerce store acting as the testing ground for the system.
- Built with **Next.js (App Router)**, **React 19**, and **Tailwind CSS**.
- Simulates realistic user journeys with routes like `/products`, `/cart`, and `/checkout`.
- Uses **Zustand** for state management and an interaction tracker (`TrackerProvider`) to record user events globally.
- Includes a `/dashboard` utilizing **Chart.js** to visualize validation and risk metrics.

### 2. `ai_service` (Python / FastAPI)
The core risk assessment engine.
- Built with **FastAPI** and **scikit-learn**.
- Exposes a `/generate-captcha` endpoint that takes the user's interaction history and evaluates it using a Random Forest model.
- Dynamically generates challenge questions and multiple-choice answers tailored to the user's recent context.

### 3. `backend` (Node.js / Prisma)
The data persistence layer.
- Likely handles database operations such as storing interaction logs, user sessions, or validation results.
