Find SV core module
Run

To analyse one bam file and put the output in the output_folder type:

python FindSV.py --bam file.bam --output output_folder

To analyse a fodler containing bam files type:

python FindSV.py --folder input_folder --output output_folder

or skip the --output flag to put the output in the directory given py the config file.

Installation
non-uppmax system:
prerequisites

FindTranslocations

CNVnator

samtools

genmod

vep

these softwares needs to be installed and their path must be added to the config file
Depending on how the root system was installed the path of the oot folder may need to be added as well

UPPMAX system:
by setting the uppmax flag in the config file to anthing except "", the uppmax settings and modules will be used. Then the following tools must be installed:
FindTranslocations

genmod
vep

their paths need to be added to the config file

Reference_dir
The path to the reference directory is set using the reference_dir flag. There reference needs to be split per chromosome.



