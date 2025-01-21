from dbmanager_class import pf_len, account_import_configuration, master_config_import_configuration, a_config_import_configuration, b_config_import_configuration
from hist_metrics_class import ConfigSwapBuilder

output_dict = {}

class RefLiBuilder:


    #initialize class
    def __init__(self, account, master_config, callback_b, callback_a):
        self.account = account
        self.master_config = master_config
        self.callback_b = callback_b        
        self.callback_a = callback_a
    
    def ref_li(self):
        match self.master_config:
            case "pct_basic":
                #NEEDS TO BE UPDATED TO CALL ON PROFORMA METHOD b
                result = output_dict[self.callback_b]              
                return result
            case "pct_stab":
                #NEEDS TO BE UPDATED TO CALL ON PROFORMA METHOD a
                result =  output_dict[self.callback_a]
                return result
            case _: 
                return 1 * pf_len

def main():
    for i in range(179):
        instance = RefLiBuilder(account_import[i], master_config_import[i], a_config_import[i])

#check if script is being run directly
if __name__ == "__main__":
    main()
