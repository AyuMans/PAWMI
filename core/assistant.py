import json

from core.api_manager import APIManager
from core.tool_manager import ToolManager
from config.personality import SYSTEM_PROMPT
from plugins.system_info import get_system_info
from plugins.datetime_tool import get_datetime
from plugins.app_launcher import open_application


class Assistant:

    def __init__(self):
        self.api_manager = APIManager()

        self.tool_manager = ToolManager()

        self.tool_manager.register(
            "get_system_info",
            get_system_info
        )
        
        self.tool_manager.register(
            "get_datetime",
            get_datetime)
        
        self.tool_manager.register(
            "open_application",
            open_application
            )

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_system_info",
                    "description": "Gets information about the computer's operating system and hardware.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_datetime",
                    "description": "Gets the current date, time, and day from the computer.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                        }
                    }
                },
            {
                "type": "function",
                "function": {
                    "name": "open_application",
                    "description": "Opens an allowed application on the computer.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "application": {
                                "type": "string",
                                "description": "The name of the application to open, such as firefox, terminal, or calculator."
                                }
                            },
                        "required": ["application"]
                        }
                    }
                }
        ]

        self.conversation = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

    def ask(self, prompt: str) -> str:

        self.conversation.append({
            "role": "user",
            "content": prompt
        })

        response = self.api_manager.ask(
            self.conversation,
            self.tools
        )

        return self.process_response(response)

    def process_response(self, response):

        message = response.choices[0].message
    
        # Normal AI response
        if not message.tool_calls:
            answer = message.content
    
            self.conversation.append({
                "role": "assistant",
                "content": answer
            })
    
            return answer
    
        # Save the assistant's tool request
        tool_calls = []
    
        for tool_call in message.tool_calls:
    
            tool_name = tool_call.function.name
            raw_arguments = tool_call.function.arguments
    
            
    
            if raw_arguments is None:
                arguments = {}
    
            elif isinstance(raw_arguments, dict):
                arguments = raw_arguments
    
            elif isinstance(raw_arguments, str):
    
                if raw_arguments.strip() in ("", "null"):
                    arguments = {}
                else:
                    arguments = json.loads(raw_arguments)
    
            else:
                raise ValueError(
                    f"Unexpected tool arguments type: {type(raw_arguments)}"
                )
    
            if arguments is None:
                arguments = {}
    
            # Execute tool
            result = self.tool_manager.execute(
                tool_name,
                **arguments
            )
    
            tool_calls.append({
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": raw_arguments or "{}"
                }
            })
    
            # Tool result
            self.conversation.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })
    
        # Insert the assistant tool-call message BEFORE the tool results
        assistant_message = {
            "role": "assistant",
            "content": message.content,
            "tool_calls": tool_calls
        }
    
        # The tool results were already appended, so move the assistant message
        # immediately before them.
        tool_count = len(tool_calls)
    
        self.conversation[-tool_count:] = [
            assistant_message
        ] + self.conversation[-tool_count:]
    
        # Ask the AI to interpret the tool result
        final_response = self.api_manager.ask(
            self.conversation,
            self.tools
        )
    
        final_message = final_response.choices[0].message
    
        # Handle another tool call if necessary
        if final_message.tool_calls:
            return self.process_response(final_response)
    
        answer = final_message.content
    
        self.conversation.append({
            "role": "assistant",
            "content": answer
        })
    
        return answer