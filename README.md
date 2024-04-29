# parse_gene_config

~Write Python code that will:
1. Use as input the provided .ini file, the list of human genes in particular .
2. Fetch information about mouse orthologs for each gene using the Ensembl API. In
particular , fetch the Ensembl mouse gene id and percent identity between the human
and mouse canonical proteins. (documentation)
3. Fetch the information about the number of exons for the canonical transcript of each
gene using UCSC MariaDB database. (documentation)
4. Output the information you gathered as a tab-separated table. (see attached example)
5. Use Prefect to organize your code in a workflow. 


~Explanation
The connection to MariaDB was based on documentation and this website: https://mariadb.com/resources/blog/how-to-connect-python-programs-to-mariadb/ 
The code was written in Thonny IDE in Python 3.10 and the following were installed:
- pip install configparser
- pip install mariadb
- pip install requests
- pip install types-requests

connect_to_ucsc_db():
taking as connection elements those of the config which I pass into a dictionary (inside try-except) and call the .connect method to connect me to MariaDB.
To see the contents of the database, I used https://genome-euro.ucsc.edu/cgi-bin/hgTables?hgsid=337547937_jUpeoDW3AMEu3CWeArQ3j4PUSDCA and specifically the select dataset>table>data format description field.

main():
First I pass the .ini file with parser to config for reading.
In a gene_names list I 'put' the gene names and in the enembl_api the URL: rest.ensembl.org from the .ini file.
I then open a file to write the results of a format like the example and connect to the database by giving the config as a parameter with the necessary data for the connection.
Manage possible network errors with try-except.
Then, in loop: for each gene name that the gene_names list had, I print gene id & URL, visit the url and do json content, parse the json file (the information it will have is also captured in the Thonny shell).  I find mouse_gene_id & percent_identity (otherwise NA if not present) within the stringdata (their positions are found by counting the characters), continue extracting the transcripts & counting the exons (both 2 processes for each gene_id) running the 2 queries (based on https://dev.mysql.com/doc/connector-python/en/connector-python-example-cursor-select.html), print them and finally, close the connection to the database. The file with all the results is coding_test.tsv.
