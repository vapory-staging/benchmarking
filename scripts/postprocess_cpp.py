#!/usr/bin/python

import sys, re
from tabulate import tabulate

#bench_bn256Add/chfast1: 8508 ns
precompiledRegexp = re.compile("bench_(.*): ([\d]+) ns") 

def getGas(precompile):
    gasLookupTable = {
        "ecrecover/" :3000 , 
        "bn256Add/chfast1" : 500 , 
        "bn256Add/chfast2" :500 , 
        "bn256Add/cdetrio1" : 500 , 
        "bn256Add/cdetrio2" : 500 , 
        "bn256Add/cdetrio3" : 500 , 
        "bn256Add/cdetrio4" : 500 , 
        "bn256Add/cdetrio5" : 500 , 
        "bn256Add/cdetrio6" : 500 , 
        "bn256Add/cdetrio7" : 500 , 
        "bn256Add/cdetrio8" : 500 , 
        "bn256Add/cdetrio9" : 500 , 
        "bn256Add/cdetrio10" : 500 , 
        "bn256Add/cdetrio11" : 500 , 
        "bn256Add/cdetrio12" : 500 , 
        "bn256Add/cdetrio13" : 500 , 
        "bn256Add/cdetrio14" : 500 , 
        "bn256ScalarMul/chfast1" : 2000 , 
        "bn256ScalarMul/chfast2" : 2000 , 
        "bn256ScalarMul/chfast3" : 2000 , 
        "bn256Pairing/jeff1" : 260000 , 
        "bn256Pairing/jeff2" : 260000 , 
        "bn256Pairing/jeff3" : 260000 , 
        "bn256Pairing/jeff4" : 340000 , 
        "bn256Pairing/jeff5" : 340000 , 
        "bn256Pairing/jeff6" : 260000 , 
        "bn256Pairing/empty_data" :100000 , 
        "bn256Pairing/one_point" : 180000 , 
        "bn256Pairing/two_point_match_2" :260000 , 
        "bn256Pairing/two_point_match_3" :260000 , 
        "bn256Pairing/two_point_match_4" :260000 , 
        "bn256Pairing/ten_point_match_1" :900000 , 
        "bn256Pairing/ten_point_match_2" :900000 , 
        "bn256Pairing/ten_point_match_3" :260000 , 
    }
    if precompile in gasLookupTable.keys():
        return gasLookupTable[precompile]

    return 0
def calc(line):
    for exp in [precompiledRegexp]:#, opRegexp]:
        m = exp.search(line)
        if m:
            (name, ns) = ( m.group(1), m.group(2))
            return {"name" : name, "gas": getGas(name), "ns" : float(ns)}


def postprocess(f):
    items = []
    lines = f.split("\n")
    #Do first pass and find the values for the ecdsarecover
    for l in lines:
        out = calc(l)
        if out:
            if out['name'].find("ecrecover") >= 0:
                ecdsaMGperS = 1000* out['gas']/out['ns']
                #print("Ecdsarecover at %f Mgas/s" %  ecdsaMGperS ) 
                ecdsaTime = out['ns']
                ecdsaGas = out['gas']

    for l in lines:
        out =  calc(l)
        if out:
            name = out['name']
            gas = out['gas']
            time = out['ns']
            gasPerNs = float(gas) / float(time)
            MgasPerS = (1e+3*float(gas)) / float(time)
            idealGasPrice = time / 100
            
            diff = 100 * gas / idealGasPrice

            diff_compared_to_ecdsa = ecdsaMGperS/MgasPerS


            item = [name, gas, "%14.02f" % float(time),  MgasPerS, idealGasPrice , "%.2f %%" % diff, "%.2f " % diff_compared_to_ecdsa]

            items.append(item)
    print "```"
    print tabulate(items, headers=['Name', 'Gascost', 'Time (ns)', 'MGas/S', 'Gasprice for 10MGas/S', "Gas/Ideal percent", "VS Ecdsa"])
    print "```"
    print """
Columns

* `MGas/S` - Shows what MGas per second was measured on that machine at that time
* `Gasprice for 10MGas/S` shows what the gasprice should have been, in order to reach 10 MGas/second
* `Gas/Ideal percent` shows how the gas should be adjusted, in order to reach 10 MGas/second
* `VS Ecdsa` shows a factor by which the gascost should be multiplied, in order to reach the same G/S as `ecRecover`
    """

def test():
    t = """
#cat /proc/cpuinfo | grep "model name" | head -n 1
model name  : Intel(R) Core(TM) i7-4790K CPU @ 4.00GHz

#cpupower -c 0 frequency-info | grep "CPU frequency"
  current CPU frequency is 4.40 GHz.

#taskset 0x1 test/testeth -t 'PrecompiledTests/bench*' -- --verbosity 1
Running 4 test cases...
Test Case "bench_ecrecover":
bench_ecrecover/: 70528 ns
Test Case "bench_bn256Add":
bench_bn256Add/chfast1: 8508 ns
bench_bn256Add/chfast2: 8511 ns
bench_bn256Add/cdetrio1: 2331 ns
bench_bn256Add/cdetrio2: 2328 ns
bench_bn256Add/cdetrio3: 2341 ns
bench_bn256Add/cdetrio4: 2317 ns
bench_bn256Add/cdetrio5: 2327 ns
bench_bn256Add/cdetrio6: 4990 ns
bench_bn256Add/cdetrio7: 4987 ns
bench_bn256Add/cdetrio8: 4993 ns
bench_bn256Add/cdetrio9: 4990 ns
bench_bn256Add/cdetrio10: 4986 ns
bench_bn256Add/cdetrio11: 7602 ns
bench_bn256Add/cdetrio12: 7598 ns
bench_bn256Add/cdetrio13: 8494 ns
bench_bn256Add/cdetrio14: 6605 ns
Test Case "bench_bn256ScalarMul":
bench_bn256ScalarMul/chfast1: 113076 ns
bench_bn256ScalarMul/chfast2: 455600 ns
bench_bn256ScalarMul/chfast3: 454158 ns
Test Case "bench_bn256Pairing":
bench_bn256Pairing/jeff1: 11390929 ns
bench_bn256Pairing/jeff2: 11386363 ns
bench_bn256Pairing/jeff3: 11391780 ns
bench_bn256Pairing/jeff4: 15662968 ns
bench_bn256Pairing/jeff5: 15668956 ns
bench_bn256Pairing/jeff6: 11515980 ns
bench_bn256Pairing/empty_data: 2549477 ns
bench_bn256Pairing/one_point: 7221599 ns
bench_bn256Pairing/two_point_match_2: 11092886 ns
bench_bn256Pairing/two_point_match_3: 11393495 ns
bench_bn256Pairing/two_point_match_4: 11396027 ns
bench_bn256Pairing/ten_point_match_1: 45259353 ns
bench_bn256Pairing/ten_point_match_2: 45700240 ns
bench_bn256Pairing/ten_point_match_3: 11390441 ns

*** No errors detected
"""
    postprocess(t)

if __name__ == '__main__':
    test()

    if len(sys.argv) < 2:
        print("usage : postprocess_geth <file>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        postprocess(f.read())
