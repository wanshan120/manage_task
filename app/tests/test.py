from django.test import TestCase
from ..sa_models import (Base, Users, EmployeeInfo, CompanyInfo,
                         EmployeeState, users_select, insert_employee,
                         drop_down, get_value, state_value,
                         update_value, get_list, column_delete)
from ..views import (login, update, logout)
from django.shortcuts import resolve_url
from django.test import Client
from ..db_con import test, session_scope, pro
import sqlalchemy as sa


"""テストをする.

setupとteardownはテスト関数の度に実行される

example_coding:
    test_function_name(self):
        result = function_name("test")
        self.assertTrue(result)

use_app:
    coverage: カバレッジを取得する
    django-nose: テストモジュール

commands:
    assertEqual: 引数を2つ渡し等価であればテスト合格
    assertTrue: 引数を１つ渡し、True であれば、テストが合格
    assertIsNone: 引数を１つ渡し、None であれば、テストが合格
    など..

if __name__ == "__main__":
    初期設定用のコードのためテストはしない。
    そのためsa_models.pyのカバレッジは99%で完了とする。

"""

url = test
engine = sa.create_engine(url)
session_id = 1
id = 1
form = [
    ("name", "test1"),
    ("name_hiragana", "テスト１"),
    ("birthday", "1994/01/20"),
    ("sex", "0"),
    ("mail_address", "akihisa120@yahoo.co.jp"),
    ("telephone_number", "09084535177"),
    ("company_info_id", 1),
    ("business_manager", "仲田"),
    ("department", "0"),
    ("commissioning_status", "0"),
    ("enter_date", ['1994/2/21']),
    ("retire_date", ['1994/2/21']),
    ("status", "0"),
]

state_form = {
    'enter_date': ['1994/2/20'],
    'retire_date': ['1994/2/21'],
    'status': ['0'],
    'is_deleted': '0',
    'created_id': 'test',
    'modified_id': None
}


