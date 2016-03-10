conda config --add channels r
conda config --add channels bioconda

conda create env --name GENMOD_FINDSV -f GENMOD.yaml
conda create --name samtools_FINDSV samtools
conda create --name VEP_FINDSV variant-effect-predictor
