#!/bin/bash

echo "Installing serverless framework and dependencies..."
npm install -g serverless
npm install serverless-python-requirements

echo "Deploying to AWS Lambda..."
serverless deploy

echo "Deployment complete!"
echo "Your API will be available at the URL shown above."