from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from .models import Recipe, Recipe_ingredient, Recipe_step, User, Fridge, Ingredient, History
from django.db import connection
import json
import datetime
from django.utils.timezone import utc

def index(request):
    pass
    #return render(request, 'fridge/index.html')
    return render(request, 'fridge/log_in.html')

def signup(request):
    pass
    return render(request, 'fridge/sign_up.html')

def newuser(request):
    uname = request.POST['uname_new'] #表单已限定类型为非空,整数
    # pword = request.POST.get('password')  # 表单已限定类型为非空,整数
    user_exist = User.objects.filter(user_name=uname)
    if user_exist:#food是否exist
        pass
        #弹窗
    else:
        u = User.objects.create(user_name=uname)
        u.save()
    return HttpResponseRedirect(reverse('fridge:index')) #json

def content(request):  # simplified function as login
    try:                                            #初次登录接收参数
        uname = request.POST['username']
    except KeyError:     #无POST输入
        try:
            uname = request.session['user_name']
        except KeyError:
            return render(request, 'fridge/index.html')  # 直接输入url
    else:
        m = get_object_or_404(User, user_name=uname) #初次登录,POST输入空白或错误 #密码验证
        request.session['user_name'] = m.user_name  #save user name in session
    with connection.cursor() as cursor:
        cursor.execute("""Select f.ingredient_name, f.quantity, i.ingredient_unit
                    From  fridge_Fridge as f LEFT JOIN fridge_Ingredient as i 
                    ON f.ingredient_name = i.ingredient_name
                    WHERE f.user_name_id = %s
                    """, [uname])
        fridge_tuple = cursor.fetchall() #是empty set也没关系
    label = ['ingredient_name', 'quantity', 'ingredient_unit']
    fridge_list = [dict(zip(label, f)) for f in fridge_tuple]
    context = {'fridge_list': fridge_list, 'user_name': uname}  #fridge_list元组改为dict，便于前端维护
    return render(request, 'fridge/shelf.html', context)
    #return render(request, 'fridge/content.html', context)

def search(request):  # search action get from url
    uname = request.session['user_name']
    fridge_list = Fridge.objects.raw('SELECT * FROM fridge_fridge WHERE user_name_id = %s', [uname])
    with connection.cursor() as cursor:
        cursor.execute("""Select r.recipe_id_id, rec.recipe_name From
    (select i.ingredient_id as ingreid
    from fridge_Fridge f, fridge_Ingredient i
    where f.user_name_id = %s
    and f.ingredient_name like i.ingredient_name) as tempingre, fridge_Recipe_ingredient r, fridge_Recipe rec
    where r.ingredient_id_id = tempingre.ingreid
    and r.recipe_id_id = rec.recipe_id
    group by r.recipe_id_id, rec.recipe_name
    order by count(*) desc
    """, [uname])
        recipe_list = cursor.fetchall() #是empty set也没关系
    context = {'recipe_list': recipe_list, 'fridge_list': fridge_list}
    #return render(request, 'fridge/search.html', context)
    # return render(request, 'fridge/search_result.html', context)
    return render(request, 'fridge/reciperesult.html', context)


def detail(request, r_id):  # 超链接或直接输入：get from url
    recipe = get_object_or_404(Recipe, recipe_id=r_id)
    step_list = Recipe_step.objects.filter(recipe_id=r_id).order_by('step_number')
    ingredient_list = Recipe_ingredient.objects.filter(recipe_id=r_id).select_related('ingredient_id')
    context = {'recipe': recipe, 'ingredient_list': ingredient_list, 'step_list': step_list}
    #return render(request, 'fridge/detail.html', context)
    # return render(request, 'fridge/recipe_detail.html', context)
    return render(request, 'fridge/recipe_details.html', context)

def add_food(request): #超链接跳转页面，仅接收表单参数
    return render(request, 'fridge/update.html')

