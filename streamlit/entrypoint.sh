#!/bin/bash

# Run health checks
python /streamlit/app/healthcheck/check.py

# Check if the health check passed
if [ $? -eq 0 ]; then
  echo "Health checks passed. Starting Streamlit..."

  # Start Streamlit
  streamlit run main.py --server.port=8501 --server.address=0.0.0.0
else
  echo "Health checks failed. Exiting."
  exit 1
fi
