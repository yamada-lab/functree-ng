##
# This script can be used to generate an annotation mapping for some common knowledge bases (e.g Uniprot, EggNOG) of functional annotation.
# Thanks to these annotations FuncTree2 can map data matrices with different annotations, onto the KEGG BRITE hierarchy.
# 
# NOTE: A KEGG subscription (https://www.bioinformatics.jp/en/keggftp.html) is required to generate these files.
#  

# Path to the annotation list
# In a KEGG release it could be found under $KEGG_HOME/genes/ko/
LIST_HOME=/home/omixer/workspace/YamadaData/iPath3/list/
# TMP output file 
OUT=tmp

# Format the mapping files
sed 's/^ko://' ${LIST_HOME}/ko_reaction.list | awk '{print $2"\t"$1}' | sed 's/^rn://' > $OUT
sed 's/^ko://' ${LIST_HOME}/ko_cog.list | awk '{print $2"\t"$1}' | sed 's/^cog://' >> $OUT
sed 's/^ko://' ${LIST_HOME}/ko_enzyme.list | awk '{print $2"\t"$1}' | sed 's/^ec:/EC:/' >> $OUT
sed 's/^ko://' ${LIST_HOME}/ko_genes.list | awk '{print $2"\t"$1}' >> $OUT
sed 's/^ko://' ${LIST_HOME}/ko_go.list | awk '{print $2"\t"$1}' | sed 's/^go:/GO:/' >> $OUT
sed 's/^ko://' ${LIST_HOME}/ko_cazy.list | awk '{print $2"\t"$1}' | sed 's/^cazy:/CAZY:/'>> $OUT



# The following section requires a little bit of coding to generate the files. 
# Therefore it will be commented out until we make the scripts available (for now they are part of a Maven project).
# As it is straightforward to generate the files, the required input files are listed below.

# Files used to generate the ko_ncbi-geneid.list
# ${LIST_HOME}/../links/genes_ncbi-geneid.list
# ${LIST_HOME}/ko_genes.list
#sed 's/ncbi-geneid:/NCBI-GI:/' /home/omixer/workspace/YamadaData/iPath3/ko_ncbi-geneid.list |awk '{print $2"\t"$1}' >> $OUT

# Files used to generate the ko_uniprots.list
# ${LIST_HOME}/../links/genes_uniprot.list
# ${LIST_HOME}/ko_genes.list
#awk '{print $2"\t"$1}' /home/omixer/workspace/YamadaData/iPath3/ko_uniprots.list | sed 's/^up:/UNIPROT:/' >> $OUT

# Files used to generate the ko_nogs file
# /home/omixer/workspace/YamadaData/iPath3/ko_uniprots.list
# http://eggnogdb.embl.de/download/eggnog_4.5/data/NOG/
# /home/omixer/workspace/YamadaData/iPath3/eggnog4.5/uniprot_mapping_latest
#awk '{print $2"\t"$1}' /home/omixer/workspace/YamadaData/iPath3/ko_nogs >> $OUT

# https://stringdb-static.org/download/COG.mappings.v10.5.txt.gz
#cat /home/omixer/workspace/YamadaData/iPath3/string_mapping/string_ko >> $OUT

sort -u $OUT > external_annotation.map
rm $OUT
