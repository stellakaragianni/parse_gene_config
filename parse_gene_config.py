import configparser
import mariadb
import requests

# Connection with MariaDB
def connect_to_ucsc_db(config):
    try:
        db_config = {
            "host": config["domain_names"]["ucsc_mysql"],
            "user": config["credentials"]["ucsc_user"],
            "database": "hg38"
        }
        connection = mariadb.connect(**db_config)
        return connection      
    except mariadb.Error as err:
        print(f"Error!!!{err}")
        return None

def main():
    config = configparser.ConfigParser()
    config.read("input.ini")
    # Get gene names and Ensembl API
    gene_names = list(config["gene_ids"])
    ensembl_api = config["domain_names"]["ensembl_api"]
    # Get file name for results output
    results_output = config["file_names"]["outfile"]
    # Open output file for writing
    with open(results_output, "w") as outfile:
        outfile.write(
            "Gene_Name\tEnsembl_Gene_ID\tEnsembl_Mouse_Gene_ID\tPct_Identity\tNumber_Of_Exons\n"
        )

        connection = connect_to_ucsc_db(config)
        if not connection:
            return

        # Loop through gene names
        for gene_name in gene_names:

            print ("Gene_Name=", gene_name)
            
            url = f"https://{ensembl_api}/homology/symbol/human/{gene_name}?target_species=mouse;type=orthologues"
            print ("URL=", url)
            
            try:
                response = requests.get(url, headers={"Content-Type": "application/json"}) # Make a request to a web page, and return the status code
                response.raise_for_status() # returns an HTTPError object

                # Parse JSON file response for gene data
                data = response.json()
                # Find gene id in json & make it stringdata type
                ensg_id = data["data"][0]["id"]                
                print("Ensembl_Gene_ID=", ensg_id)
                
                stringdata=str(data)
                search_species = stringdata.find("'species': 'mus_musculus'")
                if search_species > 0:
                    mousegid_start_pos = stringdata.rfind("ENSMUSG")
                    mouse_gene_id = stringdata[mousegid_start_pos:(mousegid_start_pos+18)]
                    print ("Ensembl_Mouse_Gene_ID=", mouse_gene_id)
                    pctid_start_pos = stringdata.rfind("'perc_id': ")
                    percent_identity = stringdata[(pctid_start_pos+11):(pctid_start_pos+18)]
                    print ("Pct_Identity=", percent_identity)
                else:
                    outfile.write(
                        f"{gene_name}\t{ensg_id}\tNA\tNA\tNA\n"
                    )
                    continue
                    
                cursor = connection.cursor() 
                # Fetch the canonical transcript of the gene via SQL query
                query = (f"SELECT knownCanonical.transcript " f"FROM knownCanonical JOIN kgXref ON knownCanonical.transcript = kgXref.kgID " f"WHERE kgXref.geneSymbol='{gene_name}'")
                cursor.execute(query)
                transcript = cursor.fetchone()[0]

                # Fetch the number of exons for the canonical transcript via SQL query
                query = (f"SELECT exonCount FROM knownGene WHERE name='{transcript}'")
                cursor.execute(query)
                num_exons = cursor.fetchone()[0]

                print(f"Transcript= {transcript}, Number of exons= {num_exons}") ### TO BE DELETED
 
                print ("==========================================================")
                # Write data to the file
                outfile.write(
                    f"{gene_name}\t{ensg_id}\t{mouse_gene_id}\t{percent_identity}\t{num_exons}\n"
                )
            except requests.exceptions.RequestException as e:
                # Handle potential request errors
                print(f"Error fetching data for {gene_name}: {e}")

    connection.close()
    
main()