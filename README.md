# Reduced-CRAM

### Setup
We first need to clone a specific branch of Parascopy. This branch includes some small modifications on Parascopy's pooling function.

```
git clone -b pool-edit https://github.com/tprodanov/parascopy.git
```

We can run `git status` to double check that we have: `On branch pool-edit`. Now, install this specific version of Parascopy. 

```
python setup.py install && pip install -e .
```

Requirements are same as the original Parascopy.

### Region Preparation

Prepares regions for depth windows and homologous regions for loci of interest.

```
time python run_prep.py \
-b depth-regions/hg38.full.bed \
-l examples/example.loci.hg38.bed \
-t homology-table/hg38.bed.gz \
-r /media/GenomeData/parascopy-sabyun/Projects/Pipeline2/reference/hg38.fa \
-z hg38 \
-o outputs
```

### Reduced CRAM generation 

Reduces CRAM files based on the provided regions BED file. 

```
time python run_reduce.py \
-i examples/example.cram.list \
-o outputs/reduced-cram \
-f /media/DATA2/1KGP-SAS-exomes/reference/GRCh38_full_analysis_set_plus_decoy_hla.fa \
-r outputs/hom.regions.hg38.bed \
-@ 8
```

