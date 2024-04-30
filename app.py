from flask import Flask, render_template, request
import boto3
import os
import json
import ast

# Set up the default AWS session region
boto3.setup_default_session(region_name='us-west-2')

# Create Boto3 clients for the Bedrock Agent and Bedrock Runtime
bedrock_agent = boto3.client('bedrock-agent')
bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name='us-west-2')

# Replace with your actual agent alias ID
agent_alias_id = 'YSVSZC1H4H' 

# Create the request body for the Bedrock service
body = json.dumps({
        "prompt": "\n\nHuman: generate just the json file (without any other text) with a set of 10 questions for aws solutions architect certification. Only give the proper json structure response and no text\n\nAssistant:",
        "max_tokens_to_sample": 1000
    })

# Invoke the Bedrock model to generate the quiz questions
response = bedrock_runtime.invoke_model(
        body=body,
        modelId="anthropic.claude-v2",
        accept='application/json',
        contentType='application/json'
    )

# Parse the response from the Bedrock service
response_body = json.loads(response.get('body').read().decode())
resp_body_completion = response_body["completion"]

# Extract the JSON-formatted quiz questions from the response
left_index = resp_body_completion.index('[')
right_index = resp_body_completion.rfind(']')
new_response = resp_body_completion[left_index:right_index+1]

# Create the Flask application
app = Flask(__name__, template_folder='template')

# Load the quiz questions into the `questions` variable
questions = json.loads(new_response)

print(questions)

# Define the index route handler
@app.route('/', methods=['GET', 'POST'])
def index():
        # Initialize the practice test and the score
        practice_test = questions
        score = 0

        # Format the options and answers in the questions
        for question in questions:
            if "options" in question:
                question["options"] = [f"{option}" for i, option in enumerate(question["options"])]
            else:
                question["answers"] = [f"{option}" for i, option in enumerate(question["answers"])]
                
        # Handle the POST request (form submission)
        if request.method == 'POST':
            for question in practice_test:
                user_answer = request.form.get(question["question"])
                if "correctAnswer" in question:
                    if user_answer is not None and user_answer.lower() == question["correctAnswer"].lower():
                        score += 1
                else:
                    if user_answer is not None and user_answer.lower() == question["answer"].lower():
                        score += 1
            return render_template('result.html', score=score, total=len(questions))
        
        # Handle the GET request (display the quiz)
        return render_template('index.html', questions=questions)

# Run the Flask application in debug mode
if __name__ == '__main__':
    app.run(debug=True)
