class Sheet:
    def __init__(self, sheet, header_row_idx=1, data_row_start=None):
        self.sheet = sheet
        self.header_row_idx = header_row_idx
        self.data_row_start= self.header_row_idx+1 if data_row_start is None else data_row_start
        self.headers = [cell.value for cell in sheet[header_row_idx]]
        self.number_of_rows = 0

    def header_idx(self):
        return self.header_row_idx

    def get_headers(self):
        return self.headers

    def get_data_row_start(self):
        return self.data_row_start

    def get_sheet(self):
        return self.sheet

    def get_col_idx(self, column_name):
        return self.headers.index(column_name)+1

    def sheet_name(self):
        return self.sheet.title

    def cell(self, row, column, value):
        self.number_of_rows+=1
        return self.sheet.cell(row=row,column=column, value=value)

    def num_data_rows(self):
        return self.number_of_rows
