# -*- coding: UTF-8 -*-
import pdb, sys, logging

# class redirecting output to a log
class LoggingIO(object):
    softspace = 0
    def __init__(self, logger):
        self._buf = ["pdb:\n"]
        self._log = logger
    def write(self,msg): self._buf.append(msg)
    def flush(self):
        self._log("".join(self._buf))
        self._buf=["pdb:\n"]
    def __getattr__(self, n):
        logging.critical("Unhandled fileio attr %s", n)

#sys.stderr = LoggingIO(logging.error)

# Python2.5's pdb fails to sys.stdout on exceptions in exec. 
# We need to overload it with the 2.6 implementation.
class P26db(pdb.Pdb):
    def default(self, line):
        if line[:1] == '!': line = line[1:]
        locals = self.curframe.f_locals
        globals = self.curframe.f_globals
        try:
            code = compile(line + '\n', '<stdin>', 'single')
            save_stdout = sys.stdout
            save_stdin = sys.stdin
            #save_displayhook = sys.displayhook
            try:
                sys.stdin = self.stdin
                sys.stdout = self.stdout
                #sys.displayhook = self.displayhook
                exec code in globals, locals
            finally:
                sys.stdout = save_stdout
                sys.stdin = save_stdin
                #sys.displayhook = save_displayhook
        except:
            t, v = sys.exc_info()[:2]
            if type(t) == type(''):
                exc_type_name = t
            else: exc_type_name = t.__name__
            print >>self.stdout, '***', exc_type_name + ':', v

def set_trace():
    P26db(stdin=sys.__stdin__, stdout=LoggingIO(logging.info)).set_trace(sys._getframe())