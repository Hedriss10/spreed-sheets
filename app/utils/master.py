import pandas as pd
import os

class BankeMaster:
    
    def __init__(self, file_path) -> None:
        self.file_path = file_path

    def extract_dataframe_banker_master(self):
        df_temp = pd.read_excel(self.file_path, dtype='object')
        df_temp.rename(columns={'Unnamed: 1': 'COD_TABLE', 'Unnamed: 2': 'EMPREGADOR', 'Unnamed: 4': 'UF', 'Unnamed: 5': 'Tipo', 
                                'Unnamed: 6': 'Flat 1 a 6', 'Unnamed: 11': 'Flat 1 a 12', 'Unnamed: 16': 'Flat 13 a 24', 'Unnamed: 21': 'Flat 25 a 36', 'Unnamed: 26': 'Flat 37 a 48', 'Unnamed: 31': 'Flat 49 a 60', 
                                'Unnamed: 36': 'Flat 61 a 72', 'Unnamed: 41': 'Flat 73 a 84', 'Unnamed: 46': 'Flat 85 a 96', 'Unnamed: 51': 'Flat 97 a 108', 'Unnamed: 56': 'Flat 109 a 120',},inplace=True)

        df_temp = df_temp.fillna(0)
        new_df = df_temp[['COD_TABLE', 'EMPREGADOR', 'UF', 'Tipo', 'Flat 1 a 6', 'Flat 1 a 12', 'Flat 13 a 24', 'Flat 25 a 36', 'Flat 37 a 48', 'Flat 49 a 60', 'Flat 61 a 72', 'Flat 73 a 84', 'Flat 85 a 96', 'Flat 97 a 108', 'Flat 109 a 120']]
        new_df = new_df.iloc[8:]        
        new_df = new_df.infer_objects(copy=False)
        return new_df

    
    def transform_dataframe_banker_master(self):
        df = self.extract_dataframe_banker_master()
        new_rows = []
        flat_ranges = {
            'Flat 1 a 6': (1, 6),
            'Flat 1 a 12': (1, 12),
            'Flat 13 a 24': (13, 24),
            'Flat 25 a 36': (25, 36),
            'Flat 37 a 48': (37, 48),
            'Flat 49 a 60': (49, 60),
            'Flat 61 a 72': (61, 72),
            'Flat 73 a 84': (73, 84),
            'Flat 85 a 96': (85, 96),
            'Flat 97 a 108': (97, 108),
            'Flat 109 a 120': (109, 120),
        }
        
        for index, row in df.iterrows():
            for flat_col, (prazo_inicio, prazo_fim) in flat_ranges.items():
                if flat_col in df.columns and row[flat_col] != 0:
                    valor_flat = round(float(row[flat_col]), 4) * 100
                    new_row = {
                        'Tipo': row['Tipo'],
                        'Tabela': row['EMPREGADOR'],
                        'Cod Tabela': str(row['COD_TABLE']).zfill(5),
                        'UF': row['UF'],
                        'Prazo Inicio': prazo_inicio,
                        'Prazo Fim': prazo_fim,
                        'Flat': f"{valor_flat:.2f}"
                    }
                    new_rows.append(new_row)

        new_df = pd.DataFrame(new_rows)
        
        output_dir = 'output_files'
        os.makedirs(output_dir, exist_ok=True)
        
        select_uf = new_df['UF'].unique()
        for uf in select_uf:
            new_df_uf = new_df[new_df['UF'] == uf]
            df_uf = new_df_uf[['Tipo', 'Tabela', 'Cod Tabela', 'Prazo Inicio', 'Prazo Fim', 'Flat']]
            output_file = os.path.join(output_dir, f'{uf}.xlsx')
            df_uf.to_excel(output_file, index=False)
            print(f'Salvo: {output_file}') 
        