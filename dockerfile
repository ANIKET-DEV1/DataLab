FROM python:3.13-slim

# 2. Set the directory inside the container where our code will live
WORKDIR /backend/app

# 3. Stop Python from writing .pyc files and force it to print logs instantly
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4. Copy the dependencies list first (saves build time if code changes but packages don't)
COPY requirements.txt .

# 5. Install the Python packages smoothly without saving temporary cache files
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your local project files into the container
COPY . .

# 7. Document that the container listens on port 8000
EXPOSE 8000

# 8. The command to start the web server when the container boots up
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]