from fastapi import FastAPI

# 1. Create a FastAPI "instance"
app = FastAPI()

# 2. Define a path operation decorator (the route)
@app.get("/")
# 3. Define the path operation function
def read_root():
    # 4. Return the content (FastAPI converts this to JSON automatically)
    return {"message": "Hello World"}