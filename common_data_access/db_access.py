from flask_sqlalchemy import BaseQuery
from sqlalchemy import Column
from werkzeug.exceptions import abort


class Query(BaseQuery):

    def get_all(self):
        return self.all()

    def get_column_like(self, value: str, col: Column):
        return self.filter(col.like(f'%{value}%')).all()

    def get_one_where(self, *criteria):
        return self.filter(*criteria).first()

    def get_one_where_or_404(self, *criteria, description=None):
        r = self.get_one_where(*criteria)
        if r is None:
            abort(404, description=description)
        return r

    def get_where(self, *criteria):
        return self.filter(*criteria).all()
