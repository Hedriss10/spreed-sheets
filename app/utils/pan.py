from pandas import read_excel
from pandas import Series
import pandas as pd
from pandas import DataFrame, Series
import os

class BankPan:
    def __init__(self, file_path: str) -> None:
        """
        Initializes the class with the path of the Excel file and contains two functions, 
        one for loading and one for handling `templatestring` so that it can be input into the database.

        :param file_path: path of the .xlsx
        """
        self.xlsx = file_path

    def load_file(self) -> DataFrame:
        """
            Automatically loads the only spreadsheet in the Excel file and redoes the transfer. 
            Contains a print marked in hardcode precisely 
            to make a treatment within the core to make it easier to count the spreadsheets in the document.
        :return: DataFrame with data sheetnames.
        """
        try:
            sheets = pd.read_excel(self.xlsx, sheet_name=None, dtype="object", engine="openpyxl")
            # print(f"O arquivo contém {len(sheets)} planilha(s): {', '.join(sheets.keys())}")
            first_sheet_name = next(iter(sheets))
            return sheets[first_sheet_name]

        except Exception as e:
            print(f"Error loading Excel file: {e}")
            return None

    def processing_xlsx_banker_pan(self, sheet_data: DataFrame) -> DataFrame:
        """
            Process data from Banco Pan, this data is the commission tables, making a treatment, where we can collect the spreadsheet index
            greater than zero, cutting lines and resetting the index, and aggregating the tables, taking the necessary columns, separating the deadlines, treating null values
            renaming the columns, converting and rounding values, formatting as a string with two decimal places and returning the value with `templatestring`
            
        :param sheet_data: DataFrame with data sheetname.
        :return: DataFrame processing with templatestring.
        """
        if len(sheet_data) > 0:
            new_sheet = sheet_data.iloc[6:]  
            new_sheet = new_sheet.reset_index(drop=True)
            new_sheet['Tabela'] = new_sheet[['Unnamed: 4', 'Unnamed: 5']].agg(' '.join, axis=1)

            df_tmp = new_sheet[['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'Tabela', 'Unnamed: 3', 'Unnamed: 6', 'Unnamed: 9']]

            df_tmp[['Prazo Inicio', 'Prazo Fim']] = df_tmp['Unnamed: 6'].apply(
                lambda x: x.split('-') if '-' in str(x) else [x, x]
            ).apply(Series)

            df_tmp['Prazo Inicio'] = df_tmp['Prazo Inicio'].fillna('0').astype(str)
            df_tmp['Prazo Fim'] = df_tmp['Prazo Fim'].fillna('0').astype(str)
            df_tmp.rename(columns={
                'Unnamed: 0': 'Convenio',
                'Unnamed: 1': 'Empregado',
                'Unnamed: 2': 'Tipo',
                'Unnamed: 3': 'Cod Tabela',
                'Unnamed: 9': 'Flat',
            }, inplace=True)

            df_tmp.loc[:, 'Flat'] = (df_tmp['Flat'].astype(float) * 100).round(2)
            df_tmp.loc[:, 'Flat'] = df_tmp['Flat'].apply(lambda x: f"{x:.2f}")
            
            output_dir = 'output_files'
            os.makedirs(output_dir, exist_ok=True)

            select_convenio = df_tmp['Convenio'].unique()
            for select in select_convenio:
                df_filtered = df_tmp[df_tmp['Convenio'] == select].copy()
                dff2 = df_filtered[['Tipo', 'Tabela', 'Cod Tabela', 'Prazo Inicio', 'Prazo Fim', 'Flat']]
                
                output_file = os.path.join(output_dir, f"{df_filtered['Empregado'].iloc[0]}.xlsx")
                
                dff2.to_excel(output_file, index=False)
                print(f'Salvo: {output_file}')
        else:
            raise ValueError("Erro ao processar o arquivo: DataFrame vazio")
