#!/bin/bash

echo $#
if [ "$#" -lt 1 ]; then
    echo "No protocol name provided"
    exit 1
fi

cwd=$(pwd)
mkdir -p $1
for file in $cwd/tests/coremark-pro/builds/linux64/gcc64/bin/*; do
    name=$(basename $file | sed "s/\.exe//g")
    config_path="$cwd/configs/learning_gem5/part3/bench.py"
    log_path=$name.log

    echo $name
    mkdir -p $cwd/$1/$name
    cd $cwd/$1/$name

    gem5=$cwd/build/X86_$1/gem5.opt
    $gem5 $config_path --bench $name --ncpus 4 2> $cwd/$1/$name/err.log 1> $cwd/$1/$name/$log_path&
done

exit 0
