"""
Utility functions for the Campus Event Management Agent Workshop.

This module provides helper functions for:
- Converting Python functions to tool schemas
- Converting agent responses to trace format for evaluation
"""

import inspect
import json
from typing import Any, Callable, Dict, List, get_type_hints, get_origin, get_args
from datetime import datetime


def function_to_tool_schema(func: Callable) -> Dict[str, Any]:
    """
    Convert a Python function to a tool schema compatible with Microsoft Agents Framework.
    
    This function extracts:
    - Function name
    - Docstring as description
    - Parameters with type hints and Field descriptions (if using Annotated)
    - Required parameters
    
    Args:
        func: The Python function to convert
        
    Returns:
        A dictionary representing the tool schema
        
    Example:
        >>> from typing import Annotated
        >>> from pydantic import Field
        >>> 
        >>> def register_for_event(
        ...     student_id: Annotated[str, Field(description="Student ID")],
        ...     event_id: Annotated[str, Field(description="Event ID")],
        ...     student_name: Annotated[str, Field(description="Student's full name")]
        ... ) -> str:
        ...     '''Register a student for a campus event.'''
        ...     return "Success"
        >>> 
        >>> schema = function_to_tool_schema(register_for_event)
    """
    # Get function signature
    sig = inspect.signature(func)
    
    # Get function docstring
    description = inspect.getdoc(func) or f"Execute {func.__name__}"
    
    # Get type hints (handles Annotated types)
    type_hints = get_type_hints(func, include_extras=True)
    
    properties = {}
    required = []
    
    for param_name, param in sig.parameters.items():
        if param_name == 'self':
            continue
            
        # Get type hint
        param_type_hint = type_hints.get(param_name, Any)
        
        # Extract base type and Field metadata if using Annotated
        param_description = ""
        base_type = param_type_hint
        
        # Check if it's an Annotated type
        origin = get_origin(param_type_hint)
        if origin is not None:
            args = get_args(param_type_hint)
            if args:
                base_type = args[0]
                # Look for Field in metadata
                for metadata in args[1:]:
                    if hasattr(metadata, 'description'):
                        param_description = metadata.description
                        break
        
        # Map Python types to JSON schema types
        json_type = _python_type_to_json_type(base_type)
        
        param_schema = {"type": json_type}
        if param_description:
            param_schema["description"] = param_description
        
        properties[param_name] = param_schema
        
        # Check if parameter is required (no default value)
        if param.default == inspect.Parameter.empty:
            required.append(param_name)
    
    # Build the tool schema
    tool_schema = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
    }
    
    return tool_schema


def _python_type_to_json_type(python_type: Any) -> str:
    """
    Map Python types to JSON schema types.
    
    Args:
        python_type: The Python type to convert
        
    Returns:
        The corresponding JSON schema type as a string
    """
    type_mapping = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }
    
    # Handle basic types
    if python_type in type_mapping:
        return type_mapping[python_type]
    
    # Handle typing generics
    origin = get_origin(python_type)
    if origin is list:
        return "array"
    elif origin is dict:
        return "object"
    
    # Default to string for unknown types
    return "string"


def convert_agent_response_to_trace(response) -> List[Dict[str, Any]]:
    """
    Convert a Microsoft Agent Framework AgentRunResponse to a standardized trace format.
    
    This format is compatible with Azure AI Evaluation's TaskAdherenceEvaluator,
    which requires traces to assess whether the agent followed the expected workflow.
    
    Args:
        response: AgentRunResponse object or dict from agent.run()
        
    Returns:
        A list of trace entries, each representing a message in the conversation
        
    Example:
        >>> response = await agent.run("Register me for AI Workshop")
        >>> trace = convert_agent_response_to_trace(response)
        >>> # Use trace with TaskAdherenceEvaluator
    """
    # Convert to dict if it's an object
    response_dict = response if isinstance(response, dict) else response.to_dict()
    
    trace = []
    created_at = response_dict.get("created_at")
    run_id = response_dict.get("response_id")
    
    for msg in response_dict.get("messages", []):
        role = msg.get("role", {}).get("value")
        content_list = []
        
        for content in msg.get("contents", []):
            ctype = content.get("type")
            
            if ctype == "function_call":
                # Assistant initiated a tool call
                content_list.append({
                    "type": "tool_call",
                    "tool_call_id": content.get("call_id"),
                    "name": content.get("name"),
                    "arguments": json.loads(content.get("arguments", "{}"))
                })
            
            elif ctype == "function_result":
                # Tool returned a result
                content_list.append({
                    "type": "tool_result",
                    "tool_result": content.get("result")
                })
            
            elif ctype == "text":
                # Normal assistant message
                content_list.append({
                    "type": "text",
                    "text": content.get("text")
                })
        
        # Construct final trace entry
        trace_entry = {
            "createdAt": created_at,
            "run_id": run_id,
            "role": role,
            "content": content_list
        }
        
        # Optional: add tool_call_id for tool messages
        if role == "tool" and content_list and "tool_call_id" not in trace_entry:
            first_content = content_list[0]
            # Try to link tool result with call id
            if msg.get("contents"):
                trace_entry["tool_call_id"] = msg["contents"][0].get("call_id")
        
        trace.append(trace_entry)
    
    return trace


def print_agent_response(response, show_details: bool = False):
    """
    Pretty print an agent response.
    
    Args:
        response: AgentRunResponse from agent.run()
        show_details: If True, show full message history and metadata
    """
    print("=" * 60)
    print("AGENT RESPONSE")
    print("=" * 60)
    
    # Main response text
    if hasattr(response, 'text'):
        print(f"\n{response.text}\n")
    elif hasattr(response, 'content'):
        print(f"\n{response.content}\n")
    
    if show_details:
        print("\n" + "-" * 60)
        print("DETAILS")
        print("-" * 60)
        
        # Show tool calls if any
        response_dict = response if isinstance(response, dict) else response.to_dict()
        
        tool_calls = []
        for msg in response_dict.get("messages", []):
            for content in msg.get("contents", []):
                if content.get("type") == "function_call":
                    tool_calls.append({
                        "name": content.get("name"),
                        "arguments": json.loads(content.get("arguments", "{}"))
                    })
        
        if tool_calls:
            print(f"\n🔧 Tool Calls Made: {len(tool_calls)}")
            for i, tc in enumerate(tool_calls, 1):
                print(f"  {i}. {tc['name']}()")
                for key, value in tc['arguments'].items():
                    print(f"     - {key}: {value}")
        else:
            print("\n🔧 Tool Calls Made: None")
    
    print("=" * 60)


# Export all public functions
__all__ = [
    'function_to_tool_schema',
    'convert_agent_response_to_trace',
    'print_agent_response'
]
