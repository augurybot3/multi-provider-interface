import streamlit as st
from pathlib import Path
from openai import OpenAI
from anthropic import Anthropic
import os
import tempfile
import datetime
from dotenv import load_dotenv
import base64
import mimetypes

load_dotenv()

class AnthropicClient:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def list_models(self):
        self.client.models.list(limit=20)

    def encode_image(self, image_path):
        mime_type = mimetypes.guess_type(image_path)[0]
        with open(image_path, "rb") as image_file:
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": mime_type,
                    "data": base64.b64encode(image_file.read()).decode('utf-8')
                }
            }

    def prepare_messages(self, messages, image_path=None):
        formatted_messages = []
        system_message = None
    
        for msg in messages:
            if msg["role"] == "developer":
                system_message = msg["content"]
                continue
            
            if isinstance(msg["content"], list):
                # If the message already contains a list (image + text)
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            elif image_path and msg == messages[-1] and msg["role"] == "user":
                # For new messages with images
                content = [
                    self.encode_image(image_path),
                    {"type": "text", "text": msg["content"]}
                ]
                formatted_messages.append({"role": msg["role"], "content": content})
            else:
                # For regular text messages
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
    
        return formatted_messages, system_message

    def send_message(self, messages, model, params, image_path=None):
        formatted_messages, system_message = self.prepare_messages(messages, image_path)
    
        request_params = {
            "model": model,
            "messages": formatted_messages,
            # "stream": True  # Enable streaming
        }
    
        additional_params = {
            "max_tokens": params["max_tokens"],
            "temperature": params["temperature"],
            "top_p": params["top_p"],
            "top_k": params["top_k"]
        }
    
        if system_message:
            request_params["system"] = system_message
    
        for key, value in additional_params.items():
            if value > 0.01:
                request_params[key] = value
    
        with self.client.messages.stream(**request_params) as stream:
            response_text = ""
            for text in stream.text_stream:
                response_text += text
                yield text
            return response_text

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def encode_image(self, image_path):
        with open(image_path, 'rb') as image_file:
            return {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode('utf-8')}"
                }
            }

    def prepare_messages(self, messages, image_path=None):
        formatted_messages = []

        for msg in messages:
            if msg["role"] == "developer":
                # Convert developer role to system role for OpenAI
                formatted_messages.append({
                    "role": "developer",
                    "content": msg["content"]
                })
            elif isinstance(msg["content"], list):
                # Handle messages that already contain images
                formatted_messages.append(msg)
            elif image_path and msg == messages[-1] and msg["role"] == "user":
                # Handle new messages with images
                formatted_messages.append({
                    "role": "user",
                    "content": [
                        self.encode_image(image_path),
                        {"type": "text", "text": msg["content"]}
                    ]
                })
            else:
                # Handle regular text messages
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        return formatted_messages

    def send_message(self, messages, model, params, image_path=None):
        formatted_messages = self.prepare_messages(messages, image_path)

        request_params = {
            "model": model,
            "messages": formatted_messages,
            "max_tokens": params["max_tokens"],
            "stream": True  # Enable streaming
        }

        if params["temperature_checkbox"]:
            request_params["temperature"] = params["temperature"]
        if params["top_p_checkbox"]:
            request_params["top_p"] = params["top_p"]

        stream = self.client.chat.completions.create(**request_params)
        response_text = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response_text += chunk.choices[0].delta.content
                yield chunk.choices[0].delta.content
        return response_text

class MultiProviderClient:
    def __init__(self):
        self.anthropic_client = AnthropicClient()
        self.openai_client = OpenAIClient()

        self.models = {
            "OpenAI": {
                "03-mini": "03-mini",
                "gpt-4o": "gpt-4o",
                "gpt-4.5-preview":"gpt-4.5-preview",
                "gpt-4o-search-preview":"gpt-4o-search-preview",
                "computer-use-preview-2025-03-11":"computer-use-preview-2025-03-11",
                "gpt-4o-mini": "gpt-4o-mini"
            },
            "Anthropic": {
                "Claude-3 Sonnet": "claude-3-5-sonnet-20241022",
                "Claude-3 Haiku": "claude-3-5-haiku-20241022",
                "Claude-3 Opus": "claude-3-opus-20240229",
                "Claude-3 Sonnet Previous": "claude-3-sonnet-20240229",
                "Claude-3 Haiku Previous": "claude-3-haiku-20240229"
            }
        }

    def send_message(self, messages, provider, model, params, image_path=None):
        if provider == "OpenAI":
            return self.openai_client.send_message(messages, model, params, image_path)
        else:
            return self.anthropic_client.send_message(messages, model, params, image_path)

