import os
import json
from types import SimpleNamespace

from google import genai
from google.genai import types


class GeminiProvider:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
    
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment.")
    
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-3.5-flash"
    
        self.last_response_content = None

    def ask(self, messages, tools=None):
        

        system_instruction = None
        gemini_messages = []

        for message in messages:

            role = message["role"]

            # System message
            if role == "system":
                system_instruction = message.get("content", "")
                continue

            # Normal user message
            if role == "user":

                # Check if this is a tool result
                if "tool_call_id" in message:
                    continue

                content = message.get("content", "")

                gemini_messages.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(text=content)
                        ]
                    )
                )

                continue

            # Assistant/tool-call message
            if role == "assistant":
            
                # Gemini tool calls must preserve the original
                # response content, including its thought_signature.
                if message.get("tool_calls") and self.last_response_content:
            
                    gemini_messages.append(
                        self.last_response_content
                    )
            
                    continue
            
                content = message.get("content")
            
                if content:
                    gemini_messages.append(
                        types.Content(
                            role="model",
                            parts=[
                                types.Part(text=content)
                            ]
                        )
                    )
            
                continue

            # Tool result
            if role == "tool":

                tool_call_id = message.get(
                    "tool_call_id"
                )

                tool_result = message.get(
                    "content",
                    ""
                )

                # Find the corresponding tool call
                tool_name = None

                for previous in reversed(messages):

                    if previous.get("role") != "assistant":
                        continue

                    for tool_call in previous.get(
                        "tool_calls",
                        []
                    ):

                        if tool_call["id"] == tool_call_id:
                            tool_name = tool_call[
                                "function"
                            ]["name"]
                            break

                    if tool_name:
                        break

                if tool_name:

                    try:
                        result_data = json.loads(
                            tool_result
                        )
                    except json.JSONDecodeError:
                        result_data = tool_result

                    function_response = (
                        types.Part.from_function_response(
                            name=tool_name,
                            response={
                                "result": result_data
                            }
                        )
                    )

                    gemini_messages.append(
                        types.Content(
                            role="user",
                            parts=[
                                function_response
                            ]
                        )
                    )

        # Convert PAWMI tools to Gemini declarations
        gemini_tools = None

        if tools:

            declarations = []

            for tool in tools:

                function = tool["function"]

                declarations.append(
                    types.FunctionDeclaration(
                        name=function["name"],
                        description=function["description"],
                        parameters=function["parameters"]
                    )
                )

            gemini_tools = [
                types.Tool(
                    function_declarations=declarations
                )
            ]

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=gemini_tools
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=gemini_messages,
            config=config
        )

        return self._convert_response(response)

    def _convert_response(self, response):

            candidate = response.candidates[0]
        
            # IMPORTANT:
            # Preserve Gemini's original Content object.
            # This contains the thought_signature required by Gemini 3.
            self.last_response_content = candidate.content
        
            parts = candidate.content.parts
        
            text = None
            tool_calls = []
        
            for index, part in enumerate(parts):
        
                if part.text:
                    text = part.text
        
                if part.function_call:
        
                    function_call = part.function_call
        
                    tool_id = getattr(
                        function_call,
                        "id",
                        None
                    )
        
                    if tool_id is None:
                        tool_id = f"gemini_call_{index}"
        
                    tool_calls.append(
                        SimpleNamespace(
                            id=tool_id,
                            type="function",
                            function=SimpleNamespace(
                                name=function_call.name,
                                arguments=json.dumps(
                                    dict(function_call.args)
                                )
                            )
                        )
                    )
        
            message = SimpleNamespace(
                content=text,
                tool_calls=tool_calls if tool_calls else None
            )
        
            choice = SimpleNamespace(
                message=message
            )
        
            return SimpleNamespace(
                choices=[choice]
            )        
    
    