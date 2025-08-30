from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_mistralai import ChatMistralAI
import pandas as pd
import os

os.environ["MISTRAL_API_KEY"] = "" #key.read()

llm  = ChatMistralAI(model="mistral-small-latest", temperature=0)

def create_agent(path=None, prompt=None):
    if path is not None:
        df = pd.read_excel(path)
        print (len(df))
        agent = create_pandas_dataframe_agent(
                    llm,
                    df,
                    verbose=False,
                    prefix=prompt,
                    agent_type='tool-calling',
                    allow_dangerous_code=True,
                    handle_parsing_errors=True
                )
        return agent
    
if __name__ == "__main__":
    path = 'MW-NIFTY-500-24-Aug-2025_2.xlsx'


    prompt = f""" You are an agent which can analyse a stock market dataset for a specific day for 500 companies.

                ## The dataset columns and their metadata mappings is below:

                1) 'SYMBOL' - Company name 
                2) 'OPEN'- Opening stock price
                3) 'HIGH' -  Days high value of stock
                4) 'LOW' - Days lowest value of stock
                5) 'PREV. CLOSE' - Previous day closure price of stock
                6) 'LTP' - last traded price of the stock
                7) 'INDICATIVE CLOSE' - expected closing price of the stock
                8) 'CHNG' - Total change 
                9) '%CHNG' - Total change in percentage
                10) 'VOLUME' -  Total volume of share bought
                11) 'VALUE' - Total value of shares bought in crores
                12) '52W H' - last 52 weeks highest value of the stock
                13) '52W L' -  last 52 weeks lowest value of the stock
                14) '30 D   %CHNG' -  last 30 days change
                15) '365 D % CHNG  22-Aug-2024' - last 365 change percentage

            ## Thought process steps
            1) Try to find all the columns for the needed query. e.g Last 52 weeks high is '52W H'.
                or last traded price is 'LTP'.
            2) Create the python pandas based query and get the values.
            3) Then calculate the answer

            ## Example process to come up with answer:

            User: Give me MARUTI company 52 weeks high value
            Agent: So I need to filter on 'SYMBOL' == 'MARUTI'. Then find column '52W H' and give its value.

            User: Give me IDEA company value by volume ratio
            Agent: So I need to filter on 'SYMBOL' == 'IDEA'. Then find column 'VALUE' and 'VOLUME'.
                   Then divide value obtained from 'VALUE' divided by 'VOLUME'.

            ## Output format:
            User: Give me MARUTI company 52 weeks high value.
            Agent: The 52 weeks high value of MARUTI is (calculated value)

            User: Give me IDEA company value by volume ratio
            Agent: The Value is (calculated value) and volume is (calculated value). So value by volume ratio of IDEA is (calculated value)


            Now answer this user query:
            """
    
    agent = create_agent(path, prompt)

    i = 5 #5 iterations
    while ( i >=0):
        print ('Please provide prompt')
        query = input()
        out =  (agent.invoke(query))
        print (out['output'])
        print ('-----------------------------------------')
        i = i - 1