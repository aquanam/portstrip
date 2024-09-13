"""Envrionmental shell."""

from typing import Any
from . import (__version__, __regional_version__,
               __py_version__)

SHELL_START_ENV: dict[str, Any] = {
                                   "PSVER":         __version__,
                                   "PSENVVER":      __regional_version__,
                                   "PYVER":         __py_version__,
                                  }

class EnvShell:
    def __init__(self) -> None:
        self.died: bool   = False
        self.finish: bool = False
        
        # NOTE: Return code of command executed 
        self.return_code: int = 0
        
        self.env: dict[str, Any] = SHELL_START_ENV
    
    # == shortcuts =
    
    def shreturn(self, retcode: int = 0) -> None:
        """Frontend to modify return command."""
        self.return_code = retcode
    
    # ==============
    
    # == main keyword functionalities =
    
    # die command function: invoked by die
    def die(self) -> None:
        """Set off the 'died' flag."""
        
        self.died = True
        self.shreturn(-1)
    
    # lsenv command function: invoked by lsenv
    def lsenv(self) -> None:
        """List out current environment variables."""
        
        lastval: Any = list(self.env.values())[-1]
        
        for k, v in self.env.items():
            thisval: str = ""
            valtype: Any = type(v)
            out: str     = ""
            
            if valtype is str: thisval = f'"{v}"'
            else:              thisval = v
            
            out = f"{k}={thisval}"
            if v != lastval: out += ' '
            
            print(out, end="")
            
        print()
        self.shreturn()
        
    # =================================
    
    # == command execution =
    
    def execcmd(self, command: str) -> None:
        """Execute a command.
        
        Parameters:
            command [str]: command to execute"""
        
        if self.died:
            # the die flag has been set
            print("psenv: error: die flag has been set")
            
            self.shreturn(-1)
            self.finish = True
            
            return
        
        match command:
            case "die":   self.die()
            case "lsenv": self.lsenv()
            # TODO: Make better error!
            case _:       print("psenv: error: invalid command")
            
        self.finish = True
    
    # ======================