def new_food(request):  #提交后显示成功的弹窗
    amount = request.POST.get('amount') #表单已限定类型为非空,整数
    food_name = request.POST.get('food_name') # 表单已限定类型为非空,text,min=0
    uname = request.session['user_name']
    food_exist = Fridge.objects.raw("""SELECT * FROM fridge_Fridge
                                    WHERE user_name_id = %s AND ingredient_name = %s """,
                                    [uname, food_name])
    if food_exist:#food是否exist
        with connection.cursor() as cursor:
            cursor.execute("""
            UPDATE fridge_Fridge SET quantity = quantity + %s
            WHERE ingredient_name = %s
            AND user_name_id = %s
        """, [amount, food_name, uname])
    else:
        # with connection.cursor() as cursor:
        #     cursor.execute("""INSERT INTO fridge_Fridge VALUES (%s, %s, %s)
        # """, [uname, food_name, amount])
        u = User.objects.get(user_name=uname)
        f = Fridge.objects.create(user_name=u, ingredient_name=food_name, quantity=amount)#自动填充id
        f.save()
    return HttpResponseRedirect(reverse('fridge:add_food')) #json


def edit(request):
    amount = int(request.GET.get('amount')) ###强制转类型
    food_name = request.GET.get('food_name') #无法获取food name
    operation = request.GET.get('operation')
    uname = request.session['user_name']
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    if amount < 0 :
        res = {'Status': 'Please enter positive number!'}
    # else:
    #     res = {
    #     'Status': 'Success',
    #     'Code': 200,
    # }
    else:
        if operation == 'addmore':
            with connection.cursor() as cursor:
                cursor.execute("""
                UPDATE fridge_fridge SET quantity = quantity + %s  WHERE ingredient_name = %s
                AND user_name_id = %s
            """, [amount, food_name, uname])
            res = {'Food': food_name, 'Status': 'Added successfully!', 'Amount': amount}
            #         f.quantity = f.quantity + food_amount
            #         f.save()
        elif operation == 'eatsome':
            amount_original = Fridge.objects.raw("""SELECT * FROM fridge_fridge
                                                            WHERE ingredient_name = %s AND user_name_id = %s""",
                                                 [food_name, uname])[0].quantity
            if amount > amount_original:
                res = {'Status': 'Food amount overflow! Enter again.', 'Food': '', 'Amount': ''}
            elif amount < amount_original:
                u = User.objects.get(user_name=uname)
                h = History.objects.create(user_name=u, ingredient_name=food_name, ingredient_amount=amount, eat_date=now)
                h.save()
                with connection.cursor() as cursor:
                    cursor.execute("""
                    UPDATE fridge_fridge SET quantity = quantity - %s  WHERE ingredient_name = %s
                    AND user_name_id = %s
                """, [amount, food_name, uname])
                res = {'Food': food_name, 'Status': 'eaten', 'Amount': amount}
            else:
                u = User.objects.get(user_name=uname)
                h = History.objects.create(user_name=u, ingredient_name=food_name, ingredient_amount=amount,
                                           eat_date=now)
                h.save()
                with connection.cursor() as cursor:
                    cursor.execute("""
                    DELETE FROM fridge_Fridge WHERE ingredient_name = %s
                    AND user_name_id = %s """,  [food_name, uname])
                res = {'Status': 'You ate them all!', 'Food': '', 'Amount': amount}
        elif operation == 'thrown':
            amount_original = Fridge.objects.raw("""SELECT * FROM fridge_fridge
                                                            WHERE ingredient_name = %s AND user_name_id = %s""",
                                                 [food_name, uname])[0].quantity
            if amount > amount_original:
                res = {'Status': 'Food amount overflow! Enter again.',  'Food': '', 'Amount': ''}
            elif amount < amount_original:
                with connection.cursor() as cursor:
                    cursor.execute("""
                    UPDATE fridge_fridge SET quantity = quantity - %s  WHERE ingredient_name = %s
                    AND user_name_id = %s
                """, [amount, food_name, uname ])
                res = {'Food': food_name, 'Status': 'thrown away', 'Amount': amount}
            else:
                with connection.cursor() as cursor:
                    cursor.execute("""
                    DELETE FROM fridge_Fridge WHERE ingredient_name = %s
                    AND user_name_id = %s """,  [food_name, uname])
                res = {'Status': 'You threw them all!', 'Food': '', 'Amount': amount}
    return HttpResponse(json.dumps(res))
    #return HttpResponseRedirect(reverse('fridge:content'))

def logout(request):  # create a log out button
    try:
        del request.session['user_name']
    except KeyError:
        pass
    return render(request, 'fridge/index.html')

# def advanced_search_ingredient(request):
#     pass
#     return render(request, 'fridge:reciperesult.html', context)

def advanced_search_reorder(request):
    return render(request, 'fridge:reciperesult.html', context)

def myhistory(request): #include eating history
    pass
    return render(request, 'fridge/profile.html')

