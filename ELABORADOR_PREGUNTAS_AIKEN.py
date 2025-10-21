"""
ELABORADOR_PREGUNTAS_AIKEN
"""

#!/usr/bin/env python
# coding: utf-8

# ### Step 1: Create a new Assistant with File Search Enabled

# In[ ]:





# In[1]:


from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY_HERE")

assistant = client.beta.assistants.create(
  name="Elaborador",
  instructions="""Eres un experto en elaboracion de preguntas didacticas para evaluaciones, 
  NUNCA proporcionas las fuentes ni haces citacines
  NUNCA das un texto de introduccion , ni de despedida 
  UNICAMENTE respondes con las preguntas solictadas haciendo como en el ejemplo, no mas y no menos""",
  model="gpt-4o",
  tools=[{"type": "file_search"}],
)


# In[2]:


# Create a vector store caled "Financial Statements"
vector_store = client.beta.vector_stores.create(name="Texto_adjunto")

# Ready the files for upload to OpenAI
file_paths = ["C:\\Users\\HP\\Desktop\\CATO CURSOS-1-2024\\GER-TI CATO1-2024\\Cursos\\SEMANA 17\\PREGUNTAS  AIKEN\\Charla virtual 10 estartegias de marketing.txt"]
file_streams = [open(path, "rb") for path in file_paths]

# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams
)

# You can print the status and the file counts of the batch to see the result of this operation.
print(file_batch.status)
print(file_batch.file_counts)


# In[3]:


assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)


# In[4]:


# Upload the user provided file to OpenAI
message_file = client.files.create(
  file=open("C:\\Users\\HP\\Desktop\\CATO CURSOS-1-2024\\GER-TI CATO1-2024\\Cursos\\SEMANA 17\\PREGUNTAS  AIKEN\\Charla virtual 10 estartegias de marketing.txt", "rb"), purpose="assistants"
)

# Create a thread and attach the file to the message
thread = client.beta.threads.create(
  messages=[
    {
      "role": "user",
      "content": """Elabora VEINTE preguntas en formato AIKEN del texto que te copio en adjunto.  
      Las preguntas deben ser principalmente del tema abordado en el texto.
      NUNCA das citaciones ni fuentes
      NUNCA das un texto de introduccion , ni de despedida 
      UNICAMENTE respondes con las preguntas solictadas haciendo como en el ejemplo, no mas y no menos
      El ejemplo de preguntas que debes generar son así:”
Según el texto de título: Business Storytelling Masterclass with Matteo Cassese, ¿qué es esencial para captar la atención del público en storytelling?
A) Utilizar terminología complicada
B) Hablar en un tono monótono
C) Empezar con una anécdota interesante
D) Presentar gráficos complejos
ANSWER: C
 """ ,
      # Attach the new file to the message.
      "attachments": [
        { "file_id": message_file.id, "tools": [{"type": "file_search"}] }
      ],
    }
  ]
)

# The thread now has a vector store with that file in its tool resources.
print(thread.tool_resources.file_search)


# In[5]:


# Use the create and poll SDK helper to create a run and poll the status of
# the run until it's in a terminal state.

run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id, assistant_id=assistant.id
)

messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

message_content = messages[0].content[0].text


print(message_content.value)


# In[ ]:




