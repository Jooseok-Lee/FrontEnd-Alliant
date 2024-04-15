import openai

def LLM_generation(engine, params, incoming_email, augmented_example, system_msg, api_key):
    # OpenAI API Setting
    openai.api_type = "azure"
    openai.api_base = "https://cap-openai-ask-my-underwriter.openai.azure.com/"
    openai.api_version = "2023-09-15-preview"
    openai.api_key = api_key
    
    # input email
    incoming_subject, incoming_body, incoming_attachment = incoming_email

    # Augmented similar example from semantic search module
    sim_subject, sim_body, sim_attachment, sim_response = augmented_example

    # Parameters
    temperature, max_tokens, top_p, frequency_penalty, presence_penalty, best_of, batch_size = params
    
    incoming_email =   'Subject: ' + str(incoming_subject) + '\n' \
                     + 'Body: ' + str(incoming_body) + '\n' \
                     + 'Attachment: ' + str(incoming_attachment)

    sim_email =   'Subject: ' + str(sim_subject) + '\n' \
                + 'Body: ' + str(sim_body) + '\n' \
                + 'Attachment: ' + str(sim_attachment)
    
    # Prompt engineering
    prompt = 'System message: ' + str(system_msg) + '\n\n' \
            + 'Incoming email-->\n' + str(incoming_email) \
            + 'Past email (Inquiry)-->\n' + str(sim_email) \
            + 'Past email (Answer)-->\n' + str(sim_response) \
            + 'Reply to the incoming email:'

    # Get a response
    response = openai.Completion.create(
            engine = engine,
            prompt = prompt,
            temperature = temperature,
            max_tokens = max_tokens,
            top_p = top_p,
            frequency_penalty = frequency_penalty,
            presence_penalty = presence_penalty,
            best_of = best_of,
            stop = None
          )

    llm_result = response['choices'][0]['text']

    return llm_result