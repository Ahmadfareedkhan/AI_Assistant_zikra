from openai import OpenAI
import time, json, os, csv, re
from dotenv import load_dotenv
from dotenv import load_dotenv
import ssl
import random
import streamlit as st


load_dotenv()

# Paste your OpenAI API key here!
api_key = st.secrets.openai.OPENAI_API_KEY
client = OpenAI(api_key=api_key)

# Paste your Assistant ID here!
assistant_id = "asst_1A3qfdoGOklFczibJiR7GnPg"

# Select your model!
model = "gpt-4o"

class Assistant:
    functions = {"functions":[]}
    registered_functions = {}

    def __init__(self):
        self.thread_id = "thread_id"


    def modify_assistant(self):
        my_updated_assistant = client.beta.assistants.update(assistant_id=assistant_id,model=model, tools=self.functions["functions"])

    # Threads
    def create_thread(self):
        thread = client.beta.threads.create()
        self.thread_id = thread.id

    def delete_thread(self):
        response = client.beta.threads.delete(self.thread_id)
        print('Thread Deleted Successfully')

    # Messages
    def add_message(self, user_input):
        message = client.beta.threads.messages.create(thread_id=self.thread_id, role='user', content=user_input)

    def get_message(self):
        messages = client.beta.threads.messages.list(self.thread_id)
        output = messages.data[0].content[0].text.value
        
        # Filter out unwanted information
        confirmation_keywords = ["confirmation email", "saved your details"]
        for keyword in confirmation_keywords:
            if keyword in output:
                # Return the part of the message containing the keyword
                return output.split(keyword)[0] + keyword + "."
        
        return output
    
    # Runs
    def run_assistant(self):
        run = client.beta.threads.runs.create(thread_id=self.thread_id, assistant_id=assistant_id)
        return run.id
    
    def retrieve_run(self, run_id):
        run = client.beta.threads.runs.retrieve(thread_id=self.thread_id, run_id=run_id)
        return run
        
    
    # Runs Steps
    def run_require_action(self, run, run_id):
        tool_outputs = []
        if run.required_action:
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = self.registered_functions.get(function_name)
                if function_to_call:
                    function_args = json.loads(tool_call.function.arguments)
                    function_response = function_to_call(**function_args)
                    tool_outputs.append({"tool_call_id": tool_call.id, "output": function_response})
            run = client.beta.threads.runs.submit_tool_outputs(thread_id=self.thread_id, run_id=run_id, tool_outputs=tool_outputs)

    def assistant_api(self):
        self.modify_assistant()
        run_id = self.run_assistant()
        run = self.retrieve_run(run_id)
        while run.status == "requires_action" or "queued":
            run = self.retrieve_run(run_id)
            if run.status == "completed":
                break
            self.run_require_action(run, run_id)
        outputs = self.get_message()
        tokens = run.usage.total_tokens
        return outputs, tokens
    
    # Function calling Decorator
    @classmethod
    def add_func(cls, func):
        cls.registered_functions[func.__name__] = func
        doc_lines = func.__doc__.strip().split('\n')
        func_info = {
            'type': 'function',
            'function': {
                'name': func.__name__,
                'description': doc_lines[0].strip(),
                'parameters': {
                    'type': 'object',
                    'properties': {k.strip(): {'type': v.strip().split(':')[0].strip(), 'description': v.strip().split(':')[1].strip()} 
                                   for k, v in (line.split(':', 1) for line in doc_lines[1:] if ':' in line)},
                    'required': [k.strip() for k, v in (line.split(':', 1) for line in doc_lines[1:] if ':' in line)],
                    'additionalProperties': False
                },
                'strict': True
            }
        }
        
        cls.functions["functions"].append(func_info)

    def speak(self, output, tokens):
        print("\nFrontdesk: ", end='')
        for char in output:
            print(char, end='', flush=True)
            time.sleep(0.08)
        print(f"\nTokens Used: {tokens}")
        print()



@Assistant.add_func
def get_current_date_time():
    """
    Get today's date and time in format Thu Jan 25 16:16:40 IST 2024 and always time format is in 12 hours.
    """
    from datetime import datetime
    now = datetime.now()
    formatted_datetime = now.strftime("%d/%m/%Y, %I:%M:%S %p")
    return formatted_datetime


