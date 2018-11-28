import re
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument("-o", "--operations", dest="operations",
                    help="Gets the comma separated list of operations and if you want to "
                         "approximate all the SIMD "
                         "operations give value == all")
parser.add_argument("-b", "--bits", dest="bits",
                    help="Number of bits you want to approximate")

parser.add_argument("-p", "--path", dest="path",
                    help="Path of the mediaops file", default="./src/arch/x86/isa/microops",
                    required=False)

options = parser.parse_args()


def main():
    operations = options.operations.split(',')
    bits = 2 ** int(options.bits)
    if options.operations == 'all':
        operations = ['add', 'sub', 'div', 'mul', 'min', 'max', 'sqrt']
    file_str = {}
    content = ''
    for operation in operations:
        f = open(options.path + '/mediaop.isa')
        i = 0
        found = False
        j = 0
        for line in f:
            if operation != 'sqrt':
                if re.search('class M' + operation + 'f', line):
                    found = True
            elif operation == 'sqrt':
                if re.search('class M' + operation, line):
                    found = True
            if found:
                if re.search('uint64_t arg\d?Bits', line):
                    reg = re.search('\(?\(?FpSrcReg\d?_uqw/?(\d+)?\)?(\*)?(\d+)?', line).group()
                    if '((' not in reg:
                        line = line.replace(reg, '(' + reg + '/' + str(bits) + ')' + '*' + str(bits))
                        file_str[j + 1] = line
                    else:
                        reg_new = reg.replace(re.search('/\d+\)(\*)*\d+', reg).group(),
                                              '/' + str(bits) + ')*' + str(bits))
                        line = line.replace(reg, reg_new)
                        file_str[j + 1] = line
                    if i == 1 and operation != 'sqrt':
                        found = False
                    elif i == 0 and operation == 'sqrt':
                        found = False
                    elif operation != 'sqrt':
                        i = i + 1
            j = j + 1
            if j not in file_str.keys():
                file_str[j] = line
    with open(options.path + '/mediaop_new.isa', 'w') as new_f:
        for key in file_str.keys():
            content = content + file_str.get(key)
        new_f.write(content)


if __name__ == '__main__':
    main()
