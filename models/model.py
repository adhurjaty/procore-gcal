class Model:
    id: str = ''
    table_name: str = ''

    def save(self, db_int):
        if not self.table_name:
            raise Exception('No database table specified')
        
        db_int.update(self.table_name, self)