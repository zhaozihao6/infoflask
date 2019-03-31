

#调用init包下的init文件下的app实例对象
from info import create_app

#使用app并根据生产环境的不同，设置不同的形参
app = create_app('development')

if __name__ == '__main__':
    print(app.url_map)
    app.run()
