
COMMON_COMBINED_FIELDS = [
    ("lab_id", "str",  "lab name. One of: DBMOL, EINSTEIN, FLEURY, HILAB, HLAGYN, SABIN, TARGET, HPARDINI, DASA"),
    ("sample_id", "str", 	"Unique identifier for the biological sample used in the test."),
    ("test_id",	"str", 	"Unique identifier for the test performed."),
    ("sex",	"str", 	"One of: F, M or NULL"),
    ("age",	"int", 	"Age in years"),
    ("date_testing",	"str", 	"Date the test was conducted, in the format YYYY-MM-DD."),
    ("patient_id",	"str", 	"Unique identifier for the patient."),
    ("file_name",	"str", 	"Name of the file where the record was originally stored."),
    ("qty_original_lines",	"str", 	"Number of original lines in the source file."),
    ("created_at",	"str", 	"Timestamp of when the record was created, in the format YYYY-MM-DD HH:MM:SS."),
    ("updated_at",	"str", 	"Timestamp of the last update to the record, in the format YYYY-MM-DD HH:MM:SS."),
    ("age_group",	"str", 	"Categorized age group of the patient."),
    ("epiweek_enddate",	"str", 	"End date of the epidemiological week corresponding to the test date, in the format YYYY-MM-DD."),
    ("epiweek_number",	"str", 	"Epidemiological week number of the year."),
    ("month",	"str", 	"Month of the test, YYYY-MM."),
    ("location",	"str", 	"Name of the city."),
    ("state",	"str", 	"Name of the state. (e.g. São Paulo, Rio de Janeiro)"),
    ("country",	"str", 	"Name of the country."),
    ("region",	"str", 	"Region (Norte, Nordeste, Centro-Oeste, Sudeste, Sul)."),
    ("macroregion",	"str", 	"Macroregion grouping multiple regions."),
    ("macroregion_code",	"str", 	"Unique code representing the macroregion."),
    ("state_code",	"str", 	"Code for the state (e.g., SP for São Paulo)."),
    ("state_ibge_code",	"str", 	"IBGE code for the state."),
    ("location_ibge_code",	"str", 	"IBGE code for the city or municipality."),
    ("lat",	"str", 	"Latitude of the city or testing location."),
    ("long",	"str", 	"Longitude of the city or testing location."),
]

ARBO_COMBINED_FIELDS = [
    *COMMON_COMBINED_FIELDS,
    ("test_kit" ,"str",	"Name of the test kit used for diagnosis. One of: arbo_pcr_3, chikv_pcr, denv_antigen, denv_pcr, denv_serum, igg_serum, igm_serum, mayv_pcr, ns1_antigen, orov_pcr, yfv_pcr, zikv_pcr"),
    ("DENV_test_result"	,"str",	"Dengue  result"),
    ("ZIKV_test_result"	,"str",	"Zika result"),
    ("CHIKV_test_result"	,"str",	"Chikungunya result"),
    ("YFV_test_result"	    ,"str",	"Yellow fever result"),
    ("MAYV_test_result"	,"str",	"Mayaro result"),
    ("OROV_test_result"	,"str",	"Oropouche result"),
    ("WNV_test_result"	    ,"str",	"West Nile result"),
]

RESPAT_COMBINED_FIELDS = [
    *COMMON_COMBINED_FIELDS,
    ("test_kit", "str",	"Name of the test kit used for diagnosis. One of: ad\eno_iga,adeno_igg,adeno_igm,adeno_pcr,bac_antigen,bac_igg,bac_igm,bac_pcr,covid_antibodies,covid_antigen,covid_iga,covid_pcr,flua_igg,flua_igm,flu_antigen,flub_igg,flub_igm,flu_pcr,sc2_igg,test_14,test_21,test_23,test_24,test_3,test_4,thermo,vsr_antigen,vsr_igg"),
    ("SC2_test_result", "str", "SARS-CoV-2 result"),
    ("FLUA_test_result",    "str", "Influenza A result"),
    ("FLUB_test_result",    "str", "Influenza B result"),
    ("VSR_test_result", "str", "VSR result"),
    ("RINO_test_result",    "str", "Rhinovirus result"),
    ("META_test_result",    "str", "Metapneumovirus result"),
    ("PARA_test_result",    "str", "Parainfluenza result"),
    ("ADENO_test_result",   "str", "Adenovirus result"),
    ("BOCA_test_result",    "str", "Bocavirus result"),
    ("COVS_test_result",    "str", "Coronavirus result"),
    ("ENTERO_test_result",  "str", "Enterovirus result"),
    ("BAC_test_result", "str", "Bacteria result"),
]

