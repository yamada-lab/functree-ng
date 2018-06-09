OUT=tmp
awk '{print $2"\t"$1}' /home/omixer/workspace/YamadaData/iPath3/ko_nogs > $OUT
sed 's/ncbi-geneid:/NCBI-GI:/' /home/omixer/workspace/YamadaData/iPath3/ko_ncbi-geneid.list |awk '{print $2"\t"$1}' >> $OUT
awk '{print $2"\t"$1}' /home/omixer/workspace/YamadaData/iPath3/ko_uniprots.list | sed 's/^up:/UNIPROT:/' >> $OUT
cat /home/omixer/workspace/YamadaData/iPath3/string_mapping/string_ko >> $OUT
sed 's/^ko://' /home/omixer/workspace/YamadaData/iPath3/list/ko_reaction.list | awk '{print $2"\t"$1}' | sed 's/^rn://' >> $OUT
sed 's/^ko://' /home/omixer/workspace/YamadaData/iPath3/list/ko_cog.list | awk '{print $2"\t"$1}' | sed 's/^cog://' >> $OUT
sed 's/^ko://' /home/omixer/workspace/YamadaData/iPath3/list/ko_enzyme.list | awk '{print $2"\t"$1}' | sed 's/^ec:/EC:/' >> $OUT
sed 's/^ko://' /home/omixer/workspace/YamadaData/iPath3/list/ko_genes.list | awk '{print $2"\t"$1}' >> $OUT
sed 's/^ko://' /home/omixer/workspace/YamadaData/iPath3/list/ko_go.list | awk '{print $2"\t"$1}' | sed 's/^go:/GO:/' >> $OUT
sed 's/^ko://' /home/omixer/workspace/YamadaData/iPath3/list/ko_cazy.list | awk '{print $2"\t"$1}' | sed 's/^cazy:/CAZY:/'>> $OUT
sort -u $OUT > external_annotation.map