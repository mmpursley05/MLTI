from dbmanager_class import pf_len, account_import_chart, account_type_import_chart, inc_grwth_rate, exp_grwth_rate


class GrowthScheduleBuilder:

    #initialize class
    def __init__(self, account, account_type):
        self.account = account
        self.account_type = account_type
        
    def grwth_rate(self):
        match self.account_type:
            case "income":
                result = []
                for i in range(pf_len):
                     result.append((1 + inc_grwth_rate/12) ** (i + 1))              
                return result

            case "expense":
                result = []
                for i in range(pf_len):
                    result.append((1 + exp_grwth_rate/12) ** (i + 1))              
                return result

def main():
    for i in range(179):
        instance = GrowthScheduleBuilder(account_import_chart[i], account_type_import_chart[i])


if __name__ == "__main__":
    main()
