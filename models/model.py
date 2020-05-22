class Model:
    id: str = ''
    table_name: str = ''

    def save(self, db_int):
        if not self.table_name:
            raise Exception('No database table specified')
        
        if self.id:
            db_int.update(self.table_name, self)
        else:
            db_int.insert(self.table_name, self)