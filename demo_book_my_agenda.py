
import os.path
import re
import openai

from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import StringPromptTemplate
from langchain import OpenAI, LLMChain
from typing import List, Union
from langchain.schema import AgentAction, AgentFinish

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

openai.api_key = "<ADD_YOUR_API_KEY>"
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly','https://www.googleapis.com/auth/calendar.events','https://www.googleapis.com/auth/calendar']

creds = None
def runOuthFlow():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
def getEvent(string: str):
    # uncomment to run google calander
    # runOuthFlow()
    # try:
    #     service = build('calendar', 'v3', credentials=creds)

    #     # Call the Calendar API
    #     now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    #     print('Getting the upcoming 10 events')
    #     events_result = service.events().list(calendarId='primary', timeMin=now,
    #                                           maxResults=10, singleEvents=True,
    #                                           orderBy='startTime').execute()
    #     events = events_result.get('items', [])

    #     if not events:
    #         print('No upcoming events found.')
    #         return

    #     # Prints the start and name of the next 10 events
    #     temp = "\n".join([f"[{ event['start'].get('dateTime', event['start'].get('date'))}] " + event['summary'].replace("\n", "").replace("\r", "") for event in events])
    #     print(temp)
    #     return temp
    #     # for event in events:
    #     #     start = event['start'].get('dateTime', event['start'].get('date'))
    #     #     print(start, event['summary'])

    # except HttpError as error:
    #     print('An error occurred: %s' % error)
    return """ already booked agenda
    start: [2023-05-18 08:00:00] end: [2023-05-18 12:30:00] -> chat over AI
    start: [2023-05-19 08:00:00] end: [2023-05-19 08:30:00] -> chat over AI
    start: [2023-05-20 16:00:00] end: [2023-05-20 17:30:00] -> chat over AI"""

def bookEvent(string: str):
    email, starttime,endtime, date = string.split(",")
    print("\nbooking  with: " + email+ " starttime "+ starttime+ " endtime "+ endtime+ " date "+ date)

    # uncomment to run google calander
    # runOuthFlow()
    # service = build('calendar', 'v3', credentials=creds)
    # event = {
    #     'summary': 'chat over AI',
    #     'description': 'lets have a chat over AI',
    #     'start': {
    #         'dateTime': date.strip()+'T'+starttime.strip()+':00Z',
    #         'timeZone': 'Europe/Amsterdam',
    #     },
    #     'end': {
    #         'dateTime': date.strip()+'T'+endtime.strip()+':00Z',
    #         'timeZone': 'Europe/Amsterdam',
    #     },
    #     'attendees': [
    #         {'email': email},
    #     ]
    #     }
    # print(event)
    # event = service.events().insert(calendarId='primary', body=event).execute()

    return "the event has been booked and event name is chat over AI"
    # else:
    #    return "email is not valid. Please enter valid email" 
tools = [
    Tool(
        name = "GetEvent",
        func=getEvent,
        description="get my last 10 event to see if i have free time"
    ),
    Tool(
        name = "BookEvent",
        func=bookEvent,
        description="use book event for booking meeting. Action Input would be comma seperated email, start time, endtime and date from Question."
    )
     
]

# Set up the base template
template = """You are personal assistant of avinash singh. you need to book event on behalf of him.
you need to first check possible free slot between 8 am  to 5 pm using tool GetEvent. 
do not book meeting if you do not have email id, time, date in Question. 
don't make any assumption if you do not have user email, time and date then do not book meeting and ask user for same.
Always say date in formate [yyyy-mm-dd]  and end time should be starttime+30min
After booking say thanks and good bye 
You have access to the following tools. use only this tool for Action:

{tools}

Use the following format:

Question: I would like to book meeting with Avnash singh
Thought: I must first check availablity. 
Action: GetEvent
Action Input:none
Observation: must tell free slot from response. response contain already booked agenda and can not be used for booking event.
Final Answer: the final answer should be free time range for upcomming 3 day and also ask user email and preferred timeslot to book event.
Question: can you book meeting at X am on y date? 
Thought: I must first check if i have valid user email address , time and date in Question then use tool BookEvent to book meeting.
Action: BookEvent
Action Input: the input to the action for BookEvent.
Observation: must validate email address.
Final Answer: I do not have have a valid email to book meeting.
Observation: answer will be event name or sorry message.

Question: {input}
{agent_scratchpad}"""


class CustomPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]
    
    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        return self.template.format(**kwargs)
    
prompt = CustomPromptTemplate(
    template=template,
    tools=tools,
    # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
    # This includes the `intermediate_steps` variable because that is needed
    input_variables=["input", "intermediate_steps"]
)

class CustomOutputParser(AgentOutputParser):
    
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)


llm = OpenAI(temperature=0.0,openai_api_key=openai.api_key)
llm_chain = LLMChain(llm=llm, prompt=prompt)
tool_names = [tool.name for tool in tools]
output_parser = CustomOutputParser()
agent = LLMSingleActionAgent(
    llm_chain=llm_chain, 
    output_parser=output_parser,
    stop=["\nObservation:"], 
    allowed_tools=tool_names
)
agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)
while True:
        # Note: Python 2.x users should use raw_input, the equivalent of 3.x's input
    userInput = input("User: ")
    if ("exit" or "thanks") in  userInput :
       break
    agent_executor.run(userInput)
