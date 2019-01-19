from .db_con import session_scope, Base, pro
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, DATETIME, Date, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
import pandas as pd


"""モデルとクエリーを定義する.

制約:
    mapping: SQLAlchemy
    query: SQLAlchemy
    migration: Do not migration
    table name: 仕様書通り
    column name: 仕様書通り

初期設定:
    MySQL:
        Commands:
            create database test_sa_test;
            ALTER DATABASE sa_test_db CHARSET utf8;
        SQLモードがNOZEROになっていたら以下を実行:
            set session sql_mode='NO_ENGINE_SUBSTITUTION';
            set global sql_mode='NO_ENGINE_SUBSTITUTION';
        SQLモードの確認方法:
            SELECT @@SESSION.sql_mode;
            SELECT @@GLOBAL.sql_mode;
"""


class CompanyInfo(Base):
    """company_infoのマッピングをする."""
    __tablename__ = 'company_info'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    company_id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(50))
    abbreviation = Column(String(3))
    is_deleted = Column(String(1), default="0")
    created = Column(DATETIME, default=datetime.now, nullable=False)
    modified = Column(DATETIME, default=datetime.now, nullable=False)
    created_id = Column(String(20))
    modified_id = Column(String(20))
    employee_info = relationship("EmployeeInfo")


class EmployeeInfo(Base):
    """employee_infoのマッピングをする."""
    __tablename__ = 'employee_info'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20))
    name_hiragana = Column(String(20))
    birthday = Column(Date, nullable=True)
    sex = Column(String(1))
    mail_address = Column(String(50))
    telephone_number = Column(String(13))
    company_info_id = Column(Integer, ForeignKey('company_info.company_id'))
    business_manager = Column(String(20))
    department = Column(String(1))
    commissioning_status = Column(String(1))
    is_deleted = Column(String(1), default="0")
    created = Column(DATETIME, default=datetime.now, nullable=False)
    modified = Column(DATETIME, default=datetime.now, nullable=False)
    created_id = Column(String(20))
    modified_id = Column(String(20))
    employeestate = relationship("EmployeeState")


class EmployeeState(Base):
    """employee_stateのマッピングをする."""
    __tablename__ = 'employee_state'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    employee_info_id = Column(Integer,
                              ForeignKey('employee_info.employee_id'),
                              primary_key=True,
                              autoincrement=True)
    enter_date = Column(Date, nullable=True)
    retire_date = Column(Date, nullable=True)
    status = Column(String(1))
    is_deleted = Column(String(1), default="0")
    created = Column(DATETIME, default=datetime.now, nullable=False)
    modified = Column(DATETIME, default=datetime.now, nullable=False)
    created_id = Column(String(20))
    modified_id = Column(String(20))


class Users(Base):
    """login_infoのマッピングをする."""
    __tablename__ = 'login_info'
    login_id = Column(String(20), primary_key=True)
    password = Column(String(20))
    is_deleted = Column(Integer, default="0")
    created = Column(DATETIME, default=datetime.now, nullable=False)
    modified = Column(DATETIME, default=datetime.now, nullable=False)
    created_id = Column(String(20))
    modified_id = Column(String(20))


def users_select(url, form_id):
    """フォームから入力されたIDとPWがDBのレコードと一致するか確認する.

    Args:
        form_id: フォームに入力されたID

    """
    with session_scope(url) as session:
        result = session.query(Users.login_id, Users.password).\
                    filter(Users.login_id == form_id).first()
        print("結果＝", result)
        return result


def insert_employee(url, form, session_id):
    """formの値をDBに格納する.

    Args:
        form: フォームに入力された値
        session_id: ログインしているID

    """
    with session_scope(url) as session:
        info = EmployeeInfo()
        state = EmployeeState()
        for key, value in form:
            if key in dir(EmployeeInfo):
                setattr(info, key, value)
            elif key in dir(EmployeeState):
                setattr(state, key, value)
        info.created_id = session_id
        state.created_id = session_id
        # raise ValueError("error")
        session.add_all([info, state])


def drop_down(url):
    """ドロップダウンリストを動的に出力する."""
    with session_scope(url) as session:
        item = session.query(CompanyInfo.company_id,
                             CompanyInfo.company_name).all()
        return item


