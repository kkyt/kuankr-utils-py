import os
import shutil

def abs_path(file_name):
    return os.path.abspath(os.path.dirname(file_name))

def walk(root, file_callback, dir_callback_pre=None, dir_callback_post=None, item_callback=None):
    """
    Recursively walks in root directory and executes callback function
    """
    for subitem in os.listdir(root):
        subpath = os.path.join(root, subitem)
        if item_callback:
            item_callback(subpath, root)
        if os.path.isdir(subpath):
            if dir_callback_pre:
                dir_callback_pre(subpath, root)
            walk(subpath, file_callback, dir_callback_pre, dir_callback_post)
            if dir_callback_post:
                dir_callback_post(subpath, root)
        else:
            if file_callback:
                file_callback(subpath, root)


def mkdir_p(dirname=None, filename=None):
    if dirname is not None:
        dirname = os.path.expanduser(dirname)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
    else:
        mkdir_p(dirname=os.path.dirname(filename))

def file_exists(filename, minsize=1):
    return os.path.exists(filename) and os.path.getsize(filename)>=minsize

def rel_filename(filename, rel_file, rel_path=None):
    if rel_path is None:
        rel_path = os.path.dirname(rel_file)
    rel_path = os.path.abspath(rel_path)
    f = os.path.os.path.join(rel_path,filename)
    return os.path.normpath(f)

def rel_pathname(*args, **kwargs):
    return os.path.dirname(rel_filename(*args, **kwargs))


def prepend_ext(filename, ext):
    a = os.path.splitext(filename)
    return a[0] + ext + a[1]

def append_ext(filename, ext):
    return filename + ext

def remove_dir(path):
    if not path:
        return
    if path=='/' or path=='~':
        raise Exception("not allowed to remove: %s" % path)
    shutil.rmtree(path, ignore_errors=True)
    #os.system('rm -rf %s' % path)

def remove_file(path):
    if os.path.exists(path):
        os.remove(path)


