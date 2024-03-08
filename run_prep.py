import os
import re
import pprint
import argparse
import subprocess

import utils as _utils

def parse_args():
    """
    Parse arguments from command-lines
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--bg-depth", required=True,
                        help="path to background depth regions")
    parser.add_argument("-l", "--loci", required=True,
                        help="path to file with loci of interest")
    parser.add_argument("-r", "--reference", required=True,
                        help="path to FASTA reference")
    parser.add_argument("-t", "--hom-table", required=True,
                        help="path to homology table")
    parser.add_argument("-z", "--hg-ver", required=True,
                        help="hg version")
    parser.add_argument("-o", "--outdir", required=True,
                        help="path for outputs")
    args = parser.parse_args()
    
    return args


def parse_file(filename):
    """ 
    Parse tab-separated file and return a list of chromosomal positions (str)
    loci_list: a list of positions
    """
    with open(filename, "r") as fp:
        lines = fp.read().splitlines()    
    loci_list = [line.split("\t")[0] + ":" + line.split("\t")[1] + "-" + line.split("\t")[2] for line in lines]
    return loci_list


def to_tab(lst):
    """ 
    Change chromosomal positions into tab-separated lines 
    """
    return sorted(["\t".join(re.split(':|-', line)) for line in lst])


def get_hom_regions(loci_list, ref, table, out_file, outdir):
    """
    Perform Parascopy pool to get exact regions used for pooling/realigning
    """
    if os.path.isfile(out_file):
        subprocess.call([f'rm {out_file}'], shell=True)

    for loci in loci_list:
        subprocess.call([f'parascopy pool -i in.bam -t {table} -f {ref} -r {loci} -o out.bam -x {out_file}'], shell=True)

    with open(out_file, "r") as inpf:
        hom_reg = inpf.read().splitlines()
    hom_reg_sorted = _utils.natural_sort(hom_reg)

    tmp_file = f"{outdir}/tmp.bed"
    with open(tmp_file, "w") as outf:
        outf.writelines("\n".join(hom_reg_sorted) + "\n")

    subprocess.call([f'bedtools merge -i {tmp_file} > {out_file}'], shell=True)
    subprocess.call([f'rm {tmp_file}'], shell=True)


def combine_all_regions(depth_outf, hom_outf):

    with open(depth_outf, "r") as d_inpf, open(hom_outf, "r") as h_inpf:
        dep_reg = d_inpf.read().splitlines() 
        hom_reg = h_inpf.read().splitlines()
    combined_reg = dep_reg + hom_reg
    combined_sorted_reg = _utils.natural_sort(combined_reg)
    
    outdir = os.path.dirname(depth_outf)
    hg_ver = os.path.basename(depth_outf).split(".")[2]
    out_fp = f"{outdir}/combined.regions.{hg_ver}.bed"
    
    with open(f"{outdir}/unmerged.bed", "w") as outf:
        outf.writelines("\n".join(combined_sorted_reg) + "\n")
    
    subprocess.call([f'bedtools merge -i {outdir}/unmerged.bed > {out_fp}'], shell=True)
    subprocess.call([f'rm {outdir}/unmerged.bed'], shell=True)


def get_regions():
    """
    Prepares 
      (1) loci of interest, 
      (2) homologous regions of these loci, and 
      (3) background depth regions
    Writes a list of these regions into BED files and also returns a list
    """
    
    args = parse_args()

    DEPTH_REG = args.bg_depth 
    LOCI_LIST = args.loci   
    HOM_TABLE = args.hom_table
    FASTA_REF = args.reference
    OUTDIR = args.outdir
    HG_VER = args.hg_ver

    print()
    print(f"\tUsing the following depth region file: {DEPTH_REG}")
    print(f"\tUsing the following loci list: {LOCI_LIST}")
    print(f"\tUsing the following homology table: {HOM_TABLE}")
    print(f"\tUsing the following reference file: {FASTA_REF}\n")

    DEPTHS_FILE = f"{OUTDIR}/depth.regions.{HG_VER}.bed"
    HOM_REGIONS = f"{OUTDIR}/hom.regions.{HG_VER}.bed"
    
    subprocess.call([f'bedtools merge -i {DEPTH_REG} > {DEPTHS_FILE}'], shell=True)
    
    print(f"\tPreparing regions...\n")

    # (1) Handle loci list
    loci_list = parse_file(LOCI_LIST)

    # (2) Handle background depth window list
    depth_list = parse_file(DEPTHS_FILE)
    
    # (3) Handle homologous regions of loci of interest
    get_hom_regions(loci_list, FASTA_REF, HOM_TABLE, HOM_REGIONS, OUTDIR)
    hom_regions = parse_file(HOM_REGIONS)

    # (4) Combine both regions (optional)
    combine_all_regions(DEPTHS_FILE, HOM_REGIONS)

    print(f"\tFound the folloing regions")
    print(f"\t- LOCI REGIONS       : {len(loci_list)}")
    print(f"\t- HOMOLOGOUS REGIONS : {len(hom_regions)}")
    print(f"\t- DEPTH REGIONS      : {len(depth_list)}")
    print("\nCompleted all processes.\n")

    return loci_list + hom_regions, depth_list


if __name__ == '__main__':
    get_regions()
