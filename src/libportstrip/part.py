"""Package parts."""

import copy
from typing import Any

PARSED_OUT_CACHES: dict[str, list[Any]] = {}


class Part:
    def __init__(self, thispart: str) -> None:
        self.thispart: str = thispart

    def __str__(self) -> str:
        return self.thispart

    def change_part(self, new: str) -> None:
        """Brief: Change the part to be used.
        
        Parameters:
            - new [str]: new part

        Alternatives:
            - change the variable with '<obj>.thispart = X'

        Frontend to change the part to be used via changing
        self.thispart. Great if, to save memory, you are not
        creating seperate classes to work with different
        parts."""

        self.thispart = new

    def parse(self, no_cache: bool = False) -> list[Any]:
        """Brief: Parse a part to be more readable.

        Parameters:
            - self.thispart [str]: part to parse
            (self.thispart is initially set by the part
             passed in via __init__)
            
            - no_cache [bool]: disable use of cache

        Cache: PARSED_OUT_CACHES
        
        Parse a part in order to be more readable. Returns a
        list which includes parsed output.

        [0] - The vary specifier. If there is no vary
              specifier in the output then this will be [1]
              instead. Type string.
                  =         => EQ
                  !=        => NE
                  >         => GR
                  <         => LS
                  >=        => GE
                  <=        => LE

        [1] or as [0] - The catpkg (category/package).
                        Type string.
                  X/Y       => [X, Y]
                  X         => [X]

        [2] - The version specifier. If there is no vary
              specifier then this index won't be valid.
              Type list with integer and string (if there
              is a revision).
                  X.Y.Z     => [X, Y, Z]
                  X.Y.Z-rA  => [X, Y, Z, REV(str), A]"""

        if self.thispart in PARSED_OUT_CACHES.keys() and not no_cache:
            return PARSED_OUT_CACHES.get(self.thispart)  # pyright: ignore[reportReturnType]

        part_copy: Any                           = copy.deepcopy(self.thispart)
        curr_parsed: list[str | list[str] | list[str | int]] = []

        _last = len(part_copy) - 1


        # vary spec

        VARYSPEC_EQ = part_copy.startswith('=')   # Equal to
        VARYSPEC_NE = part_copy.startswith('!=')  # Not equal to
        VARYSPEC_GR = part_copy.startswith('>')   # Greater than
        VARYSPEC_LS = part_copy.startswith('<')   # Less than
        VARYSPEC_GE = part_copy.startswith(">=")  # Greater than or equal to
        VARYSPEC_LE = part_copy.startswith("<=")  # Less than or equal to

        NO_VARYSPEC = True not in (VARYSPEC_EQ, VARYSPEC_NE, VARYSPEC_GR,
                                   VARYSPEC_LS, VARYSPEC_GE, VARYSPEC_LE)

        if not NO_VARYSPEC:
            if   VARYSPEC_EQ: curr_parsed.append("EQ")
            elif VARYSPEC_NE: curr_parsed.append("NE")
            elif VARYSPEC_GR: curr_parsed.append("GR")
            elif VARYSPEC_LS: curr_parsed.append("LS")
            elif VARYSPEC_GE: curr_parsed.append("GE")
            elif VARYSPEC_LE: curr_parsed.append("LE")

            # modify part_copy to leave only catpkg and version spec
            part_copy = part_copy[(1 if part_copy[1] != "=" else 2):]


        # version spec

        thisverspec: str                = ""
        copy_verspec: Any               = ""
        verspec_parsed: list[Any]       = []

        VERSPEC_STRT = -1

        for i, c in enumerate(part_copy):
            if c == '-':
                if i != _last and part_copy[i + 1].isdigit():
                    VERSPEC_STRT = i + 1
                    break

            if c == '.':
                raise ValueError(
                    "hanging '.' with uninitialized specifier"
                )
        
        if VERSPEC_STRT == -1 and not NO_VARYSPEC:
            raise ValueError(
                "part needs version specifier"
            )

        if VERSPEC_STRT != -1 and NO_VARYSPEC:
            raise ValueError(
                "part needs vary specifier"
                )

        if not NO_VARYSPEC:
            thisverspec  = part_copy[VERSPEC_STRT:]
            # modify part_copy to leave catpkg
            part_copy    = part_copy[:(VERSPEC_STRT - 1)]
            copy_verspec = copy.deepcopy(thisverspec)

            copy_verspec = copy_verspec.split('-')

            if len(copy_verspec) > 2:
                raise ValueError(
                    "part has more than 2 hyphens in version specifier"
                )

            _version_nums = copy_verspec[0].split('.')
            for i, v in enumerate(_version_nums):
                if i > 2:
                    raise ValueError(
                        "more than 3 version numbers"
                    )

                if not v.isdigit():
                    raise ValueError(
                        "string in version number"
                    )

                verspec_parsed.append(int(v))

            if len(copy_verspec) > 1:
                # TODO: Find more, not just revisions?

                _revision = copy_verspec[1]

                if not _revision.startswith('r'):
                    raise ValueError(
                        "revisions should start with 'r'"
                    )

                _revision = _revision[1:]

                if not _revision.isdigit():
                    raise ValueError(
                        "revisions cannot have a string in them"
                    )

                _revision = int(_revision)

                verspec_parsed.append("REV")
                verspec_parsed.append(_revision)


        # catpkg

        _inv_catpkg: ValueError = ValueError("invalid catpkg")

        if len(part_copy) == 0:
            raise _inv_catpkg

        _catpkg: list[str] = part_copy.split("/")

        _catpkg_ind_one: str = _catpkg[1] if len(_catpkg) == 2 else 'X'
        if _catpkg[0] == '' or _catpkg_ind_one == '':
            raise _inv_catpkg

        if len(_catpkg) > 2:
            raise ValueError(
                "there cannot be more than one catagories"
            )


        # finish

        curr_parsed.append(_catpkg)

        if not NO_VARYSPEC:
            curr_parsed.append(verspec_parsed)

        if not no_cache:
            PARSED_OUT_CACHES.update({self.thispart: curr_parsed})
        
        return curr_parsed

    @staticmethod
    def rebuild_part(parsed_out: list[Any]) -> str:
        """Rebuild a part with a parsed output.
        
        Parameters:
            - parsed_out [list[Any]]: parsed output

        Alternatives:
            - get cached part input from [XCache]
              (or cache_rebuild_part)

        Warn of use:
            This function does not get the cached part
            input from [XCache], nor does it create a
            cached output. If you want to get the part
            from [XCache] then use cache_rebuild_part.
            Depending on your program, only use this
            if you are handling a pre-parsed part not
            in [XCache].
            
        XCache: PARSED_OUT_CACHES"""

        builded_part: str = ""

        catpkg: list[str] = []

        NO_VERSPEC: bool = False
        verspec: list[int | str] = []


        # vary spec & config

        if parsed_out[0] in ("EQ", "NE", "GR",
                             "LS", "GE", "LE"):
            if parsed_out[0] == "EQ":   builded_part += '='
            elif parsed_out[0] == "NE": builded_part += "!="
            elif parsed_out[0] == "GR": builded_part += '>'
            elif parsed_out[0] == "LS": builded_part += '<'
            elif parsed_out[0] == "GE": builded_part += ">="
            elif parsed_out[0] == "LE": builded_part += "<="

            catpkg = parsed_out[1]
        else:
            catpkg = parsed_out[0]

        if type(parsed_out[-1][0]) is int:
            verspec = parsed_out[-1]
        else:
            NO_VERSPEC = True


        # catpkg

        builded_part += catpkg[0]
        if len(catpkg) == 2:
            builded_part += "/" + catpkg[1]


        # version spec

        _last_verspec = len(verspec) - 1

        if not NO_VERSPEC:
            builded_part += '-'

            for i, v in enumerate(verspec):
                if v == "REV":
                    builded_part = builded_part[:-1]
                    builded_part += "-r" + str(verspec[(i + 1)])
                    break

                builded_part += str(v)
                if i != _last_verspec:
                    builded_part += "."


        # finish
        
        return builded_part

    @staticmethod
    def cache_rebuild_part(parsed_out: list[Any]) -> str | None:
        """Rebuild a part using [Cache].
        
        Parameters:
            - parsed_out [list[Any]]: parsed output

        Alternatives:
            - use rebuild_part

        Warn of use:
            This function is not intended for the
            use of pre-parsed parts that are not
            in [Cache]. However, you can use
            rebuild_part, or for a work around, use
            change_part andparse with the rebuilded
            part output which will add the parsed
            output to [Cache], and can be used over
            again with this function using [Cache]. 

        Cache: PARSED_OUT_CACHES"""

        for i, val in enumerate(PARSED_OUT_CACHES.values()):
            if val == parsed_out:
                return list(PARSED_OUT_CACHES.keys())[i]

        return None
