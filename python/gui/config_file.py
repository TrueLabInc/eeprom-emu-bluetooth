

class ConfigFileParser():
    def __init__(self, config_path, communicate, config_header):
        self.config_path = config_path
        self.communicate = communicate
        self.header = config_header
        self.communicate("Config file: {}".format(self.config_path))

    def read_config_file(self):
        conf_file = self.check_for_config_file()
        config_entries = {}
        config = conf_file.readlines()
        conf_file.close()
        for line in config:
            if '-' in line:
                entry = self.remove_bad_characters(line).split('-')
                config_entries[entry[0]] = entry[1]
        return config_entries

    def check_for_config_file(self):
        try:
            conf_file = open(self.config_path, 'r')
        except:
            #self.print_to_main_output("Creating config file")
            self.communicate("Creating config file {}".format(self.config_path))
            conf_file = open(self.config_path, 'w')
            conf_file.writelines(self.header+'\n')
            conf_file.close()
            conf_file = open(self.config_path, 'r')
        return conf_file

    def remove_bad_characters(self, line):
        bad_chars = [' ', '\n', '\r']
        for c in bad_chars:
            while c in line:
                line = line.replace(c, '')
        return line

    def save_config_file(self, config_entries):
        conf_file = open(self.config_path, 'w')
        conf_file.writelines(self.header+'\n')
        for k in config_entries:
            line = "{}- {}\n".format(k, config_entries[k])
            conf_file.write(line)
        conf_file.close()

    def store_bt_config(self, entry, value):
        config_entries = self.read_config_file()
        config_entries[entry] = value
        self.save_config_file(config_entries)


