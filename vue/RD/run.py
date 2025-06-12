from db import User, Article, Manager
from __init__ import create_app, db
from datetime import datetime

app = create_app()

# 创建数据库
with app.app_context():
    db.create_all()  # 创建所有模型对应的表

    # 初始化管理员账户
    if not Manager.query.filter_by(mng_name="aa").first():
        manager0 = Manager(
            mng_name="aa",
            mng_gender="0",
            mng_nickname="zzz",
            mng_avatar="dgfvcdh",
            mng_phone="18352551",
            mng_email="2690598534@qq.com"
        )
        manager0.set_password("1234")  # 设置密码
        db.session.add(manager0)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)  # 在生产环境中应设置为 False

