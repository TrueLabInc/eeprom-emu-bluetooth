    def sequential_diff(self):
        buff_siz = 256
        diff = []
        seq_diff = []
        #generate diff data [[baddress_0, byte_0], .. , [baddress_n, byte_n]]
        for i in range(0,1029):
            diff.append([i,random.randint(0,255)])
        diff_siz = len(diff)
        for i in range(0,diff_siz, buff_siz):
            if i+buff_siz <= diff_siz:
                seq_diff.append(diff[i:i+buff_siz])
            else:
                seq_diff.append(diff[i:])
        return seq_diff
