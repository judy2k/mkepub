def TOOL_TIDY(env):
    def tidy_action(target, source, env):
        cmd = 'tidy -q -config tidy.config -output %(target)s %(source)s' % {
            'target': target[0].get_abspath(),
            'source': source[0].get_abspath(),
        }
        
        ret = sp.call(cmd, shell=True)
        if ret == 2:
            raise sp.CalledProcessError(ret, cmd)
        
    def tidy_emitter(target, source, env):
        source.extend(['tidy.config', 'site_init.py'])
        return target, source
    
    tidy_builder = Builder(action = tidy_action, emitter=tidy_emitter)
    
    env.Append(BUILDERS = {'Tidy' : tidy_builder})


class PythonBuilder(object):
    def __init__(self, name, env):
        builder = Builder(action = self.action, emitter=self.emitter)
        env.Append(BUILDERS = { name: builder })
        
    def emitter(self, target,source, env):
        source.extend(['site_init.py'])
        return target, source

    def action(self, target, source, env):
        raise NotImplementedError('PythonBuilders must implement action()')


class XMLBuilder(PythonBuilder):
    def action(self, target, source, env):
        tree = etree.parse(source[0].get_abspath())
        self.process(tree)
        open(target[0].get_abspath(), 'wb').write(etree.tostring(tree, encoding='utf-8'))
    
    def process(self, tree):
        raise NotImplementedError('XMLBuilders must implement process()')


class Copy(PythonBuilder):
    def action(self, target, source, env):
        shutil.copyfile(source[0].get_abspath(), target[0].get_abspath())