def get_value(url, id):
    """employee_infoテーブルのpkidレコードを取得する.

    Args:
        id: パラメータID

    """
    with session_scope(url) as session:
        for row in session.query(EmployeeInfo).\
                filter(EmployeeInfo.employee_id == id).all():
            row.birthday = "{0:%Y/%m/%d}".format(row.birthday)
            print(row.birthday)
            values = {
                "employee_id": row.employee_id,
                "name": row.name,
                "name_hiragana": row.name_hiragana,
                "birthday": row.birthday,
                "sex": row.sex,
                "mail_address": row.mail_address,
                "telephone_number": row.telephone_number,
                "company_info_id": row.company_info_id,
                "business_manager": row.business_manager,
                "department": row.department,
                "commissioning_status": row.commissioning_status,
            }
            return values


def state_value(url, id):
    """employee_stateテーブルのpkidレコードを取得する.

        Args:
            id: パラメータID

    """
    with session_scope(url) as session:
        for row in session.query(EmployeeState).\
                filter(EmployeeState.employee_info_id == id).all():
            if row.enter_date == "0000-00-00":
                row.enter_date = ""
            elif row.enter_date != "0000-00-00":
                row.enter_date = "{0:%Y/%m/%d}".format(row.enter_date)
            if row.retire_date == "0000-00-00":
                row.retire_date = ""
            elif row.retire_date != "0000-00-00":
                row.retire_date = "{0:%Y/%m/%d}".format(row.retire_date)
            values = {
                "enter_date": row.enter_date,
                "retire_date": row.retire_date,
                "status": row.status,
            }
            return values


def update_value(url, form, id, session_id):
    """formに入力された値で更新する.

    Args:
        form: HTMLフォームから取得した値
        id: パラメータID
        session_id: ログインしているID名

    """
    with session_scope(url) as session:
        info = session.query(EmployeeInfo).filter_by(employee_id=id).first()
        state = session.query(EmployeeState).filter_by(employee_info_id=id).\
            first()
        for key, value in form:
            if key in dir(EmployeeInfo):
                setattr(info, key, value)
            elif key in dir(EmployeeState):
                setattr(state, key, value)
        info.modified_id = session_id
        state.modified_id = session_id
        session.add_all([info, state])


def get_list(url):
    """全ての社員情報を取得する.

    Format:
        today: YYYY/MM/DD
        birthday: 生年月日を年齢に変換
        enter_date: YYYY/MM/DD, 0000-00-00 to ""

    """
    with session_scope(url) as session:
        list = []
        count_up = 0
        for row in session.query(EmployeeInfo, EmployeeState).\
                join(EmployeeState, EmployeeInfo.employee_id == EmployeeState.employee_info_id).\
                all():
            result = session.query(CompanyInfo.company_name).\
                filter(CompanyInfo.company_id == row[0].company_info_id).one()
            count_up += 1
            today = int(pd.to_datetime('today').strftime('%Y%m%d'))
            birth = int(pd.to_datetime(row[0].birthday).strftime('%Y%m%d'))
            if row[1].enter_date == "0000-00-00":
                row[1].enter_date = ""
            else:
                row[1].enter_date = "{0:%Y/%m/%d}".format(row[1].enter_date)
            value = {
                "count_up": count_up,
                "employee_id": row[0].employee_id,
                "company_name": result[0],
                "department": row[0].department,
                "name": row[0].name,
                "name_hiragana": row[0].name_hiragana,
                "birthday": int((today - birth) / 10000),
                "business_manager": row[0].business_manager,
                "enter_date": row[1].enter_date,
                "commissioning_status": row[0].commissioning_status,
            }
            list.append(value)
    return list


def column_delete(url, id):
    """社員情報を削除する.

    Args:
        id: パラメータID

    """
    with session_scope(url) as session:
        session.query(EmployeeState).\
            filter(EmployeeState.employee_info_id == id).delete()
        session.query(EmployeeInfo).\
            filter(EmployeeInfo.employee_id == id).delete()


if __name__ == "__main__":
    """テーブルを作成する.

    Note:
        sa_models.pyの1行目の
        ``from .db_con import session_scope, Base, engine``を
        ``from db_con import session_scope, Base, engine``にしてから
        python app/sa_models.pyを実行

    """
    Base.metadata.create_all(sa.create_engine(pro))