class StreamlitAIChat:
    def __init__(self):
        self.client = MultiProviderClient()
        self.init_session_state()


    def init_session_state(self):
        defaults = {
            'messages': [],
            'selected_provider': "OpenAI",
            'selected_model': "gpt-4o-mini",
            'logs_dir': Path.cwd() / "logs",
            'params': {
                'max_tokens_checkbox': True,
                'temperature_checkbox': False,
                'top_p_checkbox': False,
                'top_k_checkbox': False,
                'max_tokens': 5000,
                'temperature': 0.0,
                'top_p': 0.0,
                'top_k': 0
            }
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

        st.session_state.logs_dir.mkdir(exist_ok=True)

    def model_conditions(self, selected_model):
        cost = {'input' : str, 'output' : str}
        image_ingestion = bool
        if selected_model == 'gpt-4o-mini':
            cost['input'] = '$0.15 / 1m tokens'
            cost['output'] = '$0.60 / 1m tokens'
            image_ingestion = True
        elif selected_model == 'gpt-4o':
            cost['input'] = '$2.50 / 1m tokens'
            cost['output'] = '$10.00 / 1m tokens'
            image_ingestion = True
        elif selected_model == '03-mini':
            cost['input'] = '$1.10 / 1m tokens'
            cost['output'] = '$4.40 / 1m tokens'
            image_ingestion = False
        elif selected_model == 'gpt-4.5-preview-2025-02-27':
            cost['input'] = '$75.00 / 1m tokens'
            cost['output'] = '$150.00 / 1m tokens'
            image_ingestion = True
        elif selected_model == 'computer-use-preview-2025-03-11':
            cost['input'] = '  $3.00 / 1m tokens'
            cost['output'] = '$12.00 / 1m tokens'
            image_ingestion = True
        else:
            cost['input'] = '$ NA'
            cost['output'] = '$ NA'
            image_ingestion = True
        costs = {'input_cost': cost['input'], 'output_cost': cost['output']}
        supports_images = image_ingestion
        return costs, supports_images

    def save_uploaded_file(self, uploaded_file):
        if uploaded_file:
            file_extension = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_file_path = tmp_file.name
            return temp_file_path  # Ensure this is returned correctly
        return None

    def log_message(self, message):
        timestamp = datetime.datetime.now().isoformat()
        log_file = st.session_state.logs_dir / "chat_log.txt"
        with log_file.open("a") as f:
            f.write(f"\n{timestamp}\n{message['role']}: {message['content']}\n---\n")

    def render_parameter_controls(self):
        max_token_container = st.container()
        with max_token_container:
            col1, col2 = st.columns([1,5])
            with col1:
                st.session_state.params["max_tokens_checkbox"] = st.checkbox(
                    "checkbox",
                    value=st.session_state.params["max_tokens_checkbox"], 
                        key="max_tokens_checkbox", 
                        label_visibility="hidden"
                        )
            with col2:
                st.session_state.params['max_tokens'] = st.number_input(
                    "Max Tokens", 
                    min_value=0, 
                    max_value=100000, 
                    value=st.session_state.params["max_tokens"],
                    disabled= not st.session_state.params["max_tokens_checkbox"]
                )
        temperature_container = st.container()
        with temperature_container:
            col1, col2 = st.columns([1, 5])
            with col1:
                st.session_state.params["temperature_checkbox"] = st.checkbox(
                    "checkbox",
                    value=st.session_state.params["temperature_checkbox"],
                    key="temperature_checkbox",
                    label_visibility="hidden"
                )
            with col2:
                st.session_state.params["temperature"] = st.slider(
                    "Temperature",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state.params["temperature"],
                    disabled= not st.session_state.params["temperature_checkbox"]
                )
        top_p_container = st.container()
        with top_p_container:
            col1, col2 = st.columns([1, 5])
            with col1:
                st.session_state.params["top_p_checkbox"] = st.checkbox(
                    "checkbox",
                    value=st.session_state.params["top_p_checkbox"],
                    key="top_p_checkbox",
                    label_visibility="hidden"
                )
            with col2:
                st.session_state.params["top_p"] = st.slider(
                    "Top P",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state.params["top_p"],
                    disabled= not st.session_state.params["top_p_checkbox"]
                )

        top_k_container = st.container()
        with top_k_container:
            col1, col2 = st.columns([1, 5])
            with col1:
                st.session_state.params["top_k_checkbox"] = st.checkbox(
                    "checkbox",
                    value=st.session_state.params["top_k_checkbox"],
                    key="top_k_checkbox",
                    label_visibility="hidden"
                )
            with col2:
                st.session_state.params["top_k"] = st.number_input(
                    "Top K",
                    min_value=0,
                    max_value=100,
                    value=st.session_state.params["top_k"],
                    disabled= not st.session_state.params["top_k_checkbox"]
                )

    def render_sidebar(self):
        with st.sidebar:
            
            provider_expander = st.expander("Provider", expanded=False)
            with provider_expander:

                provider = st.selectbox(
                    "Select Provider",
                    options=list(self.client.models.keys()),
                    key="provider_select"
                )

                model_name = st.selectbox(
                    "Select Model",
                    options=list(self.client.models[provider].keys()),
                    index=1,
                    key="model_select"
                )
                
            image_upload_expander = st.expander("Image Upload", expanded=False)
            with image_upload_expander:
                uploaded_file = st.file_uploader(
                    "Upload an image", 
                    type=['png', 'jpg', 'jpeg', 'gif', 'webp']
                )

            st.session_state.uploaded_file = uploaded_file
            st.session_state.selected_provider = provider
            st.session_state.selected_model = self.client.models[provider][model_name]

            if st.session_state.provider_select == "OpenAI":
                dev_msg = st.text_area("Developer Message", height=100)
            elif st.session_state.provider_select == "Anthropic":
                dev_msg = st.text_area("System Message", height=100)
                
            col1, col2 = st.columns([1, 1])
                
            with col1:        
                if st.button("Clear Chat"):
                    st.session_state.messages = []
                    st.rerun()
                    
            with col2:
                if st.button(f"Set Msg"):
                    if dev_msg:
                        if st.session_state.provider_select == "OpenAI":
                            message = {"role": "developer", "content": dev_msg}
                        elif st.session_state.provider_select == "Anthropic":
                            message = {"role": "system", "content": dev_msg}
                        st.session_state.messages.append(message)
                        self.log_message(message)
            
                
            with st.expander("Additional Settings"):
                st.write(self.render_parameter_controls())

    def render_chat(self):
        st.title("Multi-Provider Chat Interface")

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if isinstance(message["content"], list):
                    # Render both text and images if the content is a list
                    for content_item in message["content"]:
                        if content_item["type"] == "text":
                            st.write(content_item["text"])
                        elif content_item["type"] == "image":
                            # Handle Anthropic format
                            image_data = content_item["source"]["data"]
                            st.image(f"data:image/jpeg;base64,{image_data}", use_container_width="auto")
                        elif content_item["type"] == "image_url":
                            # Handle OpenAI format
                            image_url = content_item["image_url"]["url"]
                            st.image(image_url, use_container_width="auto")
                else:
                    st.write(message["content"])
        
        user_input = st.chat_input("Type your message...", key="ci")

        if user_input:
            temp_image_path = None
            if st.session_state['uploaded_file']:
                temp_image_path = self.save_uploaded_file(st.session_state.uploaded_file)
                # Create message with image based on provider
                if st.session_state.selected_provider == "OpenAI":
                    user_message = {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_input},
                            self.client.openai_client.encode_image(temp_image_path)
                        ]
                    }
                else:  # Anthropic
                    user_message = {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_input},
                            self.client.anthropic_client.encode_image(temp_image_path)
                        ]
                    }
            else:
                user_message = {"role": "user", "content": user_input}

            st.session_state.messages.append(user_message)
            self.log_message(user_message)

            # Display the user message
            with st.chat_message("user", avatar=":material/person:"):
                if isinstance(user_message["content"], list):
                    for content_item in user_message["content"]:
                        if content_item["type"] == "text":
                            st.write(content_item["text"])
                        elif content_item["type"] == "image":
                            image_data = content_item["source"]["data"]
                            st.image(f"data:image/jpeg;base64,{image_data}", use_container_width="auto")
                        elif content_item["type"] == "image_url":
                            st.image(content_item["image_url"]["url"], use_container_width="auto")
                else:
                    st.write(user_message["content"])

            # Get and display the streamed response
            with st.chat_message("assistant", avatar=":material/computer:"):
                message_placeholder = st.empty()
                full_response = ""

                try:
                    # Stream the response
                    for response_chunk in self.client.send_message(
                        st.session_state.messages,
                        st.session_state.selected_provider,
                        st.session_state.selected_model,
                        st.session_state.params,
                        temp_image_path
                    ):
                        full_response += response_chunk
                        # Update the message placeholder with the growing response
                        message_placeholder.markdown(full_response + " ")

                    # Final update without the cursor
                    message_placeholder.markdown(full_response)

                    # Clean up the temporary image file if it exists
                    if temp_image_path:
                        os.unlink(temp_image_path)

                    # Add the complete response to the message history
                    assistant_message = {"role": "assistant", "content": full_response}
                    st.session_state.messages.append(assistant_message)
                    self.log_message(assistant_message)

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    if temp_image_path and os.path.exists(temp_image_path):
                        os.unlink(temp_image_path)

def main():
    chat_app = StreamlitAIChat()
    chat_app.render_sidebar()
    chat_app.render_chat()

if __name__ == "__main__":
    main()