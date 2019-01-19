from django.shortcuts import render, redirect
from .sa_models import users_select, insert_employee, drop_down, get_value,\
                       state_value, update_value, get_list, column_delete
from .db_con import pro, test

import inspect

"""ビューを定義する.

制約:
    Django Auth: Do not use
    Django Class base view: Do not use

"""

url = pro


def login(request):
    """ログイン処理をする.

    session['menber_id']: セッション。ログインしているIDを入れる

    """
    if request.method == "POST":
        form = (request.POST.get('login_id'),  request.POST.get('login_pw'))
        form_id = (request.POST.get('login_id'))
        if form == users_select(url, form_id):
            request.session['menber_id'] = request.POST.get('login_id')
            return redirect('list')
            print("認証可")
        else:
            error_msg = {"login_error": "IDまたはPWが違います"}
            print("認証不可")
            print("ネームは", __name__)
            return render(request, 'app/login.html', error_msg)
    else:
        print("POST出来てない")
        return render(request, 'app/login.html')


def detail(request):
    """社員情報を入力する.

    セッション有効時のみ表示

    """
    if 'menber_id' in request.session:
        if request.method == "POST":
            if request.POST.get('create'):
                form = request.POST.lists()
                session_id = request.session['menber_id']
                insert_employee(url, form, session_id)
                return redirect('list')
            elif request.POST.get('back'):
                return redirect('list')
        else:
            return render(request, 'app/create.html',
                          {"form_dict": drop_down(url)})
    else:
        return redirect('login')


def update(request, id):
    """社員情報を更新する.

    セッション有効時のみ有効

    """
    if 'menber_id' in request.session:
        id = request.path.replace("/detail%empId=", "")
        print("ID--------------------", get_value(url, id))
        value = {"form_value": get_value(url, id),
                 "state_value": state_value(url, id),
                 "form_dict": drop_down(url)}
        if request.method == "POST":
            if request.POST.get('update'):
                form = request.POST.lists()
                session_id = request.session['menber_id']
                update_value(url, form, id, session_id)
                # return redirect("update", id=id)
                return redirect('list')
            elif request.POST.get('back'):
                return redirect('list')
        else:
            return render(request, 'app/update.html', value)
    else:
        return redirect('login')


def logout(request):
    """ログアウト処理を行う.

    ログアウトしたときにセッションを消す

    """
    try:
        del request.session['member_id']
    except KeyError:
        pass
    return redirect('login')


def list(request):
    """社員情報一覧画面を表示する.

    セッション有効時のみ有効

    """
    if 'menber_id' in request.session:
        list = {"list": get_list(url)}
        return render(request, 'app/list.html', list)
    else:
        return redirect('login')


def delete(request, id):
    """社員情報を削除する.

    セッション有効時のみ有効

    """
    if 'menber_id' in request.session:
        column_delete(url, id)
        list = {"list": get_list(url)}
        return render(request, 'app/list.html', list)
    else:
        return redirect('login')
