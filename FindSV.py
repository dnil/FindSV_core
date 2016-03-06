import argparse
import sys
import yaml
import os
import FindSV_modules
import subprocess

#this function prints the scripts, submits the slurm job, and then returns the jobid
def submitSlurmJob(path,message):
    slurm=open( path ,"w")
    slurm.write(message)
    slurm.close()

    process = "sbatch {0}".format(path)
    p_handle = subprocess.Popen(process, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)    
    p_out, p_err = p_handle.communicate()
    try:
        return( re.match(r'Submitted batch job (\d+)', p_out).groups()[0] );
    except:
        return("123456")

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
    programDirectory = os.path.dirname(os.path.abspath(__file__))
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
    #create a folder to keep the output sbatch scripts and logs
    if not os.path.exists(os.path.join(output,"slurm/calling/")):
        os.makedirs(os.path.join(output,"slurm/calling/"))
    if not os.path.exists(os.path.join(output,"slurm/combine/")):
        os.makedirs(os.path.join(output,"slurm/combine/"))
    if not os.path.exists(os.path.join(output,"slurm/annotation/")):
        os.makedirs(os.path.join(output,"slurm/annotation/"))    
    #the prefix of the output is set to the prefix of the bam file
    prefix=args.bam.split("/")[-1]
    prefix=prefix.replace(".bam","")
        
    #run the callers
    input_vcf=""
    sbatch_ID=[]
    for caller in config["FindSV"]["calling"]:
        general_config=config["FindSV"]["general"]
        caller_config=config["FindSV"]["calling"][caller]
        #run the FT script
        if caller == "FT":
            job_name="FT_{}".format(prefix)
            process_files=os.path.join(output,"slurm/calling/",job_name)
            #generate the header
            FT=scripts["FindSV"]["header"].format(account=general_config["account"],time="30:00:00",name=job_name,filename=process_files)
            output_prefix=os.path.join(output,"{}_FT".format(prefix))
            #generate the body
            FT += scripts["FindSV"]["calling"][caller].format(output=output_prefix,FT_path=caller_config["FT_path"],bam_path=args.bam,minimum_suporting=caller_config["minimum_supporting_pairs"])
            sbatch_ID.append(submitSlurmJob( os.path.join(output,"slurm/calling/FT_{}.slurm".format(prefix)),FT) )
            input_vcf += "{}_inter_chromosomal.vcf ".format(output_prefix)
            input_vcf += "{}_intra_chromosomal.vcf ".format(output_prefix)
        #run cnvnator
        elif caller =="CNVnator":
            job_name="CNVnator_{}".format(prefix)
            process_files=os.path.join(output,"slurm/calling/",job_name)
            CNVNator=scripts["FindSV"]["header"].format(account=general_config["account"],time="30:00:00",name=job_name,filename=process_files)
            output_prefix=os.path.join(output,prefix)
            CNVNator += scripts["FindSV"]["calling"][caller].format(output=output_prefix,CNVnator_path=caller_config["CNVnator_path"],bam_path=args.bam,bin_size=caller_config["bin_size"],reference_dir=caller_config["reference_dir"],CNVnator2vcf_path=caller_config["CNVnator2vcf_path"])
            input_vcf += "{}_CNVnator.vcf ".format(output_prefix)
            sbatch_ID.append(submitSlurmJob( os.path.join(output,"slurm/calling/CNVnator_{}.slurm".format(prefix)) ,CNVNator) )
            
    #combine module; combine all the caller modules into one VCF
    job_name="combine_{}".format(prefix)
    process_files=os.path.join(output,"slurm/combine/",job_name)
    merge_VCF_path=os.path.join(programDirectory,"internal_scripts","mergeVCF.py")
    contig_sort=os.path.join(programDirectory,"internal_scripts","contigSort.py")
    combine=scripts["FindSV"]["header"].format(account=general_config["account"],time="3:00:00",name=job_name,filename=process_files)
    combine += scripts["FindSV"]["combine"]["combine"].format(output=output_prefix,merge_vcf_path=merge_VCF_path,input_vcf=input_vcf,contig_sort_path=contig_sort,bam_path=args.bam,slurm_IDs=":".join(sbatch_ID))
    combine_ID=submitSlurmJob( os.path.join(output,"slurm/combine/combine_{}.slurm".format(prefix)) , combine)
    
    #annotation module; filter and annotate the samples
    annotation_config=config["FindSV"]["annotation"]
    job_name="annotation_{}".format(prefix)
    process_files=os.path.join(output,"slurm/annotation/",job_name)
    annotation = scripts["FindSV"]["header"].format(account=general_config["account"],time="10:00:00",name=job_name,filename=process_files)
    
    output_prefix=os.path.join(output,prefix)
    annotation += scripts["FindSV"]["annotation"]["header"].format(combine_script_id=combine_ID)
    annotation += scripts["FindSV"]["annotation"]["DB"].format(query_script=annotation_config["DB"]["DB_script_path"],output=output_prefix,db_folder_path=annotation_config["DB"]["DB_path"])
    cache_dir=""
    if not annotation_config["VEP"]["cache_dir"] == "":
        cache_dir=" --dir {}".format(annotation_config["VEP"]["cache_dir"])
    annotation += scripts["FindSV"]["annotation"]["VEP"].format(vep_path=annotation_config["VEP"]["VEP.pl_path"],output=output_prefix,port=annotation_config["VEP"]["port"],cache_dir=cache_dir)
    annotation += scripts["FindSV"]["annotation"]["GENMOD"].format(genmod_score_path=annotation_config["GENMOD"]["GENMOD_rank_model_path"],output=output_prefix)
    clean_VCF_path=os.path.join(programDirectory,"internal_scripts","cleanVCF.py")
    annotation += scripts["FindSV"]["annotation"]["cleaning"].format(output=output_prefix,VCFTOOLS_path=clean_VCF_path)
    submitSlurmJob( os.path.join(output,"slurm/annotation/annotation_{}.slurm".format(prefix)) , annotation)





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
