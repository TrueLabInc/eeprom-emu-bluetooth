from collections import OrderedDict

def options_parser(args):
    options = OrderedDict()
    l = len(args)
    for i, a in enumerate(args):
        option = None
        if '-' in a:
            option = a
            options[option] = None
        if option and i + 1 <= (l - 1):
            n = args[i + 1]
            if not '-' in n:
                options[option] = n
    return options

def disp_options(s_options, output):
    output(" available options:")
    for s in s_options.keys():
        output(" "+s)

def _print(s):
    print s

def options_executor(args, s_options, output=False):
    """

    :param args:
    :param s_options:
    :param output: output(string) will print string to privided output
    :return:
    """
    if not output:
        output = _print
    #args = sys.argv[1:]
    invalid_option = False
    options = options_parser(args)
    execution_list = []
    for o in options:
        if o in s_options:
            execution_list.append(o)
        else:
            output(" '{}' option not supported".format(o))
            invalid_option = True
    try:
        execution_list.pop(execution_list.index('-v'))
        execution_list.insert(0, '-v')
    except:
        pass
    for e in execution_list:
        if not options[e]:
            s_options[e]()
            #output('Executing: {}'.format(e))
        else:
            s_options[e](options[e])
            #output('Executing: {} {}'.format(e, options[e]))
    if not execution_list or invalid_option:
        #output(execution_list)
        #output(invalid_option)
        disp_options(s_options, output)
