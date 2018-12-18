# yablog  
基于Flask和React开发的个人博客，Flask提供后端api接口，react发送异步请求获取数据.  
后端只提供一个index路由，剩下的路由工作交给React-Router完成.  
这个库里的前端文件是打包过的，未打包过的源码可以看另一个库 [Yablog-React](https://github.com/YouHaonan/yablog-react)  
项目demo可以查看这里[Yablog](http://47.102.41.155/)  

### 使用方法
从仓库复制代码到本地  
安装pipenv，执行pipenv install安装虚拟环境和依赖  
执行pipenv shell命令激活虚拟环境  
执行flask db upgrade 创建，更新数据库  
执行flask shell 命令进入命令行模式，依次执行 from app import whooshee，whooshee.reindex()命令生成全文搜索索引  
在命令行模式下，创建Admin账户， admin=Admin(), admin.username ='你想创建的用户名'， admin.set_password('密码')  
执行db.session.add(admin)和db.session.commit()提交后退出命令行  
你可以通过运行flask forge 命令来生成虚拟数据  
执行flask run命令启动服务器。  