@Assistant.add_func
def save_user_info(name: str, email: str):
    """
    Save user info in CSV format where name is Name and email is Email.
    name: string: The user's name.
    email: string: The user's email address.
    """
    filename = 'user_data.csv'
    user_exists = False

    # Check if the file exists and read its contents
    if os.path.isfile(filename):
        with open(filename, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Email'] == email:
                    user_exists = True
                    break

    if user_exists:
        # Return a message for existing users in JSON format
        return json.dumps({
            "message": f"Great to meet you again {name}, Let me send you a confirmation email to verify your identity.",
            "user_type": "existing"
        })
    else:
        # Save the new user info
        with open(filename, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['Name', 'Email'])
            
            if file.tell() == 0:
                writer.writeheader()  # Write headers only once if the file is new
            
            # Write the user's info
            writer.writerow({'Name': name, 'Email': email})
        
        # Return a message for new users in JSON format
        return json.dumps({
            "message": f"Thanks for registering {name}, Let me send you a confirmation email.",
            "user_type": "new"
        })


@Assistant.add_func
def send_confirmation_email(name: str, email: str, user_type: str):
    """
    Send a confirmation email to the user.
    name: string: The user's name.
    email: string: The user's email address.
    user_type: string: Indicates if the user is 'new' or 'existing'.
    """
    # Simulate a 20% chance of failure in sending the email
    email_sent_successfully = random.random() > 0.5

    if email_sent_successfully:
        if user_type == 'existing':
            message = f"Welcome back, {name}! I've just sent you a confirmation email to verify your identity."
        else:
            message = f"Thanks for registering, {name}! I've just sent a confirmation email. Please check your inbox and confirm your email address."
        status = "success"
    else:
        message = f"Sorry, {name}. We are currently experiencing issues in sending your confirmation email. Please try again later."
        status = "failure"

    # Return the result in JSON format
    return json.dumps({
        "status": status,
        "message": message
    })


@Assistant.add_func
def create_lead(name: str, email: str, needs: str):
    """
    Create a lead in the sales pipeline and save to a CSV file.
    name: string: The user's name.
    email: string: The user's email address.
    needs: string: Description of the user's needs or interests.
    """
    filename = 'leads.csv'
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow(['Name', 'Email', 'Needs'])  # Write header if file is new
        
        writer.writerow([name, email, needs])
    
    return json.dumps({
        "status": "success",
        "message": f"Lead created for {name} with email {email} and needs: {needs}"
    })



@Assistant.add_func
def check_booking_availability():
    """
    Check and return available time slots for booking a call with a human representative.
    """
    # Implement availability checking logic here
    available_slots = ["2024-08-27 10:00 AM", "2024-08-27 2:00 PM", "2024-08-28 11:00 AM"]
    return json.dumps({
        "available_slots": available_slots
    })

@Assistant.add_func
def create_booking(name: str, email: str, time_slot: str):
    """
    Create a booking for a call with a human representative.
    name: string: The user's name.
    email: string: The user's email address.
    time_slot: string: The selected time slot for the call.
    """
    # Implement booking creation logic here
    return json.dumps({
        "status": "success",
        "message": f"Booking created for {name} with {email} at {time_slot}"
    })

@Assistant.add_func
def create_ticket(name: str, email: str, issue: str):
    """
    Create a support ticket for complex inquiries.
    name: string: The user's name.
    email: string: The user's email address.
    issue: string: Detailed description of the user's complex issue.
    """
    # Implement ticket creation logic here
    return json.dumps({
        "status": "success",
        "message": f"Ticket created for {name} with {email} regarding: {issue}"
    })



if __name__ == "__main__":
    ai = Assistant()
    ai.create_thread()

    try:
        while True:
            user_input = input("You: ")

            if user_input == "0":
                break
            else:
                prompt = user_input

            ai.add_message(prompt)
            output, tokens = ai.assistant_api()
            ai.speak(output, tokens)

    finally:
        ai.delete_thread()
