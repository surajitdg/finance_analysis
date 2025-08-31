from langchain_mistralai import ChatMistralAI
import os
import re
import json
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import PromptTemplate

os.environ["MISTRAL_API_KEY"] = "Pcd7zIRCeLhI6JW5sZo8UMRJGCblYUIn" #key.read()

llm  = ChatMistralAI(model="mistral-small-latest", temperature=0)

instructions = """
                You are an agent who can extract important entities from a given text and define type of
                entity, description of entity and give additional attributes if any.

                # Instructions on how to process text and give output
                1) From the text recognize the named entity. Use proper entity resolution and entity disambiguation.
                2) Understand what is the type of Entity.
                3) One liner description of the entity if possible to be gathered from the text, else none.
                4) Additional attributes of the entity which helps to understand what the entity is if possible to be gathered from the text, else none.
                5) The output format should be a list of dictionaries. Each dictionary to represent details of each entity.


                # Example

                text: Microcap Excel Realty N Infra also added that the total number of securities proposed to be issued through QIP shall be determined after fixation of the issue price at the time of issuance of securities.
                output: [{'name':'Excel Realty N Infra', type:'Organization', 'desc':'Microcap realty and infra firm', 'attr':['Infra','Reality']}]

                text: TACC, a wholly owned subsidiary of HEG and part of the LNJ Bhilwara Group, has signed a Technical Collaboration Agreement with Ceylon Graphene Technologies (CGT), a subsidiary of LOLC Holdings PLC and a global pioneer in graphene technologies, to jointly accelerate the commercialization and large-scale adoption of graphene and its derivatives.
                output: [{'name':'TACC', type:'Organization', 'desc':'whole subsidiary of HEG and part of LN Bhilwara Group', 'attr':['graphene technologies']},
                         {'name':'HEG', type:'Organization', 'desc':'part of LN Bhilwara Group', 'attr':['graphene technologies']},
                         {'name':'LNJ Bhilwara Group', type:'Organization', 'desc':'None', 'attr':['graphene technologies']},
                         {'name':'Ceylon Graphene Technologies (CGT)', type:'Organization', 'desc':'a subsidiary of LOLC Holdings PLC and a global pioneer in graphene technologies', 'attr':['graphene technologies pioneer']},
                         {'name':'Ceylon', type:'Geographical Location', 'desc':'None', 'attr':['graphene technologies']},
                         {'name':'graphene', type:'concept', 'desc':'None', 'attr':['graphene technologies']},
                         ]

                Now analyse the following text and give the output:
               """

# print (prompt)
# entity_template = PromptTemplate.from_template(instructions)
res = llm.invoke(instructions+"TACC's ongoing collaborations across sectors already provide clear demonstrations of this promise. In construction, TACC is working with the National Council for Cement and Building Materials (NCB) and the Central Road Research Institute (CRRI) on graphene-based concrete solutions")
res = str(res.content)
# print (res)
match = re.search('```json',res)
res = res[match.start()+8:]
end = re.search('```', res)
res = res[:end.end()-3]
out = json.loads(res)
print (out)