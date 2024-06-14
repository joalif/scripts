import sys
import re
import argparse
import os


def write_out(outdir, cpu, freq):
    outfile = os.path.join(outdir, 'freq_' + cpu + '.txt')
    with open(outfile, 'a') as outf:
        outf.writelines(freq+'\n')


def parse(infile, outdir):
    cpu_match = re.compile(r'analyzing CPU (\d+):')
    freq_match = re.compile(r'\s+current CPU frequency is (\d+(?:\.\d+)?) (G|M)Hz')

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    with open(infile, 'r') as inf:
        for line in inf:
            if res := cpu_match.match(line):
                cpu = res.group(1)
                # print(cpu)
            if res := freq_match.match(line):
                freq = res.group(1)
                if res.group(2) == 'G':
                    freq = int(float(freq) * 1000)
                # print(int(freq))
                write_out(outdir, cpu, str(freq))

def write_out_msg(msgs, outfile=None):
    if outfile:
        with open(outfile, 'a') as f:
            for line in msgs:
                f.writelines(line+'\n')
    else:
        for line in msgs:
            print(line)


def process(indir, outfile=None):
    for cpu in range(0, 256):
        inf = os.path.join(indir, 'freq_' + str(cpu) + '.txt')
        with open(inf, 'r') as f:
            msgs = []
            msg = f'CPU {cpu}'
            init_freq = '3000'
            i = 0
            msgs.append(msg)
            for line in f:
                line = line.strip()
                i += 1
                if line != init_freq:
                    msg = f'From {init_freq} to {line} at {i}'
                    msgs.append(msg)
                    # print("Transition from %s to %s, pos %d" % (init_freq, line, i))
                    init_freq = line
            if len(msgs) > 1:
                write_out_msg(msgs, outfile)


def main():
    parser = argparse.ArgumentParser(description='Dirty hacks to parse freq data.'
                                                 'Be careful, this writes files in append mode,'
                                                 'and does not cleanup. If you run it twice '
                                                 'without cleaning up yourself, you will get '
                                                 'files with duplicate data.')
    subparsers = parser.add_subparsers(dest='command', help='Sub-command help')

    # Create the parser for the "parse" command
    parser_parse = subparsers.add_parser('parse',
                                         help='Parse the cpufreq.info and save to output directory')
    parser_parse.add_argument('input_file', type=str,
                              help='The cpufreq.info.<session>.out to parse')
    parser_parse.add_argument('output_dir', type=str,
                              help='The directory to save the parsed output. '
                                   'It will parse the data per cpu and create freq_<cpu>.txt '
                                   'files in the directory')

    # Create the parser for the "process" command
    parser_process = subparsers.add_parser('process',
                                           help='Process the data in the directory. '
                                                'By default prints to stdout, unless '
                                                'output file is provided as argument')
    parser_process.add_argument('input_dir', type=str,
                                help='The directory containing freq_<cpu>.txt files')
    parser_process.add_argument('--outfile', type=str,
                                help='Optional output file')

    args = parser.parse_args()

    if args.command == 'parse':
        parse(args.input_file, args.output_dir)
    elif args.command == 'process':
        process(args.input_dir, args.outfile)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
