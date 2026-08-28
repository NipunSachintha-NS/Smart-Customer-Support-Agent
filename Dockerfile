# 1. Base Image එක තෝරා ගැනීම
FROM python:3.12-slim

# 2. Working Directory එක සැකසීම
WORKDIR /app

# 3. පද්ධති යැපීම් (Dependencies) Copy කර Install කිරීම
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Project කේත සියල්ල Container එක තුළට Copy කිරීම
COPY . .

# 5. FastAPI run වන Port එක විවෘත කිරීම
EXPOSE 8000

# 6. Uvicorn Server එක run කිරීමේ විධානය
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]