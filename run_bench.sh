#!/bin/bash

for file in ./tests/coremark-pro/builds/linux64/gcc64/bin/*; do
    name=$(basename $file | sed "s/\.exe//g")
    config_path="configs/learning_gem5/part3/bench.py"
    log_path=$name.log
    ./build/X86_MSI/gem5.opt $config_path --bench $name > $log_path &
done

