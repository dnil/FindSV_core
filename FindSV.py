import argparse
import sys
import yaml
import os
import FindSV_modules

#read the config file, prefer command line option to config
def readconfig(path,command_line):
    config={}
    if path:
        config_file=path
    else:
        programDirectory = os.path.dirname(os.path.abspath(__file__))
        config_file=os.path.join(programDirectory,"config.txt")
    print config_file
    with open(config_file, 'r') as stream:
        config=yaml.load(stream)
    return(config)

def main(args):
    config=readconfig(args.config,args);
    caller_slurm_ID=[];
    caller_output=[];
    #fetch the scripts
    scripts=FindSV_modules.main()
    #initiate the output location
    if(args.output):
        output=args.output
    else:
        output=config["FindSV"]["general"]["output"]
    #the prefix of the output is set to the prefix of the bam file
    prefix=args.bam.split("/")[-1]
    prefix=prefix.replace(".bam","")
        
    #run the callers
    input_vcf=""
    for caller in config["FindSV"]["calling"]:
        general_config=config["FindSV"]["general"]
        caller_config=config["FindSV"]["calling"][caller]
        if caller == "FT":
            FT=scripts["FindSV"]["calling"][caller].format(account=general_config["account"],output=output,prefix=prefix,time="30:00:00",FT_path=caller_config["FT_path"],bam_path=args.bam,minimum_suporting=caller_config["minimum_supporting_pairs"])
            print(FT)
            input_vcf += "{}/{}_FT_inter_chromosomal.vcf ".format(output,prefix)
            input_vcf += "{}/{}_FT_intra_chromosomal.vcf ".format(output,prefix)
        elif caller =="CNVnator":
            CNVNator=scripts["FindSV"]["calling"][caller].format(account=general_config["account"],output=output,prefix=prefix,time="30:00:00",CNVnator_path=caller_config["CNVnator_path"],bam_path=args.bam,bin_size=caller_config["bin_size"],reference_dir=caller_config["reference_dir"])
            print(CNVNator)
            input_vcf += "{}/{}_CNVnator.vcf ".format(output,prefix)
    #combine module; combine all the caller modules into one VCF
    combine_config=config["FindSV"]["combine"]
    combine=scripts["FindSV"]["combine"]["combine"].format(account=general_config["account"],output=output,prefix=prefix,time="3:00:00",merge_vcf_path=combine_config["merge_vcf_path"],input_vcf=input_vcf,contig_sort_path=combine_config["contig_sort_path"],bam_path=args.bam)
    print(combine)
    
    #annotation module; filter and annotate the samples
    annotation_config=config["FindSV"]["annotation"]
    
    annotation=scripts["FindSV"]["annotation"]["header"].format(account=general_config["account"],output=output,prefix=prefix,time="10:00:00")
    annotation += scripts["FindSV"]["annotation"]["DB"].format(query_script=annotation_config["DB"]["DB_script_path"],output=output,prefix=prefix,db_folder_path=annotation_config["DB"]["DB_path"])
    cache_dir=""
    if not annotation_config["VEP"]["cache_dir"] == "":
        cache_dir=" --dir {}".format(annotation_config["VEP"]["cache_dir"])
    annotation += scripts["FindSV"]["annotation"]["VEP"].format(vep_path=annotation_config["VEP"]["VEP.pl_path"],output=output,prefix=prefix,port=annotation_config["VEP"]["port"],cache_dir=cache_dir)
    annotation += scripts["FindSV"]["annotation"]["GENMOD"].format(genmod_score_path=annotation_config["GENMOD"]["GENMOD_rank_model_path"],output=output,prefix=prefix)
    annotation += scripts["FindSV"]["annotation"]["cleaning"].format(output=output,prefix=prefix,VCFTOOLS_path=annotation_config["VCFTOOLS"]["VCFTOOLS_path"])
    print(annotation)
    return(None)





parser = argparse.ArgumentParser("FindSV core module")
parser.add_argument('--bam', type=str,help="run the pipeline")
parser.add_argument('--output', type=str,default=None,help="the output is stored in this folder")
parser.add_argument("--config",type=str, default=None,help="the location of the config file(default= the same folder as the FindSV-core script")
parser.add_argument("--test",action="store_true",help="Check so that all the required files are accessible")
parser.add_argument("--install",action="store_true",help="Install FindSV core module")
args = parser.parse_args()

if args.test:
    print("Testing the pipeline components")
elif args.install:
    print("Installing FindSV")
else:
    if args.bam:
        main(args)
    else:
        print("error: --bam is required")
