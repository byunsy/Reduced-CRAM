import os
import sys
import argparse
import subprocess

from pathlib import Path
from multiprocessing import Pool

def parse_args():
    """
    Parse arguments from command-lines
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True,
                        help="path to a list of input CRAM files")
    parser.add_argument("-o", "--outdir", required=True,
                        help="path to output directory")
    parser.add_argument("-f", "--reference", required=True,
                        help="path to FASTA reference")
    parser.add_argument("-r", "--regions", required=True,
                        help="path to regions BED file")
    parser.add_argument("-@", "--threads", required=True,
                        help="maximum number of threads")
    args = parser.parse_args()
    
    return args


def proc_reduce(cram_file, ref_file, region_file, outdir):
    """
    Reduce CRAM files based on the provided region_file
    """
    outfp_base = os.path.basename(cram_file)
    outfp_stem = Path(f"{outfp_base}").stem
    outfp = f"{outdir}/{outfp_stem}.reduced.cram" 

    try:
        print(f"\tWorking on {outfp_base}...")
        subprocess.check_call([f'samtools view -C -h -ML {region_file} -T {ref_file} {cram_file} > {outfp}'], shell=True)
        subprocess.check_call([f'samtools index {outfp}'], shell=True)
        return f"{outfp_base}\tSUCCESS"
    except subprocess.CalledProcessError:
        return f"{outfp_base}\tERROR"


def main():
    """
    Main function
    """
    args = parse_args()
    
    with open(args.input, "r") as inpf:
        CRAM_LIST = inpf.read().splitlines()
    REFNCE = args.reference
    REGION = args.regions
    OUTDIR = args.outdir
    THREAD = int(args.threads)

    print()
    print(f"\tUsing '{args.input}' as input-list of CRAM files.")
    print(f"\tUsing '{REFNCE}' as reference FASTA file.")
    print(f"\tUsing '{REGION}' as region BED file.")
    print(f"\tUsing '{OUTDIR}' as output directory.")
    print(f"\tUsing {THREAD} threads in total.\n")

    with Pool(processes=THREAD) as pool:
        pool_objs = [pool.apply_async(proc_reduce, args=(cram, REFNCE, REGION, OUTDIR)) for cram in CRAM_LIST]
        ret = [obj.get() for obj in pool_objs]

    with open(f"{OUTDIR}/summary.list", "w") as outf:
        outf.write("\n".join(ret) + "\n")

    print(f"\n\tCompleted all processes.")
    print(f"\tResults saved in '{OUTDIR}'.\n")


if __name__ == '__main__':
    main()
