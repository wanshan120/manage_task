from db_con import session_scope, pro
from sa_models import CompanyInfo, Users

"""DBの初期値を設定する."""


with session_scope(pro) as session:
    session.add_all([
        Users(login_id='admin', password='admin'),
        Users(login_id='user', password='user'),
        Users(login_id='test', password='test'),
        ])


with session_scope(pro) as session:
    session.add_all([
        CompanyInfo(company_name='株式会社Vライズ',
                    abbreviation='VRI',
                    created_id='admin'),
        CompanyInfo(company_name='株式会社セキュアインフラストラクチャー',
                    abbreviation='SEC',
                    created_id='admin'),
        CompanyInfo(company_name='株式会社セキュアイノベーション',
                    abbreviation='SCI',
                    created_id='admin'),
        ])
