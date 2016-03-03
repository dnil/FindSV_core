import yaml


def main():
#the FT script
    FT="""#! /bin/bash -l
#SBATCH -A {account}
#SBATCH -o {output}/slurm/calling/FT_{prefix}.out
#SBATCH -e {output}/slurm/calling/FT_{prefix}.err
#SBATCH -J FT_{prefix}.job
#SBATCH -p core
#SBATCH -t {time}

{FT_path} --sv  --bam {bam_path} --auto --minimum-supporting-pairs {minimum_suporting} --output {output}/{prefix}_FT
rm {output}/{prefix}_FT.tab"""
    
#the cnvnator script
    CNVnator="""#! /bin/bash -l
#SBATCH -A {account}
#SBATCH -o {output}/slurm/calling/CNV_{prefix}.out
#SBATCH -e {output}/slurm/calling/CNV_{prefix}.err
#SBATCH -J CNV_{prefix}.job
#SBATCH -p core
#SBATCH -t {time}

{CNVnator_path} -root {output}/{prefix}.root -tree {bam_path}
{CNVnator_path} -root {output}/{prefix}.root -his {bin_size} -d {reference_dir}
{CNVnator_path} -root {output}/{prefix}.root -stat {bin_size} >> {output}/{prefix}.cnvnator.log
{CNVnator_path} -root {output}/{prefix}.root -partition {bin_size}
{CNVnator_path} -root {output}/{prefix}.root -call {bin_size} > {output}/{prefix}.cnvnator.out
{CNVnator_path} {output}/{prefix}.cnvnator.out  >  {output}/{prefix}_CNVnator.vcf
rm {output}/{prefix}.root
rm {output}/{prefix}.cnvnator.out
"""
    calling={"FT":FT,"CNVnator":CNVnator}
    
#The combine script
    combine="""#! /bin/bash
#SBATCH -A {account}
#SBATCH -o {output}/slurm/combine/combine_{prefix}.out
#SBATCH -e {output}/slurm/combine/combine_{prefix}.err
#SBATCH -J combine_{prefix}.job
#SBATCH -p core
#SBATCH -t {time}

sbatch.write("python {merge_vcf_path} --vcf {input_vcf} > {output}/{prefix}_FindSV.unsorted.vcf
sbatch.write( "python {contig_sort_path} --vcf {output}/{prefix}_FindSV.unsorted.vcf --bam {bam_path} > {output}/{prefix}_FindSV.vcf
rm {output}/{prefix}_FindSV.unsorted.vcf"""
    combine={"combine":combine}
    
#The annotation header
    header="""#SBATCH -A {account}
#SBATCH -o {output}/slurm/annotation/annotation_{prefix}.out
#SBATCH -e {output}/slurm/annotation/annotation_{prefix}.err
#SBATCH -J annotation_{prefix}.job
#SBATCH -p core
#SBATCH -t {time}

"""
#the vep section
    VEP=""
#the DB section
    DB=""
#the genmod section
    GENMOD=""
#the cleaning sections
    cleaning=""
    filter={"header":header,"VEP":VEP,"DB":DB,"GENMOD":GENMOD,"cleaning":cleaning}
    
    scripts={"FindSV":{"calling":calling,"annotation":filter,"combine":combine}}
    return(scripts)
