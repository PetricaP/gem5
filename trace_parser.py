from file_read_backwards import FileReadBackwards
from argparse import ArgumentParser


class my_filter:
    def __init__(self, filter_fun):
        self._filter = filter_fun

    def and_(self, another):
        return my_filter(lambda l: self._filter(l) and another._filter(l))

    def __call__(self, l):
        return self._filter(l)


class basic_filter(my_filter):
    def __init__(self):
        super().__init__(lambda l: l.startswith(' ' * 6) and l[6].isdigit())


class addr_filter(my_filter):
    def __init__(self, addr):
        super().__init__(lambda l: int(l.split()[7][:-1], 0) == addr)


def auto_int(x):
    return int(x, 0)


parser = ArgumentParser()
parser.add_argument('trace_path', help='Input trace file')
parser.add_argument('-a', '--addr', type=auto_int, help='Address to monitor')
parser.add_argument('-c', '--chunk_size', type=int, default=100,
                    help='Number of transitions to check')
args = parser.parse_args()

fltr = basic_filter()
if args.addr:
    fltr = fltr.and_(addr_filter(args.addr))

with FileReadBackwards(args.trace_path) as f:
    finished = False
    while True:
        transition_lines = []
        for i in range(args.chunk_size):
            l = f.readline()

            while l and not fltr(l):
                l = f.readline()

            if not l:
                finished = True
                break

            transition_lines.append(l)

        transition_lines.reverse()

        transition_parts = [tl.split() for tl in transition_lines]
        max_cache_num = int(max(transition_parts,
                                key=lambda tp: int(tp[1]))[1])

        addr_transitions = {}
        for parts in transition_parts:
            addr = int(parts[7][:-1], 16)
            if not args.addr or addr == args.addr:
                if addr in addr_transitions:
                    addr_transitions[addr].append(parts)
                else:
                    addr_transitions[addr] = [parts]

        for addr, transitions in addr_transitions.items():
            print(f'Cache line 0x{addr:X}')
            print('\tDirectory',end='')
            for i in range(max_cache_num + 1):
                print(f'\tL1Cache {i}', end='')
            print()

            for parts in transitions:
                number = parts[1]
                device = parts[2]
                event = parts[3]
                if device == 'Directory':
                    print(f'\t{parts[3]} => {parts[4]}')
                elif device == 'L1Cache':
                    for i in range(int(number) + 1):
                        print('\t\t', end='')
                    print(f'\t{parts[3]} => {parts[4]}')
            print()

        if finished:
            break

        input('Press ENTER to get another chunk')

