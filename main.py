from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import uvicorn
import joblib
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Load the dataset (ensure the correct path)
data = pd.read_csv('twitter_leaders.csv')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Accept requests from all domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the trained model and TF-IDF vectorizer
model = joblib.load('twitter_leaders_model.pkl')
tfidf_vectorizer = joblib.load('tfidf_vectorizer.pkl')

# Serve static files (adjust path if needed)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Route to serve the HTML file
@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read())

# Route to get PQ score based on username
@app.get("/api/scores/{username}")
async def get_score(username: str):
    user_data = data[data['username'].str.lower() == username.lower()]

    if user_data.empty:
        raise HTTPException(status_code=404, detail="User not found")

    user_info = user_data.iloc[0]
    
    # Predicting the PQ score based on the bio
    bio_vectorized = tfidf_vectorizer.transform([user_info["bio"]])  # Transform the bio using TF-IDF
    pq_score = model.predict(bio_vectorized)  # Make prediction using the loaded model

    return {
        "username": user_info["username"],
        "bio": user_info["bio"],
        "profile_url": user_info["profile_url"],
        "location": user_info["location"],
        "website": user_info["website"],
        "PQ_score": pq_score[0]  # Extracting the first prediction
    }

# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
