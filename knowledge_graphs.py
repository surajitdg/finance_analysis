import uuid
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
        
instructions = """
                You are an agent who can extract important entities from a given text and define type of
                entity, description of entity and give additional attributes if any.

                # Instructions on how to process text and give output
                1) From the text recognize the named entity.
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
               """

relations = """



            """

class KnowledgeGraphs():

    def __init__(self, llm, instructions, relations):
        self.graph = {}
        self.edges = []
        self.llm = llm

    def parse_entity_info(self, entity_info):
        res = {}
        res['name'] = ''
        res['type'] = ''
        res['desc'] = ''
        res['attr'] = ''
        return res

    def add_nodes(self, entity_info):
        #parse entity_info from LLM
        entity = self.parse_entity_info(entity_info)
        node = Node(entity['name'], entity['type'], entity['desc'], entity['attr'])
        return node

    def add_relations(self, src_node, target_node, relation):
        self.graph['src_node'].append({relation:target_node})

    
    def llm_extract_entity(self, text):
        try:
            llm_output = self.llm.invoke(instructions+text)
            #check entity_info format
        except Exception as e:
            print (f'Error in invoking llm {e}')
        return llm_output.content[0]
    
    def llm_create_relations(self):
        graph_keys = self.graph.keys()
        try:
            llm_output = self.relation_template.invoke({'nodes':graph_keys})
        except Exception as e:
            print (f'Error in invoking llm {e}')
        return llm_output.content[0]


    def create_graph(self, text= None):
        if text is None:
            raise ('No next is provided, cannot create graph')
        llm_output = self.llm_extract_entity(text)
        for entity_info in llm_output:
            node =  self.add_nodes(entity_info)
            if node['name'] not in self.graph:
                self.graph[node['name']] = []
            else:
                raise ('Duplicate entity identified, please prune LLM output')
        
        #get relationships
        llm_output_relations = self.llm_invoke(self.graph)
        for r in llm_output_relations:
            src_node = self.graph[r['source']]
            dest_node = self.graph[r['target']]
            relationship = r['relation']
            self.graph.append(src_node, dest_node, relationship)


