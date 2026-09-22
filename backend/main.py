from fastapi import FastAPI
app = FastAPI(title="Weather Advisory Support Bot")


@app.get("/")
def main():
    return {"message": "Welcome to the Weather Advisory Support Bot!"}

@app.get("/health")
def health():
    return {"status": "healthy"}
