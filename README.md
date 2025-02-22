# 基于Django的图书管理系统

## 功能模块
### 1.用户管理
* 用户注册与登录
  * 支持用户注册、登录、注销等功能。

### 2.图书管理
* 图书信息管理
  * 支持查看图书详细信息（如书名、作者、ISBN、出版社、出版日期、分类等）。
* 图书检索
  * 支持按书名检索图书。
* 图书分类
  * 支持图书分类管理（如文学、科技、历史等）。

### 3.借阅管理
* 借书功能
  * 用户可以通过系统借阅图书。
* 还书功能
  * 用户可以通过系统归还图书。
* 借阅记录查询
  * 用户可以查看自己的借阅记录。

## 依赖
* Python 3.11
* Django 4.2

## 运行
创建数据库表

```shell
python manage.py migrate
```

启动服务器

```shell
python manage.py runserver
```

运行测试

```shell
python manage.py test
```
