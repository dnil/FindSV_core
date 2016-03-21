import subprocess
import os
import yaml
import fnmatch

#read the config file, prefer command line option to config
def readconfig(path):
    config={}
    with open(path, 'r') as stream:
        config=yaml.load(stream)
    return(config)

#test if file is readable
def readable_script(file):
    return(os.access(file, os.R_OK))

#test if folder/file exists
def file_exists(file):
    return(os.path.exists(file))
    
#check if command exists
def command_exists(cmd):
    return (subprocess.call("type " + cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0 )
    
#check if a conda environment is properly installed
def conda_check(environment, software):
    try:
        installed=subprocess.check_output("conda list -n {}".format(environment),shell = True)
    except:
        return(False)
    installed_software=installed.split("\n")
    for package in installed_software:
        try:
            package_name=package.split()[0]
        except:
            pass
        #the environment exists and the package of interest is installed
        if software == package_name:
            return(True)
    return(False)

def recursive_file_search(folder):
    for file in os.listdir(folder):
        if fnmatch.fnmatch(file, '*.fa'):
            return(True)
    return False

#check the callers
def caller_test(config):
    #check if FT is installed
    error=False
    FT_path=config["FindSV"]["calling"]["FT"]["FT_path"]
    if not file_exists(FT_path) and not command_exists(FT_path):
        print("ERROR: FindTranslocations is not installed")
        error=True
    UPPMAX=config["FindSV"]["general"]["UPPMAX"]
    if UPPMAX == "":
    
        cnvnator_path=config["FindSV"]["calling"]["CNVnator"]["CNVnator_path"]
        ROOTSYS_path=config["FindSV"]["calling"]["CNVnator"]["ROOTSYS"]
        reference_dir=config["FindSV"]["calling"]["CNVnator"]["reference_dir"]
        cnvnator2vcf_path=config["FindSV"]["calling"]["CNVnator"]["CNVnator2vcf_path"]
        
        #check if CNVnator is installed
        if not file_exists(cnvnator_path) and not command_exists(cnvnator_path):
            print("ERROR: Cnvnator is not installed")
            error=True
        #check if the root directory is available
        if not file_exists(ROOTSYS_path) and not ROOTSYS_path == "":
            print("ERROR: The root folder does not exist")
            error=True
        #check if cnvnator2vcf is available
        if not readable_script(cnvnator2vcf_path) and not command_exists(cnvnator2vcf_path):
            print("ERROR: unnable to find the cnvnator2VCF.pl script")
            error=True
            
        #check if the reference folder is avaialble and if it contains fa files
        if not file_exists(reference_dir):
            print("WARNING: cannot find the reference files(cnvnator will not perform GC correction")
        elif not recursive_file_search(reference_dir):
            print("WARNING: cannot find the reference files(cnvnator will not perform GC correction")
    return(error)
       
#test the annotation tools
def annotation_test(config):
    error=False
    #check the frequency db script
    db_script=config["FindSV"]["annotation"]["DB"]["DB_script_path"]
    db_folder=config["FindSV"]["annotation"]["DB"]["DB_path"]
    if db_folder == "":
        print("WARNING: the frequency db folder path is not set, the frequency db annotation will be skipped")
    elif not readable_script(db_script):
        print("WARNING: the frequency db script was not found, the frequency db annotation will be skipped")
    #check the genmod installation, genmod could either be installed via conda or present in the local python version
    genmod_conda=config["FindSV"]["conda"]["genmod"]
    if genmod_conda == "":
        if not command_exists("genmod"):
            print("WARNING: genmod is not installed, genmod annotation will be skipped")
    else:
        if not (conda_check("GENMOD_FINDSV", "genmod")):
            print("WARNING: the vep script is not readable, vep annotation will be skipped")

    genmod_file=config["FindSV"]["annotation"]["GENMOD"]["GENMOD_rank_model_path"]
    if not (readable_script(genmod_file)):
        print("WARNING: the genmod ini file was not found, genmod annotation will be skipped")

    UPPMAX=config["FindSV"]["general"]["UPPMAX"]
    if UPPMAX == "":
        #check the vep installation, vep could either be installed via conda or installed directly on the system
        vep_conda=config["FindSV"]["conda"]["vep"]
        if vep_conda =="":
            vep_path=config["FindSV"]["annotation"]["VEP"]["VEP.pl_path"]
            if not (readable_script(vep_path)):
                print("WARNING: the vep script is not readable, vep annotation will be skipped")
        else:
            if not (conda_check("VEP_FINDSV", "variant-effect-predictor")):
                print("WARNING: the vep script is not readable, vep annotation will be skipped")
    #check the samtools installtion
    if UPPMAX == "":
        samtools_conda=config["FindSV"]["conda"]["samtools"]
        if samtools_conda == "":
            if not command_exists("samtools"):
                print("ERROR: samtools is required, either install the samtools_FINDSV conda environment or add samtools to system path")
                error=True
        else:
            if not (conda_check("samtools_FINDSV", "samtools")):
                print("ERROR: samtools is required, either install the samtools_FINDSV conda environment or add samtools to system path")
    
    return(error)

#main, check if the pipeline is properly set up
def main(config_path):
    config=readconfig(config_path)
    print("-----testing the callers-----\n")
    caller_error=caller_test(config)
    print("-----testing the annoation tools-----\n")
    annotation_error=annotation_test(config)
    return(caller_error,annotation_error)
