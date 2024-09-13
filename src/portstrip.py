import libportstrip
import libportstrip.psenv

partwork = libportstrip.part.Part("=cat/pkg-1.1-r1")
parsed = partwork.parse()

print(parsed)
print(partwork.cache_rebuild_part(parsed))

shell = libportstrip.psenv.shell.EnvShell()
shell.execcmd("lsenv")
print(shell.died, shell.finish, shell.return_code)
