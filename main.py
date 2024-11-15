from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import uvicorn
import joblib  # Used for loading the trained model

# Create the FastAPI app
app = FastAPI()

# Load the dataset
data = pd.read_csv('twitter_leaders.csv')  # Update with your actual dataset path

# Load the trained model and TF-IDF vectorizer
model = joblib.load('twitter_leaders_model.pkl')  # Load your trained model
tfidf_vectorizer = joblib.load('tfidf_vectorizer.pkl')  # Load your TF-IDF vectorizer

# Serve static files (like index.html)
app.mount("/static", StaticFiles(directory="static"), name="static")  # Adjust if index.html is in a subfolder

# Route to serve the HTML file
@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html") as f:  # Adjust the path as necessary
        return HTMLResponse(content=f.read())

# Route to get PQ score based on username
@app.get("/api/scores/{username}")
async def get_score(username: str):
    # Normalize username to lower case for comparison
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
