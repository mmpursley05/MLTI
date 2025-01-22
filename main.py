from flask import Flask, request, render_template, jsonify
import pandas as pd
import sqlite3
from werkzeug.utils import secure_filename
import os

from main_class import ProFormaProjection

from grwth_sched_class import GrowthScheduleBuilder
from hist_metrics_class import ConfigSwapBuilder
from ru_rd_class import RampUpDownBuilder
from ref_li_class import RefLiBuilder, output_dict
from dbmanager_class import inc_grwth_rate, exp_grwth_rate, pf_len, account_import_chart, account_import_pf_chart, account_type_import_chart, account_import_configuration, master_config_import_configuration, a_config_import_configuration, b_config_import_configuration, c_config_import_configuration, d_config_import_configuration, t12_dict_import_historicals

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATABASE'] = 'mlti_database.db'

# Constants
inc_grwth_rate = .03
exp_grwth_rate = .03
pf_len = 60
organization_name = 'mlti'

def get_db():
    db = sqlite3.connect(app.config['DATABASE'])
    return db

def init_db():
    """Ensure upload directory and database exist"""
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize database if needed
    db = get_db()
    cursor = db.cursor()

    # Create tables if they don't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historicals (
            account TEXT,
            organization TEXT,
            deal TEXT,
            t12 REAL,
            t11 REAL,
            t10 REAL,
            t9 REAL,
            t8 REAL,
            t7 REAL,
            t6 REAL,
            t5 REAL,
            t4 REAL,
            t3 REAL,
            t2 REAL,
            t1 REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuration (
            account TEXT,
            organization TEXT,
            deal TEXT,
            master_config TEXT,
            a_config TEXT,
            b_config TEXT,
            c_config TEXT,
            d_config TEXT
        )
    """)

    db.commit()
    db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    deal_name = request.form.get('deal_name')

    if not deal_name:
        return jsonify({'error': 'Deal name is required'}), 400

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.endswith('.csv'):
        try:
            # Read CSV into DataFrame
            df = pd.read_csv(file)

            # Add organization and deal columns
            df['organization'] = 'mlti'  # hardcoded for now
            df['deal'] = deal_name

            # Initialize database connection
            db = get_db()
            cursor = db.cursor()

            # Save to historicals table
            df.to_sql('historicals', db, if_exists='append', index=False)

            # Get accounts from chart_of_accounts
            cursor.execute("SELECT account FROM chart_of_accounts")
            accounts = cursor.fetchall()

            # Initialize configurations for each account
            for account in accounts:
                cursor.execute("""
                    INSERT INTO configuration
                    (account, organization, deal, master_config, a_config, b_config, c_config, d_config)
                    VALUES (?, ?, ?, 'value_basic', 't12_avg', '0', '0', '0')
                """, (account[0], 'mlti', deal_name))

            db.commit()
            db.close()

            return jsonify({
                'message': f'Deal "{deal_name}" uploaded successfully',
                'deal_name': deal_name
            })

        except Exception as e:
            print(f"Error during upload: {str(e)}")  # For debugging
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/process', methods=['POST'])
def process_data():
    try:
        data = request.json
        deal_name = data.get('deal')

        if not deal_name:
            return jsonify({'error': 'Deal name is required'}), 400

        db = get_db()
        cursor = db.cursor()

        # Get all required data
        account_data = cursor.execute("""
            SELECT
                c.account,
                c.master_config,
                c.a_config,
                c.b_config,
                c.c_config,
                c.d_config,
                coa.account_type
            FROM configuration c
            JOIN chart_of_accounts coa ON c.account = coa.account
            WHERE c.organization = ? AND c.deal = ?
        """, (organization_name, deal_name)).fetchall()

        # Get historical data
        historicals = cursor.execute("""
            SELECT account, t12, t11, t10, t9, t8, t7, t6, t5, t4, t3, t2, t1
            FROM historicals
            WHERE organization = ? AND deal = ?
        """, (organization_name, deal_name)).fetchall()

        # Convert historicals to dictionary format
        t12_dict_import_historicals = {
            row[0]: row[1:] for row in historicals
        }

        # Process each account
        output_dict.clear()  # Clear any previous results

        for row in account_data:
            account = row[0]
            master_config = row[1]
            a_config = row[2]
            b_config = row[3]
            c_config = row[4]
            d_config = row[5]
            account_type = row[6]

            # Create instances and calculate
            grwth_sched = GrowthScheduleBuilder(account, account_type)
            config_swap = ConfigSwapBuilder(account, a_config, b_config, c_config, d_config)
            ref_li = RefLiBuilder(account, master_config, b_config, a_config)
            ru_rd = RampUpDownBuilder(account, master_config, c_config, d_config)

            # Get results
            grwth_rate_results = grwth_sched.grwth_rate()
            config_results = config_swap.config_swap_output()
            ref_li_results = ref_li.ref_li()
            ru_results = ru_rd.ru_sched()
            rd_results = ru_rd.rd_sched()

            # Calculate final projection
            pro_forma = ProFormaProjection(
                account,
                master_config,
                *config_results,
                grwth_rate_results,
                ref_li_results,
                rd_results,
                ru_results
            )
            output_dict[account] = pro_forma.pro_forma()

        db.close()
        return jsonify({'results': output_dict})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update-config', methods=['POST'])
def update_configuration():
    try:
        data = request.json
        deal_name = data.get('deal')
        account = data.get('account')
        configs = data.get('configs')  # Should contain master_config, a_config, etc.

        if not all([deal_name, account, configs]):
            return jsonify({'error': 'Missing required data'}), 400

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            UPDATE configuration
            SET master_config = ?,
                a_config = ?,
                b_config = ?,
                c_config = ?,
                d_config = ?
            WHERE organization = ?
            AND deal = ?
            AND account = ?
        """, (
            configs['master_config'],
            configs['a_config'],
            configs['b_config'],
            configs['c_config'],
            configs['d_config'],
            organization_name,
            deal_name,
            account
        ))

        db.commit()
        db.close()

        return jsonify({'message': 'Configuration updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deals', methods=['GET'])
def get_deals():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT DISTINCT deal
            FROM configuration
            WHERE organization = 'mlti'
            ORDER BY deal
        """)
        deals = [row[0] for row in cursor.fetchall()]
        db.close()
        return jsonify(deals)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/populator', methods=['POST'])
def run_populator():
    print("\n=== Starting Populator Workflow ===")

    data = request.json
    deal_name = data.get('deal_name')
    organization_name = 'mlti'  # Hardcoded as per your original code

    if not deal_name:
        print("Error: No deal name provided")
        return jsonify({'error': 'Deal name is required'}), 400

    print(f"Processing deal: {deal_name}")

    try:
        db = get_db()
        cursor = db.cursor()

        print("Fetching data from database...")

        # Get account data
        print("Getting accounts from chart_of_accounts")
        account_results = cursor.execute("SELECT account FROM chart_of_accounts").fetchall()
        account_import_chart = [result[0] for result in account_results]
        print(f"Found {len(account_import_chart)} accounts")

        # Get account types
        print("Getting account types")
        type_results = cursor.execute("SELECT account_type FROM chart_of_accounts").fetchall()
        account_type_import_chart = [result[0] for result in type_results]

        # Get configuration data
        print("Getting configuration data")
        cursor.execute(f"SELECT account FROM configuration WHERE organization = ? AND deal = ?",
                       (organization_name, deal_name))
        account_import_configuration = [result[0] for result in cursor.fetchall()]

        cursor.execute(f"SELECT master_config FROM configuration WHERE organization = ? AND deal = ?",
                       (organization_name, deal_name))
        master_config_import_configuration = [result[0] for result in cursor.fetchall()]

        cursor.execute(f"SELECT a_config FROM configuration WHERE organization = ? AND deal = ?",
                       (organization_name, deal_name))
        a_config_import_configuration = [result[0] for result in cursor.fetchall()]

        cursor.execute(f"SELECT b_config FROM configuration WHERE organization = ? AND deal = ?",
                       (organization_name, deal_name))
        b_config_import_configuration = [result[0] for result in cursor.fetchall()]

        cursor.execute(f"SELECT c_config FROM configuration WHERE organization = ? AND deal = ?",
                       (organization_name, deal_name))
        c_config_import_configuration = [result[0] for result in cursor.fetchall()]

        cursor.execute(f"SELECT d_config FROM configuration WHERE organization = ? AND deal = ?",
                       (organization_name, deal_name))
        d_config_import_configuration = [result[0] for result in cursor.fetchall()]

        # Get historical data
        print("Getting historical data")
        cursor.execute("""
            SELECT account, t12, t11, t10, t9, t8, t7, t6, t5, t4, t3, t2, t1
            FROM historicals
            WHERE organization = ? AND deal = ?""",
                       (organization_name, deal_name))
        historical_results = cursor.fetchall()
        t12_dict_import_historicals = {row[0]: row[1:] for row in historical_results}
        print(f"Found historical data for {len(t12_dict_import_historicals)} accounts")

        print("\nStarting calculations...")
        for i in range(len(account_import_chart)):
            print(f"\nProcessing account {i+1}/{len(account_import_chart)}: {account_import_chart[i]}")

            grwth_sched_instance = GrowthScheduleBuilder(account_import_chart[i], account_type_import_chart[i])
            config_swapper_instance = ConfigSwapBuilder(
                account_import_configuration[i],
                a_config_import_configuration[i],
                b_config_import_configuration[i],
                c_config_import_configuration[i],
                d_config_import_configuration[i]
            )
            ref_li_instance = RefLiBuilder(
                account_import_configuration[i],
                master_config_import_configuration[i],
                b_config_import_configuration[i],
                a_config_import_configuration[i]
            )
            ru_rd_instance = RampUpDownBuilder(
                account_import_configuration[i],
                master_config_import_configuration[i],
                c_config_import_configuration[i],
                d_config_import_configuration[i]
            )

            print(f"Calculating growth schedule for {account_import_chart[i]}")
            grwth_sched_results = grwth_sched_instance.grwth_rate()

            print(f"Swapping configs for {account_import_chart[i]}")
            config_swapper_results = config_swapper_instance.config_swap_output()

            print(f"Building reference line for {account_import_chart[i]}")
            ref_li_results = ref_li_instance.ref_li()

            print(f"Calculating ramp up/down for {account_import_chart[i]}")
            ru_results = ru_rd_instance.ru_sched()
            rd_results = ru_rd_instance.rd_sched()

            print(f"Creating pro forma projection for {account_import_chart[i]}")
            pro_forma_instance = ProFormaProjection(
                account_import_configuration[i],
                master_config_import_configuration[i],
                config_swapper_results[0],
                config_swapper_results[1],
                config_swapper_results[2],
                config_swapper_results[3],
                grwth_sched_results,
                ref_li_results,
                rd_results,
                ru_results
            )

            final_results = pro_forma_instance.pro_forma()
            print(final_results)
            print("!!!!!!!!!!!!!!!!")
            print(f"Completed calculations for {account_import_chart[i]}")

        print("\n=== Populator Workflow Completed Successfully ===")
        return jsonify({
            'message': f'Completed processing for deal: {deal_name}'
        })

    except Exception as e:
        print(f"\nERROR in populator workflow: {str(e)}")
        return jsonify({'error': str(e)}), 500

    finally:
        db.close()
        print("Database connection closed")

@app.route('/api/get-csv/<deal_name>')
def get_csv(deal_name):
    print(f"Fetching CSV data for deal: {deal_name}")
    try:
        db = get_db()
        cursor = db.cursor()

        # Get all relevant data for the deal
        cursor.execute("""
            SELECT * FROM historicals
            WHERE deal = ? AND organization = 'mlti'
            """, (deal_name,))

        # Get column names
        columns = [description[0] for description in cursor.description]

        # Get rows
        rows = cursor.fetchall()

        # Convert to list of dicts
        result = []
        for row in rows:
            row_dict = {}
            for i, column in enumerate(columns):
                row_dict[column] = row[i]
                result.append(row_dict)

        print(f"Found {len(result)} rows of data")

        return jsonify(result)

    except Exception as e:
        print(f"Error fetching CSV data: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
        print("Database connection closed")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5555)
