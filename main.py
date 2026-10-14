
## make sure to use : "uv run main.py" to run the agent

##### importing libraries
import json
from dotenv import load_dotenv
import os
import sys
from datetime import datetime
from openai import OpenAI


##### loading the .env file into my OS
##### so i can get the variables declared in it 
load_dotenv()


##### geting the api key from the environment 

API_KEY = os.getenv("GEMINI_API_KEY")



##### checks if the API KEY is there or not 
##### if not, the program stops and prints a message before it does 
if not API_KEY:
    sys.exit("Missing GEMINI_API_KEY. I must get a free api key at aistudio.google.com and set it first ")


##### choosing the model of gemini i am going to use,
##### so we either store it inside the environment or we definr it directly  
MODEL = os.getenv("GEMINI_MODEL")



##### running the AI agent client by giving it the URL and the API
client = OpenAI(
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key = API_KEY,
)



### ------ 1: Creating the tools (python functions) ------ ##



# getting the current date and time
def get_time() -> str:
    return datetime.now().strftime("%A %Y-%m-%d %H:M")


# simple calculator
def calculate(expression:str) -> str:
    allowed = "0123456789+-*/(). %"
    # checking for unallowed carachters
    for carachter in expression:
        if carachter not in allowed:
            return "Error: Invalid carachters used."
    # calculate the answer
    try:
        return str(eval(expression))
    # getting exceptions or errors and printing them
    except Exception as e:
        return f"Error: {e}"


# writing notes function : keeps the notes file inside the project folder 
def write_note(filename:str, text:str)-> str:
    filename = os.path.basename(filename)
    
    # we tell the program to consider the open(filename, "a", encoding="UTF-8")
    # as f to avoid repetition in case we add more lines afterwards
    with open(filename, "a", encoding="UTF-8") as f :
        f.write(text + "\n")
    
    return f"Your note is saved to {filename}"
    
TOOL_FUNCTIONS={
    "get_time":get_time,
    "calculate":calculate,
    "write_note":write_note,
}


### ------ 2: The tools descriptions the model reads to be able to call afterwards ------ ##


### we define each function here in its own block
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description":"get the current data and time",
            "parameters": {"type":"object", "properties":{}}
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a math expression, e.g. '18/100*250' ",
            "parameters": {
                "type": "object",
                "properties":{"expression":{"type":"string"}},
                "required":["expression"]
            }
        }
    },
    {
        "type": "function",
        "function":{
            "name":"write_note",
            "description": "Appends a new line of text directly to the user's notes file whenever they want to save a note, thought, or reminder.",
            "parameters": {
                "type": "object",
                "properties":{"filename":{"type":"string"},"text":{"type":"string"}}, 
                "required":["filename","text"]
            }
        } 
    }
]


### ------ 3: The loop that keeps the agent running ------ ##

def run_agent(messages:list,max_steps:int=8) -> str:
    ## we make sure the agent does run an infinit amount of times so we use the "max_steps" limits
    for _ in range(max_steps):
        ## generate the response
        response = client.chat.completions.create(
            model = MODEL, messages=messages, tools=tools
        )
        ## getting only the last message from the response
        msg = response.choices[0].message
        ## append the last AI message to messages list to keep track of the conversation's context
        messages.append(msg)
        ## checking if agent needs any tools
        ## this keeps checking each time the loop runs until 
        ## no tools are needed then we show the result as the final message
        if not msg.tool_calls:
            return msg.content or ""
        ## what's inside msg block? : 

        #msg:{
        #    "role": "assistant",
        #    "content": null,
        #    "tool_calls": [
        #        {
        #            "id": "call_123",
        #            "type": "function",
        #            "function": {
        #                "name": "get_weather",
        #                "arguments": "{\"location\": \"Paris\"}"
        #            }
        #        }
        #    ]
        #}

        ## if tools are neeeded 
        for call in msg.tool_calls:
            ## storing function's name 
            name = call.function.name
            try:
                ## using the json.loads to avoid getting a string like so: '{"key":"value",...}' but instead I get {"key":"value"} so I can unpack it using **arguments
                arguments = json.loads(call.function.arguments or "{}")
                result = TOOL_FUNCTIONS[name](**arguments)
            except Exception as e:
                result = f"Tools error{e}"

            ## printing a line in the console to track how my agent work
            print(f"[tool] {name}({call.function.arguments}) ->{result}")
            ## then we append the result in the messages list so the agent keeps track of what it did 
            messages.append({
                "role":"tool",
                "tool_call_id":call.id,
                "content":str(result),
            })

    ## if we pass the max steps number set earlier the Agent stops and shows the following 
    return "stopped : too many steps."




### ------ 4: Chat with memory ------ ##
if __name__ == "__main__" :
    ## setting instructions for the agent to follow 
    messages=[
        {
            "role":"system",
            "content":("You re a funny and helpful assistant. Use tools when they help."
                       "Never guess the time or do math in your head; use the tools."),
        }
    ]

    print(f"Agent ready (model:{MODEL}). type 'quit' to exit")

    while True:
        try:
            user= input("\n You: ")
        except(EOFError,KeyboardInterrupt):
            break

        if user.strip().lower() in ("quit","exit"):
            break
        ## in case the user enters blank spaces (tabs or enters)
        if not user.strip():
            continue

        ## adding the users text to the messages list 
        messages.append({"role":"user", "content":user})

        ## printing the agents result or answer
        try:
            print("Agent:",  run_agent(messages))
        except Exception as e:
            print(f"Error talking to your agent: {e}")







