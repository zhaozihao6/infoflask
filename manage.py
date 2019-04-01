
#调用init包下的init文件下的app实例对象
from info import create_app,db,models

#导入脚本管理器
from flask_script import Manager
#导入迁移框架
from flask_migrate import Migrate,MigrateCommand


#使用app并根据生产环境的不同，设置不同的形参
app = create_app('development')
#实例化管理器对象，并与程序关联
manage = Manager(app)
#使用迁移框架
Migrate(app,db)
#使用迁移命令
manage.add_command('db', MigrateCommand)
if __name__ == '__main__':
    print(app.url_map)
    manage.run()