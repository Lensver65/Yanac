##########################################
#	Kulcsok beolvasasa	                 #
#	Futtatás előtt szerkeszeteni         #
#   kell a keyz.xml fájlt,               #
#   Ott kell megadni a kulcsokat         #
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
#	Adatok beolvasasa konzolrol 		 #
#	...es tarolasa			             #
##########################################

def adatok_megadasa():
	import xml.etree.cElementTree as ET

	cikk = ET.Element("cikk")
	cim = ET.SubElement(cikk, "cim")
	text = ET.SubElement(cikk, "szoveg")
	print("Add meg a cimet: ")
	title = input()
	# print("cim: ", cim)
	ET.SubElement(cim, "title").text = title


	print("Kerem a szoveget. Ctrl-D or Ctrl-Z ( windows ) a menteshez.")
	i = 1
	while True:
	   	try:
	   		line = input()
	   	except EOFError:
	   		break
	   	ET.SubElement(text, "tartalom").text = line
	tree = ET.ElementTree(cikk)
	tree.write("forditando.xml")
	return()

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
    instructions="You are my helpful secretariat and your task is to analyse the text I gave you and provide me a 2-3 paragraphs long summary. Focus on the facts (what happened), the possible consequences and any mayor observation worth to mention. If information is missing, don't try to fill the gap. Use formal, official language.",
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

  print("ChatGPT Run completed with status: " + run.status)

  if run.status != "completed":
    print(run.status)
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
#  A szoveg beolvasasa valtozokba        #
##########################################
def olvasas():
    import xml.etree.ElementTree as ET

    # Parse the XML file
    tree = ET.parse('forditando.xml')
    root = tree.getroot()

    # Define variables to store field values
    orig_cim = ""
    one_szoveg = ""
    orig_szoveg = []

# Cim beolvasas
    for cim in root.findall("cim"): 
        orig_cim = cim.find("title").text
        #print(orig_cim)


# Szoveg beolvasas
    for szoveg in root.findall("szoveg"):
        # print("Szoveg: ",szoveg.tag, szoveg.attrib)
        for tar in szoveg.findall("tartalom"):
            one_szoveg = tar.text
            orig_szoveg.append(one_szoveg)

    print("Cim es szoveg beolvasva")    
    #print("Cim: ", orig_cim)
    #print("Szoveg: ", orig_szoveg)
    while(None in orig_szoveg): ### Ures sorok kiemelese
    	orig_szoveg.remove(None)
    return orig_cim, orig_szoveg


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
print("API KULCSOK BEOLVASVA")
print("=====================")
adatok_megadasa() # User input megadasa
print("BEOLVASAS MEGTORTENT, XML elmentve")
print("==================================")
title, raw_text = olvasas() # Inputbol elmentett fajl olvasasa
print("XML BEOLVASVA")
print("=============")
ChatGPT_Input=' '.join(raw_text)
ChatGPT_Output=ChatGPT(api2,ChatGPT_Input)
print("CHATGPT LEFUTOTT")
print("ChatGPT Output:", ChatGPT_Output)
print("================")

# print(title)
# print(raw_text)

title = str(fordito(api2, title)) # Fordito meghivasa
filename = title +".txt"
forditott=str(fordito(api2, ChatGPT_Output))
f = open(filename, "w")
f.write(title + "\r\n")
f.write(forditott)

f.close()

print("FORDITAS KESZ, WP publikalas indul")
print("==================================")

# Set your WordPress credentials and URL
wordpress_url = 'https://yanac.hu/wp-json/wp/v2/posts'
username = api1[2]
password = api2[2]

# Create the post data
post_data = {
    'title': title,
    'content': forditott,
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
print("Response headers:", response.headers)
print("Response text:", response.text)

print("MINDEN KESZ, HAPPY")
print("==================")