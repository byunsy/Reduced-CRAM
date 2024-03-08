import re
from time import perf_counter
from datetime import timedelta


def chunks(lst, n):
    return [",".join(lst[i:i + n]) for i in range(0, len(lst), n)]


def natural_sort(lst): 
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(lst, key=alphanum_key)


def check_list(lst):
    for position in lst:
        chrom = position.split(":")[0]
        if not chrom.startswith('chr') and not chrom.isdigit():
            lst.remove(position)
    return lst


def count_hg_vers(info_dict):
    counts = {}
    for ver in info_dict.values():
        counts[ver] = counts.get(ver, 0) + 1
    return counts


def write_headers_info(info, headers_dir):
    hg_ver_cnts = count_hg_vers(info)
    with open(f"{headers_dir}/summary.txt", "w") as summ:
        for ver in hg_ver_cnts:
            # how many samples in each hg version
            summ.write(f"### {ver}: {hg_ver_cnts.get(ver)} samples\n")
        for srr in info:
            # every srr and its hg version
            summ.write(f"{srr}\t{info.get(srr)}\n")
    
    # file for each hg version and list all samples with that version
    for ver in hg_ver_cnts:
        with open(f"{headers_dir}/{ver}.srr.samples", "w") as samp:
            for srr in info:
                if info.get(srr) == ver:
                    samp.write(f"{srr}\n")
    print("\tSaved header information in headers directory.")


def compute_elapsed(timer_start):
    curr = perf_counter()
    return int(curr - timer_start)


def show_elapsed(timer_start):
    curr = perf_counter()
    elapsed = str(timedelta(seconds=curr - timer_start))[:-3]
    return elapsed
    

def flatten(xss):
    """ https://realpython.com/python-flatten-list/ """
    return [x for xs in xss for x in xs]


def write_error_file(data, filename):
    """ data :  a list of tuples (srr_id, r_id, g_or_d) """
    with open(filename, 'w') as outf:
        outf.write('\n'.join('%s\t%s\t%s' % tup for tup in flatten(data))+'\n')

def write_header_error_file(data, filename):
	if any(data):
		data = [d for d in data if d]
		with open(filename, 'w') as outf:
			outf.write('\n'.join(data)+'\n')
