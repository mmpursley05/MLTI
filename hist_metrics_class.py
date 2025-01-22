from dbmanager_class import pf_len, account_import_configuration, a_config_import_configuration, b_config_import_configuration, c_config_import_configuration, d_config_import_configuration, t12_dict_import_historicals

class ConfigSwapBuilder:
    # Initialize class
    def __init__(self, account, a_config, b_config, c_config, d_config):
        self.account = account
        self.a_config = a_config
        self.b_config = b_config
        self.c_config = c_config
        self.d_config = d_config
        # Check if account exists in t12_dict_import_historicals before proceeding
        if self.account not in t12_dict_import_historicals:
            return

        self.swapped_a_config, self.swapped_b_config, self.swapped_c_config, self.swapped_d_config = self.config_swap_output()

    def config_swap_calc(self, variable):
        # Check if account exists in the dictionary
        if self.account not in t12_dict_import_historicals:
            try:
                return float(variable)  # Try to convert to float if not a special case
            except:
                return 0  # Return 0 if conversion fails

        # Fetch data from the dictionary
        dict_output = t12_dict_import_historicals[self.account]
        # Now perform the calculations based on the variable type
        match str(variable):  # Convert to string to ensure matching works
            case "t3_avg":
                swapped_variable = sum(dict_output[-3:]) / len(dict_output[-3:])
                return swapped_variable
            case "t6_avg":
                swapped_variable = sum(dict_output[-6:]) / len(dict_output[-6:])
                return swapped_variable
            case "t12_avg":
                swapped_variable = sum(dict_output) / len(dict_output)
                return swapped_variable
            case _:
                try:
                    return float(variable)
                except:
                    return 1  # Return 0 if conversion fails

    def config_swap_output(self):
        swapped_a_config = self.config_swap_calc(self.a_config)
        swapped_b_config = self.config_swap_calc(self.b_config)
        swapped_c_config = self.config_swap_calc(self.c_config)
        swapped_d_config = self.config_swap_calc(self.d_config)
        return swapped_a_config, swapped_b_config, swapped_c_config, swapped_d_config

def main():
    for i in range(len(account_import_configuration)):
        instance = ConfigSwapBuilder(
            account_import_configuration[i],
            a_config_import_configuration[i],
            b_config_import_configuration[i],
            c_config_import_configuration[i],
            d_config_import_configuration[i]
        )

if __name__ == "__main__":
    main()
