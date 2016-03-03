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
    
    scripts=FindSV_modules.main()
    #run the callers
    for caller in config["FindSV"]["calling"]:
        ID=[];OUT=[];
        print(caller)
        print(scripts["FindSV"]["calling"][caller])
    #combine module; combine all the caller modules into one VCF
    print(scripts["FindSV"]["combine"]["combine"])
    #annotation module; filter and annotate the samples
    print(scripts["FindSV"]["annotation"]["DB"])
    print(scripts["FindSV"]["annotation"]["VEP"])
    print(scripts["FindSV"]["annotation"]["GENMOD"])
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
