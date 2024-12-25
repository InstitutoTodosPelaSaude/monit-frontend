import streamlit as st
import sqlparse

import os
import json
from openai import OpenAI

import streamlit as st

COMMON_FIELDS = """
    Column Name	Type	Description
    lab_id str lab name. One of: DBMOL, EINSTEIN, FLEURY, HILAB, HLAGYN, SABIN, TARGET, HPARDINI, DASA
    sample_id str	Unique identifier for the biological sample used in the test.
    test_id	str	Unique identifier for the test performed.
    sex	str	One of: F, M or NULL
    age	int	Age in years
    date_testing	str	Date the test was conducted, in the format YYYY-MM-DD.
    patient_id	str	Unique identifier for the patient.
    file_name	str	Name of the file where the record was originally stored.
    qty_original_lines	str	Number of original lines in the source file.
    created_at	str	Timestamp of when the record was created, in the format YYYY-MM-DD HH:MM:SS.
    updated_at	str	Timestamp of the last update to the record, in the format YYYY-MM-DD HH:MM:SS.
    age_group	str	Categorized age group of the patient.
    epiweek_enddate	str	End date of the epidemiological week corresponding to the test date, in the format YYYY-MM-DD.
    epiweek_number	str	Epidemiological week number of the year.
    month	str	Month of the test, YYYY-MM.
    location	str	Name of the city.
    state	str	Name of the state.
    country	str	Name of the country.
    region	str	Region (Norte, Nordeste, Centro-Oeste, Sudeste, Sul).
    macroregion	str	Macroregion grouping multiple regions (e.g., North, South).
    macroregion_code	str	Unique code representing the macroregion.
    state_code	str	Abbreviation or code for the state (e.g., SP for São Paulo).
    state_ibge_code	str	IBGE (Brazilian Institute of Geography and Statistics) code for the state.
    location_ibge_code	str	IBGE code for the city or municipality.
    lat	str	Latitude of the city or testing location.
    long	str	Longitude of the city or testing location.
"""

ARBO_FIELDS = f"""
    The table `ARBOVIROSES_TABLE` combined contains information about test results for arbovirus.
    Data dictionary:
    {COMMON_FIELDS}
    test_kit str	Name or code of the test kit used for diagnosis. One of: arbo_pcr_3, chikv_pcr, denv_antigen, denv_pcr, denv_serum, igg_serum, igm_serum, mayv_pcr, ns1_antigen, orov_pcr, yfv_pcr, zikv_pcr
    DENV_test_result	str	Dengue  result: Pos (Positive), Neg (Negative), or NT (Not Tested).
    ZIKV_test_result	str	Zika result
    CHIKV_test_result	str	Chikungunya result
    YFV_test_result	    str	Yellow fever result
    MAYV_test_result	str	Mayaro result
    OROV_test_result	str	Oropouche result
    WNV_test_result	    str	West Nile result
"""

RESPAT_FIELDS = F"""
    The table `RESPAT_TABLE` contains information about test results for respiratory pathogens.
    Data dictionary:
    {COMMON_FIELDS}
    test_kit str	Name or code of the test kit used for diagnosis. One of: adeno_iga,adeno_igg,adeno_igm,adeno_pcr,bac_antigen,bac_igg,bac_igm,bac_pcr,covid_antibodies,covid_antigen,covid_iga,covid_pcr,flua_igg,flua_igm,flu_antigen,flub_igg,flub_igm,flu_pcr,sc2_igg,test_14,test_21,test_23,test_24,test_3,test_4,thermo,vsr_antigen,vsr_igg,    SC2_test_result str SARS-CoV-2 result: Pos (Positive), Neg (Negative), or NT (Not Tested).
    FLUA_test_result    str Influenza A result
    FLUB_test_result    str Influenza B result
    VSR_test_result str VSR result
    RINO_test_result    str Rhinovirus result
    META_test_result    str Metapneumovirus result
    PARA_test_result    str Parainfluenza result
    ADENO_test_result   str Adenovirus result
    BOCA_test_result    str Bocavirus result
    COVS_test_result    str Coronavirus result
    ENTERO_test_result  str Enterovirus result
    BAC_test_result str Bacteria result
"""


def fetch_sql_query(question, data_dictonary):

    PROMPT = f"""
        {data_dictonary}
        Create a SQL query to answer the following question betwen <q>: <q>{question}<q>"
    """ + """
        Return the SQL query in a JSON formatted as follows {query: response}.
        The query need to be formatted using \t and \n to be displayed correctly in the widget.
    """

    try:
        client = OpenAI()

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={ "type": "json_object" },
            messages=[{"role": "user", "content": PROMPT}]
        )

        # Parse and return the response
        response_content = json.loads(response.model_dump_json())
        message = response_content['choices'][0]['message']['content']

        sql_query = json.loads(message).get("query", "No query found")
        return sql_query

    except Exception as e:
        raise RuntimeError(f"Error fetching SQL query from OpenAI: {e}")


def widget_query( container ):

    # Project selection
    col_text, col_project_selection, _ = container.columns( [ 2.5, 3, 4.5 ] )
    col_text.text("Ask me anything about ")
    project = col_project_selection.selectbox(
        "Project", 
        ["Arboviroses", "Respat"], 
        label_visibility = 'collapsed'
    )

    # Question input
    col_question, col_button_go = container.columns( [ 4, 1 ] )
    question = col_question.text_input("", label_visibility = 'collapsed')

    # SQL query prompt processing
    sql_query = None
    data_dictonary = ARBO_FIELDS if project == "Arboviroses" else RESPAT_FIELDS

    if col_button_go.button("Go!"):
        if not question.strip():
            col_question.warning("Please enter a valid question.")
        else:
            try:
                sql_query = fetch_sql_query(question, data_dictonary)
            except Exception as e:
                col_button_go.error(f"An error occurred: {e}")

    if sql_query:
        sql_query_formatted = sqlparse.format(sql_query, reindent=True, keyword_case='upper')

        toggle_code = container.expander("Query", False)        
        toggle_code.code(sql_query_formatted, language="sql")

if __name__ == "__main__":
    # Streamlit UI
    st.title("🤖 Monit Chat :dna:")
    widget_query(st)
