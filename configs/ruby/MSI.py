from .Ruby import create_topology, create_directories
from .Ruby import send_evicts

import math
import m5

from m5.objects import *
from m5.defines import buildEnv


class L1Cache(RubyCache): pass

def define_options(parser):
    return

def create_system(options, full_system, system, dma_ports, bootmem,
                  ruby_system):
    if buildEnv['PROTOCOL'] != 'MSI':
        panic("This script requires the MSI protocol to be built.")

    cpu_sequencers = []
    l1_controllers = []

    block_size_bits = int(math.log(options.cacheline_size, 2))

    for i in range(options.num_cpus):
        cache = L1Cache(size = options.l1d_size,
                        assoc = options.l1d_assoc,
                        start_index_bit = block_size_bits)

        # Fro ruby random tester
        if len(system.cpu) == 1:
            clk_domain = system.cpu[0].clk_domain
        else:
            clk_domain = system.cpu[i].clk_domain

        l1_controller = L1Cache_Controller(
            version=i,
            cacheMemory=cache,
            send_evictions=send_evicts(options),
            transitions_per_cycle=options.ports,
            clk_domain=clk_domain,
            ruby_system = ruby_system)

        cpu_seq = RubySequencer(
            version=i,
            icache=cache,
            dcache=cache,
            clk_domain=clk_domain,
            ruby_system=ruby_system)

        l1_controller.sequencer = cpu_seq
        ruby_system.__dict__['l1_cntrl%d' % i] = l1_controller

        cpu_sequencers.append(cpu_seq)
        l1_controllers.append(l1_controller)

        l1_controller.mandatoryQueue = MessageBuffer()

        l1_controller.requestToDir = MessageBuffer(ordered=True)
        l1_controller.requestToDir.master = ruby_system.network.slave

        l1_controller.responseToDirOrSibling = MessageBuffer(ordered=True)
        l1_controller.responseToDirOrSibling.master = ruby_system.network.slave

        l1_controller.forwardFromDir = MessageBuffer(ordered=True)
        l1_controller.forwardFromDir.slave = ruby_system.network.master

        l1_controller.responseFromDirOrSibling = MessageBuffer(ordered=True)
        l1_controller.responseFromDirOrSibling.slave = \
            ruby_system.network.master

    phys_mem_size = sum([r.size() for r in system.mem_ranges])

    assert(phys_mem_size % options.num_dirs == 0)
    mem_module_size = phys_mem_size / options.num_dirs

    ruby_system.memctrl_clk_domain = DerivedClockDomain(
            clk_domain=ruby_system.clk_domain,
            clk_divider=3)

    mem_dir_cntrl_nodes, rom_dir_cntrl_node = create_directories(
            options,
            bootmem,
            ruby_system,
            system)

    dir_controllers = mem_dir_cntrl_nodes[:]
    if rom_dir_cntrl_node is not None:
        dir_controllers.append(rom_dir_cntrl_node)

    for dir_controller in dir_controllers:
        dir_controller.forwardToCache = MessageBuffer(ordered=True)
        dir_controller.forwardToCache.master = ruby_system.network.slave

        dir_controller.responseToCache = MessageBuffer(ordered=True)
        dir_controller.responseToCache.master = ruby_system.network.slave

        dir_controller.requestFromCache = MessageBuffer(ordered=True)
        dir_controller.requestFromCache.slave = ruby_system.network.master

        dir_controller.responseFromCache = MessageBuffer(ordered=True)
        dir_controller.responseFromCache.slave = ruby_system.network.master

        dir_controller.requestToMemory = MessageBuffer()
        dir_controller.responseFromMemory = MessageBuffer()

    # TODO:dma stuff

    controllers = l1_controllers + dir_controllers

    ruby_system.network.number_of_virtual_networks = 3
    topology = create_topology(controllers, options)

    return cpu_sequencers, mem_dir_cntrl_nodes, topology

