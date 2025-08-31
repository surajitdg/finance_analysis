import uuid
import re
import json
import os
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import PromptTemplate

class Node():
    def __init__(self, name, type, desc, attr):
        """
        id : id of node
        name: name of entity , SBI, Tatamotors
        type: type of entity ,  
        description: description of entity
        attributes: additional attributes
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.type = type
        self.desc = desc
        self.attr = attr
        
instructions_entity = """
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

instructions_relations = """
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

class KnowledgeGraphs():

    def __init__(self, llm):
        self.graph = {}
        # self.edges = []
        self.llm = llm

    def parse_entity_info(self, entity_info):
        res = {}
        try:
            res['name'] = entity_info['name']
            res['type'] = entity_info['type']
            res['desc'] = entity_info['desc']
            res['attr'] = entity_info['attr']
        except Exception as e:
            print (f'Error in getting specific key {e}')
        return res

    def add_nodes(self, entity_info):
        #parse entity_info from LLM
        entity = self.parse_entity_info(entity_info)
        node = Node(entity['name'], entity['type'], entity['desc'], entity['attr'])
        return node

    def add_relations(self, src_node, target_node, relation):
        self.graph[src_node].append({relation:target_node})

    def format_output(self, text):
        try:
            res = str(text)
            # print (res)
            match = re.search('```json',res)
            res = res[match.start()+8:]
            end = re.search('```', res)
            res = res[:end.end()-3]
            res = res.strip('\n')
            out = json.loads(res)
        except Exception as e:
            print (f'Error in formating {e}')
            return None
        return out

    
    def llm_extract_entity(self, text):
        try:
            llm_output = self.llm.invoke(instructions_entity+text)
            #check entity_info format
            llm_output = self.format_output(llm_output.content)
        except Exception as e:
            print (f'Error in invoking llm {e}')
        return llm_output
    
    def llm_create_relations(self, text):
        graph_keys = str(list(self.graph.keys()))
        try:
            llm_output = self.llm.invoke(instructions_relations+text+graph_keys)
            llm_output = self.format_output(llm_output.content)
        except Exception as e:
            print (f'Error in invoking llm {e}')
        return llm_output


    def create_graph(self, text= None):
        if text is None:
            raise ('No text is provided, cannot create graph')
        llm_output = self.llm_extract_entity(text)
        for entity_info in llm_output:
            node =  self.add_nodes(entity_info)
            if node.name not in self.graph:
                self.graph[node.name] = []
            else:
                raise ('Duplicate entity identified, please prune LLM output')
        
        #get relationships
        llm_output_relations = self.llm_create_relations(text)
        for r in llm_output_relations:
            src_node = r['Source_Entity']
            dest_node = r['Target_Entity']
            relationship = r['relationship']
            if src_node not in self.graph:
                self.graph[src_node] = [{dest_node, relationship}]
            else:
                self.graph[src_node].append({dest_node, relationship})



if __name__ == "__main__":
    os.environ["MISTRAL_API_KEY"] = "" #key.read()
    llm = ChatMistralAI(model="mistral-small-latest", temperature=0)
    kg = KnowledgeGraphs(llm=llm)
    kg.create_graph(text = "TACC's ongoing collaborations across sectors already provide clear demonstrations of this promise. In construction, TACC is working with the National Council for Cement and Building Materials (NCB) and the Central Road Research Institute (CRRI) on graphene-based concrete solutions")
    print (kg.graph)

