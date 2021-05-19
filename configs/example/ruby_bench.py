import m5
from m5.objects import *
from m5.defines import buildEnv
from m5.util import addToPath
import os
import optparse
import sys

addToPath('../')

from common import Options
from ruby import Ruby


config_path = os.path.dirname(os.path.abspath(__file__))
config_root = os.path.dirname(config_path)
m5_root = os.path.dirname(config_root)

parser = optparse.OptionParser()
Options.addNoISAOptions(parser)

parser.add_option("--test", type=int, default=0,
                  help="Run the threads program")

Ruby.define_options(parser)

exec(compile( \
    open(os.path.join(config_root, "common", "Options.py")).read(), \
    os.path.join(config_root, "common", "Options.py"), 'exec'))

options, args = parser.parse_args()

system = System(mem_ranges = [AddrRange(options.mem_size)])

system.voltage_domain = VoltageDomain(voltage = options.sys_voltage)

system.cpu = [TimingSimpleCPU() for i in range(options.num_cpus)]

thispath = os.path.dirname(os.path.realpath(__file__))
# binary = os.path.join(thispath, '../../',
# 'tests/coremark-pro/builds/linux64/gcc64/bin/core.exe')
binary = os.path.join(thispath, '../../',
        'tests/test-progs/threads/bin/x86/linux/threads')

process = Process()
# process.cmd = [binary, '-c2', '-v0']
process.cmd = [binary, '10000']
for cpu in system.cpu:
    cpu.workload = process
    cpu.createThreads()
    cpu.createInterruptController()

Ruby.create_system(options, False, system)

system.ruby.clk_domain = SrcClockDomain(
        clock=options.ruby_clock,
        voltage_domain=system.voltage_domain)

for i, cpu in enumerate(system.cpu):
    cpu.icache_port = system.ruby._cpu_ports[i].slave
    cpu.dcache_port = system.ruby._cpu_ports[i].slave

    cpu.interrupts[0].pio = system.ruby._cpu_ports[i].master
    cpu.interrupts[0].int_master = system.ruby._cpu_ports[i].slave
    cpu.interrupts[0].int_slave = system.ruby._cpu_ports[i].master


system.clk_domain = system.ruby.clk_domain

assert(options.num_cpus == len(system.ruby._cpu_ports))

root = Root(full_system=False, system=system)
root.system.mem_mode = 'timing'

m5.ticks.setGlobalFrequency('1ns')

m5.instantiate()

exit_event = m5.simulate(options.abs_max_tick)

print('Exiting @ tick', m5.curTick(), 'because', exit_event.getCause())