class TestQuery(TestCase):
    def setUp(self):
        """初期設定."""
        with session_scope(url) as session:
            Base.metadata.create_all(engine)
            session.add_all([
                Users(login_id='test', password='test'),
                CompanyInfo(company_name='testcorp',
                            abbreviation='TSC',
                            created_id='test'),
                ])
            session.execute("set session sql_mode='NO_ENGINE_SUBSTITUTION'")
            session.execute("set global sql_mode='NO_ENGINE_SUBSTITUTION'")
            self.client = Client()

    def tearDown(self):
        """テスト終了時自動実行する."""
        Base.metadata.drop_all(engine)

    def test_users_select(self):
        """user_selectのテスト."""
        result = users_select(url, "test")
        self.assertEqual(result, ('test', 'test'))

    def test_insert_employee(self):
        """insert_employeeのテスト."""
        insert_employee(url, form, session_id)
        with session_scope(url) as session:
            item = session.query(EmployeeInfo, EmployeeState).\
                    join(EmployeeState, EmployeeInfo.employee_id == EmployeeState.employee_info_id).\
                    all()
            self.assertEqual(len(item), 1)

    def test_drop_down(self):
        """drop_downのテスト."""
        result = drop_down(url)
        self.assertEqual(tuple(result), ((1, 'testcorp'),))

    def test_get_value(self):
        """get_valueのテスト."""
        insert_employee(url, form, session_id)
        result = get_value(url, session_id)
        form.insert(0, ("employee_id", 1))
        del form[11:16]
        expect = dict(form)
        self.assertEqual(result, expect)

    def test_state_value(self):
        """state_valueのテスト."""
        with session_scope(url) as session:
            Base.metadata.create_all(engine)
            session.add_all([
                EmployeeInfo(employee_id=1),
                EmployeeState(employee_info_id=1,
                              enter_date='1994-02-20',
                              retire_date='1994-02-21',
                              status='0')
                ])
        result = state_value(url, session_id)
        self.assertEqual(len(result), 3)

    def test_state_value_enter_zero(self):
        """state_valueのテスト(入社日空白の場合)."""
        with session_scope(url) as session:
            Base.metadata.create_all(engine)
            session.add_all([
                EmployeeInfo(employee_id=1),
                EmployeeState(employee_info_id=1,
                              enter_date='0000-00-00',
                              retire_date='1994-02-21',
                              status='0')
                ])
        result = state_value(url, session_id)
        self.assertEqual(len(result), 3)

    def test_state_value_retire_zero(self):
        """state_valueのテスト(退社日空白の場合)."""
        with session_scope(url) as session:
            Base.metadata.create_all(engine)
            session.add_all([
                EmployeeInfo(employee_id=1),
                EmployeeState(employee_info_id=1,
                              enter_date='1994-02-20',
                              retire_date='0000-00-00',
                              status='0')
                ])
        result = state_value(url, session_id)
        self.assertEqual(len(result), 3)

    def test_state_value_zero_zero(self):
        """state_valueのテスト(入社日、退社日が空白の場合)."""
        with session_scope(url) as session:
            Base.metadata.create_all(engine)
            session.add_all([
                EmployeeInfo(employee_id=1),
                EmployeeState(employee_info_id=1,
                              enter_date='0000-00-00',
                              retire_date='0000-00-00',
                              status='0')
                ])
        result = state_value(url, session_id)
        self.assertEqual(len(result), 3)

    def test_update_value(self):
        """update_valueのテスト."""
        with session_scope(url) as session:
            Base.metadata.create_all(engine)
            session.add_all([
                EmployeeInfo(
                    employee_id=1,
                    name="test1",
                    name_hiragana="テスト１",
                    birthday="1994/01/20",
                    sex="0",
                    mail_address="akihisa120@yahoo.co.jp",
                    telephone_number="09084535177",
                    company_info_id=1,
                    business_manager="仲田",
                    department="0",
                    commissioning_status="0",),
                EmployeeState(
                    employee_info_id=1,
                    enter_date='1994-02-20',
                    retire_date='0000-00-00',
                    status='0',)
                ])

        update_value(url, form, id, session_id)
        with session_scope(url) as session:
            item = session.query(EmployeeInfo, EmployeeState).\
                    join(EmployeeState, EmployeeInfo.employee_id == EmployeeState.employee_info_id).\
                    all()
            self.assertEqual(len(item), 1)

    def test_get_list(self):
        """get_listのテスト(入社日、退社日が空白の場合)."""
        with session_scope(url) as session:
            Base.metadata.create_all(engine)
            session.add_all([
                EmployeeInfo(
                    employee_id=1,
                    name="test1",
                    name_hiragana="テスト１",
                    birthday="1994/01/20",
                    sex="0",
                    mail_address="akihisa120@yahoo.co.jp",
                    telephone_number="09084535177",
                    company_info_id=1,
                    business_manager="仲田",
                    department="0",
                    commissioning_status="0",),
                EmployeeState(
                    employee_info_id=1,
                    enter_date='0000-00-00',
                    retire_date='0000-00-00',
                    status='0',)
                ])
        result = get_list(url)
        self.assertEqual(len(result), 1)

    def test_get_list_no_zero(self):
        """get_listのテスト(入社日、退社日に有効な数字が入っている場合)."""
        with session_scope(url) as session:
            Base.metadata.create_all(engine)
            session.add_all([
                EmployeeInfo(
                    employee_id=1,
                    name="test1",
                    name_hiragana="テスト１",
                    birthday="1994/01/20",
                    sex="0",
                    mail_address="akihisa120@yahoo.co.jp",
                    telephone_number="09084535177",
                    company_info_id=1,
                    business_manager="仲田",
                    department="0",
                    commissioning_status="0",),
                EmployeeState(
                    employee_info_id=1,
                    enter_date='1994-01-01',
                    retire_date='1994-02-02',
                    status='0',)
                ])
        result = get_list(url)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["birthday"], 24)

    def test_column_delete(self):
        """insert_employeeのテスト."""
        with session_scope(url) as session:
            Base.metadata.create_all(engine)
            session.add_all([
                EmployeeInfo(
                    employee_id=1,
                    name="test1",
                    name_hiragana="テスト１",
                    birthday="1994/01/20",
                    sex="0",
                    mail_address="akihisa120@yahoo.co.jp",
                    telephone_number="09084535177",
                    company_info_id=1,
                    business_manager="仲田",
                    department="0",
                    commissioning_status="0",),
                EmployeeState(
                    employee_info_id=1,
                    enter_date='1994-01-01',
                    retire_date='1994-02-02',
                    status='0',)
                ])
        column_delete(url, id)
        result = get_list(url)
        self.assertEqual(len(result), 0)

    def test_view_login(self):
        """"ログインページ表示出来るか."""
        response = self.client.get(resolve_url('login'))
        self.assertEqual(response.status_code, 200)

    def test_view_login_auth(self):
        """"ログイン出来るか."""
        response = self.client.post(resolve_url('login'),
                                    {'login_id': 'admin', 'login_pw': 'admin'})
        self.assertEqual(response.resolver_match.func, login)

    def test_view_detail(self):
        """"社員情報ページ表示出来るか."""
        session = self.client.session
        session['menber_id'] = 'test'
        session.save()
        response = self.client.get(resolve_url('detail'))
        self.assertEqual(response.status_code, 200)

    def test_view_update(self):
        """社員情報をテスト用に作成する"""
        with session_scope(pro) as session:
            session.add_all([
                EmployeeInfo(
                    employee_id=999999999,
                    name="test1",
                    name_hiragana="テスト１",
                    birthday="1994/01/20",
                    sex="0",
                    mail_address="akihisa120@yahoo.co.jp",
                    telephone_number="09084535177",
                    company_info_id=1,
                    business_manager="仲田",
                    department="0",
                    commissioning_status="0",),
                EmployeeState(
                    employee_info_id=999999999,
                    enter_date='1994-02-20',
                    retire_date='0000-00-00',
                    status='0',)
                ])
        """"社員情報更新ページ表示出来るか."""
        session = self.client.session
        session['menber_id'] = 'test'
        session.save()
        response = self.client.get('/detail%empId=999999999')
        self.assertEqual(response.status_code, 200)
        post = {'update': '更新'}
        response = self.client.post('/detail%empId=999999999', post)
        self.assertEqual(response.resolver_match.func, update)
        """社員情報を消す."""
        with session_scope(pro) as session:
            session.query(EmployeeState).\
                filter(EmployeeState.employee_info_id == 999999999).delete()
            session.query(EmployeeInfo).\
                filter(EmployeeInfo.employee_id == 999999999).delete()

    def test_view_list(self):
        """"社員情報一覧ページ表示出来るか."""
        session = self.client.session
        session['menber_id'] = 'test'
        session.save()
        response = self.client.get(resolve_url('list'))
        self.assertEqual(response.status_code, 200)

    def test_view_logout(self):
        """"ログアウトページ表示出来るか."""
        session = self.client.session
        session['menber_id'] = 'test'
        session.save()
        response = self.client.get(resolve_url('logout'))
        self.assertEqual(response.resolver_match.func, logout)

    def test_view_delete(self):
        """削除ページ表示出来るか."""
        session = self.client.session
        session['menber_id'] = 'test'
        session.save()
        response = self.client.get('/delete%empId=999999999')
        self.assertEqual(response.status_code, 200)

    def test_view_delete_no_session(self):
        """削除ページ表示出来るか.

        セッション無しのケース： loginにリダイレクトする.

        """
        response = self.client.get('/delete%empId=0', follow=True)
        self.assertEqual(response.redirect_chain, [('/login', 302)])
