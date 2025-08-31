from langchain_mistralai import ChatMistralAI
import os
import re
import json
from langchain_core.prompts import PromptTemplate

os.environ["MISTRAL_API_KEY"] = "" #key.read()

llm  = ChatMistralAI(model="mistral-small-latest", temperature=0)

instructions = """
                You are an agent who can extract relationships between two given entities.

                # Instructions on how to process text and give output
                1) Two entity will be provided by user
                2) Understand what could the relationship between the a 'source' entity to a 'target' entity.
                 Allowed relationships should be from the list here or should be similar to any of these.
                 ['Regulates','Supervises','Governs','Invests','Lends','Borrows','Finances','Funds','Subscribes','Underwrites','Organizes','Trades','Clears','Settles','Brokers','Manages','Custodies','Listed','Advises','Rates','Audits', 'Owns', 'Controls', 'Merges', 'Acquires']
                3) The output format should be a list of dictionaries. Each dictionary to represent relantionship between two entities.


                # Example

                text: Microcap Excel Realty N Infra also added that the total number of securities proposed to be issued through QIP shall be determined after fixation of the issue price at the time of issuance of securities.
                      Entities given ['Excel Realty N Infra','QIP']
                output: [{'Source_Entity': 'Microcap Excel Realty N Infra', 'Target_Entity': 'QIP', 'relationship': 'Finances'}]

                text: TACC, a wholly owned subsidiary of HEG and part of the LNJ Bhilwara Group, has signed a Technical Collaboration Agreement with Ceylon Graphene Technologies (CGT), a subsidiary of LOLC Holdings PLC and a global pioneer in graphene technologies, to jointly accelerate the commercialization and large-scale adoption of graphene and its derivatives.
                output: [{"Source_Entity": "HEG","Target_Entity": "TACC","relationship": "Owns"},
                        {"Source_Entity": "LNJ Bhilwara Group","Target_Entity": "TACC", "relationship": "Controls"}]

                Now analyse the following text and get the relationships between entities:
               """

# print (prompt)
# entity_template = PromptTemplate.from_template(instructions)
entities = ['TACC','National Council for Cement and Building Materials (NCB)', 'Central Road Research Institute (CRRI)','graphene-based concrete']
res = llm.invoke(instructions+f"text: TACC's ongoing collaborations across sectors already provide clear demonstrations of this promise. In construction, TACC is working with the National Council for Cement and Building Materials (NCB) and the Central Road Research Institute (CRRI) on graphene-based concrete solutions\
                Entities given {entities}")
res = str(res.content)
# print (res)
match = re.search('```json',res)
res = res[match.start()+8:]
end = re.search('```', res)
res = res[:end.end()-3]
out = json.loads(res)
print (out)