project_and_table_to_data_dictionary_and_metadata = {

    "ARBO":{
        "combined": {
            "data_dictonary": ARBO_COMBINED_FIELDS,
            "table_prompt_name": "ARBOVIROSES_TABLE",
            "table_description": """
                The table `ARBOVIROSES_TABLE` contains information about test results for arbovirus.
                
                Business Rules:
                
                a) The columns XXYYZZ_test_result have 3 possible values: 'Pos' (Positive), 'Neg' (Negative), or 'NT' (Not Tested).
                b) Positivity Rate of a pathogen definition: (number of Pos)/(number of Pos + number of Neg) if (number of Pos + number of Neg) >= 50 else NULL
                c) Each value in the column 'test_kit' contains results for a set of pathogens, described below:
                    arbo_pcr_3 → Dengue, Zika, Chikungunya
                    chikv_pcr → Chikungunya
                    denv_antigen, denv_pcr, denv_serum, igg_serumm, igm_serum, ns1_antigen → Dengue
                    mayv_pcr → Mayaro
                    orov_pcr → Oropouche
                    yfv_pcr → Yellow fever
                    zikv_pcr → Zika
            """,
            "table_database_name": """
                read_csv(
                    's3://data/arbo/data/combined/combined.tsv',   
                    delim='\\t',
                    sample_size=1000
                )
            """
        }
    },

    "RESPAT":{
        "combined": {
            "data_dictonary": RESPAT_COMBINED_FIELDS,
            "table_prompt_name": "RESPAT_TABLE",
            "table_description": """
                The table `RESPAT_TABLE` contains information about test results for respiratory pathogens.

                a) The columns XXYYZZ_test_result have 3 possible values: 'Pos' (Positive), 'Neg' (Negative), or 'NT' (Not Tested).
                b) Positivity Rate of a pathogen definition: (number of Pos)/(number of Pos + number of Neg) if (number of Pos + number of Neg) >= 50 else NULL
                c) Each value in the column 'test_kit' contains results for a set of pathogens, described below:
                    adeno_iga, adeno_igg, adeno_igm, adeno_pcr → Adenovirus  
                    bac_antigen, bac_igg, bac_igm, bac_pcr → Bacteria  
                    covid_antibodies, covid_antigen, covid_iga, covid_pcr, sc2_igg, thermo → SARS-CoV-2  
                    flua_igg, flua_igm → Influenza A  
                    flub_igg, flub_igm → Influenza B  
                    flu_antigen, flu_pcr → Influenza A, Influenza B  
                    vsr_antigen, vsr_igg → VSR  
                    test_3 → Influenza A, Influenza B, VSR  
                    test_4 → SARS-CoV-2, Influenza A, Influenza B, VSR  
                    test_14 → SARS-CoV-2, Adenovirus, Bocavirus, Sazonal Coronaviruses, Enterovirus, Influenza A, Influenza B, Metapneumovirus, Parainfluenza, Rinovirus, VSR  
                    test_21 → SARS-CoV-2, Adenovirus, Sazonal Coronaviruses, Influenza A, Influenza B, Metapneumovirus, Parainfluenza, Rinovirus, VSR, Bacteria  
                    test_23 → SARS-CoV-2, Adenovirus, Bocavirus, Sazonal Coronaviruses, Influenza A, Influenza B, Metapneumovirus, Parainfluenza, Rinovirus, VSR, Bacteria  
                    test_24 → SARS-CoV-2, Adenovirus, Bocavirus, Sazonal Coronaviruses, Enterovirus, Influenza A, Influenza B, Metapneumovirus, Parainfluenza, Rinovirus, VSR, Bacteria
            """,
            "table_database_name": """
                read_csv(
                    's3://data/respat/data/combined/combined.tsv', 
                    delim='\\t',
                    ignore_errors=True,
                    sample_size=1000
                ) 
            """
        }
    }
}

def get_table_data_dictionary(project, table):

    table_metadata = project_and_table_to_data_dictionary_and_metadata[project][table]
    data_dictonary = table_metadata["data_dictonary"]
    table_description = table_metadata["table_description"]

    return {
        "data_dictonary": data_dictonary
    }

def get_prompt(question, project, table):

    table_metadata = project_and_table_to_data_dictionary_and_metadata[project][table]
    data_dictonary = table_metadata["data_dictonary"]
    table_description = table_metadata["table_description"]
    
    data_dictonary_str = "\n".join([
        f"""{col_name}  {col_type}  {col_description}"""
        for col_name, col_type, col_description in data_dictonary
    ])

    prompt = f"""
        {table_description}
        Data dictionary:
        Name  Type  Description
        {data_dictonary_str}
        Create a SQL query to answer the following question betwen <q>: <q>{question}<q>"
    """ + """
        Return the SQL query in a JSON formatted as follows {query: response}.
    """

    return prompt

def replace_table_name_in_prompt_by_table_name_in_database(sql_raw_query):
    sql_query = sql_raw_query
    for _, table_data_dictonaries in project_and_table_to_data_dictionary_and_metadata.items():
        for _, data_dictonary in table_data_dictonaries.items():
            sql_query = sql_query.replace(
                data_dictonary["table_prompt_name"], 
                data_dictonary["table_database_name"]
            )

    return sql_query

def apply_configs_to_sql_query(sql_query, configs):

    if not configs:
        return sql_query
    
    sql_query_with_configs = sql_query
    max_num_lines = configs.get('max_num_lines')
    if max_num_lines:
        sql_query_with_configs = sql_query_with_configs.replace(';', '')
        sql_query_with_configs = f"SELECT * FROM ({sql_query_with_configs}) AS query_limit_num_of_lines LIMIT {max_num_lines}"

    return sql_query_with_configs

