import yaml


def main():
    FT=""
    CNVnator=""
    calling={"FT":FT,"CNVnator":CNVnator}
    
    
    combine=""
    combine={"combine":combine}
    
    
    VEP=""
    DB=""
    GENMOD=""
    filter={"VEP":"","DB":"","GENMOD":""}
    
    scripts={"FindSV":{"calling":calling,"annotation":filter,"combine":combine}}
    return(scripts)
