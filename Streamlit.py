# streamlit run C:\Users\John\Jupyter_Notebooks_Pharmonic\Pharmonic_Build\DDI_RxNav.py
# https://github.com/jgroehm/Pharmonic.git

import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import networkx as nx
import holoviews as hv
from holoviews import opts
from holoviews.operation.datashader import bundle_graph  # datashade, 
hv.extension('bokeh')

defaults = dict(width=800, height=500)
hv.opts.defaults(
    opts.EdgePaths(**defaults), opts.Graph(**defaults), opts.Nodes(**defaults))



@st.cache(persist = True)
def read_data():
    RxCUI_Mapping_File = r'D:\Myttee\DrugBank Database\Drugbank_API_Data.xlsx'    
    return pd.read_excel(RxCUI_Mapping_File,sheet_name='RxCUIs')


#@st.cache(allow_mutations=True)
def generate_drugs(rxcuis):
    drug_list_length = np.random.randint(3,20)
    # druglist_rxcuis = (rxcuis[np.random.randint(0,len(rxcuis))] for index in range(drug_list_length)) #generator
    druglist_rxcuis = [rxcuis[np.random.randint(0,len(rxcuis))] 
                for index in range(drug_list_length)]
    return druglist_rxcuis


#@st.cache(allow_mutations=True)
def call_api(druglist_rxcuis):
    # URL returns: https://rxnav.nlm.nih.gov/InteractionAPIREST.html#uLink=Interaction_REST_findInteractionsFromList
    rxcuis_str = '+'.join([str(item) for item in druglist_rxcuis])  #convert list to str+ format
    rxnav_interaction_url = f'https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis={rxcuis_str}'
    return requests.get(rxnav_interaction_url)


drugs = read_data().rxstring.unique()
rxcuis = read_data().rxcui.unique()
druglist_rxcuis = generate_drugs(rxcuis)
resp = call_api(druglist_rxcuis)
payload = resp.json()

# @st.cache(persist=True)
def get_interactions():
    interaction_dict = {}   #{'row_1' :[rxcui1, drug1, rxcui2, drug2, description]}
    json = dict(payload['fullInteractionTypeGroup'][0])
    fullInteractionType = json.get("fullInteractionType",{})
    for _ in json:
        
        for pair in fullInteractionType:
            
            interactionPair = (pair.get('interactionPair'))
            interaction_list = []
            
            for interaction_counter, interaction in enumerate(interactionPair):
                pk = interaction_counter
                interactionConcept = interaction.get('interactionConcept')         
                description = interaction.get('description')

                for counter, drug in enumerate(interactionConcept):
                    drug_data = drug.get('minConceptItem')
                    rxcui = drug_data['rxcui']
                    name = drug_data['name']
                    
                    interaction_list.append(rxcui)
                    interaction_list.append(name)
                    
                  
                interaction_list.append(description)
                interaction_dict[pk] = interaction_list
                interaction_list = []

                
    return interaction_dict
                #st.write(description,'\n')
                   #return(description)


def build_graph():
    df = pd.DataFrame.from_dict(get_interactions(), orient='index', columns=['RxCUI1', 'Drug1', 'RxCUI2', 'Drug2','Description'])
    G = nx.from_pandas_edgelist(df, source='Drug1',target='Drug2', edge_attr = ['Description'])
    graph = (hv.Graph.from_networkx(G, nx.layout.spring_layout).opts(tools=['hover']))
    B = bundle_graph(graph)
    #TODO: Edge Labels
        # Colors
        # Line Width
        # Node Size
        
    #L = hv.Labels(('x','y'),index,vdims='Description')
    return  B


#def ():

interaction_dict = get_interactions()
graph = build_graph()
st.write(hv.render(graph))


st.write(interaction_dict)

#for i in interaction_list:
#    st.write(i)

#  convert to networkx graph & display in HV
