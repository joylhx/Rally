# 脚本安装
##普通用户
###简便安装
Rally 提供了脚本用以进行自动化安装。其脚本的使用方式如下：
```
  wget -q -O- https://raw.githubusercontent.com/openstack/rally/master/install_rally.sh
  curl https://raw.githubusercontent.com/openstack/rally/master/install_rally.sh | bash
```
###精细安装
如果需要对安装过程进行更精细的操作，请将脚本保存到本地，查看脚本的帮助信息
```
wget https://raw.githubusercontent.com/openstack/rally/master/install_rally.sh
./install_rally.sh --help

Usage: bash [options]

This script will install Rally in your system.

Options:
  -h, --help             Print this help text
  -v, --verbose          Verbose mode
  -s, --system           Install system-wide.
  -d, --target DIRECTORY Install Rally virtual environment into DIRECTORY.
                         (Default: /home/wangxiao/rally if not root).
  --url                  Git repository public URL to download Rally from.
                         This is useful when you have only installation script and want to install Rally
                         from custom repository.
                         (Default: https://git.openstack.org/openstack/rally).
                         (Ignored when you are already in git repository).
  --branch               Git branch name, tag (Rally release), commit hash, ref, or other
                         tree-ish to install. (Default: master)
                         Ignored when you are already in git repository.
  -f, --overwrite        Deprecated. Use -r instead.
  -r, --recreate         Remove target directory if it already exist.
                         If neither '-r' nor '-R' is set default behaviour is to ask.
  -R, --no-recreate      Do not remove target directory if it already exist.
                         If neither '-r' nor '-R' is set default behaviour is to ask.
  -y, --yes              Do not ask for confirmation: assume a 'yes' reply
                         to every question.
  -D, --dbtype TYPE      Select the database type. TYPE can be one of
                         'sqlite', 'mysql', 'postgres'.
                         Default: sqlite
  --db-user USER         Database user to use. Only used when --dbtype
                         is either 'mysql' or 'postgres'.
  --db-password PASSWORD Password of the database user. Only used when
                         --dbtype is either 'mysql' or 'postgres'.
  --db-host HOST         Database host. Only used when --dbtype is
                         either 'mysql' or 'postgres'
  --db-name NAME         Name of the database. Only used when --dbtype is
                         either 'mysql' or 'postgres'
  -p, --python EXE       The python interpreter to use. Default: /home/wangxiao/rally/bin/python
  --develop              Install Rally with editable source code try.
                         (Default: false)
  --no-color             Disable output coloring.
```
###注意事项
> 1. 在安装之前，使用`sed -i s/python.org/tuna.tsinghua.edu.cn/g ./install_rally.sh`可将脚本内pip源替换为国内pip源，国内pip源有部分不纯在rally的pip包，请多尝试几个源，可以加快安装进度。
> 2. root用户通过自动化脚本安装后，其rally相关文件分别位于`/usr/local/lib/python2.7/dist-package/`和`/usr/share/rally`下。

