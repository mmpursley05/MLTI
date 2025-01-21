from dbmanager_class import pf_len, account_import_configuration, master_config_import_configuration, c_config_import_configuration, d_config_import_configuration


class RampUpDownBuilder:

    #initialize class
    def __init__(self, account, master_config, c_config, d_config):
        self.account = account
        self.master_config = master_config
        self.c_config = c_config
        self.d_config = d_config
    
    def ru_sched(self):
        match self.master_config:
            case "value_stab":
                result = []
                for i in range(pf_len):
                     result.append(min((1 / float(self.c_config)) * i, 1))              
                return result
 
            case "pct_stab":
                result = []
                for i in range(pf_len):
                     result.append(min((1 / float(self.d_config)) * i, 1))              
                return result
            
            case _:
                return [0] * pf_len
 
    def rd_sched(self):
        match self.master_config:
            case "value_stab":
                result = []
                for i in range(pf_len):
                     result.append(max(1 - ((1 / float(self.c_config)) * i), 0))            
                return result

            case "pct_stab":
                result = []
                for i in range(pf_len):
                     result.append(max(1 - ((1 / float(self.d_config)) * i), 0))            
                return result

            case _: 
                return [0] * pf_len


def main():
    for i in range(179):
        instance = RampUpDownBuilder(account_import[i], master_config_import[i], c_config_import[i], d_config_import[i])
        

#check if script is being run directly
if __name__ == "__main__":
    main()
