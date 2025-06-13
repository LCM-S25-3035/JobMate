#!/bin/bash
# Script to run SonarQube scanner with timeout

echo "Starting SonarQube scan with 5 minute timeout..."
timeout 300s sonar-scanner \
  -Dsonar.projectKey=$SONAR_PROJECT_KEY \
  -Dsonar.host.url=$SONAR_HOST_URL \
  -Dsonar.token=$SONAR_TOKEN \
  -Dsonar.scm.disabled=true \
  -Dsonar.sources=src \
  -Dsonar.exclusions=**/*.ipynb,**/logs/**,**/node_modules/**,**/__pycache__/**,**/*.pyc,**/*.pyo \
  -Dsonar.python.version=3.10 \
  -Dsonar.verbose=true \
  -X

# Check exit status
STATUS=$?
if [ $STATUS -eq 124 ]; then
  echo "SonarQube scan timed out after 5 minutes"
  exit 1
elif [ $STATUS -ne 0 ]; then
  echo "SonarQube scan failed with exit code $STATUS"
  exit $STATUS
else
  echo "SonarQube scan completed successfully!"
  exit 0
fi
