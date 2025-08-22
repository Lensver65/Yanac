##########################################
#	Kulcsok beolvasasa		             #
##########################################
def read_api_key():
    import xml.etree.ElementTree as ET

    # Parse the XML file
    tree = ET.parse('keyz.xml')
    root = tree.getroot()

    # Define variables to store field values
    field1_values = []
    field2_values = []

    # Iterate through each 'set' element
    for set_element in root.findall('set'):
        # Get field1 and field2 values
        field1 = set_element.find('field1').text
        field2 = set_element.find('field2').text

    
        # Store values in respective lists
        field1_values.append(field1)
        field2_values.append(field2)

    # print("Kulcsok beolvasva")    
    return field1_values, field2_values # Visszateresi ertek a ket kulcs


##########################################
#  ChatGPT                               #
##########################################

def ChatGPT(apikey,inputtext):
  from openai import OpenAI
  # Set your OpenAI API key
  
  client = OpenAI(
      # This is the default and can be omitted
      api_key=apikey[0],
  )

  assistant = client.beta.assistants.create(
    name="Titkar",
    instructions="You are my helpful secretariat and your task is to analyse the URL I gave you and provide me a 2-3 paragraphs long summary from this URL. Focus on the facts (what happened), the possible consequences and any major observation worth to mention. If information is missing, don't try to fill the gap. Use formal, official language. When creating summary, keep the original title and add it to the begining of the text.",
    model="gpt-4",
  )

  thread = client.beta.threads.create()

  message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=inputtext,
  )

  run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id,
  )

  print("ChatGPR Run completed with status: " + run.status)

  if run.status != "completed":
    print("Futasi hiba: ", run.status)
    client.beta.assistants.delete(assistant.id)
    return None

  messages = client.beta.threads.messages.list(thread_id=thread.id)
  # print("messages: ")
  # for message in messages:
  #     assert message.content[0].type == "text"
  #     print({"role": message.role, "message": message.content[0].text.value})

  vissza = messages.data[0].content[0].text.value
  client.beta.assistants.delete(assistant.id)
  return vissza

##########################################
#  Fordito						         #
##########################################
def fordito(key,szoveg): # Fordito function, calls DEEPL to translate the text.
    import deepl

    auth_key = key[1]  # Auth key from parameter
    translator = deepl.Translator(auth_key)

    result = translator.translate_text(text=szoveg, target_lang="HU", formality="prefer_more")
    # print("Fordito lefutott")
    return result.text


##########################################
#  MAIN							         #
##########################################
import requests
from requests.auth import HTTPBasicAuth

api1, api2 = read_api_key() # API kulcsok beolvasasa

URL=input("Kerlek, add meg az URL-t, amit be kell olvassak: ")

osszegzett=ChatGPT(api2,URL)

f = open("osszegzett.txt", "w")
f.write(osszegzett)
f.close()


# print(osszegzett)

eredeti = open("osszegzett.txt", "r")


cim=fordito(api2,eredeti.readline())
forditott=fordito(api2,eredeti.read())
hyperlink="(<a href=\""+URL+"\" target=\"_blank\" rel=\"noopener noreferrer\">forrás</a>)"

ft = open("forditott.txt", "w")
ft.write(forditott)
eredeti.close()
ft.write("\r\n")
ft.write(hyperlink)
ft.close()
# print("-----------------------")
# print("FORDITOTT:")
# print("-----------------------")

yanac = open("forditott.txt", "r")
content = yanac.read()
yanac.close()
# print("Meg egyszer a teles szoveg: \r\n",json.dumps(content))

# Set your WordPress credentials and URL
wordpress_url = 'https://yanac.hu/wp-json/wp/v2/posts'
username = api1[2]
password = api2[2]

# Create the post data
post_data = {
    'title': cim,
    'content': content,
    'status': 'draft',  # Can also be 'draft' or 'private'
    'categories': '16'
}

# Make the API request to create the post
response = requests.post(wordpress_url, json=post_data, auth=HTTPBasicAuth(username, password))

# Check if the post was created successfully
if response.status_code == 201:
    print(f"Post published with ID: {response.json()['id']}")
else:
    print(f"Failed to publish post: {response.status_code} - {response.text}")

# For additional debugging
# print("Response headers:", response.headers)
# print("Response text:", response.text)

print("MINDEN KESZ, HAPPY")
print("==================")