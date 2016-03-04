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

python {merge_vcf_path} --vcf {input_vcf} > {output}/{prefix}_FindSV.unsorted.vcf
python {contig_sort_path} --vcf {output}/{prefix}_FindSV.unsorted.vcf --bam {bam_path} > {output}/{prefix}_FindSV.vcf
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
#the DB section
    DB="python {query_script} --variations {output}/{prefix}_FindSV.vcf --db {db_folder_path} > {output}/{prefix}_frq.vcf\n"
#the vep section
    VEP="perl {vep_path} --cache --force_overwrite --poly b -i {output}/{prefix}_frq.vcf -o {output}/{prefix}_vep.vcf --buffer_size 5 --port {port} --vcf --per_gene --format vcf  {cache_dir} -q\n"
#the genmod section
    GENMOD="genmod score -c {genmod_score_path} {output}/{prefix}_vep.vcf > {output}/{prefix}_vep.vcf.tmp\nmv {output}/{prefix}_vep.vcf.tmp {output}/{prefix}_vep.vcf\n"
#the cleaning sections
    cleaning="{VCFTOOLS_path} --recode --recode-INFO-all --remove-filtered-all --vcf {output}/{prefix}_vep.vcf --stdout > {output}/{prefix}_FindSV_clean.vcf \n"
    filter={"header":header,"VEP":VEP,"DB":DB,"GENMOD":GENMOD,"cleaning":cleaning}
    
    scripts={"FindSV":{"calling":calling,"annotation":filter,"combine":combine}}
    return(scripts)
