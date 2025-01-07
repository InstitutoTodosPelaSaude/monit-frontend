
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
    state	str	Name of the state. (e.g. São Paulo, Rio de Janeiro)
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

def get_prompt(question, project, table):

    data_dictonary = (
        RESPAT_FIELDS if project == 'RESPAT' 
        else ARBO_FIELDS
    )

    prompt = f"""
        {data_dictonary}
        Create a SQL query to answer the following question betwen <q>: <q>{question}<q>"
    """ + """
        Return the SQL query in a JSON formatted as follows {query: response}.
        The query need to be formatted using \t and \n to be displayed correctly in the widget.
    """

    return prompt

def fill_table_name(sql_raw_query):

    dict_table_name = {
        "ARBOVIROSES_TABLE": 
        """
        read_csv(
            's3://data/arbo/data/combined/combined.tsv',   
            delim='\\t',
            columns = {
                "lab_id": "VARCHAR",
                "sample_id": "VARCHAR",
                "test_id": "VARCHAR",
                "test_kit": "VARCHAR",
                "sex": "VARCHAR",
                "age": "INTEGER",
                "date_testing": "DATE",
                "patient_id": "VARCHAR",
                "file_name": "VARCHAR",
                "DENV_test_result": "VARCHAR",
                "ZIKV_test_result": "VARCHAR",
                "CHIKV_test_result": "VARCHAR",
                "YFV_test_result": "VARCHAR",
                "MAYV_test_result": "VARCHAR",
                "OROV_test_result": "VARCHAR",
                "WNV_test_result": "VARCHAR",
                "qty_original_lines": "VARCHAR",
                "created_at": "TIMESTAMP",
                "updated_at": "TIMESTAMP",
                "age_group": "VARCHAR",
                "epiweek_enddate": "DATE",
                "epiweek_number": "VARCHAR",
                "month": "VARCHAR",
                "location": "VARCHAR",
                "state": "VARCHAR",
                "country": "VARCHAR",
                "region": "VARCHAR",
                "macroregion": "VARCHAR",
                "macroregion_code": "VARCHAR",
                "state_code": "VARCHAR",
                "state_ibge_code": "VARCHAR",
                "location_ibge_code": "VARCHAR",
                "lat": "VARCHAR",
                "long": "VARCHAR"
            }
        )
        """,

        "RESPAT_TABLE":
        """
        read_csv(
            's3://data/respat/data/combined/combined.tsv', 
            delim='\\t',
            columns = {
                "lab_id": "VARCHAR",
                "sample_id": "VARCHAR",
                "test_id": "VARCHAR",
                "test_kit": "VARCHAR",
                "sex": "VARCHAR",
                "age": "INTEGER",
                "date_testing": "DATE",
                "patient_id": "VARCHAR",
                "file_name": "VARCHAR",
                "FLUA_test_result": "VARCHAR",
                "FLUB_test_result": "VARCHAR",
                "VSR_test_result": "VARCHAR",
                "RINO_test_result": "VARCHAR",
                "META_test_result": "VARCHAR",
                "PARA_test_result": "VARCHAR",
                "ADENO_test_result": "VARCHAR",
                "BOCA_test_result": "VARCHAR",
                "COVS_test_result": "VARCHAR",
                "ENTERO_test_result": "VARCHAR",
                "BAC_test_result": "VARCHAR",
                "qty_original_lines": "VARCHAR",
                "created_at": "TIMESTAMP",
                "updated_at": "TIMESTAMP",
                "age_group": "VARCHAR",
                "epiweek_enddate": "DATE",
                "epiweek_number": "VARCHAR",
                "month": "VARCHAR",
                "location": "VARCHAR",
                "state": "VARCHAR",
                "country": "VARCHAR",
                "region": "VARCHAR",
                "macroregion": "VARCHAR",
                "macroregion_code": "VARCHAR",
                "state_code": "VARCHAR",
                "state_ibge_code": "VARCHAR",
                "location_ibge_code": "VARCHAR",
                "lat": "VARCHAR",
                "long": "VARCHAR"
            }
        ) 
        """
    }

    sql_query = sql_raw_query
    for table_generic_name, table_name_in_the_database in dict_table_name.items():
        sql_query = sql_query.replace(table_generic_name, table_name_in_the_database)

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

