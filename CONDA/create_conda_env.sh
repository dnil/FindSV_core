conda config --add channels r
conda config --add channels bioconda

conda env create --name GENMOD_FINDSV -f GENMOD.yml
conda create --name samtools_FINDSV samtools
conda create --name VEP_FINDSV variant-effect-predictor
