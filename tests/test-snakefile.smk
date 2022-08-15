rule get_annotation:
    output:
        "refs/annotation.gtf",
    params:
        species="homo_sapiens",
        release="87",
        build="GRCh37",
        flavor="",  # optional, e.g. chr_patch_hapl_scaff, see Ensembl FTP.
    log:
        "logs/get_annotation.log",
    wrapper:
        "v1.4.0/bio/reference/ensembl-annotation"
