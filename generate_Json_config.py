import yaml

config=[]
general={"account":""}

calling={"FT":{"FT_path":"","minimum_supporting_pairs":"6"},"CNVnator":{"CNVnator_path":"cnvnator","ROOTSYS":"","bin_size":"1000","reference_dir":""}}

filter={"VEP":{"VEP.pl_path":"","vep.cache_dir":"","port":"3337"},"DB":{"DB_path":"","overlap_parameter":"0.7"},"GENMOD":{"GENMOD_rank_model_path":""}}
config=[{"FindSV":{"general":general,"calling":calling,"annotation":filter}}]
for entry in config:
    print(yaml.dump(entry).strip())
