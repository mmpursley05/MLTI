from prettytable import PrettyTable
from grwth_sched_class import GrowthScheduleBuilder
from hist_metrics_class import ConfigSwapBuilder
from ru_rd_class import RampUpDownBuilder
from ref_li_class import RefLiBuilder, output_dict
from dbmanager_class import inc_grwth_rate, exp_grwth_rate, pf_len, account_import_chart, account_import_pf_chart, account_type_import_chart, account_import_configuration, master_config_import_configuration, a_config_import_configuration, b_config_import_configuration, c_config_import_configuration, d_config_import_configuration, t12_dict_import_historicals
import pandas as pd
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8') # Set the locale to 'en_US'
import time

class ProFormaProjection:

    def __init__(self, account, master_config, a_config, b_config, c_config, d_config, grwth_rate, ref_li, rd_sched, ru_sched):
        self.account = account
        self.master_config = master_config
        self.a_config = a_config
        self.b_config = b_config
        self.c_config = c_config
        self.d_config = d_config
        self.grwth_rate = grwth_rate
        self.ref_li = ref_li
        self.rd_sched = rd_sched
        self.ru_sched = ru_sched

    def pro_forma(self):

            match self.master_config:
                case "value_basic":
                    result = []
                    for i in range(pf_len):
                        result.append(float(self.a_config) * self.grwth_rate[i])           
                    return result
                case "pct_basic":
                    result = []
                    for i in range(pf_len):
                        result.append(float(self.a_config) * self.ref_li[i])
                    return result
                case "value_stab":
                    result = []
                    for i in range(pf_len):
                        result.append((float(self.a_config) * self.rd_sched[i]) + (float(self.b_config) * self.ru_sched[i]))              
                    return result
                case "pct_stab":
                    result = []
                    for i in range(pf_len):
                        result.append(self.ref_li[i] * ((float(self.b_config) * self.rd_sched[i]) + (float(self.c_config) * self.ru_sched[i])))              
                    return result
                case "ru_basic":
                    result = []
                    for i in range(pf_len):
                        result.append(float(self.a_config) * min(float(self.b_config) * float(self.c_config), float(self.b_config) * i))              
                    return result
                case "ru_cmplx":
                    return "to be built"

def main():

    
    table = PrettyTable()

    table.field_names = ["Account"] + [f"Pf Mo {i+1}" for i in range(pf_len)]

     
    for i in range(len(account_import_pf_chart)):
        
        output_dict[account_import_pf_chart[i]] = [0] * pf_len


    for i in range(len(account_import_chart)):

        grwth_sched_instance = GrowthScheduleBuilder(account_import_chart[i], account_type_import_chart[i])
        config_swapper_instance = ConfigSwapBuilder(account_import_configuration[i], a_config_import_configuration[i], b_config_import_configuration[i], c_config_import_configuration[i], d_config_import_configuration[i])
        ref_li_instance = RefLiBuilder(account_import_configuration[i], master_config_import_configuration[i], b_config_import_configuration[i], a_config_import_configuration[i])
        ru_rd_instance = RampUpDownBuilder(account_import_configuration[i], master_config_import_configuration[i], c_config_import_configuration[i], d_config_import_configuration[i])

        grwth_sched_results = grwth_sched_instance.grwth_rate()        
        config_swapper_results = config_swapper_instance.config_swap_output()
        ref_li_results = ref_li_instance.ref_li()
        ru_results = ru_rd_instance.ru_sched()
        rd_results = ru_rd_instance.rd_sched()

        pro_forma_instance = ProFormaProjection(account_import_configuration[i], master_config_import_configuration[i], config_swapper_results[0], config_swapper_results[1], config_swapper_results[2], config_swapper_results[3], grwth_sched_results, ref_li_results, rd_results, ru_results)
        final_results = pro_forma_instance.pro_forma()

        output_dict[account_import_chart[i]] = final_results
    

        if i == 1:
            selected_values = list(output_dict.values())[:2]
            gross_potential_rent = [sum(values) for values in zip(*selected_values)]
            output_dict['gross_potential_rent'] = gross_potential_rent

        if i == 8:
            selected_values = list(output_dict.values())[3:10]
            total_economic_vacancies = [sum(values) for values in zip(*selected_values)]
            output_dict['total_economic_vacancies'] = total_economic_vacancies

        if i == 8:

            net_effective_rental_income = [sum(values) for values in zip(gross_potential_rent, total_economic_vacancies)]
            output_dict['net_effective_rental_income'] = net_effective_rental_income

        if i == 49:

            selected_values = list(output_dict.values())[12:53]
            other_income = [sum(values) for values in zip(*selected_values)]
            output_dict['other_income'] = other_income

        if i == 49:

            total_income = [sum(values) for values in zip(other_income, net_effective_rental_income)]
            output_dict['total_income'] = total_income

        if i == 76:

            selected_values = list(output_dict.values())[55:82]
            g_and_a_expense = [sum(values) for values in zip(*selected_values)]
            output_dict['g_and_a_expense'] = g_and_a_expense

        if i == 97:

            selected_values = list(output_dict.values())[83:104]
            payroll_expense = [sum(values) for values in zip(*selected_values)]
            output_dict['payroll_expense'] = payroll_expense

        if i == 114:

            selected_values = list(output_dict.values())[105:122]
            service_contracts_expense = [sum(values) for values in zip(*selected_values)]
            output_dict['service_contracts_expense'] = service_contracts_expense

        if i == 144:

            selected_values = list(output_dict.values())[123:153]
            r_and_m_expense = [sum(values) for values in zip(*selected_values)]
            output_dict['r_and_m_expense'] = r_and_m_expense

        if i == 155:

            selected_values = list(output_dict.values())[154:165]
            marketing_expense = [sum(values) for values in zip(*selected_values)]        
            output_dict['marketing_expense'] = marketing_expense

        if i == 162:

            selected_values = list(output_dict.values())[166:173]
            utilities_expense = [sum(values) for values in zip(*selected_values)]
            output_dict['utilities_expense'] = utilities_expense

        if i == 173:
                        
            selected_values = list(output_dict.values())[174:185]
            make_ready_expense = [sum(values) for values in zip(*selected_values)]
            output_dict['make_ready_expense'] = make_ready_expense

        if i == 175:

            selected_values = list(output_dict.values())[186:188]
            tax_expense = [sum(values) for values in zip(*selected_values)]
            output_dict['tax_expense'] = tax_expense

        if i == 177:

            selected_values = list(output_dict.values())[189:191]
            insurance_expense = [sum(values) for values in zip(*selected_values)]
            output_dict['insurance_expense'] = insurance_expense

        if i == 178:

            operating_expenses = [sum(values) for values in zip(final_results, g_and_a_expense, payroll_expense, service_contracts_expense, r_and_m_expense, marketing_expense, utilities_expense, make_ready_expense, tax_expense, insurance_expense)]
            output_dict['operating_expenses'] = operating_expenses

        if i == 178:

            net_operating_income = [a - b for a, b in zip(total_income, operating_expenses)]
            output_dict['net_operating_income'] = net_operating_income


    for i in range(len(account_import_pf_chart)):
        row_data = [account_import_pf_chart[i]] + [locale.currency(output_dict[account_import_pf_chart[i]][j], symbol=True, grouping=True) for j in range(pf_len)]
        table.add_row(row_data)

    with open('output.txt', 'w') as f:
        print(table, file=f)

    start_time = time.time()
    for i in range(1000000):
        pass
    end_time = time.time()
    runtime = end_time - start_time
    print("Runtime:", runtime, "seconds")

if __name__ == "__main__":
    main()
