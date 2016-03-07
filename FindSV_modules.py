import yaml


def main():
#Slurm header
    header="""#! /bin/bash -l
#SBATCH -A {account}
#SBATCH -o {filename}.out
#SBATCH -e {filename}.err
#SBATCH -J {name}.job
#SBATCH -p core
#SBATCH -t {time}"""

    #the FT script
    FT="""
{FT_path} --sv  --bam {bam_path} --bai NONE --auto --minimum-supporting-pairs {minimum_suporting} --output {output}
rm {output}.tab"""
    
#the cnvnator script
ROOTPATH ="""
export ROOTSYS={rootdir}
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ROOTSYS/lib
"""

    CNVnator="""
{CNVnator_path} -root {output}.root -tree {bam_path}
{CNVnator_path} -root {output}.root -his {bin_size} -d {reference_dir}
{CNVnator_path} -root {output}.root -stat {bin_size} >> {output}.cnvnator.log
{CNVnator_path} -root {output}.root -partition {bin_size}
{CNVnator_path} -root {output}.root -call {bin_size} > {output}.cnvnator.out
{CNVnator2vcf_path} {output}.cnvnator.out  >  {output}_CNVnator.vcf
rm {output}.root
rm {output}.cnvnator.out
"""
    calling={"FT":FT,"CNVnator":CNVnator,"ROOTSYS":ROOTPATH}
    
#The combine script
    combine="""
#SBATCH -d afterok:{slurm_IDs}

python {merge_vcf_path} --vcf {input_vcf} > {output}_FindSV.unsorted.vcf
python {contig_sort_path} --vcf {output}_FindSV.unsorted.vcf --bam {bam_path} > {output}_FindSV.vcf
rm {output}_FindSV.unsorted.vcf"""
    combine={"combine":combine}
    
#The annotation header
    annotation_header="""
#SBATCH -d afterok:{combine_script_id}

"""
#the DB section
    DB="python {query_script} --variations {output}_FindSV.vcf --db {db_folder_path} > {output}_frq.vcf\n"
#the vep section
    VEP="perl {vep_path} --cache --force_overwrite --poly b -i {output}_frq.vcf -o {output}_vep.vcf --buffer_size 5 --port {port} --vcf --per_gene --format vcf  {cache_dir} -q\n"
#the genmod section
    GENMOD="genmod score -c {genmod_score_path} {output}_vep.vcf > {output}_vep.vcf.tmp\nmv {output}_vep.vcf.tmp {output}_vep.vcf\n"
    
    cleaning="python {VCFTOOLS_path} --vcf {output}_vep.vcf > {output}_FindSV_clean.vcf \n"
    filter={"header":annotation_header,"VEP":VEP,"DB":DB,"GENMOD":GENMOD,"cleaning":cleaning}
    
    scripts={"FindSV":{"calling":calling,"annotation":filter,"combine":combine,"header":header,"UPPMAX":"module load {modules}\n"}}
    return(scripts)
